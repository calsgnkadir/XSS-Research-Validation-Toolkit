"""Run bounded R4 ingress regression/live acceptance and retain sanitized evidence."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'bench'))

def docker_inventory():
    commands = {'containers': ['ps','-a','--no-trunc','--format','{{.ID}} {{.Names}}'],
                'volumes': ['volume','ls','--format','{{.Name}}'],
                'networks': ['network','ls','--no-trunc','--format','{{.ID}} {{.Name}}']}
    return {k: sorted(subprocess.run(['docker', *v], capture_output=True, text=True,
                                    check=True, timeout=20).stdout.splitlines()) for k,v in commands.items()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--browser')
    args = parser.parse_args()
    paths = ['bench/bludit_adapter.py','bench/bludit_ingress.py',
             'bench/test_bludit_adapter.py','bench/test_bludit_ingress.py',
             'bench/targets/bludit/local-inspected.yml','.github/workflows/ci.yml','audit/2026-10-12-r4-ingress-live/run_validation.py']
    hashes = lambda: {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    before = hashes()
    result = {'base_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'python': platform.python_version(), 'platform': platform.system(), 'source_hashes': before}
    if not args.live:
        command = [sys.executable,'-m','pytest','bench/test_bludit_adapter.py','bench/test_bludit_ingress.py',
                   'bench/test_bench.py','bench/test_proof_adapter.py','bench/test_ci_self_scan.py',
                   'bench/test_ci_acceptance.py','-q','-p','no:cacheprovider','--tb=short',
                   '--junitxml='+str(OUT/'acceptance.xml')]
        started = time.monotonic()
        run = subprocess.run(command,cwd=ROOT,timeout=180,capture_output=True,text=True)
        print(run.stdout); print(run.stderr)
        tree = ET.parse(OUT/'acceptance.xml')
        suites = list(tree.getroot().iter('testsuite'))
        totals = {k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
        result.update(test_command=command[1:],exit_code=run.returncode,totals=totals,elapsed_seconds=round(time.monotonic()-started,2))
        passed = run.returncode==0 and totals['tests']>0 and all(totals[k]==0 for k in ('failures','errors','skipped'))
        filename = 'acceptance.json'
    else:
        import bludit_adapter as adapter
        baseline = docker_inventory()
        private = ROOT/'.dxa/r4-ingress-resume'/('acceptance-'+uuid.uuid4().hex)
        private.mkdir(parents=True,exist_ok=True)
        (private/'live-before.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
        def mismatch(origin,cases,browser):
            proof = adapter.observe_cases(origin,cases,browser)
            proof['cases'][0].update(execution_observed=False,status='no-execution-observed')
            return proof
        cases = [('success',None,args.browser),('missing-browser',None,str(private/'missing-browser.exe')),
                 ('control-mismatch',mismatch,args.browser)]
        runs = {}
        for name, proof_runner, browser in cases:
            report = adapter.BluditAdapter(proof_runner=proof_runner).run(private/name,browser)
            runs[name] = report
            (OUT/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({'run':name,'status':report['status'],'events':report['events'],'cleanup':report['cleanup_status']}),flush=True)
            if report['cleanup_status']!='passed': break
        success = runs.get('success', {})
        rows = success.get('cases', [])
        positive_control = (success.get('session') == {'session_checked':True,'author':'admin','role_verified':False}
            and success.get('triage') == 'by-design' and len(rows)==2
            and [r.get('case_id') for r in rows]==['raw-admin-content','escaped-admin-content']
            and [r.get('expected_execution') for r in rows]==[True,False]
            and [r.get('execution_observed') for r in rows]==[True,False]
            and all(r.get('matched') is True for r in rows))
        mismatch_rows = runs.get('control-mismatch',{}).get('cases',[])
        negative_control = (len(mismatch_rows)==2
            and [r.get('execution_observed') for r in mismatch_rows]==[False,False]
            and [r.get('matched') for r in mismatch_rows]==[False,True])
        snapshots = {}
        for name in runs:
            snapshot = json.loads((private/name/'observations.json').read_text(encoding='utf-8'))
            snapshots[name] = snapshot.get('cleanup_status')=='pending' and snapshot.get('status')==('awaiting-cleanup' if name=='success' else 'error')
        after = docker_inventory()
        preservation = {k:{'before':len(baseline[k]),'after':len(after[k]),'exact_match':baseline[k]==after[k]} for k in baseline}
        passed = len(runs)==3 and runs['success']['status']=='passed' and all(r['cleanup_status']=='passed' for r in runs.values()) and all(v['exact_match'] for v in preservation.values())
        passed = passed and runs['missing-browser']['status']=='error' and runs['missing-browser']['events']==[{'stage':'browser','kind':'error','reason':'browser-unavailable'}]
        passed = passed and runs['control-mismatch']['status']=='error' and runs['control-mismatch']['events']==[{'stage':'acceptance','kind':'error','reason':'control-mismatch'}]
        result.update(preservation=preservation,runs={k:{'status':v['status'],'cleanup':v['cleanup_status'],'events':v['events']} for k,v in runs.items()})
        passed = passed and positive_control and negative_control and all(snapshots.values())
        result.update(positive_control=positive_control,negative_control=negative_control,pre_cleanup_snapshots=snapshots)
        filename='live-acceptance.json'
    result['sources_unchanged'] = before==hashes()
    result['accepted'] = passed and result['sources_unchanged']
    (OUT/filename).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return 0 if result['accepted'] else 1

if __name__=='__main__':
    raise SystemExit(main())
