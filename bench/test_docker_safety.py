"""R4/R9 preflight oracles. Mock Docker; never start or remove a real lab."""
import json
import pathlib
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run as runner


@pytest.fixture
def target():
    return runner.DockerTarget("unused.yml", "http://127.0.0.1:18080/")


def safe_config(target):
    return {"services": {"lab": {
        "image": "sha256:" + "a" * 64, "pull_policy": "never",
        "ports": [{"host_ip": "127.0.0.1", "published": "18080", "target": 80, "protocol": "tcp"}],
        "volumes": [{"type": "volume", "source": "data", "target": "/data"}],
    }}, "volumes": {"data": {"name": target.project + "_data"}}}


def use_config(monkeypatch, config):
    monkeypatch.setattr(runner.subprocess, "run", lambda args, **k:
                        SimpleNamespace(returncode=0, stdout=json.dumps(config) if "config" in args else ""))


def test_owned_loopback_immutable_project_allowed(target, monkeypatch):
    use_config(monkeypatch, safe_config(target))
    target._preflight()


@pytest.mark.parametrize("field,value", [
    ("image", "lab:latest"), ("image", "lab:3.16.2"),
    ("image", "sha256:abc"), ("pull_policy", "always"),
    ("build", {"context": "."}), ("container_name", "existing-app"),
    ("network_mode", "host"), ("privileged", True),
    ("volumes", [{"type": "bind", "source": "existing", "target": "/data"}]),
    ("ports", [{"host_ip": "0.0.0.0", "published": "18080", "target": 80}]),
])
def test_unsafe_service_never_started(target, monkeypatch, field, value):
    config = safe_config(target)
    config["services"]["lab"][field] = value
    use_config(monkeypatch, config)
    calls = []
    monkeypatch.setattr(runner, "_docker_compose_up", lambda *a, **k: calls.append("up"))
    monkeypatch.setattr(runner, "_docker_compose_down", lambda *a, **k: calls.append("down"))
    with target:
        assert not target.up_ok
    assert calls == []


@pytest.mark.parametrize("resource", [{"external": True}, {"name": "existing-data"},
                                    {"driver_opts": {"device": "/existing"}}])
def test_existing_volume_never_attached(target, monkeypatch, resource):
    config = safe_config(target)
    config["volumes"]["data"] = resource
    use_config(monkeypatch, config)
    with pytest.raises(ValueError):
        target._preflight()


def test_teardown_scoped_and_retains_volumes(target, monkeypatch):
    calls = []
    def command(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(runner.subprocess, "run", command)
    assert runner._docker_compose_down("unused.yml", project=target.project)
    assert calls == [["docker", "compose", "-p", target.project, "-f", "unused.yml", "down"]]
