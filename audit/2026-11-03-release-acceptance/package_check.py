"""Offline local artifact/isolated-install gate; never publishes a package."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MODULES = ('dxa', 'dxadyn', 'dxaprove', 'dxadom', 'dxa_evidence',
           'dxa_callback', 'dxa_attempts', 'dxa_proof_lab', 'dxa2dyn',
           'dxa_sarif', 'dxa_sarif_cli')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output already exists')
    private = ROOT / '.dxa/release-acceptance-package'
    private.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix='run-', dir=private))
    paths = [ROOT / 'tools/dom-xss-analyzer' / (name + '.py') for name in MODULES]
    paths += [ROOT / 'pyproject.toml', ROOT / 'bench/check_installed_cli.py', Path(__file__),
              ROOT / 'audit/2026-11-03-r8-m1/cases.json',
              ROOT / 'audit/2026-11-03-r8-m1/split-manifest.json']
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in paths}
    result = {'roadmap': 'R6/R8-M1', 'source_commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'python': platform.python_version(), 'platform': platform.system(),
        'source_sha256': hashes, 'commands': [], 'accepted': False,
        'limits': ['Local unreleased build; version metadata remains 0.2.2',
                   'No PyPI/GitHub publication or hosted CI check',
                   'Synthetic static JSX candidates; no XSS/browser claim']}

    def run(command, *, cwd=ROOT):
        record = {'argv': [str(arg).replace(str(run_dir), '<run>').replace(
            str(ROOT), '<repo>').replace(sys.executable, '<python>') for arg in command],
            'cwd': 'outside-source' if cwd != ROOT else '<repo>'}
        result['commands'].append(record)
        proc = subprocess.run(list(map(str, command)), cwd=cwd, capture_output=True,
                              text=True, timeout=180)
        record['exit_code'] = proc.returncode
        (run_dir / ('command-%02d.log' % len(result['commands']))).write_text(
            proc.stdout + proc.stderr, encoding='utf-8')
        if proc.returncode:
            raise RuntimeError('Command %d failed, exit %d (private log)' % (
                len(result['commands']), proc.returncode))
        return proc

    try:
        dist = run_dir / 'dist'
        dist.mkdir()
        # Use the declared PEP 517 backend directly without environment/index
        # resolution. The system interpreter has setuptools and wheel; an
        # installed `build` frontend is not required by this offline gate.
        for method in ('build_sdist', 'build_wheel'):
            run([sys.executable, '-c',
                 'import setuptools.build_meta as b,sys; '
                 'output=sys.argv[1]; print(b.' + method + '(output))', dist])
        wheel, = dist.glob('*.whl')
        sdist, = dist.glob('*.tar.gz')
        result['artifact_sha256'] = {p.name: digest(p) for p in (wheel, sdist)}
        with zipfile.ZipFile(wheel) as archive:
            for name in MODULES:
                assert hashlib.sha256(archive.read(name + '.py')).hexdigest() == hashes[
                    'tools/dom-xss-analyzer/' + name + '.py'], name
        with tarfile.open(sdist) as archive:
            for name in MODULES:
                member, = [m for m in archive.getmembers() if m.name.endswith(
                    '/tools/dom-xss-analyzer/' + name + '.py')]
                assert hashlib.sha256(archive.extractfile(member).read()).hexdigest() == hashes[
                    'tools/dom-xss-analyzer/' + name + '.py'], name
        environment = run_dir / 'venv'
        run([sys.executable, '-m', 'venv', environment])
        bin_dir = environment / ('Scripts' if platform.system() == 'Windows' else 'bin')
        python = bin_dir / ('python.exe' if platform.system() == 'Windows' else 'python')
        run([python, '-m', 'pip', 'install', '--no-index', '--no-deps', wheel])
        installed_result = run_dir / 'installed.json'
        run([sys.executable, ROOT / 'bench/check_installed_cli.py', '--bin-dir',
             bin_dir, '--wheel', wheel, '--output', installed_result])
        installed = json.loads(installed_result.read_text(encoding='utf-8'))
        result['installed_checks'] = installed['results']
        result['installed_module_sha256'] = installed['packaged_module_sha256']
        cases = json.loads((ROOT / 'audit/2026-11-03-r8-m1/cases.json').read_text(encoding='utf-8'))['cases']
        executable = bin_dir / ('dxa.exe' if platform.system() == 'Windows' else 'dxa')
        with tempfile.TemporaryDirectory(prefix='dxa-installed-jsx-') as temp:
            outside = Path(temp)
            result['installed_jsx'] = {}
            for case in cases:
                source = outside / (case['id'] + '.' + case['extension'])
                source.write_text(case['source'], encoding='utf-8')
                proc = subprocess.run([str(executable), str(source), '--json'],
                                      cwd=outside, capture_output=True, text=True, timeout=30)
                rows = json.loads(proc.stdout)
                candidates = [row for row in rows if row.get('sink') == 'jsx-href']
                expected = case['expected_candidates']
                assert len(candidates) == expected, case['id']
                assert proc.returncode == (1 if rows else 0), case['id']
                if expected:
                    assert candidates[0]['line'] == case['expected_line'], case['id']
                    assert candidates[0]['confidence'] == case['expected_confidence'], case['id']
                result['installed_jsx'][case['id']] = {'exit_code': proc.returncode,
                    'expected_candidates': expected, 'observed_candidates': len(candidates)}
        assert all(digest(ROOT / path) == value for path, value in hashes.items())
        result['source_unchanged'] = True
        result['accepted'] = True
    except Exception as exc:
        result['error'] = str(exc).replace(str(ROOT), '<repo>')
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'accepted': result['accepted'], 'error': result.get('error'),
                      'installed_checks': len(result.get('installed_checks', {})),
                      'jsx_cases': len(result.get('installed_jsx', {}))}))
    return 0 if result['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
