"""Independent R4 product-adapter negative oracles; Docker is never invoked."""
import copy
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bludit_adapter as adapter

PROJECT = 'dxa-bludit-' + 'a' * 32


def inspected():
    return {
        'Id': 'a' * 64,
        'Image': adapter.PINNED_IMAGE,
        'Config': {'Labels': {'com.docker.compose.project': PROJECT,
                              'com.docker.compose.service': 'bludit'}},
        'Mounts': [],
        'HostConfig': {'Privileged': False, 'NetworkMode': PROJECT + '_isolated'},
        'State': {'Running': True},
        'NetworkSettings': {'Ports': {'80/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '49152'}]}}
    }


def test_single_loopback_mapping_is_discovered():
    assert adapter.parse_port('127.0.0.1:49152\n') == 'http://127.0.0.1:49152'
    assert adapter.validate_inspect(inspected(), PROJECT) == 'http://127.0.0.1:49152'


@pytest.mark.parametrize('value', [
    '', '0.0.0.0:49152', '[::]:49152', 'localhost:49152', '127.0.0.2:49152',
    '127.0.0.1:0', '127.0.0.1:65536', '127.0.0.1:-1', '127.0.0.1:nan',
    '127.0.0.1:49152\n127.0.0.1:49153', 'http://127.0.0.1:49152',
    '127.0.0.1:49152/path', '127.0.0.1:49152 evil',
])
def test_ambiguous_or_unsafe_port_is_rejected(value):
    with pytest.raises(adapter.AdapterError):
        adapter.parse_port(value)


@pytest.mark.parametrize('mutation', [
    'project', 'service', 'labels-missing', 'image', 'mount', 'privileged',
    'host-network', 'stopped', 'wildcard-ip', 'extra-binding', 'extra-port',
    'no-port', 'invalid-port',
])
def test_runtime_inspect_rejects_unowned_or_unsafe_container(mutation):
    row = inspected()
    if mutation == 'project':
        row['Config']['Labels']['com.docker.compose.project'] = 'existing-user-site'
    elif mutation == 'service':
        row['Config']['Labels']['com.docker.compose.service'] = 'other'
    elif mutation == 'labels-missing':
        row['Config']['Labels'] = {}
    elif mutation == 'image':
        row['Image'] = 'sha256:' + 'f' * 64
    elif mutation == 'mount':
        row['Mounts'] = [{'Type': 'volume', 'Name': 'existing-data'}]
    elif mutation == 'privileged':
        row['HostConfig']['Privileged'] = True
    elif mutation == 'host-network':
        row['HostConfig']['NetworkMode'] = 'host'
    elif mutation == 'stopped':
        row['State']['Running'] = False
    elif mutation == 'wildcard-ip':
        row['NetworkSettings']['Ports']['80/tcp'][0]['HostIp'] = '0.0.0.0'
    elif mutation == 'extra-binding':
        row['NetworkSettings']['Ports']['80/tcp'].append({'HostIp': '127.0.0.1', 'HostPort': '49153'})
    elif mutation == 'extra-port':
        row['NetworkSettings']['Ports']['22/tcp'] = [{'HostIp': '127.0.0.1', 'HostPort': '49153'}]
    elif mutation == 'no-port':
        row['NetworkSettings']['Ports'] = {}
    else:
        row['NetworkSettings']['Ports']['80/tcp'][0]['HostPort'] = '0'
    with pytest.raises(adapter.AdapterError):
        adapter.validate_inspect(row, PROJECT)


def compose_config():
    return {'name': PROJECT, 'services': {'bludit': {
        'image': adapter.PINNED_IMAGE, 'pull_policy': 'never', 'restart': 'no',
        'command': None, 'entrypoint': None,
        'ports': [{'target': 80, 'published': '0', 'host_ip': '127.0.0.1', 'protocol': 'tcp'}],
        'networks': {'isolated': None},
        'healthcheck': {'test': ['CMD', 'curl', '-f', 'http://localhost/']},
    }}, 'networks': {'isolated': {'name': PROJECT + '_isolated', 'internal': True, 'ipam': {}}}}


def test_isolated_ephemeral_compose_config_is_accepted():
    adapter.validate_config(compose_config(), PROJECT)


@pytest.mark.parametrize('mutation', ['image', 'pull', 'volume', 'bind', 'privileged',
                                       'external-network', 'public-network', 'port',
                                       'extra-service', 'container-name', 'command', 'entrypoint', 'ipam'])
def test_compose_guard_rejects_data_attachment_or_scope_expansion(mutation):
    config = compose_config()
    svc = config['services']['bludit']
    if mutation == 'image':
        svc['image'] = 'bludit:latest'
    elif mutation == 'pull':
        svc['pull_policy'] = 'always'
    elif mutation == 'volume':
        svc['volumes'] = [{'type': 'volume', 'source': 'existing', 'target': '/var/www/html'}]
    elif mutation == 'bind':
        svc['volumes'] = [{'type': 'bind', 'source': 'C:/user', 'target': '/data'}]
    elif mutation == 'privileged':
        svc['privileged'] = True
    elif mutation == 'external-network':
        config['networks']['isolated']['external'] = True
    elif mutation == 'public-network':
        config['networks']['isolated']['internal'] = False
    elif mutation == 'port':
        svc['ports'][0]['host_ip'] = '0.0.0.0'
    elif mutation == 'extra-service':
        config['services']['foreign'] = copy.deepcopy(svc)
    elif mutation == 'command':
        svc['command'] = ['sh', '-c', 'echo unexpected']
    elif mutation == 'entrypoint':
        svc['entrypoint'] = ['sh']
    elif mutation == 'ipam':
        config['networks']['isolated']['ipam'] = {'config': [{'subnet': '10.0.0.0/24'}]}
    else:
        svc['container_name'] = 'existing-user-container'
    with pytest.raises(adapter.AdapterError):
        adapter.validate_config(config, PROJECT)

ORIGIN = 'http://127.0.0.1:49152'
FORM = '<input name="tokenCSRF" value="FAKE_CSRF"><input name="uuid" value="uuid"><input name="title"><textarea name="content"></textarea><input disabled value="admin">'
INSTALLER = 'Bludit<input name="password"><input name="timezone">'
LOGIN = '<input name="tokenCSRF" value="FAKE_LOGIN_TOKEN"><input name="username"><input name="password">'


class ScriptedClient:
    origin = ORIGIN

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, path, data=None):
        self.calls.append((path, data))
        assert self.responses, 'Unexpected HTTP request'
        expected_path, response = self.responses.pop(0)
        assert path == expected_path
        return response


def response(body='', status=200, location=None):
    return adapter.Response(status, body, ORIGIN, {'Location': location} if location else {})


def bootstrap_script():
    return [('/install.php?language=en', response(INSTALLER)),
            ('/install.php?language=en', response(status=302, location='/')),
            ('/admin/new-content', response(status=302, location='/admin/login')),
            ('/admin/login', response(LOGIN)),
            ('/admin/login', response(status=302, location='/admin/dashboard')),
            ('/admin/new-content', response(FORM))]


def test_bootstrap_proves_denial_then_authenticated_author_form():
    client = ScriptedClient(bootstrap_script())
    returned_client, result = adapter.bootstrap(client)
    assert returned_client is client
    assert result['session_checked'] is True
    assert result['role_verified'] is False
    assert not client.responses
    assert client.calls[4][1]['tokenCSRF'] == 'FAKE_LOGIN_TOKEN'
    assert client.calls[1][1]['password'] == client.calls[4][1]['password']
    assert 'password' not in result


@pytest.mark.parametrize('step,bad', [
    (0, response('Already installed')),
    (1, response(status=302, location='https://outside.invalid/')),
    (2, response(FORM)),
    (3, response(LOGIN.replace('FAKE_LOGIN_TOKEN', ''))),
    (4, response(LOGIN)),
    (4, response(status=302, location='/admin/login')),
    (5, response(LOGIN)),
    (5, response(FORM.replace('value="admin"', 'value="author"'))),
    (5, response(FORM, status=403)),
])
def test_bootstrap_failure_stops_before_further_requests(step, bad):
    script = bootstrap_script()
    script[step] = (script[step][0], bad)
    client = ScriptedClient(script)
    with pytest.raises(adapter.AdapterError):
        adapter.bootstrap(client)
    assert len(client.calls) == step + 1


@pytest.mark.parametrize('path', ['https://outside.invalid/', '//outside.invalid/',
                                 'http://127.0.0.1:49153/', 'http://user@127.0.0.1:49152/'])
def test_http_client_rejects_scope_escape_before_network(path):
    client = adapter.HTTPClient(ORIGIN)
    class NeverOpen:
        def open(self, *args, **kwargs):
            pytest.fail('Scope guard allowed network request')
    client.opener = NeverOpen()
    with pytest.raises(adapter.AdapterError):
        client.request(path)


def test_redirect_does_not_establish_successful_content_write():
    client = ScriptedClient([('/admin/new-content', response(FORM)),
                             ('/admin/new-content', response(status=302, location='/admin/content')),
                             ('/dxa-fixture-raw', response('No saved payload'))])
    with pytest.raises(adapter.AdapterError, match='fixture-readback-mismatch'):
        adapter.seed_cases(client, 'fixture')
    assert len(client.calls) == 3


def test_seeded_controls_read_back_exact_different_encodings():
    class StorageClient:
        origin = ORIGIN
        def __init__(self):
            self.stored = {}
        def request(self, path, data=None):
            if path == '/admin/new-content' and data is None:
                return response(FORM)
            if data is not None:
                self.stored['/' + data['slug']] = data['content']
                return response(status=302, location='/admin/content')
            return response('<article>' + self.stored[path] + '</article>')
    client = StorageClient()
    cases = adapter.seed_cases(client, 'fixture')
    assert [c['expected_execution'] for c in cases] == [True, False]
    assert '<img ' in client.stored[cases[0]['path']]
    assert '<img ' not in client.stored[cases[1]['path']]
    assert '&lt;img ' in client.stored[cases[1]['path']]
    assert cases[0]['canary_id'] != cases[1]['canary_id']
    assert all(c['triage'] == 'by-design' for c in cases)

import json
import subprocess


class DockerScript:
    """Protocol fake: no subprocess/daemon call can escape this object."""
    def __init__(self, failure=None):
        self.calls = []
        self.failure = failure
        self.down = False

    def __call__(self, cmd, **kwargs):
        self.calls.append(cmd)
        assert cmd[0] == 'docker'
        assert kwargs['timeout'] > 0
        if 'config' in cmd:
            value = json.dumps(compose_config())
        elif cmd[1:3] == ['image', 'inspect']:
            value = json.dumps([{'Id': adapter.PINNED_IMAGE, 'Config': {'Volumes': None}}])
        elif cmd[1] in ('container', 'network', 'volume') and cmd[2] == 'ls':
            value = 'existing-id' if self.failure == 'collision' and not self.down else ''
            if self.failure == 'leftover' and self.down:
                value = 'owned-resource-remains'
        elif 'up' in cmd:
            if self.failure == 'startup-timeout':
                raise subprocess.TimeoutExpired(cmd, 90, stderr='FAKE_PROCESS_SECRET')
            value = ''
        elif 'ps' in cmd:
            value = 'a' * 64
        elif cmd[1] == 'inspect':
            row = inspected()
            if self.failure == 'foreign-container':
                row['Config']['Labels']['com.docker.compose.project'] = 'foreign'
            value = json.dumps([row])
        elif 'port' in cmd:
            value = '127.0.0.1:49153' if self.failure == 'port-mismatch' else '127.0.0.1:49152'
        elif cmd[1:3] == ['network', 'inspect']:
            value = json.dumps([{'Internal': True, 'Labels': {'com.docker.compose.project': PROJECT}}])
        elif 'down' in cmd:
            self.down = True
            if self.failure == 'cleanup':
                return subprocess.CompletedProcess(cmd, 1, '', 'FAKE_PROCESS_SECRET')
            value = ''
        else:
            pytest.fail('Unexpected Docker command: ' + repr(cmd))
        return subprocess.CompletedProcess(cmd, 0, value, '')


def seeded():
    return [{'case_id': case_id, 'path': '/' + case_id, 'canary_id': 'dxa' + str(i) * 32,
             'expected_execution': positive, 'payload_sha256': 'a' * 64,
             'triage': 'by-design', 'read_status': 200}
            for i, (case_id, positive) in enumerate([
                ('raw-admin-content', True), ('escaped-admin-content', False)])]


def successful_proof(origin, cases, browser):
    return {'browser_version': '155.0.8059.39', 'cases': [
        {**c, 'execution_observed': c['expected_execution'],
         'status': 'execution-observed' if c['expected_execution'] else 'no-execution-observed',
         'observation_ms': 1000, 'matched': True} for c in cases]}


def run_fake(tmp_path, monkeypatch, *, failure=None, proof_runner=successful_proof):
    docker = DockerScript(failure)
    client = ScriptedClient([('/install.php?language=en', response(INSTALLER))])
    monkeypatch.setattr(adapter, 'bootstrap', lambda c: (c, {'session_checked': True, 'role_verified': False}))
    monkeypatch.setattr(adapter, 'seed_cases', lambda c, run_id: seeded())
    lab = adapter.BluditAdapter(run_command=docker, client_factory=lambda origin: client,
                                proof_runner=proof_runner, project=PROJECT)
    result = lab.run(tmp_path / 'report')
    return result, docker


def test_successful_lifecycle_uses_fresh_project_and_cleans_only_that_project(tmp_path, monkeypatch):
    result, docker = run_fake(tmp_path, monkeypatch)
    assert result['status'] == 'passed'
    assert result['cleanup_status'] == 'passed'
    assert docker.down
    for cmd in docker.calls:
        if cmd[1] == 'compose':
            assert cmd[cmd.index('-p') + 1] == PROJECT
        assert '--volumes' not in cmd and '-v' not in cmd and 'prune' not in cmd
    up = next(cmd for cmd in docker.calls if 'up' in cmd)
    assert up[up.index('--pull') + 1] == 'never'
    assert json.loads((tmp_path / 'report/result.json').read_text())['status'] == 'passed'


def test_existing_project_collision_does_not_start_or_teardown(tmp_path, monkeypatch):
    result, docker = run_fake(tmp_path, monkeypatch, failure='collision')
    assert result['status'] == 'error'
    assert not any('up' in cmd or 'down' in cmd for cmd in docker.calls)
    assert result['cleanup_status'] == 'not-started'


@pytest.mark.parametrize('failure', ['startup-timeout', 'port-mismatch', 'foreign-container', 'cleanup', 'leftover'])
def test_lifecycle_failure_cannot_be_successful_negative(tmp_path, monkeypatch, failure):
    result, docker = run_fake(tmp_path, monkeypatch, failure=failure)
    assert result['status'] == 'error'
    assert docker.down
    assert result['events']
    assert 'FAKE_PROCESS_SECRET' not in json.dumps(result)
    if failure == 'startup-timeout':
        assert result['events'][0]['reason'] == 'command-timeout'
    if failure in ('cleanup', 'leftover'):
        assert result['cleanup_status'] == 'error'


@pytest.mark.parametrize('failure', ['exception', 'timeout', 'playwright-timeout', 'empty', 'duplicate', 'wrong-cid',
                                     'wrong-path', 'wrong-label', 'error-negative', 'forged-match'])
def test_invalid_or_incomplete_proof_cannot_pass(tmp_path, monkeypatch, failure):
    def proof(origin, cases, browser):
        if failure == 'exception':
            raise RuntimeError('FAKE_BROWSER_SECRET')
        if failure == 'timeout':
            raise TimeoutError('FAKE_BROWSER_SECRET')
        if failure == 'playwright-timeout':
            # Mirror Playwright's non-builtin TimeoutError without requiring its package.
            browser_timeout = type('TimeoutError', (Exception,), {'__module__': 'playwright._impl._errors'})
            raise browser_timeout('FAKE_BROWSER_SECRET')
        result = successful_proof(origin, cases, browser)
        if failure == 'empty':
            result['cases'] = []
        elif failure == 'duplicate':
            result['cases'][1] = copy.deepcopy(result['cases'][0])
        elif failure == 'wrong-cid':
            result['cases'][0]['canary_id'] = 'foreign-canary'
        elif failure == 'wrong-path':
            result['cases'][0]['path'] = '/unrelated'
        elif failure == 'wrong-label':
            result['cases'][0]['expected_execution'] = False
        elif failure == 'error-negative':
            result['cases'][1]['status'] = 'error'
        elif failure == 'forged-match':
            result['cases'][0]['execution_observed'] = False
        return result
    result, docker = run_fake(tmp_path, monkeypatch, proof_runner=proof)
    assert result['status'] == 'error'
    assert result['cleanup_status'] == 'passed'
    assert docker.down
    assert 'FAKE_BROWSER_SECRET' not in (tmp_path / 'report/result.json').read_text()
    if failure in ('timeout', 'playwright-timeout'):
        assert result['events'][0]['reason'] == 'timeout'


def test_arbitrary_proof_fields_do_not_leak_to_shared_reports(tmp_path, monkeypatch):
    original = None
    captured = None
    def proof(origin, cases, browser):
        nonlocal original, captured
        captured = successful_proof(origin, cases, browser)
        captured['cases'][0]['password'] = 'FAKE_PROOF_SECRET'
        captured['cases'][0]['cookie'] = 'FAKE_PROOF_COOKIE'
        original = copy.deepcopy(captured)
        return captured
    result, _ = run_fake(tmp_path, monkeypatch, proof_runner=proof)
    assert captured == original, 'Adapter must not mutate producer evidence'
    exported = ''.join(p.read_text() for p in (tmp_path / 'report').iterdir())
    assert 'FAKE_PROOF_SECRET' not in exported
    assert 'FAKE_PROOF_COOKIE' not in exported


@pytest.mark.parametrize('value', [None, {}, {'cases': [None, None], 'browser_version': '155.0'},
                                   {'cases': [{}, {}], 'browser_version': '155.0'}])
def test_malformed_proof_returns_error_report_and_cleanup(tmp_path, monkeypatch, value):
    result, docker = run_fake(tmp_path, monkeypatch, proof_runner=lambda *args: value)
    assert result['status'] == 'error'
    assert result['cleanup_status'] == 'passed'
    assert docker.down
    assert (tmp_path / 'report/result.md').is_file()


def test_producer_cannot_rewrite_expected_labels_via_input_alias(tmp_path, monkeypatch):
    def proof(origin, cases, browser):
        cases[0]['expected_execution'] = False
        return successful_proof(origin, cases, browser)
    result, _ = run_fake(tmp_path, monkeypatch, proof_runner=proof)
    assert result['status'] == 'error'


@pytest.mark.parametrize('stage', ['readiness', 'bootstrap'])
def test_http_setup_failure_always_cleans_created_resources(tmp_path, monkeypatch, stage):
    docker = DockerScript()
    class BadClient:
        origin = ORIGIN
        def request(self, path, data=None):
            if stage == 'readiness':
                raise OSError('FAKE_TRANSPORT_SECRET')
            return response(INSTALLER)
    monkeypatch.setattr(adapter.time, 'sleep', lambda seconds: None)
    def bad_bootstrap(client):
        raise adapter.AdapterError('bootstrap', 'installer-rejected')
    monkeypatch.setattr(adapter, 'bootstrap', bad_bootstrap)
    lab = adapter.BluditAdapter(run_command=docker, client_factory=lambda origin: BadClient(), project=PROJECT)
    result = lab.run(tmp_path / 'report')
    assert result['status'] == 'error'
    assert result['cleanup_status'] == 'passed'
    assert result['cases'] == []
    assert result['events'][0]['stage'] == stage
    assert docker.down
    assert 'FAKE_TRANSPORT_SECRET' not in json.dumps(result)


def test_existing_output_is_preserved_without_starting_docker(tmp_path):
    output = tmp_path / 'report'
    output.mkdir()
    prior = output / 'result.json'
    prior.write_text('previous-evidence')
    docker = DockerScript()
    lab = adapter.BluditAdapter(run_command=docker, project=PROJECT)
    with pytest.raises(FileExistsError):
        lab.run(output)
    assert prior.read_text() == 'previous-evidence'
    assert docker.calls == []
