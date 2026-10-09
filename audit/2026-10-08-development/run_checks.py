"""Run local acceptance with explicit browser and retain per-file JUnit counts."""
import argparse
import json
import os
from pathlib import Path
import platform
import sys
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--browser')
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    if not args.name.replace('-', '').replace('_', '').isalnum():
        parser.error('name must be an artifact basename')
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    os.chdir(repo)
    os.environ.pop('BENCH_ENABLE_DOCKER', None)
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.path.insert(0, str(repo / 'tools/dom-xss-analyzer'))
    if args.browser:
        if not Path(args.browser).is_file():
            parser.error('browser does not exist')
        os.environ['DXA_BROWSER'] = args.browser
        os.environ['DXA_REQUIRE_BROWSER'] = '1'
        import dxadom
        dxadom._CHROMIUM_HINTS.insert(0, args.browser)
    import pytest
    raw_dir = repo / '.dxa/2026-10-08-development'
    raw_dir.mkdir(parents=True, exist_ok=True)
    junit = raw_dir / (args.name + '.xml')
    result = pytest.main([*args.paths, '-q', '-p', 'no:cacheprovider',
                          '--tb=short', '--junitxml=' + str(junit)])
    counts = {}
    if junit.exists():
        tree = ET.parse(junit)
        for case in tree.iter('testcase'):
            module = case.get('classname', '').split('.Test', 1)[0]
            row = counts.setdefault(module, dict(tests=0, passed=0, failures=0,
                                                errors=0, skipped=0))
            row['tests'] += 1
            state = ('failures' if case.find('failure') is not None else
                     'errors' if case.find('error') is not None else
                     'skipped' if case.find('skipped') is not None else 'passed')
            row[state] += 1
        for suite in tree.iter('testsuite'):
            suite.set('hostname', 'local-windows')
        # Keep raw failures locally; the structured summary carries acceptance counts.
        if result == 0:
            tree.write(here / (args.name + '.xml'), encoding='utf-8', xml_declaration=True)
    summary = dict(exit_code=int(result), python=platform.python_version(),
                   browser_required=bool(args.browser), docker_enabled=False,
                   paths=args.paths, modules=counts)
    (here / (args.name + '-summary.json')).write_text(
        json.dumps(summary, indent=2), encoding='utf-8')
    return int(result)


if __name__ == '__main__':
    raise SystemExit(main())
