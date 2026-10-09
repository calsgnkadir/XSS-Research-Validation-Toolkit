"""Local acceptance with explicit browser, source hashes and fresh artifacts."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    browser = Path(args.browser)
    if not browser.is_file():
        parser.error('browser executable missing')
    result = here / 'acceptance.xml'
    if result.exists():
        parser.error('acceptance artifact already exists; preserve prior evidence')
    os.chdir(repo)
    os.environ['DXA_BROWSER'] = str(browser)
    os.environ['DXA_REQUIRE_BROWSER'] = '1'
    os.environ.pop('BENCH_ENABLE_DOCKER', None)
    sys.path.insert(0, str(repo / 'tools/dom-xss-analyzer'))
    import dxadom
    dxadom._CHROMIUM_HINTS.insert(0, str(browser))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        instance = pw.chromium.launch(headless=True, executable_path=str(browser))
        browser_version = instance.version
        instance.close()
    sources = sorted(set(repo.glob('bench/**/*.py')) | set(repo.glob('bench/targets/**/*.yml'))
                     | set(repo.glob('tools/dom-xss-analyzer/*.py')))
    hashes = {p.relative_to(repo).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sources}
    environment = {
        'python': platform.python_version(), 'platform': platform.platform(),
        'pytest': importlib.metadata.version('pytest'),
        'playwright': importlib.metadata.version('playwright'),
        'browser_version': browser_version, 'browser_required': True,
        'docker_enabled': False,
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'browser_discovery': 'explicit installed Chrome prepended to hints for test process',
        'source_sha256': hashes,
    }
    (here / 'environment.json').write_text(json.dumps(environment, indent=2), encoding='utf-8')
    import pytest
    code = pytest.main(['tools/dom-xss-analyzer', 'bench', '-q', '-ra', '-p',
                       'no:cacheprovider', '--tb=short', '--junitxml=' + str(result)])
    tree = ET.parse(result)
    suites = list(tree.getroot().iter('testsuite'))
    summary = {key: sum(int(s.attrib.get(key, 0)) for s in suites)
               for key in ('tests', 'failures', 'errors', 'skipped')}
    summary['pytest_exit'] = int(code)
    summary['source_unchanged_during_run'] = all(
        hashlib.sha256((repo / path).read_bytes()).hexdigest() == digest
        for path, digest in hashes.items())
    (here / 'acceptance-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return int(code) or int(summary['skipped'] > 0 or not summary['source_unchanged_during_run'])


if __name__ == '__main__':
    raise SystemExit(main())
