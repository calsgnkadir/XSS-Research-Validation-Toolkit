"""Independent two-service topology oracles. No Docker or network calls."""
import copy
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bludit_ingress as ingress

PROJECT = 'dxa-bludit-' + 'a' * 32
APP_ID = 'a' * 64
INGRESS_ID = 'b' * 64


def compose_config():
    common = {'image': ingress.PINNED_IMAGE, 'pull_policy': 'never', 'restart': 'no'}
    return {'name': PROJECT, 'services': {
        'bludit': {**common, 'networks': {'isolated': None},
                   'healthcheck': {'test': ['CMD', 'curl', '-f', 'http://localhost/']}},
        'ingress': {**common, 'entrypoint': list(ingress.INGRESS_ENTRYPOINT),
                    'command': list(ingress.INGRESS_COMMAND),
                    'networks': {'isolated': None, 'edge': None},
                    'ports': [{'target': 80, 'published': '0', 'host_ip': '127.0.0.1', 'protocol': 'tcp'}]},
    }, 'networks': {
        'isolated': {'name': PROJECT + '_isolated', 'internal': True, 'ipam': {}},
        'edge': {'name': PROJECT + '_edge', 'internal': False, 'ipam': {}},
    }}


def inspected(service='ingress'):
    app = service == 'bludit'
    networks = {'isolated': {'Aliases': ['bludit'] if app else ['ingress']}}
    if not app:
        networks['edge'] = {'Aliases': ['ingress']}
    return {
        'Id': APP_ID if app else INGRESS_ID, 'Image': ingress.PINNED_IMAGE,
        'Config': {'Labels': {'com.docker.compose.project': PROJECT, 'com.docker.compose.service': service},
                   'Entrypoint': ['docker-php-entrypoint'] if app else list(ingress.INGRESS_ENTRYPOINT),
                   'Cmd': ['apache2-foreground'] if app else list(ingress.INGRESS_COMMAND)},
        'Mounts': [], 'State': {'Running': True},
        'HostConfig': {'Privileged': False, 'PortBindings': {} if app else {'80/tcp': [{'HostIp': '127.0.0.1', 'HostPort': ''}]}, 'NetworkMode': PROJECT + ('_isolated' if app else '_edge')},
        'NetworkSettings': {'Networks': {PROJECT + '_' + n: v for n, v in networks.items()},
                            'Ports': {'80/tcp': None if app else [{'HostIp': '127.0.0.1', 'HostPort': '49152'}]}},
    }


def network(name):
    ids = [APP_ID, INGRESS_ID] if name == 'isolated' else [INGRESS_ID]
    return {'Name': PROJECT + '_' + name, 'Driver': 'bridge', 'Internal': name == 'isolated',
            'Labels': {'com.docker.compose.project': PROJECT, 'com.docker.compose.network': name},
            'Containers': {cid: {} for cid in ids}}


def test_reviewed_two_service_topology_is_accepted():
    ingress.validate_config(compose_config(), PROJECT)
    assert ingress.validate_inspect(inspected('bludit'), PROJECT, 'bludit') is None
    assert ingress.validate_inspect(inspected(), PROJECT, 'ingress') == 'http://127.0.0.1:49152'
    ingress.validate_network(network('isolated'), PROJECT, 'isolated', [APP_ID, INGRESS_ID])
    ingress.validate_network(network('edge'), PROJECT, 'edge', [INGRESS_ID])


@pytest.mark.parametrize('mutation', ['app-port', 'app-edge', 'proxy-wildcard', 'proxy-fixed-port',
    'proxy-udp', 'proxy-extra-port', 'proxy-destination', 'proxy-entrypoint', 'app-command',
    'image', 'pull', 'volume', 'bind', 'privileged', 'external-network', 'public-app-network',
    'foreign-network-name', 'ipam', 'extra-service', 'container-name', 'network-alias'])
def test_config_rejects_scope_or_destination_changes(mutation):
    cfg = compose_config()
    app, proxy = cfg['services']['bludit'], cfg['services']['ingress']
    if mutation == 'app-port': app['ports'] = copy.deepcopy(proxy['ports'])
    elif mutation == 'app-edge': app['networks']['edge'] = None
    elif mutation == 'proxy-wildcard': proxy['ports'][0]['host_ip'] = '0.0.0.0'
    elif mutation == 'proxy-fixed-port': proxy['ports'][0]['published'] = '8080'
    elif mutation == 'proxy-udp': proxy['ports'][0]['protocol'] = 'udp'
    elif mutation == 'proxy-extra-port': proxy['ports'].append(dict(proxy['ports'][0]))
    elif mutation == 'proxy-destination': proxy['command'] = [x.replace('http://bludit:80/', 'http://example.invalid/') for x in proxy['command']]
    elif mutation == 'proxy-entrypoint': proxy['entrypoint'] = ['/bin/sh']
    elif mutation == 'app-command': app['command'] = ['sh']
    elif mutation == 'image': proxy['image'] = 'bludit:latest'
    elif mutation == 'pull': app['pull_policy'] = 'always'
    elif mutation == 'volume': app['volumes'] = [{'type': 'volume', 'source': 'existing-data', 'target': '/var/www/html'}]
    elif mutation == 'bind': proxy['volumes'] = [{'type': 'bind', 'source': '/private', 'target': '/data'}]
    elif mutation == 'privileged': proxy['privileged'] = True
    elif mutation == 'external-network': cfg['networks']['edge']['external'] = True
    elif mutation == 'public-app-network': cfg['networks']['isolated']['internal'] = False
    elif mutation == 'foreign-network-name': cfg['networks']['isolated']['name'] = 'existing-network'
    elif mutation == 'ipam': cfg['networks']['edge']['ipam'] = {'config': [{'subnet': '10.0.0.0/24'}]}
    elif mutation == 'extra-service': cfg['services']['foreign'] = copy.deepcopy(app)
    elif mutation == 'container-name': app['container_name'] = 'existing-app'
    elif mutation == 'network-alias': app['networks']['isolated'] = {'aliases': ['foreign']}
    assert cfg != compose_config(), 'Mutation must actually modify the accepted fixture'
    with pytest.raises(ingress.IngressError): ingress.validate_config(cfg, PROJECT)


@pytest.mark.parametrize('service', ['bludit', 'ingress'])
@pytest.mark.parametrize('mutation', ['project', 'service', 'image', 'mount', 'privileged', 'host-network',
    'stopped', 'extra-network', 'missing-network', 'entrypoint', 'command'])
def test_runtime_rejects_unowned_or_changed_container(service, mutation):
    row = inspected(service)
    if mutation == 'project': row['Config']['Labels']['com.docker.compose.project'] = 'foreign'
    elif mutation == 'service': row['Config']['Labels']['com.docker.compose.service'] = 'foreign'
    elif mutation == 'image': row['Image'] = 'sha256:' + 'f' * 64
    elif mutation == 'mount': row['Mounts'] = [{'Type': 'volume', 'Name': 'existing-data'}]
    elif mutation == 'privileged': row['HostConfig']['Privileged'] = True
    elif mutation == 'host-network': row['HostConfig']['NetworkMode'] = 'host'
    elif mutation == 'stopped': row['State']['Running'] = False
    elif mutation == 'extra-network': row['NetworkSettings']['Networks']['foreign'] = {}
    elif mutation == 'missing-network': row['NetworkSettings']['Networks'].pop(PROJECT + '_isolated')
    elif mutation == 'entrypoint': row['Config']['Entrypoint'] = ['/bin/sh']
    elif mutation == 'command': row['Config']['Cmd'] = ['-c', 'echo unsafe']
    with pytest.raises(ingress.IngressError): ingress.validate_inspect(row, PROJECT, service)


@pytest.mark.parametrize('mutation', ['app-published', 'app-alias', 'wildcard', 'double-binding', 'extra-port', 'zero-port', 'absent-port'])
def test_runtime_port_and_backend_identity_guards(mutation):
    service = 'bludit' if mutation.startswith('app-') else 'ingress'
    row = inspected(service)
    ports = row['NetworkSettings']['Ports']
    if mutation == 'app-published': ports['80/tcp'] = [{'HostIp': '127.0.0.1', 'HostPort': '49152'}]
    elif mutation == 'app-alias': row['NetworkSettings']['Networks'][PROJECT + '_isolated']['Aliases'] = ['other']
    elif mutation == 'wildcard': ports['80/tcp'][0]['HostIp'] = '0.0.0.0'
    elif mutation == 'double-binding': ports['80/tcp'].append({'HostIp': '127.0.0.1', 'HostPort': '49153'})
    elif mutation == 'extra-port': ports['22/tcp'] = []
    elif mutation == 'zero-port': ports['80/tcp'][0]['HostPort'] = '0'
    elif mutation == 'absent-port': ports['80/tcp'] = []
    with pytest.raises(ingress.IngressError): ingress.validate_inspect(row, PROJECT, service)


@pytest.mark.parametrize('name', ['isolated', 'edge'])
@pytest.mark.parametrize('mutation', ['project', 'name', 'internal', 'driver', 'extra-container', 'missing-container'])
def test_network_ownership_and_exact_membership(name, mutation):
    row = network(name)
    ids = list(row['Containers'])
    if mutation == 'project': row['Labels']['com.docker.compose.project'] = 'foreign'
    elif mutation == 'name': row['Name'] = 'foreign-network'
    elif mutation == 'internal': row['Internal'] = not row['Internal']
    elif mutation == 'driver': row['Driver'] = 'host'
    elif mutation == 'extra-container': row['Containers']['f' * 64] = {}
    elif mutation == 'missing-container': row['Containers'].pop(ids[0])
    with pytest.raises(ingress.IngressError): ingress.validate_network(row, PROJECT, name, ids)



def test_proxy_command_is_fixed_reverse_only_without_application_module():
    command = ingress.INGRESS_COMMAND
    assert command[:3] == ['-f', '/dev/null', '-DFOREGROUND']
    directives = command[4::2]
    assert command[3::2] == ['-C'] * len(directives)
    assert 'ProxyRequests Off' in directives
    assert 'ProxyPass / http://bludit:80/ connectiontimeout=3 timeout=10' in directives
    assert 'ProxyPassReverse / http://bludit:80/' in directives
    assert not any('php' in d.lower() or 'Rewrite' in d for d in directives)
    assert [d for d in directives if d.startswith('ProxyPass ')] == ['ProxyPass / http://bludit:80/ connectiontimeout=3 timeout=10']


@pytest.mark.parametrize('mutation', ['missing', 'wildcard', 'different-port', 'double', 'app-binding'])
def test_configured_binding_cannot_disagree_with_effective_mapping(mutation):
    service = 'bludit' if mutation == 'app-binding' else 'ingress'
    row = inspected(service)
    bindings = row['HostConfig']['PortBindings']
    if mutation == 'missing': bindings.clear()
    elif mutation == 'wildcard': bindings['80/tcp'][0]['HostIp'] = '0.0.0.0'
    elif mutation == 'different-port': bindings['80/tcp'][0]['HostPort'] = '49153'
    elif mutation == 'double': bindings['80/tcp'].append(dict(bindings['80/tcp'][0]))
    elif mutation == 'app-binding': bindings['80/tcp'] = [{'HostIp': '127.0.0.1', 'HostPort': ''}]
    with pytest.raises(ingress.IngressError): ingress.validate_inspect(row, PROJECT, service)


@pytest.mark.parametrize('options', [{}, {'com.docker.network.enable_ipv4': 'true'},
    {'com.docker.network.enable_ipv6': 'false'},
    {'com.docker.network.enable_ipv4': 'true', 'com.docker.network.enable_ipv6': 'false'}])
def test_network_accepts_only_daemon_ip_family_defaults(options):
    row = network('isolated')
    row['Options'] = options
    ingress.validate_network(row, PROJECT, 'isolated', [APP_ID, INGRESS_ID])


@pytest.mark.parametrize('options', [
    {'com.docker.network.enable_ipv4': 'false'}, {'com.docker.network.enable_ipv6': 'true'},
    {'com.docker.network.bridge.host_binding_ipv4': '0.0.0.0'},
    {'com.docker.network.enable_ipv4': True},
    {'com.docker.network.enable_ipv4': 'true', 'com.docker.network.bridge.name': 'foreign'},
])
def test_network_rejects_custom_daemon_options(options):
    row = network('isolated')
    row['Options'] = options
    with pytest.raises(ingress.IngressError):
        ingress.validate_network(row, PROJECT, 'isolated', [APP_ID, INGRESS_ID])
