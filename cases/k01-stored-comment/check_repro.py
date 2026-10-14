"""Run and independently check the disposable K01 browser reproduction."""

import argparse
from contextlib import contextmanager
import difflib
import hashlib
import html
import importlib.metadata
import json
from pathlib import Path
import platform
import socket
import sys
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import prove

NAMES = ("vulnerable", "javascript-disabled", "fixed", "json-only", "normal-dialog")
SOURCE_NAMES = ("prove.py", "render_fixed.py", "render_vulnerable.py")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(output, ports, expected_platform="Linux", expected_python="3.12."):
    """Check proof semantics, artifact integrity and fixture shutdown."""
    output = Path(output)
    members = {p.name for p in output.iterdir() if p.is_file()}
    expected_members = {"result.json", "fix.diff"} | {
        name + suffix for name in NAMES for suffix in ("-request.json", "-response.txt")
    }
    require(members == expected_members, "missing or unexpected proof members")
    report = json.loads((output / "result.json").read_text(encoding="utf-8"))
    require(report.get("case_version") == "k01-v1.0", "wrong case version")
    require(report.get("platform") == expected_platform, "wrong platform")
    require(report.get("python", "").startswith(expected_python), "wrong Python version")
    require(report.get("playwright") == "1.63.0", "wrong Playwright version")
    require(importlib.metadata.version("playwright") == "1.63.0", "installed Playwright differs")
    require(report.get("passed") is True, "proof did not complete")
    require(isinstance(report.get("browser_version"), str) and report["browser_version"],
            "missing browser version")
    sources = {name: sha256(ROOT / name) for name in SOURCE_NAMES}
    require(report.get("source_sha256") == sources, "source hashes differ")
    vulnerable = (ROOT / "render_vulnerable.py").read_text(encoding="utf-8").splitlines(True)
    fixed = (ROOT / "render_fixed.py").read_text(encoding="utf-8").splitlines(True)
    expected_diff = "".join(difflib.unified_diff(vulnerable, fixed,
                            fromfile="render_vulnerable.py", tofile="render_fixed.py"))
    require((output / "fix.diff").read_text(encoding="utf-8") == expected_diff,
            "fix diff differs from source")
    cid = report.get("cid")
    require(isinstance(cid, str) and len(cid) == 27 and cid.startswith("k01"), "invalid CID")
    payload = report.get("payload")
    require(isinstance(payload, str) and payload.startswith(cid) and
            "window.__k01='" + cid + "'" in payload, "invalid payload")
    cases = report.get("cases")
    require(isinstance(cases, list) and [row.get("name") for row in cases] == list(NAMES),
            "missing, duplicate or reordered controls")
    require(len(ports) == 5 and len(set(ports)) == 5, "fixture ports not recorded")
    expected_execution = (True, False, False, False, False)
    for index, (name, row) in enumerate(zip(NAMES, cases)):
        request = json.loads((output / (name + "-request.json")).read_text(encoding="utf-8"))
        body = (output / (name + "-response.txt")).read_text(encoding="utf-8")
        read_path = "/json" if name == "json-only" else "/notice" if name == "normal-dialog" else "/comments"
        require(request.get("method") == "POST" and request.get("path") == "/comments" and
                request.get("status") == 201 and request.get("read_path") == read_path and
                request.get("content_type") == "application/x-www-form-urlencoded", "request identity differs")
        require(parse_qs(request.get("body", "")) == {"comment": [payload]}, "submitted payload differs")
        expected_content_type = "application/json" if name == "json-only" else "text/html; charset=utf-8"
        require(request.get("response_content_type") == expected_content_type,
                "response content type differs")
        if name == "json-only":
            require(json.loads(body) == {"comment": payload}, "JSON response differs")
        elif name == "normal-dialog":
            require(body == '<!doctype html><script>alert("ordinary application dialog")</script>',
                    "ordinary dialog response differs")
        else:
            expected_value = html.escape(payload, quote=True) if name == "fixed" else payload
            require(body == '<!doctype html><meta charset="utf-8"><h1>Comments</h1>'
                    '<article id="comment">' + expected_value + '</article>', "HTML response differs")
        require(row.get("expected_execution") is expected_execution[index] and
                row.get("observed_canary") == (cid if expected_execution[index] else None) and
                row.get("passed") is True and row.get("posts") == 1 and
                row.get("javascript") is (name != "javascript-disabled"),
                "browser control result differs")
        require(row.get("dialogs") == (["ordinary application dialog"] if name == "normal-dialog" else []),
                "dialog control differs")
        finding = row.get("bot_finding")
        expected_http = {
            "vulnerable": ("html-reflection", "reflection", "unencoded"),
            "javascript-disabled": ("html-reflection", "reflection", "unencoded"),
            "fixed": ("-", "candidate", "encoded"),
            "json-only": ("json-only", "reflection", "unencoded"),
            "normal-dialog": ("-", "candidate", "absent"),
        }
        require(isinstance(finding, dict) and finding.get("canary_id") == cid and
                finding.get("method") == "GET" and finding.get("param") == "comment" and
                (finding.get("severity"), finding.get("evidence_level"),
                 finding.get("reflection")) == expected_http[name],
                "HTTP candidate classification differs")
        url = urlsplit(finding.get("url", ""))
        require(url.hostname == "127.0.0.1" and url.port == ports[index] and url.path == read_path,
                "finding origin differs from fixture")
    closed = []
    for port in ports:
        with socket.socket() as client:
            client.settimeout(1)
            closed.append(client.connect_ex(("127.0.0.1", port)) != 0)
    require(all(closed), "fixture port remained open")
    return {
        "case_version": "k01-v1.0",
        "environment": {key: report[key] for key in ("python", "platform", "playwright", "browser_version")},
        "result": {"passed": 5, "total": 5, "fixture_ports_closed": sum(closed),
                   "distinct_fixture_ports": len(set(ports))},
        "source_sha256": sources,
        "proof_sha256": {name: sha256(output / name) for name in sorted(expected_members)},
        "scope": "fresh 127.0.0.1 fixture; anonymous author and separate reader context",
        "limitation": "Hosted Linux repetition is not an independent second person or product/CVE claim",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="new proof directory; must not exist")
    args = parser.parse_args()
    output = Path(args.output)
    ports = []
    original_fixture = prove.fixture

    @contextmanager
    def observed_fixture(renderer):
        with original_fixture(renderer) as (origin, handler):
            require(urlsplit(origin).hostname == "127.0.0.1", "fixture is not loopback")
            ports.append(urlsplit(origin).port)
            yield origin, handler

    prove.fixture = observed_fixture
    try:
        prove.run(output)
        record = validate(output, ports)
        (output / "acceptance.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print("K01 Linux: 5/5 controls; 5/5 loopback fixtures closed; artifact gate passed")
    finally:
        prove.fixture = original_fixture


if __name__ == "__main__":
    main()
