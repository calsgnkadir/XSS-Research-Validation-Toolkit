"""R4 local auth/CSRF failure controls, excluded from XSS accuracy.

The fixture is disposable memory-only loopback. A matching expected failure is
control acceptance, never a completed negative XSS observation.
"""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sys
import threading
import urllib.parse

CASES = {
    "login-rejected": ("http-auth", 0, 0),
    "http-identity-mismatch": ("http-auth", 0, 0),
    "browser-role-mismatch": ("browser-auth", 0, 0),
    "csrf-missing": ("submit", 0, 0),
    "csrf-rejected": ("submit", 1, 0),
    "session-expired-after-submit": ("browser-auth-after-submit", 1, 1),
}


@contextmanager
def failure_lab(case):
    """Yield proof spec and aggregate counters; credentials stay in memory."""
    if case not in CASES:
        raise ValueError("unknown auth failure case")
    cookie = secrets.token_hex(20)
    token = secrets.token_hex(20)
    state = {"login_requests": 0, "checks": 0, "submit_requests": 0,
             "posts": 0, "reads": 0, "csrf_fetches": 0}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, body, content_type="text/html", set_cookie=False):
            raw = body.encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            if set_cookie:
                self.send_header("Set-Cookie", "session=" + cookie + "; Path=/; HttpOnly")
            self.end_headers()
            self.wfile.write(raw)

        def authed(self):
            return self.headers.get("Cookie") == "session=" + cookie

        def do_POST(self):
            size = int(self.headers.get("Content-Length", 0))
            if not 0 <= size <= 16384:
                return self.send(413, "too large")
            fields = urllib.parse.parse_qs(self.rfile.read(size).decode())
            if self.path == "/login":
                state["login_requests"] += 1
                if case == "login-rejected" or fields.get("user") != ["alice"]:
                    return self.send(401, "denied")
                return self.send(200, "ok", set_cookie=True)
            if self.path != "/comments" or not self.authed():
                return self.send(403, "denied")
            state["submit_requests"] += 1
            if case.startswith("csrf-"):
                # Rejected case intentionally rejects the freshly issued token.
                return self.send(403, "csrf rejected")
            state["posts"] += 1
            return self.send(201, "stored")

        def do_GET(self):
            if not self.authed():
                return self.send(401, "denied")
            if self.path == "/me":
                state["checks"] += 1
                if case == "session-expired-after-submit" and state["posts"]:
                    return self.send(401, "expired")
                user = "other" if case == "http-identity-mismatch" else "alice"
                role = "wrong" if case == "browser-role-mismatch" and state["checks"] >= 2 else "reader"
                return self.send(200, json.dumps({"user": user, "role": role}), "application/json")
            if self.path == "/comments":
                state["csrf_fetches"] += 1
                body = "missing" if case == "csrf-missing" else '<input name="csrf" value="' + token + '">'
                return self.send(200, body)
            if self.path == "/view":
                state["reads"] += 1
                return self.send(200, "read must not be reached in these controls")
            return self.send(404, "missing")

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:" + str(server.server_port)
    spec = {
        "origin": base, "role_path": "$.role", "observe_ms": 100,
        "auth_flow": {"steps": [{"url": base + "/login", "method": "POST", "body": {"user": "alice"}}]},
        "session_check": {"url": base + "/me", "expect": {"$.user": "alice", "$.role": "reader"}},
        "submit": {"url": base + "/comments", "field": "comment",
                   "csrf_field": "csrf" if case.startswith("csrf-") else ""},
        "read_url": base + "/view",
    }
    try:
        yield spec, state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        if thread.is_alive():
            raise RuntimeError("auth failure fixture did not stop")


def accept_failure(case, proof, counters):
    """Validate expected failure separately from scanner accuracy."""
    stage, requests, posts = CASES[case]
    if not isinstance(proof, dict) or not isinstance(counters, dict):
        return False
    events = proof.get("events", [])
    if not isinstance(events, list):
        return False
    errors = [event for event in events if isinstance(event, dict) and event.get("kind") == "error"]
    return (
        proof.get("schema") == "dxa-browser-proof/1"
        and proof.get("status") == "error"
        and proof.get("execution_observed") is False
        and proof.get("proofs") == []
        and len(errors) == 1
        and errors[0].get("stage") == stage
        and errors[0].get("reason") == "ValueError"
        and counters.get("login_requests") == 1
        and counters.get("submit_requests") == requests
        and counters.get("posts") == posts
        and counters.get("reads") == 0
        and counters.get("csrf_fetches") == int(case.startswith("csrf-"))
        and proof.get("submit_status") == (403 if case == "csrf-rejected" else
                                          201 if case == "session-expired-after-submit" else None)
    )


def run_case(case, browser_path=None):
    """Run existing proof API; return only sanitized failure/control metadata."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "dom-xss-analyzer"))
    import dxaprove
    with failure_lab(case) as (spec, state):
        proof = dxaprove.run(spec, browser_path)
        counters = dict(state)
    return {
        "case_id": "auth-failure-v1:" + case,
        "measurement": "expected-operational-failure-not-xss-accuracy",
        "expected_status": "error", "expected_stage": CASES[case][0],
        "control_passed": accept_failure(case, proof, counters),
        "scanner_status": proof["status"], "accuracy_evaluated": False,
        "fixture": counters, "proof": proof,
    }


def run_suite(browser_path=None):
    """Run six bounded owned workers; expected errors are control outcomes."""
    import subprocess
    from process_control import OwnedProcess
    rows = []
    for case in CASES:
        worker = None
        try:
            worker = OwnedProcess([sys.executable, str(Path(__file__).resolve()), "--worker"])
            output = worker.communicate(json.dumps({"case": case, "browser": browser_path}), 30)
            if worker.proc.returncode:
                raise ValueError("worker failed")
            row = json.loads(output)
            if row.get("case_id") != "auth-failure-v1:" + case:
                raise ValueError("wrong case identity")
            # Parent independently repeats acceptance rather than trusting worker boolean.
            row["control_passed"] = accept_failure(case, row["proof"], row["fixture"])
            row["accuracy_evaluated"] = False
            row["scanner_status"] = row["proof"].get("status")
        except Exception as error:
            row = {"case_id": "auth-failure-v1:" + case, "control_passed": False,
                   "scanner_status": "timeout" if isinstance(error, subprocess.TimeoutExpired) else "error",
                   "reason": type(error).__name__, "accuracy_evaluated": False}
        finally:
            if worker is not None:
                try:
                    worker.close()
                    row["cleanup_status"] = "passed"
                except Exception:
                    row.update(control_passed=False, cleanup_status="error", reason="cleanup-failed")
            else:
                row["cleanup_status"] = "not-started"
        rows.append(row)
    import hashlib
    return {"schema": "auth-failure-controls/1",
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "measurement": "expected-operational-failure-not-xss-accuracy",
            "selected": len(CASES),
            "passed": sum(row["control_passed"] is True for row in rows),
            "rows": rows}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--browser")
    parser.add_argument("--out")
    args = parser.parse_args()
    if args.worker:
        config = json.loads(sys.stdin.read())  # containment gate, before lab/browser start
        print(json.dumps(run_case(config["case"], config.get("browser"))))
        return 0
    if not args.out:
        parser.error("--out is required")
    destination = Path(args.out)
    if destination.exists():
        parser.error("--out must be a new file")
    report = run_suite(args.browser)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    print("Auth failure controls: %d/%d; excluded from XSS accuracy" %
          (report["passed"], report["selected"]))
    return 0 if report["passed"] == report["selected"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
