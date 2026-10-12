"""Run two privacy regressions against the pre-fix committed exporter in memory."""
import json
from pathlib import Path
import subprocess
import sys
import types
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = 'c5d5451cc81dc94ce65aab330e3925a3a6150c04'
xml_path = OUT / 'before.xml'
if xml_path.exists():
    raise SystemExit('Existing before.xml preserved')
source = subprocess.check_output(['git', 'show', BASE + ':tools/dom-xss-analyzer/dxa_evidence.py'], cwd=ROOT, text=True)
module = types.ModuleType('dxa_evidence')
sys.modules['dxa_evidence'] = module
exec(compile(source, '<committed-exporter>', 'exec'), module.__dict__)
tests = 'tools/dom-xss-analyzer/test_report_privacy.py'
args = [tests + '::test_known_credential_fields_are_redacted_in_sharing_copies[api_key]',
        tests + '::test_evidence_links_preserve_location_but_remove_url_credentials',
        '-q', '-p', 'no:cacheprovider', '--tb=short', '--junitxml=' + str(xml_path.relative_to(ROOT))]
result = pytest.main(args)
tree = ET.parse(xml_path)
for element in tree.iter():
    element.attrib.pop('hostname', None)
tree.write(xml_path, encoding='utf-8', xml_declaration=True)
suites = list(tree.iter('testsuite'))
counts = {key: sum(int(s.get(key, 0)) for s in suites) for key in ('tests', 'failures', 'errors', 'skipped')}
(OUT / 'before-summary.json').write_text(json.dumps({'base_commit': BASE, 'pytest_exit': int(result), 'junit': counts,
    'scope': 'Fake credential sentinels only; old module loaded from git show into memory; worktree unchanged.'}, indent=2) + '\n', encoding='utf-8')
raise SystemExit(0 if int(result) == 1 and counts == {'tests': 2, 'failures': 2, 'errors': 0, 'skipped': 0} else 1)
