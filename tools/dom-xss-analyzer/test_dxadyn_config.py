"""R6 dynamic CLI tuning configuration: precedence, strict input and scope."""
import json
import sys

import pytest

import dxadom
import dxadyn


@pytest.fixture(autouse=True)
def preserve_tuning(monkeypatch):
    for name in ("PARALLEL_WORKERS", "_RATE_LIMITER", "JITTER_MS_MIN", "JITTER_MS_MAX"):
        monkeypatch.setattr(dxadyn, name, getattr(dxadyn, name))


def config_file(tmp_path, body, encoding="utf-8"):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(body), encoding=encoding)
    return path


def run_cli(monkeypatch, args, expected=0):
    monkeypatch.setattr(sys, "argv", ["dxadyn", *args])
    with pytest.raises(SystemExit) as result:
        dxadyn.main()
    assert result.value.code == expected


@pytest.mark.parametrize("config,cli,expected", [
    (None, [], (0, 1, None)),
    ({"schema_version": 1}, [], (0, 1, None)),
    ({"schema_version": 1, "depth": 2, "parallel": 3, "rate": 2.5}, [], (2, 3, 2.5)),
    ({"schema_version": 1, "depth": 2, "parallel": 3, "rate": 2.5},
     ["--depth", "0", "--parallel", "1", "--rate", "0"], (0, 1, None)),
    ({"schema_version": 1, "depth": 2, "parallel": 3, "rate": 2.5},
     ["--parallel", "4"], (2, 4, 2.5)),
])
def test_cli_config_precedence(monkeypatch, tmp_path, config, cli, expected):
    observed = []

    def crawl(url, depth, **kwargs):
        observed.append((depth, dxadyn.PARALLEL_WORKERS, dxadyn._RATE_LIMITER))
        return []

    monkeypatch.setattr(dxadyn, "crawl", crawl)
    monkeypatch.setattr(dxadyn, "_TokenBucket", lambda rate: rate)
    args = ["http://127.0.0.1/fixture", *cli]
    if config is not None:
        args += ["--config", str(config_file(tmp_path, config, "utf-8-sig"))]
    run_cli(monkeypatch, args)
    assert observed == [expected]


@pytest.mark.parametrize("body", [
    [], None, {}, {"schema_version": True}, {"schema_version": 1.0},
    {"schema_version": "1"}, {"schema_version": 2},
    {"schema_version": 1, "cookie": "LOCAL_CONFIG_SECRET"},
    {"schema_version": 1, "url": "http://127.0.0.1/LOCAL_CONFIG_SECRET"},
    {"schema_version": 1, "html": "LOCAL_CONFIG_SECRET"},
    {"schema_version": 1, "depth": True}, {"schema_version": 1, "depth": -1},
    {"schema_version": 1, "depth": 1.0}, {"schema_version": 1, "depth": "2"},
    {"schema_version": 1, "parallel": False}, {"schema_version": 1, "parallel": 0},
    {"schema_version": 1, "parallel": 1.5}, {"schema_version": 1, "parallel": "2"},
    {"schema_version": 1, "rate": True}, {"schema_version": 1, "rate": -0.1},
    {"schema_version": 1, "rate": "1"}, {"schema_version": 1, "rate": None},
    {"schema_version": 1, "rate": float("nan")},
    {"schema_version": 1, "rate": float("inf")},
    {"schema_version": 1, "rate": 10 ** 400},
])
def test_invalid_config_stops_before_io(monkeypatch, tmp_path, capsys, body):
    def unexpected(*args, **kwargs):
        pytest.fail("invalid config reached target/session IO")

    for name in ("crawl", "login", "apply_cookie", "run_auth_flow"):
        monkeypatch.setattr(dxadyn, name, unexpected)
    report = tmp_path / "report.json"
    page = tmp_path / "report.html"
    run_cli(monkeypatch, ["http://127.0.0.1/fixture", "--config",
                         str(config_file(tmp_path, body)), "--cookie", "LOCAL_CONFIG_SECRET",
                         "--json-out", str(report), "--html", str(page)], 2)
    assert not report.exists() and not page.exists()
    assert "LOCAL_CONFIG_SECRET" not in capsys.readouterr().err


@pytest.mark.parametrize("raw", [
    b'{"schema_version":1,"rate":1,"rate":2}',
    b'{"schema_version":1,"schema_version":1}',
    b'{"schema_version":1,"rate":LOCAL_CONFIG_SECRET}',
    b'\xff\xfeLOCAL_CONFIG_SECRET',
    None,
])
def test_unreadable_or_ambiguous_config(monkeypatch, tmp_path, capsys, raw):
    path = tmp_path / "LOCAL_CONFIG_SECRET.json"
    if raw is not None:
        path.write_bytes(raw)
    run_cli(monkeypatch, ["http://127.0.0.1/fixture", "--config", str(path)], 2)
    assert "LOCAL_CONFIG_SECRET" not in capsys.readouterr().err


@pytest.mark.parametrize("key,value,mode", [
    ("depth", 0, ["--stored"]), ("depth", 0, ["--flow", "absent.json"]),
    ("depth", 0, ["--auth-check", "absent.json"]),
    ("depth", 0, ["--dom"]), ("parallel", 1, ["--dom"]),
    ("parallel", 1, ["--flow", "absent.json"]),
    ("parallel", 1, ["--auth-check", "absent.json"]),
    ("rate", 0, ["--dom"]),
])
@pytest.mark.parametrize("source", ["config", "cli"])
def test_irrelevant_tuning_is_rejected_before_io(monkeypatch, tmp_path, key, value, mode, source):
    def unexpected(*args, **kwargs):
        pytest.fail("unsupported tuning reached IO")

    monkeypatch.setattr(dxadom, "is_available", unexpected)
    monkeypatch.setattr(dxadom, "summarize_availability", unexpected)
    monkeypatch.setattr(dxadyn, "_load_flow", unexpected)
    monkeypatch.setattr(dxadyn, "probe_stored", unexpected)
    args = list(mode)
    if source == "config":
        args += ["--config", str(config_file(tmp_path, {"schema_version": 1, key: value}))]
    else:
        args += ["--" + key, str(value)]
    run_cli(monkeypatch, args, 2)


@pytest.mark.parametrize("option,value", [
    ("--depth", "-1"), ("--parallel", "0"), ("--parallel", "-2"),
    ("--rate", "-1"), ("--rate", "nan"), ("--rate", "inf"),
])
def test_cli_tuning_bounds(monkeypatch, option, value):
    monkeypatch.setattr(dxadyn, "crawl", lambda *args, **kwargs: pytest.fail("invalid tuning scanned"))
    run_cli(monkeypatch, ["http://127.0.0.1/fixture", option, value], 2)


def test_stored_parallel_and_rate_config_reach_probe(monkeypatch, tmp_path):
    seen = []

    def probe(*args, **kwargs):
        seen.append((dxadyn.PARALLEL_WORKERS, dxadyn._RATE_LIMITER))
        return [], "local-cid"

    monkeypatch.setattr(dxadyn, "probe_stored", probe)
    monkeypatch.setattr(dxadyn, "_TokenBucket", lambda rate: rate)
    path = config_file(tmp_path, {"schema_version": 1, "parallel": 2, "rate": 3})
    run_cli(monkeypatch, ["--stored", "--target", "http://127.0.0.1/form", "--target-field",
                         "comment", "--check", "http://127.0.0.1/read", "--config", str(path)])
    assert seen == [(2, 3)]


@pytest.mark.parametrize("mode", ["flow", "auth-flow"])
def test_rate_config_reaches_http_flow(monkeypatch, tmp_path, mode):
    seen = []
    monkeypatch.setattr(dxadyn, "_load_flow", lambda path: {})
    monkeypatch.setattr(dxadyn, "_TokenBucket", lambda rate: rate)

    def run(*args, **kwargs):
        seen.append(dxadyn._RATE_LIMITER)
        return {"name": "local", "error": None, "steps_run": 0, "verdicts": [],
                "auth_header": None, "authenticated": True}

    monkeypatch.setattr(dxadyn, "run_flow" if mode == "flow" else "run_auth_flow", run)
    path = config_file(tmp_path, {"schema_version": 1, "rate": 1.5})
    run_cli(monkeypatch, ["--" + mode, "fixture.json", "--config", str(path)])
    assert seen == [1.5]


def test_invalid_config_cannot_be_hidden_by_cli_override(monkeypatch, tmp_path):
    path = config_file(tmp_path, {"schema_version": 1, "rate": -1})
    run_cli(monkeypatch, ["http://127.0.0.1/fixture", "--config", str(path), "--rate", "0"], 2)


def test_schema_only_config_allows_dom_availability(monkeypatch, tmp_path):
    monkeypatch.setattr(dxadom, "summarize_availability", lambda: "local test browser")
    monkeypatch.setattr(dxadom, "is_available", lambda: (True, "test"))
    path = config_file(tmp_path, {"schema_version": 1})
    run_cli(monkeypatch, ["--dom", "--config", str(path)])


def test_help_describes_config_and_worker_limits(monkeypatch, capsys):
    run_cli(monkeypatch, ["--help"])
    text = " ".join(capsys.readouterr().out.split())
    assert "CLI > config > defaults" in text
    assert "targets, credentials and output paths are not supported" in text
    assert "reflected/stored modes: schedule probe jobs" in text
    assert "Shared-session HTTP transactions remain serialized" in text
    assert "does not promise parallel HTTP throughput" in text
    assert "one round-trip" not in text
