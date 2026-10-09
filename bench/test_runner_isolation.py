"""R4 real subprocess deadline, descendant ownership, and adapter boundary tests."""
import json
import pathlib
import socket
import subprocess
import sys
import time

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run as runner
import process_control


def safe_docker_service():
    return {"image": "sha256:" + "a" * 64, "pull_policy": "never",
            "ports": [{"host_ip": "127.0.0.1", "published": "9999", "target": 80}]}


@pytest.mark.parametrize("bad", [None, [], {}, {"status": "completed", "ok": True},
    {"status": "completed", "ok": True, "findings": []},
    {"status": "completed", "ok": True, "findings": [], "negative_window_completed": "yes"},
    {"status": "completed", "ok": True, "findings": [None]},
    {"status": "completed", "ok": True, "findings": [{"finding_id": []}]},
    {"status": "completed", "ok": False, "findings": []},
    {"status": "bogus", "ok": True, "findings": []},
    {"status": "completed", "ok": True, "findings": [], "wall": float("nan")},
    {"status": "completed", "ok": True, "findings": [], "wall": "secret"},
    {"status": "completed", "ok": True, "findings": [], "wall": -1},
    {"status": "completed", "ok": True, "findings": [], "extra": object()}])
def test_malformed_result_is_unscored_and_next_case_survives(monkeypatch, bad):
    def adapter(target):
        if target["mode"] == "raw":
            return bad
        return {"status": "completed", "ok": True, "findings": [],
                "negative_window_completed": True}
    monkeypatch.setattr(runner, "run_dxaprove", adapter)
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], ["proof-raw", "proof-fixed"])
    total = report["totals"]["dxaprove"]
    assert (total["error"], total["completed"], total["tp"], total["fp"], total["fn"]) == (1, 1, 0, 0, 0)
    assert report["rows"][0]["results"]["dxaprove"]["score"]["evaluated"] is False
    assert runner.strict_failed(report)
    assert "secret" not in json.dumps(report)


# Test worker deliberately leaves a listening descendant alive. It is our
# disposable child, not a scan of an existing service or external host.
CHILD = """
import json, socket, sys, time
s = socket.socket()
s.bind(('127.0.0.1', 0))
s.listen()
with open(sys.argv[1], 'w') as f:
    json.dump({'port': s.getsockname()[1]}, f)
time.sleep(60)
"""
WORKER = """
import json, pathlib, subprocess, sys, time
target = json.loads(sys.stdin.read())
if target['mode'] == 'raw':
    subprocess.Popen([sys.executable, '-c', CHILD, MARKER],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    until = time.monotonic() + 5
    while not pathlib.Path(MARKER).exists() and time.monotonic() < until:
        time.sleep(.01)
    if BEHAVIOR == 'timeout':
        time.sleep(60)
    if BEHAVIOR == 'crash':
        sys.exit(7)
    if BEHAVIOR == 'malformed':
        print('not-json PRIVATE_WORKER_BODY')
    else:
        print(json.dumps({'status': 'completed', 'ok': True, 'findings': [], 'negative_window_completed': True}))
else:
    print(json.dumps({'status': 'completed', 'ok': True, 'findings': [], 'negative_window_completed': True}))
"""


def assert_port_closed(port):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        with socket.socket() as probe:
            probe.settimeout(.1)
            if probe.connect_ex(("127.0.0.1", port)) != 0:
                return
        time.sleep(.02)
    pytest.fail("owned worker descendant still listening after cleanup")


@pytest.mark.parametrize("behavior,status", [("timeout", "timeout"), ("crash", "error"),
                                             ("malformed", "error"), ("success", "completed")])
def test_real_worker_tree_cleanup_and_cli_continuation(monkeypatch, tmp_path, behavior, status):
    marker = tmp_path / "owned-child.json"
    script = tmp_path / "worker.py"
    script.write_text("CHILD = " + repr(CHILD) + "\nMARKER = " + repr(str(marker))
                      + "\nBEHAVIOR = " + repr(behavior) + "\n" + WORKER, encoding="utf-8")
    original = process_control.OwnedProcess
    monkeypatch.setattr(process_control, "OwnedProcess", lambda command: original([sys.executable, str(script)]))
    corpus = runner.proof_corpus()
    corpus["targets"][0]["budget_seconds"] = 2
    monkeypatch.setattr(runner, "proof_corpus", lambda browser=None: corpus)
    output = tmp_path / "result.md"
    monkeypatch.setenv("BENCH_STRICT", "1")
    monkeypatch.setattr(sys, "argv", ["bench/run.py", "--proof-suite", "--targets",
                        "proof-raw,proof-fixed", "--out", str(output), "--no-history"])
    # An unrelated owned test process must survive the benchmark's cleanup.
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
    try:
        started = time.monotonic()
        assert runner.main() == 1  # success test intentionally misses positive => FN
        assert time.monotonic() - started < 12
        assert unrelated.poll() is None
        assert marker.exists(), "worker did not exercise the descendant before returning"
        assert_port_closed(json.loads(marker.read_text())["port"])
        report = json.loads(output.with_suffix(".json").read_text(encoding="utf-8"))
        first, second = [row["results"]["dxaprove"] for row in report["rows"]]
        assert first["observed"]["status"] == status
        assert second["observed"]["status"] == "completed"
        assert first["score"]["evaluated"] is (status == "completed")
        assert second["score"] == {"tp": 0, "fp": 0, "fn": 0, "evaluated": True}
        assert "PRIVATE_WORKER_BODY" not in output.read_text(encoding="utf-8") + json.dumps(report)
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)


def test_real_proof_worker_missing_browser_is_error():
    target = runner.proof_corpus(str(pathlib.Path(__file__).with_name("missing-browser.exe")))["targets"][0]
    report = runner.run_all({"targets": [target]}, ["dxaprove"], None)
    result = report["rows"][0]["results"]["dxaprove"]
    assert result["observed"]["status"] == "error"
    assert result["observed"]["proof"]["schema"] == "dxa-browser-proof/1"
    assert result["score"]["evaluated"] is False
    assert runner.strict_failed(report)


@pytest.mark.parametrize("budget", [None, "invalid", float("nan"), float("inf"), 0, -1])
def test_invalid_budget_isolated_before_worker_creation(monkeypatch, budget):
    corpus = runner.proof_corpus()
    corpus["targets"][0]["budget_seconds"] = budget
    calls = []

    class Worker:
        proc = type("Process", (), {"returncode": 0})()

        def __init__(self, command):
            calls.append(command)

        def communicate(self, data, timeout):
            return json.dumps({"status": "completed", "ok": True, "findings": [],
                               "negative_window_completed": True})

        def close(self):
            pass

    monkeypatch.setattr(process_control, "OwnedProcess", Worker)
    report = runner.run_all(corpus, ["dxaprove"], ["proof-raw", "proof-fixed"])
    first, second = [row["results"]["dxaprove"] for row in report["rows"]]
    assert first["observed"]["status"] == "error"
    assert first["score"]["evaluated"] is False
    assert second["observed"]["status"] == "completed"
    assert len(calls) == 1


@pytest.mark.parametrize("times_out", [False, True])
def test_cleanup_failure_is_unscored_and_next_case_survives(monkeypatch, times_out):
    class Worker:
        proc = type("Process", (), {"returncode": 0})()

        def __init__(self, command):
            self.first = False

        def communicate(self, data, timeout):
            self.first = json.loads(data)["mode"] == "raw"
            if self.first and times_out:
                raise subprocess.TimeoutExpired("owned-worker", timeout)
            return json.dumps({"status": "completed", "ok": True, "findings": [],
                               "negative_window_completed": True})

        def close(self):
            if self.first:
                raise OSError("PRIVATE_CLEANUP_ERROR")

    monkeypatch.setattr(process_control, "OwnedProcess", Worker)
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], ["proof-raw", "proof-fixed"])
    first, second = [row["results"]["dxaprove"] for row in report["rows"]]
    assert first["observed"]["status"] == "error"
    assert first["score"]["evaluated"] is False
    assert second["observed"]["status"] == "completed"
    assert "PRIVATE_CLEANUP_ERROR" not in json.dumps(report)


@pytest.mark.parametrize("unsafe", [
    {"services": {"web": {"container_name": "existing-user-app"}}},
    {"services": {"web": {"volumes": [{"type": "bind", "source": "user-data"}]}}},
    {"services": {"web": {"network_mode": "host"}}},
    {"services": {"web": {"privileged": True}}},
    {"services": {"web": {"ports": [{"target": 80, "published": "9999"}]}}},
    {"services": {"web": {"ports": [{"target": 80, "host_ip": "0.0.0.0"}]}}},
    {"services": {"web": {}}, "volumes": {"data": {"name": "existing-data"}}},
    {"services": {"web": {}}, "volumes": {"data": {"external": True}}},
    {"services": {"web": {}}, "networks": {"default": {"external": True}}},
])
def test_docker_refuses_shared_resources_without_start_or_teardown(monkeypatch, unsafe):
    unsafe = dict(unsafe)
    unsafe["services"] = {"web": dict(safe_docker_service(), **unsafe["services"]["web"])}
    calls = []

    def command(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, json.dumps(unsafe), "")

    monkeypatch.setattr(runner.subprocess, "run", command)
    with runner.DockerTarget("lab.yml", "http://127.0.0.1:9999") as target:
        assert not target.up_ok
        assert target._up_msg == "compose ownership preflight failed"
    assert len(calls) == 1
    assert calls[0][-3:] == ["config", "--format", "json"]


@pytest.mark.parametrize("failure", ["none", "up", "ready", "scan"])
def test_docker_only_tears_down_unique_owned_project_and_preserves_volumes(monkeypatch, tmp_path, failure):
    compose = tmp_path / "lab.yml"
    compose.write_text("services: {}", encoding="utf-8")
    calls = []

    def command(cmd, **kwargs):
        calls.append(cmd)
        if "config" in cmd:
            project = cmd[cmd.index("-p") + 1]
            service = safe_docker_service()
            service["volumes"] = [{"type": "volume", "source": "data"}]
            config = {"services": {"web": service},
                      "volumes": {"data": {"name": project + "_data"}}}
            return subprocess.CompletedProcess(cmd, 0, json.dumps(config), "")
        return subprocess.CompletedProcess(cmd, int(failure == "up" and "up" in cmd), "", "")

    monkeypatch.setattr(runner.subprocess, "run", command)
    monkeypatch.setattr(runner, "_wait_for_http", lambda *a, **kw: failure != "ready")
    target = runner.DockerTarget(str(compose), "http://127.0.0.1:9999")
    other = runner.DockerTarget(str(compose), "http://127.0.0.1:9999")
    assert target.project != other.project
    try:
        with target:
            assert target.up_ok is (failure in ("none", "scan"))
            if failure == "scan":
                raise RuntimeError("scanner failure")
    except RuntimeError:
        assert failure == "scan"
    assert len(calls) == 6
    assert calls[-1][-1] == "down"
    for cmd in calls:
        if "compose" in cmd:
            assert cmd[cmd.index("-p") + 1] == target.project
        else:
            assert "label=com.docker.compose.project=" + target.project in cmd
        assert "-v" not in cmd and "--volumes" not in cmd


@pytest.mark.parametrize("failure", ["daemon", "timeout", "malformed"])
def test_docker_preflight_failure_never_tears_down(monkeypatch, failure):
    calls = []

    def command(cmd, **kwargs):
        calls.append(cmd)
        if failure == "timeout":
            raise subprocess.TimeoutExpired(cmd, 30)
        return subprocess.CompletedProcess(cmd, int(failure == "daemon"), "not-json", "private")

    monkeypatch.setattr(runner.subprocess, "run", command)
    with runner.DockerTarget("lab.yml", "http://127.0.0.1:9999") as target:
        assert not target.up_ok
    assert len(calls) == 1


@pytest.mark.parametrize("timeout", [False, True])
@pytest.mark.parametrize("ready", [False, True])
def test_docker_cleanup_failure_overrides_success_and_preserves_project(monkeypatch, tmp_path, timeout, ready):
    compose = tmp_path / "lab.yml"
    compose.write_text("services: {}", encoding="utf-8")

    def command(cmd, **kwargs):
        if "config" in cmd:
            return subprocess.CompletedProcess(cmd, 0, json.dumps({"services": {"web": safe_docker_service()}}), "")
        if "down" in cmd:
            if timeout:
                raise subprocess.TimeoutExpired(cmd, 60)
            return subprocess.CompletedProcess(cmd, 1, "", "PRIVATE_DOCKER_ERROR")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(runner.subprocess, "run", command)
    monkeypatch.setattr(runner, "_docker_available", lambda: True)
    monkeypatch.setattr(runner, "_wait_for_http", lambda *a, **kw: ready)
    monkeypatch.setitem(runner.SCANNERS, "dxadyn", lambda *a: {"ok": True, "status": "completed"})
    target = {"id": "owned", "kind": "docker", "compose_file": str(compose),
              "url": "http://127.0.0.1:9999/", "expect": {}}
    report = runner.run_all({"targets": [target]}, ["dxadyn"], None)
    row = report["rows"][0]
    assert row["results"]["dxadyn"]["observed"]["reason"] == "docker-cleanup-failed"
    assert report["totals"]["dxadyn"]["error"] == 1
    assert report["totals"]["dxadyn"]["completed"] == 0
    assert runner.strict_failed(report)
    assert row["docker_project"].startswith("dxa-bench-")
    assert row["docker_project"] in runner.render_md(report)
    assert "PRIVATE_DOCKER_ERROR" not in json.dumps(report)
