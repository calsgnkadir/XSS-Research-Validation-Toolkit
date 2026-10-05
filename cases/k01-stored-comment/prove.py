"""Reproduce K01 only on a fresh loopback fixture; no external target option."""
import argparse
from contextlib import contextmanager
import difflib
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.metadata
import json
from pathlib import Path
import platform
import secrets
import sys
import threading
import urllib.parse
import urllib.request

from render_fixed import render as fixed
from render_vulnerable import render as vulnerable

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "tools" / "dom-xss-analyzer"))
import dxadyn


@contextmanager
def fixture(renderer):
    class Handler(BaseHTTPRequestHandler):
        comment = ""
        posts = 0

        def send(self, body, content_type="text/html; charset=utf-8", status=200):
            raw = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            if self.path != "/comments":
                self.send("Not found", status=404)
                return
            size = int(self.headers.get("Content-Length", 0))
            if size > 8192:
                self.send("Too large", status=413)
                return
            data = urllib.parse.parse_qs(self.rfile.read(size).decode())
            Handler.comment = data.get("comment", [""])[0]
            Handler.posts += 1
            self.send("Stored", "text/plain", 201)

        def do_GET(self):
            if self.path == "/comments":
                self.send(renderer(Handler.comment))
            elif self.path == "/json":
                self.send(json.dumps({"comment": Handler.comment}), "application/json")
            elif self.path == "/notice":
                self.send('<!doctype html><script>alert("ordinary application dialog")</script>')
            else:
                self.send("Not found", "text/plain", 404)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", Handler
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def run(output, browser_path=None):
    from playwright.sync_api import sync_playwright
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)  # preserve previous evidence
    cid = "k01" + secrets.token_hex(12)
    payload = cid + '<img src="/missing" onerror="window.__k01=\'' + cid + '\'">'
    result = {"case_version": "k01-v1.0", "cid": cid, "payload": payload,
              "scope": "fresh loopback fixture; anonymous submission and separate reader browser context",
              "execution_claim": "case-specific browser evidence; not a bot execution-confirmed finding",
              "python": platform.python_version(), "platform": platform.system(),
              "playwright": importlib.metadata.version("playwright"), "cases": [],
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                (ROOT / "prove.py", ROOT / "render_fixed.py", ROOT / "render_vulnerable.py")}}
    try:
        with sync_playwright() as pw:
            launch = {"headless": True}
            if browser_path:
                launch["executable_path"] = str(browser_path)
            browser = pw.chromium.launch(**launch)
            result["browser_version"] = browser.version
            try:
                for name, renderer, javascript, path, expected in (
                    ("vulnerable", vulnerable, True, "/comments", True),
                    ("javascript-disabled", vulnerable, False, "/comments", False),
                    ("fixed", fixed, True, "/comments", False),
                    ("json-only", vulnerable, True, "/json", False),
                    ("normal-dialog", vulnerable, True, "/notice", False),
                ):
                    with fixture(renderer) as (base, handler):
                        encoded = urllib.parse.urlencode({"comment": payload}).encode()
                        # Author submits using urllib, never the reader's browser/context.
                        with urllib.request.urlopen(urllib.request.Request(base + "/comments", data=encoded), timeout=3) as response:
                            assert response.status == 201
                        with urllib.request.urlopen(base + path, timeout=3) as response:
                            body = response.read().decode()
                            content_type = response.headers["Content-Type"]
                        (output / (name + "-response.txt")).write_text(body, encoding="utf-8")
                        request = {"method": "POST", "path": "/comments",
                                   "content_type": "application/x-www-form-urlencoded",
                                   "body": encoded.decode(), "status": 201,
                                   "read_path": path, "response_content_type": content_type}
                        (output / (name + "-request.json")).write_text(json.dumps(request, indent=2), encoding="utf-8")
                        context = browser.new_context(java_script_enabled=javascript)
                        try:
                            # Even if the fixture changes, prohibit network outside its origin.
                            def local_only(route):
                                if route.request.url.startswith(base + "/"):
                                    route.continue_()
                                else:
                                    route.abort()
                            context.route("**/*", local_only)
                            page = context.new_page()
                            dialogs = []
                            page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
                            page.goto(base + path, wait_until="load", timeout=10000)
                            if expected:
                                page.wait_for_function("cid => window.__k01 === cid", arg=cid, timeout=3000)
                            else:
                                page.wait_for_timeout(500)
                            observed = page.evaluate("window.__k01 || null")
                            assert (observed == cid) is expected, (name, observed)
                            if name == "fixed":
                                assert page.locator("#comment").inner_text() == payload
                                assert page.locator("#comment img").count() == 0
                            if name == "normal-dialog":
                                assert dialogs == ["ordinary application dialog"]
                            assert handler.posts == 1
                            reflection = dxadyn.verdict(cid, body, marker="<img")
                            finding = dxadyn._finding(base + path, "GET", "comment", reflection, 200,
                                                      dxadyn.find_context(cid, body), cid, content_type, "k01-img")
                            # Bot records HTTP evidence; browser proof stays in this case artifact.
                            assert finding["evidence_level"] != "execution-confirmed"
                            if name == "json-only":
                                assert finding["severity"] == "json-only"
                            result["cases"].append({"name": name, "javascript": javascript,
                                                    "expected_execution": expected, "observed_canary": observed,
                                                    "passed": True, "posts": handler.posts,
                                                    "dialogs": dialogs, "bot_finding": finding})
                        finally:
                            context.close()
            finally:
                browser.close()
        result["passed"] = len(result["cases"]) == 5
    except Exception as exc:
        result.update(passed=False, error_type=type(exc).__name__)
        raise
    finally:
        (output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        diff = difflib.unified_diff((ROOT / "render_vulnerable.py").read_text().splitlines(True),
                                    (ROOT / "render_fixed.py").read_text().splitlines(True),
                                    fromfile="render_vulnerable.py", tofile="render_fixed.py")
        (output / "fix.diff").write_text("".join(diff), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="new evidence directory (must not exist)")
    parser.add_argument("--browser", help="optional installed Chromium/Chrome executable")
    args = parser.parse_args()
    result = run(args.output, args.browser)
    print(f"K01: {len(result['cases'])}/5 controls passed; browser {result['browser_version']}")
