"""Regression tests for explicit, non-scoring Bludit product controls."""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run as bench_run  # noqa: E402


def _adapter_result(*, status="passed", cleanup="passed", raw=True, escaped=False,
                    events=None):
    return {
        "schema": "dxa-bludit-lab/1", "status": status,
        "product": "Bludit", "embedded_version": "3.16.2", "triage": "by-design",
        "project": "dxa-bludit-0123456789abcdef0123456789abcdef",
        "origin": "http://127.0.0.1:49152", "session": {"author": "admin"},
        "cleanup_status": cleanup,
        "cases": [
            {"case_id": "raw-admin-content", "path": "/private-slug", "canary_id": "secret-cid",
             "payload_sha256": "a" * 64, "expected_execution": True,
             "execution_observed": raw, "status": "execution-observed" if raw else "no-execution-observed",
             "observation_ms": 1000, "matched": raw},
            {"case_id": "escaped-admin-content", "path": "/another-private-slug", "canary_id": "secret-cid-2",
             "payload_sha256": "b" * 64, "expected_execution": False,
             "execution_observed": escaped,
             "status": "execution-observed" if escaped else "no-execution-observed",
             "observation_ms": 1000, "matched": not escaped},
        ],
        "events": events or [],
    }


def _base_report():
    return {"run_at": "fixed", "corpus_version": "test/1", "scanners": ["dxadyn"],
            "rows": [], "totals": {"dxadyn": {"tp": 2, "fp": 1, "fn": 0,
                                                       "wall": 0.5, "selected": 1,
                                                       "completed": 1, "skipped": 0,
                                                       "error": 0, "timeout": 0,
                                                       "invalid": 0, "inconclusive": 0}}}


def test_valid_control_is_sanitized_and_never_scored():
    result = bench_run.validate_bludit_control(_adapter_result())
    assert result["kind"] == "product-control"
    assert result["triage"] == "by-design"
    assert [(case["case_id"], case["expected_execution"], case["execution_observed"], case["matched"])
            for case in result["cases"]] == [
                ("raw-admin-content", True, True, True),
                ("escaped-admin-content", False, False, True)]
    serialized = json.dumps(result)
    for secret in ("secret-cid", "payload_sha256", "private-slug", "49152", "session", "project"):
        assert secret not in serialized

    report = _base_report()
    report["product_controls"] = [result]
    assert report["totals"] == _base_report()["totals"]
    markdown = bench_run.render_md(report)
    assert "Product controls (by-design; excluded from vulnerability scoring)" in markdown
    assert "TP | FP | FN" in markdown
    assert "raw-admin-content | true | true | true" in markdown


@pytest.mark.parametrize("mutate", [
    lambda result: result.update(cases=result["cases"][:1]),
    lambda result: result["cases"][0].update(case_id="wrong-case"),
    lambda result: result["cases"][0].update(matched=False),
    lambda result: result["cases"][0].update(execution_observed="true"),
    lambda result: result["cases"][1].update(expected_execution=True),
    lambda result: result.update(status="passed", cleanup_status="error"),
])
def test_incomplete_mismatched_or_contradictory_results_are_rejected(mutate):
    result = _adapter_result()
    mutate(result)
    with pytest.raises(ValueError):
        bench_run.validate_bludit_control(result)


def test_cleanup_failure_is_a_sanitized_failure():
    result = _adapter_result(status="error", cleanup="error",
                             events=[{"stage": "cleanup", "kind": "error",
                                      "reason": "cleanup-failed", "detail": "cookie=do-not-copy"}])
    clean = bench_run.validate_bludit_control(result)
    assert clean["status"] == "error"
    assert clean["cleanup_status"] == "error"
    assert clean["events"] == [{"stage": "cleanup", "kind": "error", "reason": "cleanup-failed"}]
    assert "cookie" not in json.dumps(clean)


def test_adapter_error_with_incomplete_cases_remains_nonpassing():
    result = _adapter_result(status="error", cleanup="passed",
                             events=[{"stage": "browser", "kind": "error", "reason": "browser-unavailable"}])
    result["cases"] = []
    clean = bench_run.validate_bludit_control(result)
    assert clean["status"] == "error"
    assert clean["cases"] == []
    assert clean["events"][0]["reason"] == "browser-unavailable"


def test_runner_preserves_cleanup_error_and_sanitizes_malformed_adapter(tmp_path, monkeypatch):
    browser = tmp_path / "chrome.exe"
    browser.write_bytes(b"test executable placeholder")
    compose = tmp_path / "local-inspected.yml"
    compose.write_text("fixture", encoding="utf-8")
    monkeypatch.delenv("CI", raising=False)

    class CleanupError:
        def __init__(self, compose_file):
            pass

        def run(self, output_dir, browser_path):
            return _adapter_result(status="error", cleanup="error", events=[
                {"stage": "cleanup", "kind": "error", "reason": "cleanup-failed",
                 "detail": "cookie=must-not-leak"}])

    failed = bench_run.run_bludit_control(compose_file=str(compose), browser=str(browser),
                                           adapter_class=CleanupError)
    assert failed["status"] == "error"
    assert failed["cleanup_status"] == "error"
    assert "cookie" not in json.dumps(failed)

    class Malformed:
        def __init__(self, compose_file):
            pass

        def run(self, output_dir, browser_path):
            return {"status": "passed", "cleanup_status": "error", "cases": [],
                    "events": [{"stage": "cleanup", "kind": "error",
                                "reason": "cleanup-failed", "cookie": "redacted"}]}

    rejected = bench_run.run_bludit_control(compose_file=str(compose), browser=str(browser),
                                             adapter_class=Malformed)
    assert rejected["status"] == "error"
    assert rejected["cleanup_status"] == "error"
    assert rejected["events"] == [{"stage": "cleanup", "kind": "error", "reason": "cleanup-failed"}]
    assert "redacted" not in json.dumps(rejected)


def test_run_bludit_control_calls_real_adapter_shape_and_validates(tmp_path, monkeypatch):
    browser = tmp_path / "chrome.exe"
    browser.write_bytes(b"test executable placeholder")
    compose = tmp_path / "local-inspected.yml"
    compose.write_text("fixture", encoding="utf-8")
    monkeypatch.delenv("CI", raising=False)
    calls = {}

    class FakeAdapter:
        def __init__(self, compose_file):
            calls["compose_file"] = compose_file

        def run(self, output_dir, browser_path):
            calls["output_dir"] = output_dir
            calls["browser"] = browser_path
            assert pathlib.Path(output_dir).parent.is_dir()
            assert not pathlib.Path(output_dir).exists()
            return _adapter_result()

    result = bench_run.run_bludit_control(compose_file=str(compose), browser=str(browser),
                                           adapter_class=FakeAdapter)
    assert result["status"] == "passed"
    assert calls["compose_file"] == str(compose.resolve())
    assert calls["browser"] == str(browser)
    assert not pathlib.Path(calls["output_dir"]).exists()


def test_cli_does_not_run_bludit_without_explicit_opt_in(tmp_path, monkeypatch):
    monkeypatch.setattr(bench_run, "load_corpus", lambda _: {"corpus_version": "test/1", "targets": []})
    monkeypatch.setattr(bench_run, "run_all", lambda *_: _base_report())
    calls = []
    monkeypatch.setattr(bench_run, "run_bludit_control", lambda **kwargs: calls.append(kwargs))
    out = tmp_path / "ordinary.md"
    monkeypatch.setattr(sys, "argv", ["bench/run.py", "--out", str(out), "--no-history"])
    assert bench_run.main() == 0
    assert calls == []
    report = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
    assert "product_controls" not in report


def test_cli_requires_browser_for_explicit_opt_in(tmp_path, monkeypatch):
    monkeypatch.setattr(bench_run, "load_corpus", lambda _: {"corpus_version": "test/1", "targets": []})
    monkeypatch.setattr(bench_run, "run_all", lambda *_: _base_report())
    monkeypatch.setattr(sys, "argv", ["bench/run.py", "--bludit-control", "--no-history",
                                       "--out", str(tmp_path / "result.md")])
    with pytest.raises(SystemExit) as exc:
        bench_run.main()
    assert exc.value.code == 2


def test_cli_explicit_opt_in_keeps_product_control_out_of_totals(tmp_path, monkeypatch):
    browser = tmp_path / "chrome.exe"
    browser.write_bytes(b"test executable placeholder")
    monkeypatch.setattr(bench_run, "load_corpus", lambda _: {"corpus_version": "test/1", "targets": []})
    monkeypatch.setattr(bench_run, "run_all", lambda *_: _base_report())
    control = bench_run.validate_bludit_control(_adapter_result())
    calls = []
    monkeypatch.setattr(bench_run, "run_bludit_control",
                        lambda **kwargs: calls.append(kwargs) or control)
    out = tmp_path / "controls.md"
    monkeypatch.setattr(sys, "argv", ["bench/run.py", "--bludit-control", "--bludit-browser",
                                       str(browser), "--out", str(out), "--no-history"])
    assert bench_run.main() == 0
    report = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
    assert calls == [{"compose_file": None, "browser": str(browser)}]
    assert report["product_controls"] == [control]
    assert report["totals"] == _base_report()["totals"]
    assert "raw-admin-content | true | true | true" in out.read_text(encoding="utf-8")


def test_cli_returns_failure_for_control_or_cleanup_error(tmp_path, monkeypatch):
    browser = tmp_path / "chrome.exe"
    browser.write_bytes(b"test executable placeholder")
    monkeypatch.setattr(bench_run, "load_corpus", lambda _: {"corpus_version": "test/1", "targets": []})
    monkeypatch.setattr(bench_run, "run_all", lambda *_: _base_report())
    failed = bench_run._bludit_failure("cleanup-failed", "error", [
        {"stage": "cleanup", "kind": "error", "reason": "cleanup-failed"}])
    monkeypatch.setattr(bench_run, "run_bludit_control", lambda **kwargs: failed)
    out = tmp_path / "failed.md"
    monkeypatch.setattr(sys, "argv", ["bench/run.py", "--bludit-control", "--bludit-browser",
                                       str(browser), "--out", str(out), "--no-history"])
    assert bench_run.main() == 2
    report = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
    assert report["product_controls"][0]["cleanup_status"] == "error"
    assert report["totals"] == _base_report()["totals"]


def test_ci_and_missing_browser_refuse_before_adapter(tmp_path, monkeypatch):
    monkeypatch.setenv("CI", "true")
    class NeverCalled:
        def __init__(self, **kwargs):
            raise AssertionError("adapter must not start in CI")
    refused = bench_run.run_bludit_control(browser=str(tmp_path / "missing"), adapter_class=NeverCalled)
    assert refused["status"] == "error"
    assert refused["events"][0]["reason"] == "ci-execution-refused"

    monkeypatch.delenv("CI")
    refused = bench_run.run_bludit_control(browser=str(tmp_path / "missing"), adapter_class=NeverCalled)
    assert refused["status"] == "error"
    assert refused["events"][0]["reason"] == "invalid-browser-path"
