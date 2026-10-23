"""Roadmap E02: conservative SARIF 2.1.0 export for R1 evidence."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import jsonschema
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dxa
import dxa2dyn
import dxa_evidence as evidence
import dxa_sarif
import dxadyn

SARIF_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "sarif-schema-2.1.0.json"
with SARIF_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
    SARIF_21_SCHEMA = json.load(schema_file)
jsonschema.Draft7Validator.check_schema(SARIF_21_SCHEMA)
SARIF_21_VALIDATOR = jsonschema.Draft7Validator(
    SARIF_21_SCHEMA, format_checker=jsonschema.FormatChecker()
)


def r1_finding(evidence_level="candidate", triage="unreviewed", **overrides):
    finding = {
        "finding_id": "finding-stable-1",
        "attempt_id": "attempt-1",
        "canary_id": "canary-1",
        "source": {"url": "http://127.0.0.1/submit?token=URL_SECRET"},
        "sink": {"url": "http://127.0.0.1/read?sid=QUERY_SECRET"},
        "context": "html-body",
        "content_type": "text/html",
        "session_role": "unspecified",
        "evidence_level": evidence_level,
        "triage": triage,
        "role_verified": False,
        "evidence_links": [],
        "observations": [],
        "schema_version": 1,
    }
    finding.update(overrides)
    return finding


def r1_report(*findings, events=None):
    return {
        "schema_version": 1,
        "mode": "test",
        "findings": list(findings),
        "events": list(events or []),
        "meta": {},
        "skipped_submits": sum(event.get("kind") == "skip" for event in events or []),
    }


def r1_event(kind="info", **overrides):
    event = {"event_id": "event-1", "stage": "fixture", "kind": kind,
             "reason": "fixture observation", "observed_at": 123.5,
             "url": "", "status": None, "canary_id": None}
    event.update(overrides)
    return event


def validate_sarif_21(document):
    """Validate against the locally saved full OASIS SARIF 2.1.0 Draft 7 schema."""
    errors = sorted(
        SARIF_21_VALIDATOR.iter_errors(document),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    assert not errors, "SARIF schema validation errors:\n" + "\n".join(
        f"/{'/'.join(map(str, error.absolute_path))}: {error.message}"
        for error in errors
    )

    # Keep small semantic assertions alongside normative schema validation.
    assert document["version"] == "2.1.0"
    assert document["$schema"] == dxa_sarif.SARIF_SCHEMA
    assert isinstance(document["runs"], list) and document["runs"]
    for run in document["runs"]:
        driver = run["tool"]["driver"]
        assert isinstance(driver["name"], str) and driver["name"]
        rules = driver["rules"]
        rule_ids = {rule["id"] for rule in rules}
        assert rule_ids
        for rule in rules:
            assert isinstance(rule["name"], str) and rule["name"]
        assert isinstance(run["results"], list)
        for result in run["results"]:
            assert result["ruleId"] in rule_ids
            assert result["kind"] in {
                "notApplicable", "pass", "fail", "review", "open", "informational"
            }
            assert result["level"] in {"none", "note", "warning", "error"}
            if result["kind"] != "fail":
                assert result["level"] == "none"
            assert isinstance(result["message"]["text"], str)
            for location in result.get("locations", []):
                physical = location["physicalLocation"]
                assert isinstance(physical["artifactLocation"]["uri"], str)
                assert type(physical["region"]["startLine"]) is int
                assert physical["region"]["startLine"] >= 1
        for invocation in run.get("invocations", []):
            for notification in invocation.get("toolExecutionNotifications", []):
                assert notification["level"] in {"none", "note", "warning", "error"}
                assert isinstance(notification["message"]["text"], str)


@pytest.mark.parametrize("evidence_level", [
    "candidate", "reflection", "sink-observed", "resource-callback",
])
@pytest.mark.parametrize("triage", [
    "unreviewed", "candidate", "by-design", "self-xss", "rejected",
])
def test_r1_evidence_and_triage_do_not_become_sarif_severity(evidence_level, triage):
    document = dxa_sarif.to_sarif(r1_report(r1_finding(evidence_level, triage)))
    result = document["runs"][0]["results"][0]

    assert result["kind"] == "review"
    assert result["level"] == "none"
    assert result["properties"]["evidence_level"] == evidence_level
    assert result["properties"]["triage"] == triage
    assert "security-severity" not in result["properties"]
    assert "severity" not in result
    validate_sarif_21(document)


def test_export_is_deterministic_and_does_not_mutate_input():
    report = r1_report(r1_finding(observations=[{"nested": {"token": "SECRET"}}]),
                       events=[r1_event()])
    before = deepcopy(report)
    first = dxa_sarif.to_sarif(report)
    assert report == before
    assert first == dxa_sarif.to_sarif(report)


@pytest.mark.parametrize("kind,successful", [("info", True), ("skip", False), ("error", False)])
def test_operational_completion_distinguishes_skips_and_errors(kind, successful):
    run = dxa_sarif.to_sarif(r1_report(events=[r1_event(kind)]))["runs"][0]
    assert run["results"] == []
    assert run["invocations"][0]["executionSuccessful"] is successful


@pytest.mark.parametrize("field,value", [
    ("schema_version", True), ("schema_version", 2), ("schema_version", "1"),
    ("mode", ""), ("mode", None), ("events", {}), ("events", ["bad"]),
    ("findings", {}), ("meta", []), ("skipped_submits", True),
    ("skipped_submits", -1), ("skipped_submits", 1),
])
def test_invalid_report_contract_is_not_empty_success(field, value):
    report = r1_report()
    report[field] = value
    with pytest.raises((TypeError, ValueError)):
        dxa_sarif.to_sarif(report)


@pytest.mark.parametrize("field,value", [
    ("finding_id", ""), ("attempt_id", 1), ("canary_id", False),
    ("source", []), ("sink", None), ("context", 7), ("content_type", []),
    ("session_role", None), ("evidence_level", "execution-confirmed"),
    ("triage", "confirmed"), ("role_verified", True), ("schema_version", True),
    ("evidence_links", [1]), ("observations", ["raw"]),
])
def test_invalid_finding_contract_is_rejected(field, value):
    finding = r1_finding()
    finding[field] = value
    with pytest.raises((TypeError, ValueError)):
        dxa_sarif.to_sarif(r1_report(finding))


@pytest.mark.parametrize("field", ["finding_id", "attempt_id", "source", "sink", "context"])
def test_missing_required_finding_fields_are_rejected(field):
    finding = r1_finding()
    del finding[field]
    with pytest.raises((TypeError, ValueError)):
        dxa_sarif.to_sarif(r1_report(finding))


@pytest.mark.parametrize("field,value", [
    ("event_id", ""), ("stage", ""), ("reason", ""), ("kind", "ignored"),
    ("observed_at", float("nan")), ("observed_at", float("inf")),
    ("observed_at", True), ("observed_at", "now"), ("url", []),
    ("status", True), ("canary_id", 123),
])
def test_invalid_events_are_rejected_instead_of_silently_discarded(field, value):
    event = r1_event()
    event[field] = value
    with pytest.raises((TypeError, ValueError)):
        dxa_sarif.to_sarif(r1_report(events=[event]))


@pytest.mark.parametrize("field", ["event_id", "stage", "reason", "observed_at", "kind"])
def test_missing_event_fields_are_rejected(field):
    event = r1_event()
    del event[field]
    with pytest.raises((TypeError, ValueError)):
        dxa_sarif.to_sarif(r1_report(events=[event]))


@pytest.mark.parametrize("path", ["../private.js", "src/../../secret.js", "C:\\private.js",
    "/root/private.js", "//host/file", "javascript:alert(1)", "https://host/a",
    "//[invalid", "src/a.js?token=secret", "src/a.js#secret", "bad\x00name"])
def test_unsafe_paths_never_become_file_locations(path):
    result = dxa_sarif.to_sarif(r1_report(r1_finding(
        source={"file": path, "line": 1}, sink={"file": path, "line": 2}
    )))["runs"][0]["results"][0]
    assert "locations" not in result
    assert "relatedLocations" not in result


@pytest.mark.parametrize("line", [None, 0, -1, True, "12", 1.5])
def test_invalid_lines_do_not_invent_source_locations(line):
    result = dxa_sarif.to_sarif(r1_report(r1_finding(
        source={}, sink={"file": "src/app.js", "line": line}
    )))["runs"][0]["results"][0]
    assert "locations" not in result


def test_relative_path_uri_encodes_spaces_and_unicode():
    document = dxa_sarif.to_sarif(r1_report(r1_finding(
        source={}, sink={"file": "src/my café.js", "line": 12}
    )))
    validate_sarif_21(document)
    location = document["runs"][0]["results"][0]["locations"][0]
    assert location["physicalLocation"]["artifactLocation"]["uri"] == "src/my%20caf%C3%A9.js"


def test_source_only_location_is_preserved_without_duplicate_related_location():
    document = dxa_sarif.to_sarif(r1_report(r1_finding(
        source={"file": "src/source.py", "line": 7}, sink={}
    )))
    validate_sarif_21(document)
    result = document["runs"][0]["results"][0]
    assert result["locations"][0]["physicalLocation"]["region"]["startLine"] == 7
    assert "relatedLocations" not in result


def test_privacy_allowlist_omits_arbitrary_metadata_and_identifier_text():
    report = r1_report(r1_finding(
        finding_id="FINDING_SECRET", attempt_id="ATTEMPT_SECRET", canary_id="CANARY_SECRET",
        session_role="ROLE_SECRET", context="CONTEXT_SECRET", content_type="TYPE_SECRET",
        evidence_links=["javascript:LINK_SECRET", "http://u:PASS_SECRET@host/?key=QUERY_SECRET"],
        source={"file": "../PRIVATE_SECRET", "line": 1},
        payload="PAYLOAD_SECRET", snippet="SNIPPET_SECRET"))
    report["meta"] = {"anything": "META_SECRET"}
    serialized = json.dumps(dxa_sarif.to_sarif(report))
    assert "SECRET" not in serialized


def test_sarif_envelope_schema_and_same_report_correlation_without_stable_fingerprints():
    report = r1_report(r1_finding())
    first = dxa_sarif.to_sarif(report)
    second = dxa_sarif.to_sarif(report)

    validate_sarif_21(first)
    result = first["runs"][0]["results"][0]
    second_result = second["runs"][0]["results"][0]
    assert "finding_id" not in result["properties"]
    assert "finding-stable-1" not in json.dumps(first)
    assert "partialFingerprints" not in result
    assert "fingerprints" not in result
    digest = hashlib.sha256(b"finding-stable-1").hexdigest()
    assert result["properties"]["finding_id_sha256"] == digest
    assert second_result == result


def test_empty_report_and_operational_events_keep_distinct_meaning():
    report = r1_report(events=[
        r1_event("skip", reason="SECRET_REASON", url="http://u:p@host/?token=SECRET"),
        r1_event("error", reason="SECRET_ERROR", url="http://host/?key=SECRET"),
    ])
    document = dxa_sarif.to_sarif(report)

    validate_sarif_21(document)
    run = document["runs"][0]
    assert run["results"] == []
    notifications = run["invocations"][0]["toolExecutionNotifications"]
    assert [item["level"] for item in notifications] == ["warning", "error"]
    assert all("SECRET" not in item["message"]["text"] for item in notifications)
    assert run["invocations"][0]["executionSuccessful"] is False


def test_export_omits_raw_observations_credentials_and_untrusted_urls():
    finding = r1_finding(
        observations=[{
            "body_preview": "BODY_SECRET",
            "raw_dom": "DOM_SECRET",
            "callback_body": "CALLBACK_SECRET",
            "headers": {"Authorization": "Bearer HEADER_SECRET"},
            "url": "http://user:PASS_SECRET@host/path?token=QUERY_SECRET#FRAGMENT_SECRET",
        }],
        source={"url": "http://user:PASS_SECRET@host/submit?token=QUERY_SECRET#FRAGMENT_SECRET"},
        sink={"url": "http://host/read?sid=QUERY_SECRET"},
    )
    event = r1_event("skip", reason="REASON_SECRET",
        url="http://user:PASS_SECRET@host/?token=QUERY_SECRET#FRAGMENT_SECRET")
    serialized = json.dumps(dxa_sarif.to_sarif(r1_report(finding, events=[event])))

    for secret in (
        "BODY_SECRET", "DOM_SECRET", "CALLBACK_SECRET", "HEADER_SECRET",
        "PASS_SECRET", "QUERY_SECRET", "FRAGMENT_SECRET", "REASON_SECRET",
    ):
        assert secret not in serialized


def test_only_safe_relative_file_locations_are_emitted():
    supported = r1_finding(
        source={"file": "src/client/app.js", "line": 7},
        sink={"file": "src/client/app.js", "line": 12, "identity": "innerHTML"},
    )
    unsupported = r1_finding(
        finding_id="finding-unsafe-path",
        source={"file": "../private/token.js", "line": 1},
        sink={"file": "C:\\Users\\private\\secret.js", "line": 3},
    )
    http_only = r1_finding(
        finding_id="finding-http-only",
        source={"url": "http://127.0.0.1/?token=SECRET"},
        sink={"url": "http://127.0.0.1/read"},
    )
    results = dxa_sarif.to_sarif(
        r1_report(supported, unsupported, http_only)
    )["runs"][0]["results"]

    assert [loc["physicalLocation"]["region"]["startLine"]
            for loc in results[0]["locations"]] == [12]
    assert [loc["physicalLocation"]["region"]["startLine"]
            for loc in results[0]["relatedLocations"]] == [7]
    assert "locations" not in results[1]
    assert "locations" not in results[2]


@pytest.mark.parametrize("bad_report", [None, {}, {"findings": ["not-an-object"]}])
def test_export_rejects_malformed_report_containers(bad_report):
    with pytest.raises((TypeError, ValueError)):
        dxa_sarif.to_sarif(bad_report)


@pytest.mark.parametrize("mode", ["static", "dynamic", "static-guided"])
def test_each_r1_cli_writes_sarif_without_network_access(mode, monkeypatch, tmp_path):
    output = tmp_path / f"{mode}.sarif"
    if mode == "static":
        dxa.REPORT_EVENTS.clear()
        monkeypatch.setattr(dxa, "iter_files", lambda _target: [])
        monkeypatch.setattr(sys, "argv", ["dxa.py", str(tmp_path), "--sarif-out", str(output)])
        main = dxa.main
    elif mode == "dynamic":
        monkeypatch.setattr(dxadyn, "crawl", lambda *_args, **_kwargs: [])
        monkeypatch.setattr(sys, "argv", [
            "dxadyn.py", "http://127.0.0.1/", "--sarif-out", str(output),
        ])
        main = dxadyn.main
    else:
        monkeypatch.setattr(dxa2dyn, "run_dxa", lambda _path: [])
        monkeypatch.setattr(dxadyn, "crawl", lambda *_args, **_kwargs: [])
        monkeypatch.setattr(dxa2dyn, "probe_hints", lambda *_args: [])
        monkeypatch.setattr(sys, "argv", [
            "dxa2dyn.py", str(tmp_path), "http://127.0.0.1/",
            "--sarif-out", str(output),
        ])
        main = dxa2dyn.main

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    validate_sarif_21(json.loads(output.read_text(encoding="utf-8")))


@pytest.mark.parametrize("flow_mode", ["--flow", "--auth-flow"])
def test_dynamic_cli_error_path_emits_sarif_notification(flow_mode, monkeypatch, tmp_path):
    output = tmp_path / "error.sarif"
    monkeypatch.setattr(sys, "argv", [
        "dxadyn.py", flow_mode, str(tmp_path / "missing-flow.json"),
        "--sarif-out", str(output),
    ])

    with pytest.raises(SystemExit) as exc:
        dxadyn.main()

    assert exc.value.code == 2
    document = json.loads(output.read_text(encoding="utf-8"))
    validate_sarif_21(document)
    run = document["runs"][0]
    assert run["results"] == []
    notifications = run["invocations"][0]["toolExecutionNotifications"]
    assert len(notifications) == 1
    assert notifications[0]["level"] == "error"
    assert "missing-flow.json" not in notifications[0]["message"]["text"]


@pytest.mark.parametrize("mode", ["static", "dynamic", "static-guided"])
def test_each_r1_cli_rejects_sarif_path_collision_before_scanning(mode, monkeypatch, tmp_path):
    output = tmp_path / "same.out"
    if mode == "static":
        monkeypatch.setattr(sys, "argv", [
            "dxa.py", str(tmp_path), "--json-out", str(output), "--sarif-out", str(output),
        ])
        main = dxa.main
    elif mode == "dynamic":
        monkeypatch.setattr(sys, "argv", [
            "dxadyn.py", "http://127.0.0.1/", "--json-out", str(output),
            "--sarif-out", str(output),
        ])
        main = dxadyn.main
    else:
        monkeypatch.setattr(sys, "argv", [
            "dxa2dyn.py", str(tmp_path), "http://127.0.0.1/",
            "--json-out", str(output), "--sarif-out", str(output),
        ])
        main = dxa2dyn.main

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 2


def run_converter(input_path, output_path):
    return subprocess.run([
        sys.executable, str(Path(__file__).with_name("dxa_sarif_cli.py")),
        str(input_path), "--output", str(output_path),
    ], capture_output=True, text=True, timeout=30)


def test_offline_converter_subprocess_writes_schema_valid_report(tmp_path):
    input_path = tmp_path / "evidence.json"
    output_path = tmp_path / "evidence.sarif"
    report = r1_report(r1_finding("resource-callback"), events=[r1_event("skip")])
    input_path.write_text(json.dumps(report), encoding="utf-8")
    result = run_converter(input_path, output_path)
    assert result.returncode == 0, result.stderr
    converted = json.loads(output_path.read_text(encoding="utf-8"))
    validate_sarif_21(converted)
    assert converted["runs"][0]["invocations"][0]["executionSuccessful"] is False
    assert json.loads(input_path.read_text(encoding="utf-8")) == report


@pytest.mark.parametrize("contents", ["{broken", "[]", '{"schema_version":2}',
    '{"schema_version":1,"mode":"test","findings":[],"events":[],"extra":NaN}',
    '{"schema":"dxa-browser-proof/1","status":"execution-observed"}'])
def test_offline_converter_subprocess_rejects_bad_input_without_success_report(tmp_path, contents):
    input_path = tmp_path / "bad.json"
    output_path = tmp_path / "bad.sarif"
    input_path.write_text(contents, encoding="utf-8")
    result = run_converter(input_path, output_path)
    assert result.returncode == 2
    assert not output_path.exists()


def test_offline_converter_rejects_same_input_output_and_preserves_source(tmp_path):
    path = tmp_path / "source.json"
    contents = json.dumps(r1_report(r1_finding()))
    path.write_text(contents, encoding="utf-8")
    result = run_converter(path, path)
    assert result.returncode == 2
    assert path.read_text(encoding="utf-8") == contents


def test_invalid_conversion_preserves_existing_output(tmp_path):
    source = tmp_path / "source.json"
    output = tmp_path / "existing.sarif"
    source.write_text("{broken", encoding="utf-8")
    output.write_text("previous evidence", encoding="utf-8")
    result = run_converter(source, output)
    assert result.returncode == 2
    assert output.read_text(encoding="utf-8") == "previous evidence"


def test_converter_missing_input_and_unwritable_destination_return_error(tmp_path):
    source = tmp_path / "missing.json"
    destination = tmp_path / "output.sarif"
    missing = run_converter(source, destination)
    assert missing.returncode == 2
    assert not destination.exists()
    source.write_text(json.dumps(r1_report()), encoding="utf-8")
    unwritable = run_converter(source, tmp_path / "absent-parent" / "output.sarif")
    assert unwritable.returncode == 2
    assert not (tmp_path / "absent-parent").exists()


def test_vendored_schema_matches_recorded_oasis_download_digest():
    assert hashlib.sha256(SARIF_SCHEMA_PATH.read_bytes()).hexdigest() == (
        "ad6db49878699b091f3eeb765b6e29e92a34bad4da88664d000c923b549c3a25"
    )
