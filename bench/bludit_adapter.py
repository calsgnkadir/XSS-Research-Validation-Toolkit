"""R4 disposable pinned Bludit adapter; admin-authored controls, not CVE tests."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import hashlib
import html
from html.parser import HTMLParser
import http.cookiejar
import json
from pathlib import Path
import re
import secrets
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

PINNED_IMAGE = 'sha256:7eb101cdb879f549d6e0088b13c07afa231292e9e15eeff741491abeafb3ebb8'
DEFAULT_COMPOSE = Path(__file__).parent / 'targets/bludit/local-inspected.yml'

class AdapterError(Exception):
    def __init__(self, stage, code):
        self.stage, self.code = stage, code
        super().__init__(code)

def require(ok, stage, code):
    if not ok:
        raise AdapterError(stage, code)

def parse_port(text):
    match = re.fullmatch(r'127\.0\.0\.1:([0-9]{1,5})', text.strip())
    require(match is not None, 'port', 'invalid-loopback-port')
    port = int(match[1])
    require(1 <= port <= 65535, 'port', 'invalid-loopback-port')
    return f'http://127.0.0.1:{port}'

def validate_config(config, project, image=PINNED_IMAGE):
    require(set(config) <= {'name', 'services', 'networks'}, 'preflight', 'unsupported-compose-resource')
    require(set(config.get('services', {})) == {'bludit'}, 'preflight', 'single-service-required')
    s = config['services']['bludit']
    require(set(s) <= {'image','pull_policy','restart','ports','networks','healthcheck','command','entrypoint'}, 'preflight', 'unsupported-service-option')
    require(s.get('image') == image and s.get('pull_policy') == 'never' and s.get('restart') == 'no', 'preflight', 'immutable-image-required')
    require(s.get('command') is None and s.get('entrypoint') is None, 'preflight', 'image-default-command-required')
    ports = s.get('ports', [])
    require(len(ports) == 1, 'preflight', 'single-port-required')
    p = ports[0]
    require(p.get('host_ip') == '127.0.0.1' and str(p.get('target')) == '80' and p.get('protocol','tcp') == 'tcp' and p.get('published') in (None,'',0,'0'), 'preflight', 'ephemeral-loopback-required')
    require(set(s.get('networks', {})) == {'isolated'}, 'preflight', 'isolated-network-required')
    networks = config.get('networks', {})
    require(set(networks) == {'isolated'}, 'preflight', 'single-network-required')
    n = networks['isolated']
    require(set(n) <= {'name','internal','driver','ipam'} and not n.get('ipam') and n.get('internal') is True and n.get('driver','bridge') == 'bridge' and n.get('name',project+'_isolated') == project+'_isolated', 'preflight', 'owned-internal-network-required')
    h = s.get('healthcheck', {})
    require(h.get('test') == ['CMD','curl','-f','http://localhost/'], 'preflight', 'reviewed-healthcheck-required')

def validate_inspect(container, project, image=PINNED_IMAGE):
    labels = container.get('Config', {}).get('Labels') or {}
    require(labels.get('com.docker.compose.project') == project and labels.get('com.docker.compose.service') == 'bludit', 'ownership', 'foreign-container')
    require(container.get('Image') == image and not container.get('Mounts'), 'ownership', 'image-or-mount-mismatch')
    host = container.get('HostConfig', {})
    require(not host.get('Privileged') and host.get('NetworkMode') == project+'_isolated', 'ownership','unsafe-runtime')
    require(container.get('State', {}).get('Running') is True, 'readiness','container-not-running')
    ports = container.get('NetworkSettings', {}).get('Ports', {})
    require(set(ports) == {'80/tcp'} and isinstance(ports['80/tcp'],list) and len(ports['80/tcp']) == 1, 'port','unexpected-port-map')
    p = ports['80/tcp'][0]
    return parse_port(str(p.get('HostIp',''))+':'+str(p.get('HostPort','')))

@dataclass
class Response:
    status: int
    body: str
    url: str
    headers: dict

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

class HTTPClient:
    def __init__(self, origin):
        require(parse_port(urllib.parse.urlsplit(origin).netloc) == origin, 'scope','invalid-origin')
        self.origin = origin
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), _NoRedirect())
    def request(self, path, data=None):
        url = urllib.parse.urljoin(self.origin+'/', path)
        require(urllib.parse.urlsplit(url).netloc == urllib.parse.urlsplit(self.origin).netloc and url.startswith(self.origin+'/'), 'scope','foreign-url')
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        request = urllib.request.Request(url, data=body, headers={'Accept-Language':'en','User-Agent':'DXA-R4-local-adapter'})
        try:
            response = self.opener.open(request, timeout=5)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read(2_000_001)
            require(len(raw) <= 2_000_000, 'http','response-too-large')
            return Response(response.code, raw.decode('utf-8','replace'), response.url, dict(response.headers))

class Form(HTMLParser):
    def __init__(self, body):
        super().__init__(); self.fields = {}; self.admin_author = False
        self.feed(body)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('input','textarea'):
            if a.get('name'):
                self.fields[a['name']] = a.get('value','')
            if tag == 'input' and 'disabled' in a and a.get('value') == 'admin':
                self.admin_author = True

def redirect(response, origin, path, stage):
    location = response.headers.get('Location', response.headers.get('location',''))
    require(response.status in (301,302,303) and urllib.parse.urljoin(origin+'/',location) == origin+path, stage, 'unexpected-redirect')

def authenticated_form(client):
    response = client.request('/admin/new-content')
    form = Form(response.body)
    require(response.status == 200 and {'tokenCSRF','content','title','uuid'} <= set(form.fields) and bool(form.fields['tokenCSRF']) and form.admin_author and 'password' not in form.fields, 'login','session-not-verified')
    return form.fields

def bootstrap(client):
    page = client.request('/install.php?language=en')
    require(page.status == 200 and {'password','timezone'} <= set(Form(page.body).fields) and 'Bludit' in page.body, 'bootstrap','fresh-installer-required')
    password = secrets.token_urlsafe(30)
    response = client.request('/install.php?language=en', {'password':password,'timezone':'UTC'})
    redirect(response, client.origin, '/', 'bootstrap')
    # Discard installer cookies and prove an independent login is required.
    client = HTTPClient(client.origin) if isinstance(client, HTTPClient) else client
    redirect(client.request('/admin/new-content'), client.origin, '/admin/login', 'login')
    page = client.request('/admin/login')
    fields = Form(page.body).fields
    require(page.status == 200 and bool(fields.get('tokenCSRF')) and {'username','password'} <= set(fields), 'login','login-form-unavailable')
    response = client.request('/admin/login', {'username':'admin','password':password,'tokenCSRF':fields['tokenCSRF']})
    redirect(response, client.origin, '/admin/dashboard', 'login')
    authenticated_form(client)
    return client, {'session_checked':True,'author':'admin','role_verified':False}

def seed_cases(client, run_id):
    cases = []
    for case_id, positive in (('raw-admin-content',True),('escaped-admin-content',False)):
        cid = 'dxa'+secrets.token_hex(16)
        payload = '<img src="/__dxa_missing_'+cid+'" onerror="window.__dxaProof=\''+cid+'\'">'
        content = payload if positive else html.escape(payload)
        slug = 'dxa-'+run_id+'-'+('raw' if positive else 'escaped')
        fields = authenticated_form(client)
        response = client.request('/admin/new-content', {'tokenCSRF':fields['tokenCSRF'],'uuid':fields['uuid'],'title':slug,'slug':slug,'type':'published','content':content})
        redirect(response,client.origin,'/admin/content','submit')
        page = client.request('/'+slug)
        require(page.status == 200 and content in page.body, 'submit','fixture-readback-mismatch')
        cases.append({'case_id':case_id,'path':'/'+slug,'canary_id':cid,'expected_execution':positive,'payload_sha256':hashlib.sha256(content.encode()).hexdigest(),'triage':'by-design','read_status':page.status})
    return cases

def observe_cases(origin, cases, browser=None):
    from playwright.sync_api import sync_playwright
    observations=[]
    with sync_playwright() as pw:
        launch={'headless':True}
        if browser: launch['executable_path']=str(browser)
        engine=pw.chromium.launch(**launch)
        try:
            version=engine.version
            for case in cases:
                context=engine.new_context(service_workers='block')
                try:
                    def route(request_route):
                        url=request_route.request.url
                        if urllib.parse.urlsplit(url).scheme == 'http' and urllib.parse.urlsplit(url).netloc == urllib.parse.urlsplit(origin).netloc:
                            request_route.continue_()
                        else: request_route.abort()
                    context.route('**/*',route)
                    # WebSockets are unnecessary for these static public fixtures.
                    context.route_web_socket('**/*',lambda ws: ws.close())
                    page=context.new_page()
                    page.on('dialog',lambda dialog: dialog.dismiss())
                    response=page.goto(origin+case['path'],wait_until='load',timeout=10000)
                    require(response is not None and response.status == 200 and page.url == origin+case['path'], 'browser','reader-unavailable')
                    observed=False
                    for _ in range(40):
                        observed=page.evaluate('() => window.__dxaProof || null') == case['canary_id']
                        if observed: break
                        page.wait_for_timeout(25)
                    observations.append({**case,'execution_observed':observed,'status':'execution-observed' if observed else 'no-execution-observed','observation_ms':1000,'matched':observed == case['expected_execution']})
                finally: context.close()
        finally: engine.close()
    return {'browser_version':version,'cases':observations}

def validate_proof(proof, expected):
    require(isinstance(proof, dict), 'acceptance', 'invalid-proof')
    rows = proof.get('cases')
    require(isinstance(rows, list) and len(rows) == len(expected) == 2,
            'acceptance', 'invalid-proof')
    version = proof.get('browser_version')
    require(isinstance(version, str) and re.fullmatch(r'[0-9.]{1,60}', version),
            'acceptance', 'invalid-browser-version')
    clean = []
    for row, case in zip(rows, expected):
        require(isinstance(row, dict) and all(row.get(k) == case[k] for k in
                ('case_id', 'path', 'canary_id', 'expected_execution', 'payload_sha256', 'triage', 'read_status')),
                'acceptance', 'proof-case-mismatch')
        observed = row.get('execution_observed')
        require(type(observed) is bool and type(row.get('expected_execution')) is bool
                and row.get('status') == ('execution-observed' if observed else 'no-execution-observed')
                and row.get('observation_ms') == 1000,
                'acceptance', 'invalid-observation')
        clean.append({**case, 'execution_observed': observed, 'status': row['status'],
                      'observation_ms': 1000, 'matched': observed == case['expected_execution']})
    return {'browser_version': version, 'cases': clean}

class BluditAdapter:
    def __init__(self, compose_file=DEFAULT_COMPOSE, *, run_command=None, client_factory=None, proof_runner=None, project=None):
        self.compose_file=str(Path(compose_file).resolve())
        self.run_command=run_command or subprocess.run
        self.client_factory=client_factory or HTTPClient
        self.proof_runner=proof_runner or observe_cases
        self.project=project or 'dxa-bludit-'+uuid.uuid4().hex
        require(re.fullmatch(r'dxa-bludit-[a-f0-9]{32}',self.project) is not None,'preflight','invalid-project-name')
        self.owned=False
    def command(self,args,stage,timeout=30):
        try: result=self.run_command(['docker',*args],capture_output=True,text=True,timeout=timeout,check=False)
        except subprocess.TimeoutExpired: raise AdapterError(stage,'command-timeout') from None
        except Exception: raise AdapterError(stage,'command-unavailable') from None
        require(result.returncode == 0,stage,'command-failed')
        return result.stdout
    def compose(self,args,stage,timeout=30):
        return self.command(['compose','-p',self.project,'-f',self.compose_file,*args],stage,timeout)
    def preflight(self):
        config=json.loads(self.compose(['config','--format','json'],'preflight'))
        validate_config(config,self.project)
        image=json.loads(self.command(['image','inspect',PINNED_IMAGE],'preflight'))
        require(len(image)==1 and image[0].get('Id')==PINNED_IMAGE and not image[0].get('Config',{}).get('Volumes'),'preflight','image-declares-volumes')
        for kind,field in (('container','ID'),('network','ID'),('volume','Name')):
            args=[kind,'ls']+(['--all'] if kind=='container' else [])+['--filter','label=com.docker.compose.project='+self.project,'--format','{{.'+field+'}}']
            require(not self.command(args,'preflight').strip(),'preflight','project-collision')
        self.owned=True
    def start(self):
        self.compose(['up','-d','--pull','never'],'startup',90)
        ids=self.compose(['ps','-q','bludit'],'ownership').split()
        require(len(ids)==1 and re.fullmatch('[a-f0-9]{12,64}',ids[0]),'ownership','single-container-required')
        info=json.loads(self.command(['inspect',ids[0]],'ownership'))
        require(len(info)==1,'ownership','ambiguous-container')
        origin=validate_inspect(info[0],self.project)
        require(parse_port(self.compose(['port','bludit','80'],'port'))==origin,'port','port-inspect-mismatch')
        networks=json.loads(self.command(['network','inspect',self.project+'_isolated'],'ownership'))
        require(len(networks)==1 and networks[0].get('Internal') is True and networks[0].get('Labels',{}).get('com.docker.compose.project')==self.project,'ownership','network-not-owned-internal')
        return origin
    def run(self,output_dir,browser=None):
        output=Path(output_dir); output.mkdir(parents=True,exist_ok=False)
        report={'schema':'dxa-bludit-lab/1','status':'error','product':'Bludit','embedded_version':'3.16.2','image':PINNED_IMAGE,'project':self.project,'triage':'by-design','cases':[],'events':[],'cleanup_status':'not-started','limitations':['Admin-authored raw/escaped controls; no vulnerability or role-boundary claim.','Bounded public-reader observation; not general scanner coverage.']}
        try:
            self.preflight(); origin=self.start(); report['origin']=origin
            client=self.client_factory(origin)
            ready=False
            for _ in range(20):
                try:
                    if client.request('/install.php?language=en').status == 200: ready=True; break
                except (OSError,urllib.error.URLError): pass
                time.sleep(.5)
            require(ready,'readiness','installer-timeout')
            client, report['session']=bootstrap(client)
            cases=seed_cases(client,self.project.removeprefix('dxa-bludit-'))
            proof=validate_proof(self.proof_runner(origin,[dict(c) for c in cases],browser),cases)
            report['cases']=proof['cases']; report['browser_version']=proof['browser_version']
            require(len(report['cases'])==2 and all(c.get('matched') is True for c in report['cases']),'acceptance','control-mismatch')
            report['status']='passed'
        except Exception as exc:
            report['events'].append({'stage':exc.stage if isinstance(exc,AdapterError) else 'adapter','kind':'error','reason':exc.code if isinstance(exc,AdapterError) else ('timeout' if isinstance(exc, TimeoutError) or type(exc).__name__ == 'TimeoutError' else 'unexpected-error')})
        finally:
            if self.owned:
                try:
                    # Unique project was empty before startup. Down removes only its resources,
                    # never volumes. This also handles partially failed startup.
                    self.compose(['down','--timeout','10'],'cleanup',45)
                    leftovers=self.command(['container','ls','--all','--filter','label=com.docker.compose.project='+self.project,'--format','{{.ID}}'],'cleanup')
                    networks=self.command(['network','ls','--filter','label=com.docker.compose.project='+self.project,'--format','{{.ID}}'],'cleanup')
                    require(not leftovers.strip() and not networks.strip(),'cleanup','owned-resources-remain')
                    report['cleanup_status']='passed'
                except Exception:
                    report['cleanup_status']='error'; report['status']='error'
                    report['events'].append({'stage':'cleanup','kind':'error','reason':'cleanup-failed'})
            (output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            lines=['# Bludit local application acceptance','',f"Status: {report['status']}",f"Cleanup: {report['cleanup_status']}",'','Admin-authored controls; no vulnerability claim.','', '| Case | Expected execution | Observed | Match |','|---|---|---|---|']
            for c in report['cases']: lines.append(f"| {c['case_id']} | {c['expected_execution']} | {c['execution_observed']} | {c['matched']} |")
            for event in report['events']: lines.append(f"\nError: {event['stage']}/{event['reason']}")
            (output/'result.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        return report

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    parser.add_argument('--browser')
    args=parser.parse_args(argv)
    result=BluditAdapter().run(args.output,args.browser)
    print(json.dumps({'status':result['status'],'cleanup_status':result['cleanup_status']}))
    return 0 if result['status']=='passed' else 2

if __name__=='__main__':
    raise SystemExit(main())
