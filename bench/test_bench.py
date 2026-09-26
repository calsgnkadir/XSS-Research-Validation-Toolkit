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


def test_end_to_end_runner_on_mock_corpus():
    """The whole harness against the real dxadyn CLI on the mock corpus.
    This is the smoke test that guards regressions in the parser or corpus."""
    corpus = bench_run.load_corpus(HERE / "targets.json")
    report = bench_run.run_all(corpus, ["dxadyn"], only=None)
    totals = report["totals"]["dxadyn"]
    # dxadyn must catch both vulnerable mock targets and not FP on the safe one.
    assert totals["tp"] >= 2, f"expected >=2 TP, got {totals}"
    assert totals["fp"] == 0, f"expected 0 FP, got {totals}"
    assert totals["fn"] == 0, f"expected 0 FN, got {totals}"


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
