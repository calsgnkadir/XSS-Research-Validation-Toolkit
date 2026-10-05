"""R1 contract v1: observations, findings and operational events (stdlib only).

Evidence levels are categories, not an ordered severity ladder. This module
does not verify execution or authentication; current producers cannot mint
execution-confirmed records. Future proof support requires a schema revision.
"""
from copy import deepcopy
from dataclasses import asdict, dataclass, field
import hashlib
import html
import json
import math
import secrets
import time
import urllib.parse

LEVELS = {"candidate", "reflection", "sink-observed", "resource-callback"}
PRIVATE_KEYS = {"headers", "cookies", "cookie", "authorization", "auth_headers",
                "password", "token", "vars", "body_preview"}


def safe_url(value):
    p = urllib.parse.urlsplit(value or "")
    if p.scheme not in ("http", "https"):
        return value or ""
    query = urllib.parse.urlencode([(k, "[redacted]") for k, _ in
                                   urllib.parse.parse_qsl(p.query, keep_blank_values=True)])
    return urllib.parse.urlunsplit((p.scheme, p.netloc.rsplit("@", 1)[-1], p.path, query, ""))


def clean(value, key=""):
    if key.lower() in PRIVATE_KEYS:
        return "[redacted]"
    if isinstance(value, dict):
        return {k: clean(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, str) and ("url" in key or key in ("target", "hit_from_referer")):
        return safe_url(value)
    return value


@dataclass
class Finding:
    finding_id: str
    attempt_id: str | None
    canary_id: str | None
    source: dict
    sink: dict
    context: str
    content_type: str
    session_role: str
    evidence_level: str
    triage: str = "unreviewed"
    role_verified: bool = False
    evidence_links: list = field(default_factory=list)
    observations: list = field(default_factory=list)
    schema_version: int = 1

    def __post_init__(self):
        if not isinstance(self.finding_id, str) or not self.finding_id:
            raise ValueError("finding_id is required")
        if self.evidence_level not in LEVELS:
            raise ValueError("unsupported evidence level; execution proof is not implemented")
        if self.triage not in {"unreviewed", "candidate", "by-design", "self-xss", "rejected"}:
            raise ValueError("unsupported triage; vulnerability confirmation requires independent review")
        if self.role_verified is not False:
            raise ValueError("verified role is not implemented")
        if not isinstance(self.source, dict) or not isinstance(self.sink, dict):
            raise ValueError("source and sink must be objects")
        for key in ("attempt_id", "canary_id"):
            value = getattr(self, key)
            if value is not None and not isinstance(value, str):
                raise ValueError(key + " must be a string or null")
        for key in ("context", "content_type", "session_role"):
            if not isinstance(getattr(self, key), str):
                raise ValueError(key + " must be a string")
        if self.schema_version != 1:
            raise ValueError("unsupported schema version")
        for key in ("evidence_links", "observations"):
            if not isinstance(getattr(self, key), list):
                raise ValueError(key + " must be a list")
        if any(not isinstance(link, str) for link in self.evidence_links):
            raise ValueError("evidence links must be strings")
        if any(not isinstance(item, dict) for item in self.observations):
            raise ValueError("observations must be objects")


@dataclass
class ReportEvent:
    stage: str
    kind: str
    reason: str
    url: str = ""
    status: int | None = None
    canary_id: str | None = None
    event_id: str = field(default_factory=lambda: secrets.token_hex(16))
    observed_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if self.kind not in {"error", "skip", "info"}:
            raise ValueError("invalid event kind")
        if not self.stage or not self.reason:
            raise ValueError("event stage and reason required")
        if self.status is not None and type(self.status) is not int:
            raise ValueError("event status must be an integer or null")
        if not math.isfinite(self.observed_at):
            raise ValueError("event timestamp must be finite")


def normalize(row):
    """Adapt legacy HTTP, stored attempts and DOM observations without promotion."""
    raw = deepcopy(row)
    identity = row.get("finding_id") or row.get("attempt_id")
    if not identity:
        identity = hashlib.sha256(json.dumps(raw, sort_keys=True, default=str).encode()).hexdigest()[:32]
    cid = row.get("canary_id")
    level = row.get("evidence_level") or (
        "reflection" if row.get("reflection") in {"unencoded", "attr-only"} else "candidate")
    source = row.get("source") or {"url": row.get("target") or row.get("url", ""),
                                    "method": row.get("submission_method") or row.get("method", ""),
                                    "parameter": row.get("field") or row.get("param", "")}
    sink = row.get("sink") or {"url": row.get("check_url") or row.get("url", ""),
                                "identity": row.get("sink_identity", "unknown")}
    observations = row.get("observations") or [{k: v for k, v in raw.items()
                                                if k not in ("duplicates", "observations")}]
    model = Finding(str(identity), row.get("attempt_id") or cid, cid, source, sink,
                    row.get("context", "unknown"), row.get("content_type", ""),
                    row.get("session_role", "unspecified"), level,
                    triage=row.get("triage", "unreviewed"),
                    role_verified=row.get("role_verified", False),
                    evidence_links=row.get("evidence_links", []), observations=observations)
    raw.update(asdict(model))
    return clean(raw)


def deduplicate(rows):
    """Conservative grouping; no cross-attempt, cross-role or cross-sink inference.

    Unknown identity is kept separate. Preserve original observations in memory;
    exports redact known credential fields and URL values without mutating input.
    """
    groups, output = {}, []
    for row in rows:
        cid = row.get("attempt_id") or row.get("canary_id")
        source = row.get("source") or {"url": row.get("target") or row.get("url"),
                                       "method": row.get("submission_method") or row.get("method"),
                                       "parameter": row.get("field") or row.get("param")}
        sink = row.get("sink") or {"url": row.get("check_url") or row.get("url"),
                                   "identity": row.get("sink_identity", "unknown")}
        key = None
        if (cid and source.get("url") and source.get("parameter") and sink.get("url")
                and sink.get("identity") not in (None, "", "unknown")
                and row.get("session_role") not in (None, "", "unknown", "unspecified")):
            key = json.dumps([cid, source, sink, row.get("context"), row.get("session_role", "unspecified"),
                              row.get("variant"), row.get("reflection"), row.get("content_type"),
                              row.get("evidence_level"), row.get("triage", "unreviewed")], sort_keys=True)
        if key is not None and key in groups:
            primary = groups[key]
            primary.setdefault("duplicates", []).append(deepcopy(row))
            primary["observations"].extend(deepcopy(row.get("observations") or [row]))
        else:
            primary = deepcopy(row)
            primary["observations"] = deepcopy(row.get("observations") or [row])
            output.append(primary)
            if key is not None:
                groups[key] = primary
    return output


def report(rows, mode, events=(), meta=None):
    findings = [normalize(row) for row in rows]
    event_rows = []
    for event in events:
        event_rows.append(clean(asdict(event) if isinstance(event, ReportEvent) else asdict(ReportEvent(**event))))
    return {"schema_version": 1, "mode": mode, "findings": findings, "events": event_rows,
            "meta": clean(meta or {}), "skipped_submits": sum(e["kind"] == "skip" for e in event_rows)}


def render_events(events):
    esc = lambda value: html.escape(str(value))
    rows = "".join("<tr>" + "".join("<td>" + esc(e.get(k, "")) + "</td>" for k in
                                  ("event_id", "stage", "kind", "reason", "url", "status")) + "</tr>"
                   for e in events)
    return ("<h2>Operational events</h2><p>No observations does not mean safe.</p>"
            "<table><tr><th>event_id</th><th>stage</th><th>kind</th><th>reason</th><th>url</th><th>status</th></tr>"
            + rows + "</table>")


def render_report(document):
    """Common standalone renderer for journal adapters; values are always escaped."""
    columns = ("finding_id", "attempt_id", "canary_id", "session_role", "evidence_level", "triage")
    rows = "".join("<tr>" + "".join("<td>" + html.escape(str(row.get(k, ""))) + "</td>"
                                  for k in columns) + "</tr>" for row in document["findings"])
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><title>Evidence report</title>"
            "<h1>Evidence report</h1><p>Resource callbacks do not establish JavaScript execution. "
            "Roles are operator labels, not verified identity. No-hit does not mean safe.</p>"
            "<table border='1'><tr>" + "".join("<th>" + k + "</th>" for k in columns)
            + "</tr>" + rows + "</table>" + render_events(document["events"])
            + "<details><summary>Observation records</summary><pre>"
            + html.escape(json.dumps(document["findings"], ensure_ascii=False, indent=2))
            + "</pre></details></html>")


def dom_observations(summary, role="unspecified"):
    rows = []
    for kind, values in (("sink", summary.get("sinks", [])), ("dialog", summary.get("dialogs", []))):
        for index, value in enumerate(values):
            # Browser arguments can contain tokens; preserve a fingerprint, not credentials.
            digest = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
            rows.append({"finding_id": secrets.token_hex(16), "url": summary["url"],
                         "method": "GET", "param": "bare-visit", "context": "dom",
                         "sink_identity": f"{kind}:{value.get('sink', value.get('type', 'unknown'))}:{index}",
                         "session_role": role, "evidence_level": "sink-observed" if kind == "sink" else "candidate",
                         "severity": "sink-observed" if kind == "sink" else "observed-dialog",
                         "observations": [{"kind": kind, "sha256": digest,
                                           "content": "omitted: may contain credentials"}]})
    events = [ReportEvent("browser", "error", "browser reported an error; raw message omitted", summary["url"])
              for _ in summary.get("errors", [])]
    return rows, events


def static_observations(rows):
    result = []
    for row in rows:
        data = {k: v for k, v in row.items() if k != "code"}
        data.update(source={"file": row["file"], "line": row["line"]},
                    sink={"file": row["file"], "line": row["line"], "identity": row["sink"]},
                    context="source-code", evidence_level="candidate", triage="unreviewed",
                    observations=[{"code_sha256": hashlib.sha256(row.get("code", "").encode()).hexdigest(),
                                   "content": "source snippet omitted: may contain credentials"}])
        result.append(data)
    return result
