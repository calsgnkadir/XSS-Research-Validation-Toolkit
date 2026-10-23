"""Conservative SARIF 2.1.0 export for validated R1 evidence reports.

R1 evidence categories are not severity levels. The exporter therefore marks
each observation as requiring review and uses SARIF level ``none``; callers
must not interpret these records as confirmed vulnerabilities.
"""

from collections.abc import Mapping
import hashlib
import math
from pathlib import PurePosixPath, PureWindowsPath
import re
from urllib.parse import quote, urlsplit

from dxa_evidence import Finding


SARIF_SCHEMA = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/"
    "os/schemas/sarif-schema-2.1.0.json"
)
SARIF_VERSION = "2.1.0"
RULE_ID = "dxa.observation"
EVIDENCE_LEVELS = {"candidate", "reflection", "sink-observed", "resource-callback"}
TRIAGE_VALUES = {"unreviewed", "candidate", "by-design", "self-xss", "rejected"}

_EVENT_MESSAGES = {
    "error": ("error", "The analysis recorded an operational error."),
    "skip": ("warning", "The analysis skipped an operation; coverage may be incomplete."),
    "info": ("note", "The analysis recorded an informational event."),
}


def _safe_relative_uri(value):
    """Return a relative file URI only for non-absolute, traversal-free paths."""
    if not isinstance(value, str) or not value or "\x00" in value:
        return None
    normalized = value.replace("\\", "/")
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if (normalized.startswith("/") or PureWindowsPath(value).is_absolute()
            or parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
            or normalized.lower().startswith("www.")):
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", normalized):
        return None
    if any(part in (".", "..") for part in normalized.split("/")):
        return None
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        return None
    return quote("/".join(parts), safe="/-._~")


def _file_location(descriptor):
    """Expose a file location only when its relative URI and line are safe."""
    if not isinstance(descriptor, Mapping):
        return None
    uri = _safe_relative_uri(descriptor.get("file"))
    line = descriptor.get("line")
    if uri is None or type(line) is not int or line < 1:
        return None
    return {
        "physicalLocation": {
            "artifactLocation": {"uri": uri},
            "region": {"startLine": line},
        }
    }


def _result(finding):
    evidence_level = finding.get("evidence_level")
    triage = finding.get("triage", "unreviewed")
    if evidence_level not in EVIDENCE_LEVELS:
        raise ValueError("finding has an unsupported R1 evidence_level")
    if triage not in TRIAGE_VALUES:
        raise ValueError("finding has an unsupported R1 triage value")

    result = {
        "ruleId": RULE_ID,
        "kind": "review",
        "level": "none",
        "message": {
            "text": "Analyzer observation; review the evidence and triage before treating it as a vulnerability."
        },
        "properties": {
            "evidence_level": evidence_level,
            "triage": triage,
        },
    }
    finding_id = finding.get("finding_id")
    if isinstance(finding_id, str) and finding_id:
        # IDs can be caller-controlled text. Export only a correlation hash,
        # never a SARIF fingerprint (R1 IDs have no cross-run identity).
        result["properties"]["finding_id_sha256"] = hashlib.sha256(
            finding_id.encode("utf-8", errors="surrogatepass")
        ).hexdigest()

    sink_location = _file_location(finding.get("sink"))
    source_location = _file_location(finding.get("source"))
    if sink_location is not None:
        result["locations"] = [sink_location]
    elif source_location is not None:
        result["locations"] = [source_location]
    if (source_location is not None
            and sink_location is not None
            and source_location != sink_location):
        result["relatedLocations"] = [{
            "id": 0,
            "message": {"text": "Source location"},
            **source_location,
        }]
    return result


def _notifications(events):
    notifications = []
    for event in events:
        message = _EVENT_MESSAGES[event["kind"]]
        level, text = message
        # Free-form reasons and URLs can contain credentials or personal data.
        notifications.append({"level": level, "message": {"text": text}})
    return notifications


def _validate_report(document):
    """Validate saved R1 records without synthesizing defaults for events."""
    if not isinstance(document, Mapping):
        raise TypeError("R1 report must be a mapping")
    if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise ValueError("R1 report requires integer schema_version 1")
    if not isinstance(document.get("mode"), str) or not document["mode"].strip():
        raise ValueError("R1 report requires a nonempty mode")
    findings = document.get("findings")
    events = document.get("events")
    if not isinstance(findings, list) or not isinstance(events, list):
        raise ValueError("R1 report findings and events must be lists")
    if "meta" in document and not isinstance(document["meta"], dict):
        raise ValueError("R1 report meta must be an object")
    for finding in findings:
        if not isinstance(finding, Mapping):
            raise ValueError("R1 report findings must contain objects")
        if "schema_version" in finding and (
            type(finding["schema_version"]) is not int or finding["schema_version"] != 1
        ):
            raise ValueError("finding requires integer schema_version 1")
        # Extra legacy adapter fields may exist, but are never exported.
        try:
            Finding(**{key: finding[key] for key in Finding.__dataclass_fields__ if key in finding})
        except (TypeError, ValueError):
            raise ValueError("finding does not satisfy the R1 contract") from None
    for event in events:
        if not isinstance(event, Mapping):
            raise ValueError("R1 report events must contain objects")
        for key in ("event_id", "stage", "reason"):
            if not isinstance(event.get(key), str) or not event[key].strip():
                raise ValueError("R1 event requires nonempty identity, stage and reason")
        if not isinstance(event.get("kind"), str) or event["kind"] not in _EVENT_MESSAGES:
            raise ValueError("R1 event kind must be error, skip or info")
        timestamp = event.get("observed_at")
        try:
            finite_timestamp = type(timestamp) in (int, float) and math.isfinite(timestamp)
        except OverflowError:
            finite_timestamp = False
        if not finite_timestamp:
            raise ValueError("R1 event timestamp must be finite")
        if "url" in event and not isinstance(event["url"], str):
            raise ValueError("R1 event URL must be a string")
        if event.get("status") is not None and type(event["status"]) is not int:
            raise ValueError("R1 event status must be an integer or null")
        if event.get("canary_id") is not None and not isinstance(event["canary_id"], str):
            raise ValueError("R1 event canary_id must be a string or null")
    if "skipped_submits" in document:
        count = document["skipped_submits"]
        if type(count) is not int or count != sum(event["kind"] == "skip" for event in events):
            raise ValueError("R1 skipped_submits must agree with the skip events")


def to_sarif(document):
    """Convert a validated R1 report mapping to a JSON-serializable SARIF log.

    Only R1 evidence/triage labels, a SHA-256 finding-id correlation hash, and safe
    relative source-code locations are exported. Raw observations,
    request/response content, headers, credentials, and URLs are omitted.
    """
    _validate_report(document)
    findings = document["findings"]

    run = {
        "tool": {
            "driver": {
                "name": "XSS Research Validation Toolkit",
                "version": "0.1.0",
                "rules": [{
                    "id": RULE_ID,
                    "name": "Analyzer observation",
                    "shortDescription": {
                        "text": "An analyzer observation that has not been confirmed as a vulnerability."
                    },
                    "help": {
                        "text": "R1 evidence levels describe observation types, not severity or proof of execution."
                    },
                }],
            }
        },
        "properties": {
            "dxa": {
                "r1_schema_version": document.get("schema_version", 1),
                "finding_count": len(findings),
            }
        },
        "results": [_result(finding) for finding in findings],
    }
    events = document["events"]
    notifications = _notifications(events)
    if notifications:
        incomplete = any(event["kind"] in ("error", "skip") for event in events)
        run["invocations"] = [{
            "executionSuccessful": not incomplete,
            "toolExecutionNotifications": notifications,
        }]
    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [run],
    }
