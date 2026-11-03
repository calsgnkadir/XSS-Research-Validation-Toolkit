"""Reproduce bounded R8 acceptance; source-signal labels are not XSS labels."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PRIVATE = ROOT / '.dxa/r8-followup-20261103'
FILES = [
    'test_static_r8_followup.py', 'test_static_python_helpers.py',
    'test_static_leaflet.py', 'test_static_jsx_href.py',
    'test_static_inline_messages.py', 'test_static_receiver_bindings.py',
    'test_dxa.py', 'test_static_context.py', 'test_dxa_config.py',
    'test_r8_sanitizer.py', 'test_r8_ast_pilot.py', 'test_sarif.py',
    'test_r6_cli_modes.py',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(path):
    result = dict.fromkeys(('tests', 'failures', 'errors', 'skipped'), 0)
    for suite in ET.parse(path).getroot().iter('testsuite'):
        for key in result:
            result[key] += int(suite.get(key, 0))
    result['passed'] = result['tests'] - sum(result[k] for k in ('failures', 'errors', 'skipped'))
    return result


def run(args):
    return subprocess.run([str(a) for a in args], cwd=ROOT).returncode


def main():
    PRIVATE.mkdir(parents=True, exist_ok=True)
    paths = ['tools/dom-xss-analyzer/' + name for name in FILES]
    identities = ['tools/dom-xss-analyzer/dxa.py',
                  str(HERE.relative_to(ROOT) / 'measure.py')] + paths
    hashes = {p: digest(ROOT / p) for p in identities}
    code = run([sys.executable, '-m', 'pytest', *paths, '-q', '-p', 'no:cacheprovider',
                '--tb=short', '--junitxml=' + str(PRIVATE / 'combined.xml')])
    fixed = counts(PRIVATE / 'combined.xml')
    measurement = run([sys.executable, HERE / 'measure.py', '--scanner',
                       ROOT / 'tools/dom-xss-analyzer/dxa.py', '--out',
                       HERE / 'measurement-final.json'])
    self_scan = run([sys.executable, 'bench/ci_self_scan.py'])
    if any(digest(ROOT / p) != value for p, value in hashes.items()):
        raise RuntimeError('Acceptance source/test/measurement changed during run')
    result = {
        'roadmap': 'R8', 'base_commit': '1c01c69',
        'environment': {'os': platform.system(), 'python': platform.python_version()},
        'source_sha256': hashes, 'fixed': fixed, 'pytest_exit': code,
        'measurement_exit': measurement, 'local_self_scan_exit': self_scan,
        'release_status': 'unreleased; PyPI 0.2.2 unchanged',
        'hosted_ci': 'not checked', 'evidence_level': 'candidate', 'triage': 'unreviewed',
        'limits': 'Local synthetic sources; no application/HTTP/browser or general accuracy claim',
    }
    (HERE / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return int(code != 0 or measurement != 0 or self_scan != 0 or any(
        fixed[k] for k in ('failures', 'errors', 'skipped')))


if __name__ == '__main__':
    raise SystemExit(main())
