"""Tests for the benchmark harness. Zero-dep, CI-friendly."""
from __future__ import annotations
import json
import pathlib
import sys
import urllib.request

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from mock_target import MockServer  # noqa: E402
import run as bench_run  # noqa: E402


def _get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.read().decode("utf-8", errors="replace")


def test_mock_echo_reflects_raw():
    with MockServer(port=0) as srv:
        body = _get(f"http://127.0.0.1:{srv.port}/echo?q=%3Cscript%3Ex%3C/script%3E")
        assert "<script>x</script>" in body


def test_mock_safe_echo_escapes():
    with MockServer(port=0) as srv:
        body = _get(f"http://127.0.0.1:{srv.port}/safe-echo?q=%3Cscript%3Ex%3C/script%3E")
        assert "<script>x</script>" not in body
        assert "&lt;script&gt;" in body


def test_mock_guestbook_stores_and_reflects():
    import urllib.parse
    with MockServer(port=0) as srv:
        data = urllib.parse.urlencode({"msg": "<b>hi</b>"}).encode()
        req = urllib.request.Request(f"http://127.0.0.1:{srv.port}/guestbook", data=data, method="POST")
        urllib.request.urlopen(req, timeout=5).read()
        body = _get(f"http://127.0.0.1:{srv.port}/guestbook")
        assert "<b>hi</b>" in body


def test_score_true_positive():
    s = bench_run.score({"reflected": 1, "stored": 0, "dom": 0},
                        {"reflected": 1, "stored": 0, "dom": 0})
    assert s == {"tp": 1, "fp": 0, "fn": 0}


def test_partial_detection_keeps_missing_findings():
    assert bench_run.score({"reflected": 3}, {"reflected": 1}) == {"tp": 1, "fp": 0, "fn": 2}


@pytest.mark.parametrize("status", ["error", "timeout", "skipped"])
def test_incomplete_observation_is_not_scored(status):
    assert bench_run.score({"reflected": 3}, {"status": status, "reflected": 3}) == {"tp": 0, "fp": 0, "fn": 0}
    assert bench_run.strict_failed({"totals": {"dxadyn": {"completed": 1, status: 1}}})


def test_identity_matching_rejects_wrong_sink_and_deduplicates():
    observations = [{"finding_id": value, "evidence": "execution-observed", "canary_matched": True}
                    for value in ("a", "a", "wrong-sink")]
    assert bench_run.score_findings(["a", "b", "c"], observations) == {
        "tp": 1, "fp": 1, "fn": 2, "evaluated": True}


@pytest.mark.parametrize("evidence", ["candidate", "reflection", "resource-callback", "sink-observed"])
def test_non_execution_evidence_never_scores_as_execution(evidence):
    result = bench_run.score_findings(["a"], [{"finding_id": "a", "evidence": evidence, "canary_matched": True}])
    assert result["tp"] == 0 and result["fn"] == 1


def test_strict_gate_rejects_fp_and_empty_runs():
    assert bench_run.strict_failed({"totals": {"dxadyn": {"completed": 1, "fp": 1}}})
    assert bench_run.strict_failed({"totals": {"dxadyn": {"completed": 0}}})


@pytest.mark.parametrize("failure", ["timeout", "crash"])
def test_adapter_process_failures(monkeypatch, failure):
    def fake_run(*args, **kwargs):
        if failure == "timeout":
            raise bench_run.subprocess.TimeoutExpired("scanner", 1)
        return bench_run.subprocess.CompletedProcess([], 2, "", "failed")
    monkeypatch.setattr(bench_run.subprocess, "run", fake_run)
    target = {"url": "http://127.0.0.1:{port}/echo", "expect": {"stored": 0}}
    result = bench_run.run_dxadyn(target, "http://127.0.0.1:12345", 1)
    assert result["ok"] is False
    assert result["status"] == ("timeout" if failure == "timeout" else "error")


def test_unrecognized_output_is_error():
    assert bench_run._parse_dxadyn("unexpected output", 0)["status"] == "error"


def test_unknown_target_is_rejected():
    with pytest.raises(ValueError, match="Unknown target"):
        bench_run.run_all({"targets": []}, ["dxadyn"], ["typo"])


def test_coverage_keeps_skips_and_errors_visible(monkeypatch):
    monkeypatch.setattr(bench_run, "run_one", lambda target, scanners: {
        "id": target["id"], "results": {} if target["id"] == "skip" else {
            "dxadyn": {"observed": {"status": "timeout"}, "score": {"tp": 0, "fp": 0, "fn": 0}}}})
    report = bench_run.run_all({"targets": [{"id": "skip"}, {"id": "timeout"}]}, ["dxadyn"], None)
    totals = report["totals"]["dxadyn"]
    assert totals["selected"] == 2 and totals["skipped"] == 1 and totals["timeout"] == 1
    assert totals["completed"] == 0 and bench_run.strict_failed(report)


def test_score_false_positive_on_safe_target():
    s = bench_run.score({"reflected": 0, "stored": 0, "dom": 0},
                        {"reflected": 2, "stored": 0, "dom": 0})
    assert s == {"tp": 0, "fp": 2, "fn": 0}


def test_score_false_negative_on_vulnerable_target():
    s = bench_run.score({"reflected": 0, "stored": 1, "dom": 0},
                        {"reflected": 0, "stored": 0, "dom": 0})
    assert s == {"tp": 0, "fp": 0, "fn": 1}


def test_score_skipped_scanner_returns_zeros():
    s = bench_run.score({"reflected": 1}, {"skipped": "dalfox not on PATH"})
    assert s == {"tp": 0, "fp": 0, "fn": 0}


def test_corpus_loads_and_has_expected_keys():
    corpus = bench_run.load_corpus(HERE / "targets.json")
    assert "targets" in corpus
    ids = {t["id"] for t in corpus["targets"]}
    assert "mock-reflected-easy" in ids
    assert "mock-reflected-escaped" in ids
    assert "mock-stored-guestbook" in ids
    for t in corpus["targets"]:
        assert "expect" in t and "budget_seconds" in t and "kind" in t


def test_dalfox_and_xsstrike_skip_cleanly_when_absent(monkeypatch):
    monkeypatch.setattr(bench_run.shutil, "which", lambda name: None)
    tgt = {"url": "http://127.0.0.1:12345/echo", "expect": {"reflected": 1}}
    assert "skipped" in bench_run.run_dalfox(tgt, "http://127.0.0.1:12345", 5)
    assert "skipped" in bench_run.run_xsstrike(tgt, "http://127.0.0.1:12345", 5)


def test_render_md_shape():
    report = {
        "run_at": "2026-09-26T00:00:00Z",
        "corpus_version": "test",
        "scanners": ["dxadyn"],
        "rows": [{
            "id": "mock-x",
            "expect": {"reflected": 1, "stored": 0, "dom": 0},
            "results": {"dxadyn": {
                "observed": {"reflected": 1, "stored": 0, "dom": 0, "wall": 0.5},
                "score": {"tp": 1, "fp": 0, "fn": 0},
            }},
        }],
        "totals": {"dxadyn": {"tp": 1, "fp": 0, "fn": 0, "wall": 0.5}},
    }
    md = bench_run.render_md(report)
    assert "# Benchmark run" in md
    assert "| dxadyn |" in md
    assert "mock-x" in md


def test_parse_dxadyn_reflected_summary():
    out = "1 reflected candidate(s) - 1 EXECUTABLE (body/free context)\n"
    parsed = bench_run._parse_dxadyn(out, 0.5)
    assert parsed["reflected"] == 1
    assert parsed["stored"] == 0


def test_parse_dxadyn_stored_summary():
    out = "1 unique stored candidate(s) - 1 EXECUTABLE (body/free context)\n"
    parsed = bench_run._parse_dxadyn(out, 0.5)
    assert parsed["stored"] == 1
    assert parsed["reflected"] == 0


def test_parse_dxadyn_no_findings():
    out = "No unencoded reflections found.\n"
    parsed = bench_run._parse_dxadyn(out, 0.5)
    assert parsed["reflected"] == 0
    assert parsed["stored"] == 0


def test_end_to_end_runner_on_mock_corpus(monkeypatch):
    """The whole harness against the real dxadyn CLI on the mock corpus.
    This is the smoke test that guards regressions in the parser or corpus.
    Docker targets are opt-in (BENCH_ENABLE_DOCKER=1); this test runs with
    them skipped so the mock corpus is the whole scoring surface."""
    monkeypatch.delenv("BENCH_ENABLE_DOCKER", raising=False)
    corpus = bench_run.load_corpus(HERE / "targets.json")
    report = bench_run.run_all(corpus, ["dxadyn"], only=None)
    totals = report["totals"]["dxadyn"]
    # dxadyn must catch both vulnerable mock targets and not FP on the safe one.
    assert totals["tp"] >= 2, f"expected >=2 TP, got {totals}"
    assert totals["fp"] == 0, f"expected 0 FP, got {totals}"
    assert totals["fn"] == 0, f"expected 0 FN, got {totals}"


# --- Phase 7.0: docker target adapter ---------------------------------------

def test_docker_available_returns_bool(monkeypatch):
    """The check is a boolean function that never raises."""
    monkeypatch.delenv("BENCH_ENABLE_DOCKER", raising=False)
    result = bench_run._docker_available()
    assert isinstance(result, bool)


def test_docker_available_false_by_default(monkeypatch):
    """Docker targets are opt-in; BENCH_ENABLE_DOCKER unset -> False
    even when the docker binary is on PATH. Keeps CI green without a
    per-runner exclude list."""
    monkeypatch.delenv("BENCH_ENABLE_DOCKER", raising=False)
    monkeypatch.setattr(bench_run.shutil, "which", lambda name: "/usr/bin/docker")
    assert bench_run._docker_available() is False


def test_docker_available_true_with_env_and_binary(monkeypatch):
    """The two-condition contract: env opt-in AND binary present."""
    monkeypatch.setenv("BENCH_ENABLE_DOCKER", "1")
    monkeypatch.setattr(bench_run.shutil, "which", lambda name: "/usr/bin/docker")
    assert bench_run._docker_available() is True


def test_docker_available_false_when_binary_missing_even_with_env(monkeypatch):
    """Opt-in is necessary but not sufficient - missing docker binary
    still returns False so the adapter's error path fires."""
    monkeypatch.setenv("BENCH_ENABLE_DOCKER", "1")
    monkeypatch.setattr(bench_run.shutil, "which", lambda name: None)
    assert bench_run._docker_available() is False


def test_docker_available_recognises_truthy_env_values(monkeypatch):
    """Accept common truthy strings so a shell-set var is tolerant."""
    monkeypatch.setattr(bench_run.shutil, "which", lambda name: "/usr/bin/docker")
    for val in ("1", "true", "TRUE", "yes", "on"):
        monkeypatch.setenv("BENCH_ENABLE_DOCKER", val)
        assert bench_run._docker_available() is True, val
    for val in ("0", "false", "no", "off", ""):
        monkeypatch.setenv("BENCH_ENABLE_DOCKER", val)
        assert bench_run._docker_available() is False, val


def test_docker_compose_up_reports_missing_file(tmp_path):
    """A compose file that doesn't exist is a clean error, not a crash."""
    ok, msg = bench_run._docker_compose_up(str(tmp_path / "nope.yml"), project="dxa-test-missing")
    assert ok is False
    assert "not found" in msg


def test_wait_for_http_returns_false_on_unreachable():
    """A URL that doesn't respond within the deadline returns False,
    not raise."""
    result = bench_run._wait_for_http("http://127.0.0.1:1/", deadline_s=1)
    assert result is False


def test_wait_for_http_returns_true_when_reachable():
    """Point at our own mock server - reachable in one poll. Uses /echo
    because the mock's root path returns 404, and _wait_for_http only
    considers 2xx/3xx as ready."""
    with bench_run.start_mock("reflected_easy") as srv:
        result = bench_run._wait_for_http(
            f"http://127.0.0.1:{srv.port}/echo?q=hi", deadline_s=5)
        assert result is True


def test_readiness_redirect_never_contacts_other_endpoint():
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    hits = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            hits.append(self.path)
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", "/outside-ready-scope")
            else:
                self.send_response(200)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        assert bench_run._wait_for_http(f"http://127.0.0.1:{server.server_port}/redirect", 2)
        assert hits == ["/redirect"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(3)


def test_run_one_docker_target_skipped_by_default(monkeypatch):
    """Default state: BENCH_ENABLE_DOCKER unset -> docker target rows
    are skipped with a `_note` explaining how to opt in. This is what
    CI sees and why docker rows never break the green path."""
    monkeypatch.delenv("BENCH_ENABLE_DOCKER", raising=False)
    target = {
        "id": "test-docker", "kind": "docker",
        "compose_file": "bench/targets/nope/docker-compose.yml",
        "url": "http://127.0.0.1:9999/",
        "expect": {"reflected": 0, "stored": 0, "dom": 0},
        "budget_seconds": 5,
    }
    row = bench_run.run_one(target, ["dxadyn"])
    assert row["id"] == "test-docker"
    assert "_note" in row["results"]
    assert "BENCH_ENABLE_DOCKER" in row["results"]["_note"]


def test_run_one_docker_target_records_missing_compose_when_docker_present(monkeypatch):
    """If docker IS installed AND opted in but the compose file is missing,
    we get a docker-setup error - never a crash."""
    monkeypatch.setattr(bench_run, "_docker_available", lambda: True)
    target = {
        "id": "test-missing", "kind": "docker",
        "compose_file": "/tmp/does/not/exist.yml",
        "url": "http://127.0.0.1:9999/",
        "expect": {"reflected": 0, "stored": 0, "dom": 0},
        "budget_seconds": 5,
    }
    row = bench_run.run_one(target, ["dxadyn"])
    assert "_note" in row["results"]
    assert "docker setup" in row["results"]["_note"].lower()


def test_docker_target_class_teardown_is_best_effort(tmp_path):
    """DockerTarget context-manager exit MUST NOT raise even when the
    compose file was never brought up. Enables safe use inside `with`
    blocks that hit a mid-setup failure."""
    dt = bench_run.DockerTarget(
        compose_file=str(tmp_path / "nonexistent.yml"),
        ready_url="http://127.0.0.1:9999/",
        ready_timeout=1,
    )
    dt.__enter__()
    # Regardless of up_ok, __exit__ must not raise
    dt.__exit__(None, None, None)


def test_corpus_has_docker_targets_after_7_0():
    """After Phase 7.0 lands, the corpus must include the three
    documented docker rows so operators can discover them."""
    corpus = bench_run.load_corpus(HERE / "targets.json")
    ids = {t["id"] for t in corpus["targets"]}
    assert "bludit-3.16" in ids
    assert "dvwa" in ids
    assert "webgoat-8.2" in ids
    # And each carries a compose_file path pointing under bench/targets/
    for tgt in corpus["targets"]:
        if tgt["kind"] == "docker":
            assert tgt.get("compose_file", "").startswith("bench/targets/")


def test_corpus_docker_compose_files_exist():
    """Every docker target's compose_file must exist in the repo -
    a broken path is a shipping bug the operator hits on first run."""
    corpus = bench_run.load_corpus(HERE / "targets.json")
    repo_root = HERE.parent
    for tgt in corpus["targets"]:
        if tgt["kind"] != "docker":
            continue
        path = repo_root / tgt["compose_file"]
        assert path.is_file(), f"missing compose file: {tgt['compose_file']}"


def test_history_append(tmp_path):
    report = {
        "run_at": "2026-09-26T00:00:00Z",
        "corpus_version": "test",
        "totals": {"dxadyn": {"tp": 1, "fp": 0, "fn": 0, "wall": 0.1}},
    }
    hist = tmp_path / "history.jsonl"
    bench_run.append_history(report, hist)
    bench_run.append_history(report, hist)
    lines = hist.read_text().strip().splitlines()
    assert len(lines) == 2
    parsed = json.loads(lines[0])
    assert parsed["totals"]["dxadyn"]["tp"] == 1
