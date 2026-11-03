"""Repeat local R8-M1 verification; historical first evaluation stays immutable."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FILES = [
    'test_static_m1.py', 'test_m1_parser_boundaries.py',
    'test_static_r8_followup.py', 'test_static_python_helpers.py',
    'test_static_leaflet.py', 'test_static_jsx_href.py',
    'test_static_inline_messages.py', 'test_static_receiver_bindings.py',
    'test_dxa.py', 'test_static_context.py', 'test_dxa_config.py',
    'test_r8_sanitizer.py', 'test_r8_ast_pilot.py', 'test_sarif.py',
    'test_r6_cli_modes.py',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='New result file; refuses overwrite')
    args = parser.parse_args()
    if args.out and args.out.exists():
        parser.error('Result already exists; choose a new output file')
    private = ROOT / '.dxa/r8-m1'
    private.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix='acceptance-', dir=private))
    identities = [ROOT / 'tools/dom-xss-analyzer/dxa.py',
                  HERE / 'cases.json', HERE / 'split-manifest.json',
                  HERE / 'measure.py', Path(__file__)]
    identities += [ROOT / 'tools/dom-xss-analyzer' / name for name in FILES]
    hashes = {str(path.relative_to(ROOT)): digest(path) for path in identities}
    command = [sys.executable, '-m', 'pytest',
               *['tools/dom-xss-analyzer/' + name for name in FILES],
               '-q', '-p', 'no:cacheprovider', '--tb=short',
               '--junitxml=' + str(run_dir / 'combined.xml')]
    tested = subprocess.run(command, cwd=ROOT).returncode
    counts = dict.fromkeys(('tests', 'failures', 'errors', 'skipped'), 0)
    for suite in ET.parse(run_dir / 'combined.xml').getroot().iter('testsuite'):
        for key in counts:
            counts[key] += int(suite.get(key, 0))
    counts['passed'] = counts['tests'] - sum(counts[key] for key in
                                            ('failures', 'errors', 'skipped'))
    measured = subprocess.run([
        sys.executable, str(HERE / 'measure.py'), '--out',
        str(run_dir / 'measurement-repeat.json')], cwd=ROOT).returncode
    measurement = json.loads((run_dir / 'measurement-repeat.json').read_text(encoding='utf-8'))
    self_scan = subprocess.run([sys.executable, 'bench/ci_self_scan.py'], cwd=ROOT).returncode
    if any(digest(ROOT / path) != value for path, value in hashes.items()):
        raise RuntimeError('Source, tests or measurement changed during acceptance')
    success = (tested == measured == self_scan == 0
               and not any(counts[key] for key in ('failures', 'errors', 'skipped'))
               and not any(row['property_mismatches'] for row in measurement['counts'].values()))
    result = {
        'roadmap': 'R8-M1', 'base_commit': '220bbd2',
        'environment': {'os': platform.system(), 'python': platform.python_version()},
        'source_sha256': hashes, 'tests': counts, 'pytest_exit': tested,
        'measurement_exit': measured, 'measurement_counts': measurement['counts'],
        'local_self_scan_exit': self_scan, 'accepted': success,
        'evaluation': 'Repeat of frozen cases; first evaluation is recorded separately in final.json',
        'limits': 'Local synthetic source only; no app/HTTP/browser, general accuracy or user-time claim',
        'release': 'Unreleased source; PyPI 0.2.2 unchanged', 'hosted_ci': 'not checked',
    }
    destination = args.out or run_dir / 'result.json'
    with destination.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'tests': counts, 'accepted': success}))
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
