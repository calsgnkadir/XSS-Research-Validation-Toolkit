"""R4: a scanner summary is not proof that its HTTP window completed."""
from pathlib import Path
import socket
import sys
import urllib.request

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run as bench_run
from mock_target import MockServer


def target(path="/echo-land", stored=False):
    return {"url": "http://127.0.0.1:{port}" + path,
            "expect": {"stored": int(stored), "reflected": int(not stored)},
            "params": ["msg"], "csrf_field": ""}


def test_stored_auto_origin_root_seed_is_a_valid_fixture_page():
    with MockServer(port=0) as server:
        with urllib.request.urlopen(f"http://127.0.0.1:{server.port}/", timeout=5) as response:
            assert response.status == 200
            assert response.headers.get_content_type() == "text/html"
            assert b"Local benchmark fixture" in response.read()


def test_real_http_rejection_remains_incomplete():
    with MockServer(port=0) as server:
        case = target("/missing-fixture-page")
        observed = bench_run.run_dxadyn(case, f"http://127.0.0.1:{server.port}", 20)
    assert observed["status"] == "skipped", observed
    assert bench_run.score(case["expect"], observed) == {"tp": 0, "fp": 0, "fn": 0}


@pytest.mark.parametrize("stored", [False, True])
def test_real_connection_refusal_is_error_and_never_false_negative(stored):
    # Reserve the port without listening so no unrelated process can take it.
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        base = "http://127.0.0.1:" + str(reserved.getsockname()[1])
        case = target(stored=stored)
        observed = bench_run.run_dxadyn(case, base, 20)
    assert observed["status"] == "error", observed
    assert observed["ok"] is False
    assert bench_run.score(case["expect"], observed) == {"tp": 0, "fp": 0, "fn": 0}
    assert bench_run.strict_failed({"totals": {"dxadyn": {"completed": 0, "error": 1}}})


@pytest.mark.parametrize("path,stored,positive", [
    ("/echo-land", False, True),
    ("/safe-echo-land", False, False),
    ("/guestbook", True, True),
])
def test_real_completed_controls_remain_scoreable(path, stored, positive):
    with MockServer(port=0) as server:
        observed = bench_run.run_dxadyn(target(path, stored),
                                       f"http://127.0.0.1:{server.port}", 30)
    assert observed["status"] == "completed", observed
    assert observed["ok"] is True
    count = observed["stored" if stored else "reflected"]
    assert (count > 0) is positive
    if not positive:
        # A completed miss on a positive label must still be an FN.
        assert bench_run.score({"reflected": 1}, observed)["fn"] == 1


def report():
    return {"schema_version": 1, "mode": "reflected", "findings": [],
            "events": [], "meta": {}, "skipped_submits": 0}


@pytest.mark.parametrize("kind,status", [("error", "error"), ("skip", "skipped")])
@pytest.mark.parametrize("with_finding", [False, True])
def test_partial_report_is_unscored_even_with_a_candidate(kind, status, with_finding):
    document = report()
    document["events"] = [{"kind": kind}]
    if with_finding:
        document["findings"] = [{"schema_version": 1, "finding_id": "case",
                                 "evidence_level": "reflection"}]
    observed = bench_run._parse_dxadyn_report(document, 0, stored=False)
    assert observed["status"] == status
    assert bench_run.score({"reflected": 1}, observed) == {"tp": 0, "fp": 0, "fn": 0}


@pytest.mark.parametrize("field,value", [
    ("schema_version", True), ("mode", "dom"), ("findings", {}),
    ("events", None), ("events", [{"kind": "unknown"}]),
    ("skipped_submits", -1), ("skipped_submits", False),
    ("findings", [{"finding_id": "x"}]),
])
def test_malformed_reports_do_not_grant_completion(field, value):
    document = report()
    document[field] = value
    assert bench_run._parse_dxadyn_report(document, 0, stored=False)["status"] == "invalid"


def test_skipped_submit_count_does_not_grant_completion():
    document = report()
    document["skipped_submits"] = 1
    assert bench_run._parse_dxadyn_report(document, 0, stored=False)["status"] == "skipped"


@pytest.mark.parametrize("contents", [None, "not json", "{}"])
def test_successful_process_and_console_summary_cannot_replace_report(monkeypatch, contents):
    def fake_run(command, **kwargs):
        if contents is not None:
            Path(command[command.index("--json-out") + 1]).write_text(contents, encoding="utf-8")
        return bench_run.subprocess.CompletedProcess(command, 0, "No unencoded reflections found.", "")
    monkeypatch.setattr(bench_run.subprocess, "run", fake_run)
    observed = bench_run.run_dxadyn(target(), "http://127.0.0.1:12345", 1)
    assert observed["status"] == "invalid"
    assert bench_run.score({"reflected": 1}, observed)["fn"] == 0


def test_legacy_summary_alone_is_unscored():
    observed = bench_run._parse_dxadyn("No unencoded reflections found.", 0)
    assert observed["ok"] is False and observed["status"] == "error"
    assert bench_run.score({"reflected": 1}, observed)["fn"] == 0
