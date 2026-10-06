"""R3 local stored proof pipeline. Explicit loopback origin, no JS instrumentation."""
import argparse
import datetime
import hashlib
import html
import importlib.metadata
import json
from pathlib import Path
import platform
import secrets
import time
import urllib.parse
import urllib.request

import dxadyn
import dxa_evidence as evidence

ROUTE_INIT = r"""
(() => {
  window.__dxaRoutes = [];
  const add = (kind, value) => {
    try { const u = new URL(String(value || ''), location.href); if (u.origin === location.origin)
      window.__dxaRoutes.push({kind, url: u.href}); } catch (_) {}
  };
  for (const name of ['pushState', 'replaceState']) {
    const original = history[name];
    history[name] = function(state, title, url) { add(name, url); return original.apply(this, arguments); };
  }
  addEventListener('hashchange', () => add('hashchange', location.href));
})();
"""


def origin(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password:
        raise ValueError("invalid URL")
    return p.scheme, p.hostname.lower(), p.port or (443 if p.scheme == "https" else 80)


def validate(spec):
    base = origin(spec["origin"])
    if base[1] not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("this proof pipeline supports loopback labs only")
    check = spec["session_check"]
    expect = check["expect"]
    role_path = spec["role_path"]
    if (not isinstance(expect, dict) or role_path not in expect
            or not isinstance(expect[role_path], str) or not expect[role_path]
            or any(not k.startswith("$.") or v is None for k, v in expect.items())):
        raise ValueError("explicit expected role and identity contract required")
    if len(expect) < 2:
        raise ValueError("check must include identity and role")
    if spec.get("variant", "image") not in ("image", "href"):
        raise ValueError("supported proof variants: image, href")
    urls = [check["url"], spec["submit"]["url"], spec["read_url"]]
    for step in spec.get("auth_flow", {}).get("steps", []):
        urls.append(step["url"])
    if any(origin(url) != base for url in urls):
        raise ValueError("all endpoints must share the declared origin")
    window = spec.get("observe_ms", 1000)
    if type(window) is not int or not 100 <= window <= 10000:
        raise ValueError("observe_ms must be 100..10000")
    return base


def matches(body, expect):
    return all(type(dxadyn._jsonpath_get(body, path)) is type(value)
               and dxadyn._jsonpath_get(body, path) == value for path, value in expect.items())


def run(spec, browser_path=None):
    result = {"schema": "dxa-browser-proof/1", "status": "error", "triage": "unreviewed",
              "execution_observed": False, "http_session_checked": False,
              "browser_session_checked": False, "events": [], "proofs": [],
              "scope": "loopback, single origin, one shared account, no vulnerability confirmation",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    result.update(python=platform.python_version(), platform=platform.system(),
                  created_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    stage = "configuration"
    browser = context = None
    try:
        allowed = validate(spec)
        result["observe_ms"] = spec.get("observe_ms", 1000)
        result["read_url"] = evidence.safe_url(spec["read_url"])
        result["session_role"] = spec["session_check"]["expect"][spec["role_path"]]
        result["source"] = {"url": evidence.safe_url(spec["submit"]["url"]),
                            "parameter": spec["submit"]["field"], "method": "POST"}

        class ScopedRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                if origin(newurl) != allowed:
                    raise ValueError("redirect outside proof origin")
                return super().redirect_request(req, fp, code, msg, headers, newurl)

        stage = "browser-start"
        from playwright.sync_api import sync_playwright
        result["playwright"] = importlib.metadata.version("playwright")
        with sync_playwright() as pw, dxadyn._SESSION_LOCK:
            names = ("OPENER", "EXTRA_HEADERS", "REPORT_EVENTS", "SESSION_ROLE", "SESSION_CHECK",
                     "CSRF_REFRESH_URL", "CSRF_HEADER_NAME", "_RATE_LIMITER")
            previous = {name: getattr(dxadyn, name) for name in names}
            try:
                launch = {"headless": True}
                if browser_path:
                    launch["executable_path"] = str(browser_path)
                browser = pw.chromium.launch(**launch)
                result["browser_version"] = browser.version
                jar = dxadyn.http.cookiejar.CookieJar()
                dxadyn.OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), ScopedRedirect())
                dxadyn.EXTRA_HEADERS, dxadyn.REPORT_EVENTS = {}, []
                dxadyn.CSRF_REFRESH_URL = dxadyn.CSRF_HEADER_NAME = ""
                dxadyn._RATE_LIMITER = None
                dxadyn.SESSION_ROLE = result["session_role"]
                stage = "http-auth"
                if spec.get("auth_flow"):
                    auth = dxadyn.run_auth_flow(spec["auth_flow"])
                    if auth["error"] or not auth["authenticated"]:
                        raise ValueError("auth failed")
                if not dxadyn.verify_session(spec["session_check"]):
                    raise ValueError("HTTP identity mismatch")
                result["http_session_checked"] = True
                # Only explicitly configured credentials are transferred; never harvest
                # page traffic or copy arbitrary captured headers to another origin.
                headers = dict(dxadyn.EXTRA_HEADERS)
                explicit_headers = spec.get("browser_headers", {})
                if not isinstance(explicit_headers, dict):
                    raise ValueError("browser_headers must be an object")
                allowed_header_names = {"authorization", "x-csrf-token", "csrf-token", "x-xsrf-token"}
                if any(str(k).lower() not in allowed_header_names or not isinstance(v, str) or not v for k, v in explicit_headers.items()):
                    raise ValueError("browser_headers contains unsupported or empty header")
                headers.update(explicit_headers)
                result["browser_header_names"] = sorted(k.lower() for k in headers)
                context = browser.new_context(service_workers="block", java_script_enabled=spec.get("javascript", True))
                context.add_init_script(ROUTE_INIT)

                def route_request(route):
                    try:
                        in_scope = origin(route.request.url) == allowed
                    except ValueError:
                        in_scope = False
                    if not in_scope:
                        result["events"].append({"stage": "scope", "kind": "skip", "reason": "request-blocked"})
                        route.abort()
                    else:
                        route.continue_(headers={**route.request.headers, **headers})

                context.route("**/*", route_request)

                def transfer_cookies():
                    context.clear_cookies()
                    cookies = []
                    for cookie in jar:
                        domain = cookie.domain.lstrip(".")
                        if domain not in (allowed[1], allowed[1] + ".local") or cookie.is_expired():
                            continue
                        cookies.append({"name": cookie.name, "value": cookie.value,
                                        "domain": allowed[1], "path": cookie.path or "/",
                                        "secure": cookie.secure, "httpOnly": cookie.has_nonstandard_attr("HttpOnly")})
                    if cookies:
                        context.add_cookies(cookies)

                def check_browser_session():
                    response = context.request.get(spec["session_check"]["url"], headers=headers,
                                                   max_redirects=0, timeout=5000)
                    try:
                        return (response.status == 200 and "application/json" in response.headers.get("content-type", "")
                                and matches(response.json(), spec["session_check"]["expect"]))
                    finally:
                        response.dispose()

                stage = "browser-auth"
                transfer_cookies()
                if not check_browser_session():
                    raise ValueError("browser identity mismatch")
                result["browser_session_checked"] = True
                stage = "submit"
                cid = "dxa" + secrets.token_hex(16)
                result["canary_id"] = cid
                payload = cid + '<img src="/__dxa_missing" onerror="window.__dxaProof=\'' + cid + '\'">'
                result["variant"] = spec.get("variant", "image")
                if result["variant"] == "href":
                    payload = '<a id="' + cid + '" href="javascript:void(window.__dxaProof=\'' + cid + '\')">proof</a>'
                result["payload_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
                status, _ = dxadyn._submit_form(spec["submit"]["url"], spec["submit"]["field"],
                                                spec["submit"].get("extra", {}), payload,
                                                csrf_field=spec["submit"].get("csrf_field", ""))
                result["submit_status"] = status
                if status is None or not 200 <= status < 300:
                    raise ValueError("submit rejected")
                transfer_cookies()  # include rotations made by the HTTP submit
                stage = "browser-auth-after-submit"
                if not check_browser_session():
                    result["browser_session_checked"] = False
                    raise ValueError("browser identity changed")
                stage = "read"
                page = context.new_page()
                page.on("dialog", lambda dialog: dialog.dismiss())
                response = page.goto(spec["read_url"], wait_until="load", timeout=10000)
                if response is None or response.status != 200:
                    raise ValueError("reader unavailable")
                result["read_status"] = response.status
                try:
                    routes = page.evaluate("() => window.__dxaRoutes || []")
                    unique = []
                    seen = set()
                    budget = int(spec.get("route_budget", 32))
                    for item in routes:
                        key = (item.get("kind"), item.get("url"))
                        if key not in seen and len(unique) < budget:
                            seen.add(key)
                            unique.append(item)
                    result["routes"] = {"runtime": unique, "budget": budget}
                except Exception:
                    result["routes"] = {"runtime": [], "budget": int(spec.get("route_budget", 32))}
                if result["variant"] == "href":
                    link = page.locator("a#" + cid)
                    if link.count() == 1:
                        link.click(timeout=1000, no_wait_after=True)
                stage = "observe"
                deadline = time.monotonic() + result["observe_ms"] / 1000
                while time.monotonic() < deadline:
                    for frame in page.frames:
                        if frame.url == "about:blank":
                            continue
                        try:
                            if origin(frame.url) != allowed:
                                continue
                            # Read an existing value; never evaluate the injected payload.
                            observed = frame.evaluate("() => window.__dxaProof || null")
                            if observed == cid:
                                result["proofs"].append({"canary_id": cid, "frame_url": evidence.safe_url(frame.url),
                                                        "event": "matching-browser-canary"})
                        except Exception:
                            continue  # navigation/detachment is not execution evidence
                    if result["proofs"]:
                        break
                    page.wait_for_timeout(25)
                result["execution_observed"] = bool(result["proofs"])
                result["status"] = "execution-observed" if result["proofs"] else "inconclusive"
                if not result["proofs"]:
                    result["events"].append({"stage": "observe", "kind": "info", "reason": "no-canary-within-window"})
            finally:
                if context:
                    context.close()
                if browser:
                    browser.close()
                for name, value in previous.items():
                    setattr(dxadyn, name, value)
    except Exception as exc:
        result["status"] = "error"
        result["events"].append({"stage": stage, "kind": "error",
                                 "reason": "browser-unavailable" if stage == "browser-start" else type(exc).__name__})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--spec")
    source.add_argument("--demo", action="store_true", help="Create and tear down a fresh authenticated loopback lab")
    parser.add_argument("--output", required=True, help="New artifact directory")
    parser.add_argument("--browser", help="Installed Chrome/Chromium executable; omitted uses Playwright Chromium")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    if args.demo:
        from dxa_proof_lab import lab
        with lab() as (spec, _):
            result = run(spec, args.browser)
    else:
        try:
            spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            spec = {}
        result = run(spec, args.browser)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    (output / "result.json").write_text(serialized, encoding="utf-8")
    (output / "result.html").write_text('<!doctype html><meta charset="utf-8"><title>Browser proof</title><h1>'
                                       + html.escape(result["status"]) + '</h1><pre>' + html.escape(serialized) + '</pre>', encoding="utf-8")
    print("[dxaprove] " + result["status"])
    return 2 if result["status"] == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
