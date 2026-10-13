"""Strict topology guards for the disposable R4 fixed Apache reverse proxy."""
from __future__ import annotations
import re

PINNED_IMAGE = "sha256:7eb101cdb879f549d6e0088b13c07afa231292e9e15eeff741491abeafb3ebb8"
APP_ENTRYPOINT = ["docker-php-entrypoint"]
APP_COMMAND = ["apache2-foreground"]
INGRESS_ENTRYPOINT = ["/usr/sbin/apache2"]
# /dev/null bypasses the image application configuration and PHP module entirely.
# No client URL, header, environment variable or filesystem path chooses upstream.
PROXY_DIRECTIVES = [
    "ServerRoot /etc/apache2",
    "LoadModule mpm_event_module /usr/lib/apache2/modules/mod_mpm_event.so",
    "LoadModule authz_core_module /usr/lib/apache2/modules/mod_authz_core.so",
    "LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so",
    "LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so",
    "Listen 80", "ServerName 127.0.0.1",
    "PidFile /tmp/dxa-ingress.pid", "DefaultRuntimeDir /tmp",
    "User www-data", "Group www-data", "ErrorLog /proc/self/fd/2",
    "ProxyRequests Off", "ProxyPreserveHost On",
    "ProxyPass / http://bludit:80/ connectiontimeout=3 timeout=10",
    "ProxyPassReverse / http://bludit:80/",
]
INGRESS_COMMAND = ["-f", "/dev/null", "-DFOREGROUND"] + [
    value for directive in PROXY_DIRECTIVES for value in ("-C", directive)
]

class IngressError(Exception):
    def __init__(self, stage, code):
        self.stage, self.code = stage, code
        super().__init__(code)


def _require(ok, stage, code):
    if not ok:
        raise IngressError(stage, code)


def _mapping(value, stage, code):
    _require(isinstance(value, dict), stage, code)
    return value


def validate_config(config, project, image=PINNED_IMAGE):
    """Accept only normalized Compose with two fresh, volume-free services."""
    _mapping(config, "preflight", "invalid-config")
    _require(set(config) <= {"name", "services", "networks"} and config.get("name", project) == project,
             "preflight", "unsupported-compose-resource")
    services = _mapping(config.get("services"), "preflight", "two-services-required")
    _require(set(services) == {"bludit", "ingress"}, "preflight", "two-services-required")
    for name, s in services.items():
        _mapping(s, "preflight", "invalid-service")
        _require(set(s) <= {"image", "pull_policy", "restart", "ports", "networks", "healthcheck", "command", "entrypoint"},
                 "preflight", "unsupported-service-option")
        _require(s.get("image") == image and s.get("pull_policy") == "never" and s.get("restart") == "no",
                 "preflight", "immutable-image-required")
        attachments = _mapping(s.get("networks"), "preflight", "invalid-attachments")
        expected = {"isolated"} if name == "bludit" else {"isolated", "edge"}
        _require(set(attachments) == expected and all(v in (None, {}) for v in attachments.values()),
                 "preflight", "unexpected-network-attachment")
        if name == "bludit":
            _require(not s.get("ports") and s.get("command") is None and s.get("entrypoint") is None,
                     "preflight", "isolated-app-required")
            h = _mapping(s.get("healthcheck"), "preflight", "reviewed-healthcheck-required")
            _require(set(h) <= {"test", "interval", "timeout", "retries"} and h.get("test") == ["CMD", "curl", "-f", "http://localhost/"],
                     "preflight", "reviewed-healthcheck-required")
        else:
            _require(s.get("entrypoint") == INGRESS_ENTRYPOINT and s.get("command") == INGRESS_COMMAND and not s.get("healthcheck"),
                     "preflight", "fixed-proxy-command-required")
            ports = s.get("ports")
            _require(isinstance(ports, list) and len(ports) == 1 and isinstance(ports[0], dict),
                     "preflight", "single-port-required")
            port = ports[0]
            _require(set(port) <= {"mode", "host_ip", "target", "published", "protocol"} and port.get("mode", "ingress") == "ingress"
                     and port.get("host_ip") == "127.0.0.1" and str(port.get("target")) == "80"
                     and port.get("protocol", "tcp") == "tcp" and port.get("published") in (None, "", 0, "0"),
                     "preflight", "ephemeral-loopback-required")
    networks = _mapping(config.get("networks"), "preflight", "two-networks-required")
    _require(set(networks) == {"isolated", "edge"}, "preflight", "two-networks-required")
    for name, n in networks.items():
        _mapping(n, "preflight", "invalid-network")
        _require(set(n) <= {"name", "driver", "internal", "ipam"} and not n.get("ipam")
                 and n.get("driver", "bridge") == "bridge" and n.get("name", project + "_" + name) == project + "_" + name
                 and n.get("internal", False) is (name == "isolated"),
                 "preflight", "owned-network-required")


def validate_inspect(container, project, service, image=PINNED_IMAGE):
    """Validate both endpoints before issuing HTTP; return ingress origin only."""
    _require(service in ("bludit", "ingress"), "ownership", "unknown-service")
    _mapping(container, "ownership", "invalid-container")
    config = _mapping(container.get("Config"), "ownership", "invalid-container-config")
    labels = config.get("Labels") or {}
    _require(labels.get("com.docker.compose.project") == project and labels.get("com.docker.compose.service") == service,
             "ownership", "foreign-container")
    _require(container.get("Image") == image and not container.get("Mounts"), "ownership", "image-or-mount-mismatch")
    entrypoint, command = (APP_ENTRYPOINT, APP_COMMAND) if service == "bludit" else (INGRESS_ENTRYPOINT, INGRESS_COMMAND)
    _require(config.get("Entrypoint") == entrypoint and config.get("Cmd") == command,
             "ownership", "runtime-command-mismatch")
    host = _mapping(container.get("HostConfig"), "ownership", "invalid-host-config")
    _require(not any(host.get(k) for k in ("Privileged", "Binds", "CapAdd", "Devices", "ExtraHosts", "VolumesFrom", "PublishAllPorts"))
             and host.get("PidMode", "") == "" and host.get("IpcMode", "private") in ("", "private")
             and host.get("RestartPolicy", {}).get("Name", "no") == "no",
             "ownership", "unsafe-runtime")
    settings = _mapping(container.get("NetworkSettings"), "ownership", "invalid-network-settings")
    nets = _mapping(settings.get("Networks"), "ownership", "invalid-runtime-networks")
    expected = {project + "_isolated"} if service == "bludit" else {project + "_isolated", project + "_edge"}
    _require(set(nets) == expected and host.get("NetworkMode") in expected, "ownership", "unexpected-runtime-networks")
    _require(service in (nets[project + "_isolated"].get("Aliases") or []), "ownership", "missing-service-alias")
    _require(container.get("State", {}).get("Running") is True, "readiness", "container-not-running")
    ports = _mapping(settings.get("Ports", {}), "port", "unexpected-port-map")
    bindings = host.get("PortBindings") or {}
    if service == "bludit":
        _require(set(ports) <= {"80/tcp"} and all(p in (None, []) for p in ports.values()) and not bindings,
                 "port", "app-port-published")
        return None
    _require(set(ports) == {"80/tcp"} and isinstance(ports["80/tcp"], list) and len(ports["80/tcp"]) == 1,
             "port", "unexpected-port-map")
    p = ports["80/tcp"][0]
    _require(isinstance(p, dict) and p.get("HostIp") == "127.0.0.1"
             and re.fullmatch(r"[0-9]{1,5}", str(p.get("HostPort", ""))) is not None,
             "port", "invalid-loopback-port")
    number = int(p["HostPort"])
    _require(1 <= number <= 65535, "port", "invalid-loopback-port")
    _require(set(bindings) == {"80/tcp"} and isinstance(bindings["80/tcp"], list) and len(bindings["80/tcp"]) == 1
             and bindings["80/tcp"][0].get("HostIp") == "127.0.0.1"
             and str(bindings["80/tcp"][0].get("HostPort", "")) in ("", "0", str(number)),
             "port", "unexpected-port-binding")
    return "http://127.0.0.1:" + str(number)


def validate_network(network, project, name, container_ids):
    """Reject attached foreign containers or non-owned/custom network drivers."""
    _mapping(network, "ownership", "invalid-network-inspect")
    _require(name in ("isolated", "edge"), "ownership", "unknown-network")
    labels = network.get("Labels") or {}
    # Docker Desktop materializes these default bridge flags at runtime.
    options = network.get("Options") or {}
    defaults = {"com.docker.network.enable_ipv4": "true", "com.docker.network.enable_ipv6": "false"}
    _require(isinstance(options, dict) and all(k in defaults and v == defaults[k] for k, v in options.items()),
             "ownership", "unexpected-network-options")
    _require(network.get("Name") == project + "_" + name and network.get("Driver") == "bridge"
             and network.get("Internal") is (name == "isolated") and network.get("Scope", "local") == "local"
             and labels.get("com.docker.compose.project") == project
             and labels.get("com.docker.compose.network") == name,
             "ownership", "network-not-owned")
    members = _mapping(network.get("Containers"), "ownership", "invalid-network-members")
    _require(set(members) == set(container_ids), "ownership", "unexpected-network-members")
