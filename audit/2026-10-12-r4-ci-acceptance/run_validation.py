"""Record focused integration acceptance; preserve existing evidence files."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FILES = [
    '.github/workflows/ci.yml', 'bench/check_ci_acceptance.py',
    'bench/test_ci_acceptance.py', 'bench/run.py', 'bench/process_control.py',
    'bench/proof_worker.py', 'bench/test_proof_adapter.py',
    'bench/test_proof_corpus.py', 'tools/dom-xss-analyzer/dxaprove.py',
    'tools/dom-xss-analyzer/dxa_proof_lab.py',
    'tools/dom-xss-analyzer/test_browser_proof.py',
    'tools/dom-xss-analyzer/test_proof_cleanup.py',
]

def hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES}

if (OUT / 'acceptance.json').exists() or (OUT / 'integration.xml').exists():
    raise SystemExit('Existing acceptance evidence preserved; choose a new output location.')
before = hashes()
prefix = OUT.relative_to(ROOT).as_posix()
commands = [
    [sys.executable, '-m', 'pytest', 'bench/test_ci_acceptance.py',
     'bench/test_ci_self_scan.py', 'bench/test_bench.py', 'bench/test_proof_adapter.py',
     '-q', '-p', 'no:cacheprovider', '--tb=short', f'--junitxml={prefix}/integration.xml'],
    [sys.executable, 'bench/check_ci_acceptance.py', '--junit', f'{prefix}/browser-acceptance.xml',
     '--corpus', f'{prefix}/proof.json', '--demo', f'{prefix}/demo/result.json'],
]
results = []
for command in commands:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    results.append({'command': ['python', *command[1:]], 'exit_code': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr})
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)
for name in ('browser-acceptance.xml', 'integration.xml'):
    path = OUT / name
    if path.exists():
        tree = ET.parse(path)
        for element in tree.iter():
            element.attrib.pop('hostname', None)
        tree.write(path, encoding='utf-8', xml_declaration=True)
after = hashes()
record = {'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'python': platform.python_version(), 'platform': platform.system(),
          'commands': results, 'source_sha256': before, 'source_unchanged_during_integration': before == after,
          'browser_evidence_note': 'Browser suite, strict corpus and demo were run earlier in this session; this script validates their artifacts, not a new browser run.',
          'remote_artifact_accepted': False}
(OUT / 'acceptance.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
raise SystemExit(0 if before == after and all(r['exit_code'] == 0 for r in results) else 1)
