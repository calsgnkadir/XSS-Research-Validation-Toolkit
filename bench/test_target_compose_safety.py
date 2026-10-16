"""Static Docker target config guardrails; these tests never call Docker."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "bench" / "targets"


def test_active_compose_templates_require_reviewed_images_and_loopback_ports():
    manifest = json.loads((ROOT / "bench" / "targets.json").read_text(encoding="utf-8"))
    compose_paths = {
        item["compose_file"] for item in manifest["targets"]
        if item.get("kind") == "docker"
    }
    assert compose_paths == {
        "bench/targets/bludit/docker-compose.yml",
        "bench/targets/dvwa/docker-compose.yml",
        "bench/targets/webgoat/docker-compose.yml",
    }

    for relative in compose_paths:
        content = (ROOT / relative).read_text(encoding="utf-8")
        image_lines = re.findall(r"(?m)^\s+image:\s*(.+)$", content)
        assert image_lines
        assert all(
            re.fullmatch(r"\$\{DXA_[A-Z]+_IMAGE:\?Set a reviewed immutable .+ image reference\}", line)
            for line in image_lines
        ), relative
        assert re.search(r"(?m)^\s+pull_policy:\s*never\s*$", content), relative
        assert re.search(r"(?m)^\s+restart:\s*[\"']?no[\"']?\s*$", content), relative

        ports = re.search(r"(?ms)^\s{4}ports:\n((?:^\s{6}- .*\n)+)", content)
        assert ports, relative
        published = re.findall(r"^\s{6}-\s*[\"']([^\"']+)[\"']\s*$", ports.group(1), re.M)
        assert published and all(port.startswith("127.0.0.1:") for port in published), relative


def test_disposable_bludit_ingress_is_digest_pinned_volume_free_and_loopback_only():
    content = (TARGETS / "bludit" / "local-inspected.yml").read_text(encoding="utf-8")
    config = json.loads(content[content.index("{"):])
    services = config["services"]
    assert set(services) == {"bludit", "ingress"}
    for service in services.values():
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", service["image"])
        assert service["pull_policy"] == "never"
        assert service["restart"] == "no"
        assert not service.get("volumes")
    assert not services["bludit"].get("ports")
    assert services["bludit"]["networks"] == ["isolated"]
    assert services["ingress"]["ports"] == ["127.0.0.1::80"]
    assert set(services["ingress"]["networks"]) == {"edge", "isolated"}
    assert config["networks"]["isolated"]["internal"] is True


def test_target_docs_separate_daemon_liveness_from_application_acceptance():
    docs = (TARGETS / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(docs.split())
    assert "infrastructure/liveness signals" in normalized
    assert "application setup and scan oracle not verified" in normalized
    assert "fresh bootstrap, login" in normalized
    assert "no target-specific login/lesson acceptance adapter" in normalized
    assert "Do not use `down -v`" in normalized
