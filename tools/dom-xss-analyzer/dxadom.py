"""dxadom - the browser harness for dxa/dxadyn.

Phase 2.1: skeleton + graceful availability check + basic navigation.
Phase 2.2: DOM sink detection via a pre-user-JS init script that wraps
           Element.innerHTML/outerHTML setters, document.write/writeln,
           Range.createContextualFragment, Function, Location.href.
           Native eval is deliberately not wrapped (lexical scope preservation).
Phase 2.3: page.on('dialog') captures alert / confirm / prompt /
           beforeunload observations. Legacy correlation helpers remain;
           bare visits and dialogs do not establish XSS execution evidence.
           The separate dxaprove pipeline records correlated canary execution.
Phase 2.4: SPA route discovery - init script intercepts
           history.pushState / replaceState / hashchange to capture
           runtime navigations; static pass scans <script> text and
           bundle content for React/Vue/Angular route declarations.
Phase 2.5: page.on('request') observes allowlisted auth/CSRF header
           names on XHR/fetch traffic. The visit summary keeps origin,
           route and presence, never credential values or replay material.

Zero-dep discipline for the CORE tool stays: this module imports
playwright *inside* is_available() so an install missing playwright
still runs the rest of dxadyn without an ImportError. The `--dom`
CLI flag in dxadyn.py imports this module and either delegates to
its harness or prints a clear install line and continues.

Install:
    pip install playwright
    playwright install chromium

For pre-installed browsers (like the SDK's /opt/pw-browsers layout),
find_chromium_executable() also probes the well-known versioned
directories that Playwright's default lookup misses.
"""
from __future__ import annotations
import contextlib
import glob
import ipaddress
import os
from urllib.parse import urljoin, urlsplit
from typing import Any, Iterator, List, Optional

# Known chromium binary paths, in probe order. First hit wins.
# The versioned entries cover SDK / CI images where playwright's
# default lookup fails because PLAYWRIGHT_BROWSERS_PATH is set to
# the parent dir but the actual binary lives in a versioned child.
_CHROMIUM_HINTS = [
    # SDK layout (Anthropic Code sandboxes and similar):
    "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
    "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
    # User install layout on Linux:
    os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
    os.path.expanduser(
        "~/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux/headless_shell"
    ),
    # macOS user install:
    os.path.expanduser(
        "~/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
    ),
]


# Phase 2.2: DOM sink detection init script. Runs BEFORE any user JS
# via page.add_init_script(), replaces each dangerous sink with a
# wrapper that records the call to window.__dxadom_sinks[] and then
# delegates to the original. IIFE-wrapped so no globals leak besides
# __dxadom_sinks itself.
#
# Every recorded entry is a plain object:
#   { sink: str, arg: str (truncated to 4 KiB), stack: str, ts: number }
#
# Sinks patched:
#   Element.prototype.innerHTML setter
#   Element.prototype.outerHTML setter
#   document.write / document.writeln
#   Range.prototype.createContextualFragment
#   eval is intentionally not wrapped: reassignment breaks direct lexical eval.
#   window.Function (via Proxy so both call + construct fire)
#   Location.prototype.href setter (records; navigation still fires -
#     see caveat in visit_with_sinks docstring)

_SINK_INIT_SCRIPT = r"""
(() => {
  if (window.__dxadom_installed__) { return; }
  window.__dxadom_installed__ = true;
  window.__dxadom_sinks = [];
  const cap = 4096;
  const record = (name, arg) => {
    try {
      const s = (typeof arg === 'string') ? arg : String(arg);
      // Suppress introspection into our own tracking: Playwright's
      // page.evaluate() reads window.__dxadom_sinks via an eval-ish
      // path and would otherwise record itself as a sink hit.
      if (s.indexOf('__dxadom_sinks') >= 0) return;
      window.__dxadom_sinks.push({
        sink: name,
        arg: s.length > cap ? s.slice(0, cap) + '...[truncated]' : s,
        stack: (new Error()).stack || '',
        ts: Date.now(),
      });
    } catch (_) { /* never break user JS */ }
  };

  // Element.prototype.innerHTML - setter interception via defineProperty
  try {
    const d = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
    if (d && d.set) {
      Object.defineProperty(Element.prototype, 'innerHTML', {
        get: d.get,
        set: function(v) { record('Element.innerHTML', v); return d.set.call(this, v); },
        configurable: true,
      });
    }
  } catch (_) {}

  // Element.prototype.outerHTML
  try {
    const d = Object.getOwnPropertyDescriptor(Element.prototype, 'outerHTML');
    if (d && d.set) {
      Object.defineProperty(Element.prototype, 'outerHTML', {
        get: d.get,
        set: function(v) { record('Element.outerHTML', v); return d.set.call(this, v); },
        configurable: true,
      });
    }
  } catch (_) {}

  // document.write / writeln
  try {
    const origWrite = document.write;
    document.write = function(...args) {
      args.forEach(a => record('document.write', a));
      return origWrite.apply(document, args);
    };
  } catch (_) {}
  try {
    const origWriteln = document.writeln;
    document.writeln = function(...args) {
      args.forEach(a => record('document.writeln', a));
      return origWriteln.apply(document, args);
    };
  } catch (_) {}

  // Range.prototype.createContextualFragment
  try {
    if (window.Range && Range.prototype.createContextualFragment) {
      const orig = Range.prototype.createContextualFragment;
      Range.prototype.createContextualFragment = function(s) {
        record('Range.createContextualFragment', s);
        return orig.call(this, s);
      };
    }
  } catch (_) {}

  // Preserve native eval identity. A wrapper also intercepts direct eval and
  // turns it into indirect eval, losing the caller's lexical environment.
  // Eval calls are therefore outside the sink observer's coverage.

  // Function constructor - Proxy handles both call and construct.
  try {
    const origFn = window.Function;
    window.Function = new Proxy(origFn, {
      apply(t, thisArg, args) {
        args.forEach(a => record('Function', a));
        return Reflect.apply(t, thisArg, args);
      },
      construct(t, args) {
        args.forEach(a => record('Function', a));
        return Reflect.construct(t, args);
      },
    });
  } catch (_) {}

  // Location.href setter. Recording fires BEFORE navigation, but the
  // subsequent nav wipes window.__dxadom_sinks. Callers who care about
  // Location.href sinks should snapshot sinks BEFORE any user event
  // that could trigger navigation, or wire a page.on('framenavigated')
  // listener that pre-fetches sinks (Phase 2.3+).
  try {
    const d = Object.getOwnPropertyDescriptor(Location.prototype, 'href');
    if (d && d.set) {
      Object.defineProperty(Location.prototype, 'href', {
        get: d.get,
        set: function(v) { record('Location.href', v); return d.set.call(this, v); },
        configurable: true,
      });
    }
  } catch (_) {}

  // Phase 2.4: SPA route discovery. React Router, Vue Router, Angular
  // and hand-rolled hash-routers all navigate WITHOUT a full page load
  // by calling history.pushState / replaceState or mutating location.hash.
  // A plain crawler sees the initial URL only. We intercept the three
  // documented mechanisms so post-load enumeration reveals every route
  // the SPA opened during the current page's lifetime.
  window.__dxadom_routes = [];
  const recRoute = (kind, url) => {
    try {
      window.__dxadom_routes.push({
        kind: kind,
        url: String(url),
        ts: Date.now(),
      });
    } catch (_) {}
  };

  try {
    const origPush = history.pushState;
    history.pushState = function(state, title, url) {
      if (url != null) recRoute('pushState', url);
      return origPush.apply(this, arguments);
    };
  } catch (_) {}

  try {
    const origReplace = history.replaceState;
    history.replaceState = function(state, title, url) {
      if (url != null) recRoute('replaceState', url);
      return origReplace.apply(this, arguments);
    };
  } catch (_) {}

  try {
    window.addEventListener('hashchange', function() {
      recRoute('hashchange', location.hash || '');
    });
  } catch (_) {}
})();
"""


def sink_hits_for(sinks: List[dict], needle: str) -> List[dict]:
    """Filter a sinks list to only entries whose `arg` contains `needle`.
    Used to attribute DOM sink calls to an injected canary cid."""
    if not needle:
        return []
    return [s for s in (sinks or []) if needle in (s.get("arg") or "")]


# Legacy dialog-correlation API. These helpers and their historical label
# remain for compatibility; the current bare DOM CLI and shared evidence
# adapter report dialogs as observations. A dialog or marker-looking string
# alone is not correlated browser execution or a vulnerability verdict.

PROVEN_EXECUTABLE = "proven-executable"


def dialog_hits_for(dialogs: List[dict], needle: str) -> List[dict]:
    """Filter a dialogs list to only entries whose `message` contains the
    needle. Same shape as sink_hits_for: empty needle -> empty list,
    None/[] input -> empty list.

    A non-empty return means the browser actually ran an alert/confirm/
    prompt with the canary embedded in the argument - the payload
    executed, not just landed."""
    if not needle:
        return []
    return [d for d in (dialogs or []) if needle in (d.get("message") or "")]


# --- Phase 2.4: SPA route discovery -----------------------------------------
#
# Two complementary passes:
#   1. Runtime capture (in the init script) - intercepts pushState /
#      replaceState / hashchange, so any route the SPA opens during the
#      first render lands in window.__dxadom_routes.
#   2. Static extraction (extract_static_routes) - after load, we scan
#      every <script> tag's text content for route-declaration patterns
#      (React `<Route path="...">`, Vue `{ path: "..." }`, Angular
#      `RouterLink`, bare `#/foo` hash-router literals). Static wins
#      for routes the initial render never opens; runtime wins for
#      route strings that were computed at runtime and never appear
#      as literals.

import re as _re

# Route-string patterns. Every capture group extracts ONE path candidate.
# Kept conservative: paths must start with `/` or `#/`, contain only URL-
# safe chars, and be at least 2 chars. Names include `:param` / `*` for
# dynamic segments.
_ROUTE_PATTERNS = [
    # React Router <Route path="/foo">, `path: "/foo"`, `to="/foo"`
    _re.compile(r'''(?:path|to)\s*[=:]\s*["'](/[A-Za-z0-9_/:\-\.\*]{1,200})["']'''),
    # Bare hash-router literal `#/foo` (Vue hash mode, jQuery-era SPAs)
    _re.compile(r'''["'](#/[A-Za-z0-9_/:\-\.]{1,200})["']'''),
    # Angular routerLink="/foo" (attribute value in HTML, not just JS).
    # Case-insensitive: browsers lowercase attribute names when serializing
    # DOM back to HTML, so a `routerLink="/foo"` in the raw response
    # comes back as `routerlink="/foo"` from page.content().
    _re.compile(r'''routerLink\s*=\s*["'](/[A-Za-z0-9_/:\-\.]{1,200})["']''',
                _re.IGNORECASE),
    # navigate("/foo") / router.push("/foo") - covers React Router 6,
    # Next.js router.push, Vue Router push.
    _re.compile(r'''(?:navigate|router\.push|router\.replace)\s*\(\s*["'](/[A-Za-z0-9_/:\-\.]{1,200})["']'''),
]


# --- Phase 2.5: CSRF-in-header auto-detect ---------------------------------
#
# Modern SPAs can attach anti-CSRF and session headers to XHR/fetch
# requests. This observer records allowlisted header names and request
# locations for operator review; it does not retain or transfer values.
#
# Names recognized (case-insensitive; the extractor normalises keys).

_CSRF_HEADER_NAMES = {
    "x-csrf-token",     # Rails, Laravel meta-injected
    "x-xsrf-token",     # Angular (double-submit cookie pattern)
    "csrf-token",       # some hand-rolled SPAs
    "x-csrftoken",      # Django REST framework
    "anti-csrf-token",  # older .NET
}
_SESSION_HEADER_NAMES = {
    "authorization",    # Bearer / Basic
    "x-api-key",        # AWS API Gateway, many SaaS
    "x-auth-token",     # Kubernetes, some SPAs
    "x-access-token",   # JWT wrappers
}
_METADATA_HEADER_NAMES = {
    "x-requested-with", # `XMLHttpRequest` marker Rails/Django expect
    "x-correlation-id",
    "x-request-id",
}


def extract_auth_headers(requests: List[dict]) -> dict:
    """Return allowlisted header names with presence booleans, never values.

    This is observation only. A present header does not establish an active
    session, a working CSRF token, permission to replay it or JS execution.
    """
    if not requests:
        return {}
    known = _CSRF_HEADER_NAMES | _SESSION_HEADER_NAMES | _METADATA_HEADER_NAMES
    out: dict = {}
    for req in requests:
        headers = req.get("headers") or {}
        for name, value in headers.items():
            key = name.lower()
            if key in known and value:
                out[key] = True
    return out


def observe_auth_headers(requests: List[dict]) -> List[dict]:
    """Describe each allowlisted XHR/fetch header without retaining its value.

    Query, fragment and userinfo are omitted from request locations. The
    route is a path, and can still contain application data; sharing a
    summary requires the normal evidence review.
    """
    known = _CSRF_HEADER_NAMES | _SESSION_HEADER_NAMES | _METADATA_HEADER_NAMES
    observations = []
    for req in requests or []:
        parsed = urlsplit(req.get("url") or "")
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            continue
        try:
            origin = f"{parsed.scheme}://{parsed.hostname}"
            if parsed.port is not None:
                origin += f":{parsed.port}"
        except ValueError:
            continue
        for name, value in (req.get("headers") or {}).items():
            key = name.lower()
            if key in known:
                observations.append({
                    "name": key, "origin": origin,
                    "route": parsed.path or "/", "present": bool(value),
                })
    return observations


def extract_static_routes(script_text: str) -> List[str]:
    """Regex-scan JS/HTML text for route declarations. Returns a
    deduplicated, order-preserved list of route strings. Never raises;
    an empty or None input returns [].

    Precision-first: the patterns are conservative on purpose. A
    false-positive route just adds one wasted crawl step; a false-
    negative miss is worse (the whole surface stays invisible)."""
    if not script_text:
        return []
    seen = set()
    out: List[str] = []
    for pat in _ROUTE_PATTERNS:
        for m in pat.finditer(script_text):
            route = m.group(1)
            if route and route not in seen:
                seen.add(route)
                out.append(route)
    return out


def find_chromium_executable() -> Optional[str]:
    """Return the path of a Chromium binary Playwright can launch, or
    None if no pre-installed browser was found in any known location.

    Uses glob to match versioned directories - Playwright bumps the
    build number roughly every release, so hard-coding `chromium-1194`
    would rot fast."""
    # Explicit operator selection also supports installed Chrome on Windows,
    # where Playwright's browser cache may not contain a Chromium build.
    override = os.environ.get("DXA_BROWSER", "").strip().strip('"')
    if override and os.path.isfile(override):
        return override
    for hint in _CHROMIUM_HINTS:
        # If the hint has no glob metachars, os.path.isfile is the check.
        if any(c in hint for c in "*?["):
            matches = glob.glob(hint)
            if matches:
                # Newest first if multiple versions coexist.
                matches.sort(reverse=True)
                return matches[0]
        elif os.path.isfile(hint) and os.access(hint, os.X_OK):
            return hint
    return None


def is_available() -> tuple[bool, str]:
    """Return (available, reason). available=True means dxadom can
    launch a browser; reason is a short human sentence for logging.

    Does NOT raise. Missing playwright -> (False, 'playwright not
    installed'). Present playwright but no chromium binary anywhere
    -> (False, 'chromium not found ...'). All good -> (True, '<path>').
    """
    try:
        import playwright  # noqa: F401
    except ImportError:
        return (False,
                "playwright not installed - run `pip install playwright && "
                "playwright install chromium` for --dom support")
    exe = find_chromium_executable()
    if exe is None:
        return (False,
                "chromium binary not found in any known location - run "
                "`playwright install chromium`")
    return (True, exe)


def _loopback_http_origin(url: str) -> Optional[tuple[str, str, int]]:
    """Return a normalized HTTP(S) origin only for literal loopback IPs.

    Hostnames such as ``localhost`` are deliberately rejected: name resolution
    is environment-controlled and is not a reliable network boundary.
    """
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        address = ipaddress.ip_address(parsed.hostname)
        if not address.is_loopback:
            return None
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
        return parsed.scheme.lower(), address.compressed.lower(), port
    except (ValueError, TypeError):
        return None


def _websocket_origin(url: str) -> Optional[str]:
    """Return a credential-free WebSocket origin for event reporting."""
    try:
        parsed = urlsplit(url)
        scheme = parsed.scheme.lower()
        if scheme not in ("ws", "wss") or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        default_port = 443 if scheme == "wss" else 80
        port = parsed.port or default_port
        host = parsed.hostname.lower()
        if ":" in host:
            host = f"[{host}]"
        suffix = "" if port == default_port else f":{port}"
        return f"{scheme}://{host}{suffix}"
    except (ValueError, TypeError):
        return None


def _safe_http_origin_label(url: str) -> Optional[str]:
    """Return a credential-free HTTP(S) origin; omit path and query data."""
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        host = parsed.hostname.lower()
        if ":" in host:
            host = f"[{host}]"
        port = parsed.port
        default = 443 if parsed.scheme.lower() == "https" else 80
        suffix = f":{port}" if port is not None and port != default else ""
        return f"{parsed.scheme.lower()}://{host}{suffix}"
    except (ValueError, TypeError):
        return None


class BrowserSession:
    """Context manager around a headless Chromium page. Two-level context:
    the class starts the playwright driver + a browser; each visit()
    creates a fresh page so state doesn't leak between navigations.

    Console messages, page errors and dialogs are captured into
    per-visit lists so callers can grade a visit without wiring event
    listeners themselves.

    Init scripts observe supported DOM sinks and SPA routes; dialog capture
    records observations without promoting them to execution proof. Native
    eval is preserved and its instrumentation limit is included in summaries.
    """

    def __init__(self, headless: bool = True,
                 executable_path: Optional[str] = None,
                 timeout_ms: int = 15000):
        self.headless = headless
        self.executable_path = executable_path
        self.timeout_ms = timeout_ms
        self._pw = None
        self._browser = None

    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise RuntimeError(
                "playwright not installed - see dxadom.is_available()"
            ) from e
        exe = self.executable_path or find_chromium_executable()
        self._pw = sync_playwright().start()
        launch_kwargs: dict[str, Any] = {"headless": self.headless}
        if exe:
            launch_kwargs["executable_path"] = exe
        self._browser = self._pw.chromium.launch(**launch_kwargs)
        return self

    def __exit__(self, *exc):
        try:
            if self._browser is not None:
                self._browser.close()
        finally:
            if self._pw is not None:
                self._pw.stop()

    @contextlib.contextmanager
    def _page_scope(self) -> Iterator[Any]:
        assert self._browser is not None, (
            "BrowserSession must be used inside `with` block"
        )
        context = self._browser.new_context(service_workers="block")
        try:
            yield context
        finally:
            context.close()

    def visit(self, url: str) -> dict:
        """Navigate to url, return a summary dict:
          {
            'url': str, 'status': int | None, 'title': str,
            'body_len': int, 'console': [str], 'errors': [str],
            'sinks':   [ {sink, arg, stack, ts} ],     # Phase 2.2
            'dialogs': [ {type, message, ts} ],        # Phase 2.3
            'routes':  {                               # Phase 2.4
              'runtime': [ {kind, url, ts} ],  # pushState/replaceState/hashchange
              'static':  [str],                # regex-extracted from <script>
            },
            'requests': [ {method, origin, route} ],
            'network_events': [ {channel, kind, reason, origin} ],
            'header_observations': [ {name, origin, route, present} ],
            'auth_headers': { name_lower: True },       # names only
          }

        The sink init script runs BEFORE any user JS, so every subsequent
        assignment to innerHTML/outerHTML, call to document.write /
        Function / Range.createContextualFragment, or setter on
        Location.href gets recorded into window.__dxadom_sinks[]. After
        `load`, we snapshot that list into `summary['sinks']`.

        Caveat for Location.href sinks: recording fires BEFORE navigation
        starts, but the navigation itself wipes the sinks array on the
        NEW page. If the very first user JS on a page sets Location.href,
        we may snapshot after the navigation completed and miss the
        record. A framenavigated listener (Phase 2.3) will handle that.

        Never raises for network errors; those land in `errors`. Timeout
        is `self.timeout_ms`."""
        summary: dict = {
            "url": url, "status": None, "title": "",
            "body_len": 0, "console": [], "errors": [],
            "sinks": [], "dialogs": [],
            "routes": {"runtime": [], "static": []},
            "requests": [], "header_observations": [], "auth_headers": {},
            "network_events": [],
            "limitations": ["eval-not-instrumented-to-preserve-lexical-scope"],
        }
        origin = _loopback_http_origin(url)
        if origin is None:
            summary["network_events"].append({
                "channel": "http", "kind": "blocked",
                "reason": "initial-url-outside-literal-loopback-scope",
                "origin": None,
            })
            summary["errors"].append("initial URL blocked by loopback browser scope")
            return summary

        with self._page_scope() as context:
            # Context-level routing covers top-level navigation, redirects,
            # frames and subresources. Service workers are disabled because
            # Playwright routing does not intercept service-worker-owned work.
            def _route_http(route):
                request_url = route.request.url
                request_origin = _loopback_http_origin(request_url)
                if request_origin != origin:
                    summary["network_events"].append({
                        "channel": "http", "kind": "blocked",
                        "reason": "request-outside-same-loopback-origin",
                        "origin": _safe_http_origin_label(request_url),
                    })
                    route.abort()
                    return
                try:
                    # Playwright invokes route handlers only for the first
                    # request in a redirect chain. Fetch exactly one hop, so
                    # the adapter can reject every redirect before Chromium
                    # follows its Location header.
                    response = route.fetch(max_redirects=0)
                    if 300 <= response.status < 400:
                        location = response.headers.get("location", "")
                        destination = urljoin(request_url, location) if location else request_url
                        summary["network_events"].append({
                            "channel": "http", "kind": "blocked",
                            "reason": "http-redirect-disabled-by-dxadom-scope",
                            "origin": _safe_http_origin_label(destination),
                        })
                        route.abort()
                        return
                    route.fulfill(response=response)
                except Exception:                         # noqa: BLE001
                    summary["network_events"].append({
                        "channel": "http", "kind": "error",
                        "reason": "request-routing-failed-closed",
                        "origin": _safe_http_origin_label(request_url),
                    })
                    try:
                        route.abort()
                    except Exception:                     # noqa: BLE001
                        pass

            context.route("**/*", _route_http)

            # Playwright >=1.48 supports explicit WebSocket routing. If this
            # guard is absent, fail before navigation rather than silently
            # running without the promised HTTP-only boundary.
            route_web_socket = getattr(context, "route_web_socket", None)
            if not callable(route_web_socket):
                summary["network_events"].append({
                    "channel": "websocket", "kind": "error",
                    "reason": "playwright-websocket-routing-unavailable",
                    "origin": None,
                })
                summary["errors"].append(
                    "browser visit unavailable: WebSocket guard is unsupported")
                return summary

            pending_websockets = []

            def _route_websocket(ws):
                ws_url = getattr(ws, "url", "") or ""
                summary["network_events"].append({
                    "channel": "websocket", "kind": "unsupported",
                    "reason": "websocket-channel-disabled-by-dxadom-scope",
                    "origin": _websocket_origin(ws_url),
                })
                # Do not call the sync API from inside Playwright's route
                # callback: it blocks that callback's event loop. Without
                # connect_to_server(), this route is a local mock and cannot
                # open a network connection. Close it from the caller thread
                # after navigation and evidence collection.
                pending_websockets.append(ws)

            route_web_socket("**/*", _route_websocket)
            page = context.new_page()
            page.on("console", lambda msg: summary["console"].append(
                f"{msg.type}: {msg.text}"))
            page.on("pageerror", lambda exc: summary["errors"].append(str(exc)))

            # Phase 2.3: capture + auto-dismiss window.alert/confirm/prompt/
            # beforeunload dialogs. Recording happens BEFORE dismissal so
            # the message is always preserved. Every dialog MUST be
            # dismissed or the page hangs waiting for a response - even
            # if the recorder throws.
            # Phase 2.5: observe XHR/fetch header names. Values are read
            # only inside this callback and never enter the visit summary.
            # Only browser-classified XHR/fetch requests enter the pool.
            def _on_request(req):
                try:
                    if req.resource_type not in ("xhr", "fetch"):
                        return
                    observations = observe_auth_headers([{
                        "url": req.url, "headers": req.headers,
                    }])
                    parsed = urlsplit(req.url)
                    if parsed.scheme not in ("http", "https") or not parsed.hostname:
                        return
                    origin = f"{parsed.scheme}://{parsed.hostname}"
                    if parsed.port is not None:
                        origin += f":{parsed.port}"
                    summary["requests"].append({
                        "method": req.method, "origin": origin,
                        "route": parsed.path or "/",
                    })
                    summary["header_observations"].extend(observations)
                except Exception:                         # noqa: BLE001
                    summary["errors"].append("request observation failed")
            page.on("request", _on_request)

            def _on_dialog(d):
                import time as _t
                try:
                    summary["dialogs"].append({
                        "type": d.type,
                        "message": d.message or "",
                        "ts": int(_t.time() * 1000),
                    })
                except Exception as e:                    # noqa: BLE001
                    summary["errors"].append(f"dialog record: {e}")
                finally:
                    try:
                        d.dismiss()
                    except Exception:                     # noqa: BLE001
                        pass                              # already handled
            page.on("dialog", _on_dialog)

            # Phase 2.2: install the sink init script BEFORE any user JS.
            try:
                page.add_init_script(_SINK_INIT_SCRIPT)
            except Exception as e:                        # noqa: BLE001
                summary["errors"].append(f"add_init_script(): {e}")
            try:
                resp = page.goto(url, timeout=self.timeout_ms,
                                 wait_until="load")
                summary["status"] = resp.status if resp else None
                summary["title"] = page.title() or ""
                try:
                    summary["body_len"] = len(page.content())
                except Exception as e:                    # noqa: BLE001
                    summary["errors"].append(f"content(): {e}")
                # Snapshot the sinks list. If the page navigated away,
                # __dxadom_sinks may be gone; treat that as no capture.
                try:
                    sinks = page.evaluate(
                        "() => window.__dxadom_sinks || []")
                    if isinstance(sinks, list):
                        summary["sinks"] = sinks
                except Exception as e:                    # noqa: BLE001
                    summary["errors"].append(f"sink-snapshot: {e}")

                # Phase 2.4: snapshot runtime SPA routes (pushState /
                # replaceState / hashchange captured by the init script).
                try:
                    runtime = page.evaluate(
                        "() => window.__dxadom_routes || []")
                    if isinstance(runtime, list):
                        summary["routes"]["runtime"] = runtime
                except Exception as e:                    # noqa: BLE001
                    summary["errors"].append(f"route-snapshot: {e}")

                # Phase 2.4: static route extraction. Concatenate every
                # inline <script> tag's text and every <a routerLink=...>
                # attribute-carrying HTML fragment, then regex-scan for
                # route declarations. Bundled external scripts are NOT
                # fetched in this MVP - they will land in the SPA
                # runtime capture above once React/Vue/Angular mounts.
                try:
                    script_texts = page.evaluate(
                        "() => Array.from(document.scripts)"
                        ".map(s => s.textContent || '').join('\\n')")
                    html = ""
                    try:
                        html = page.content() or ""
                    except Exception:                     # noqa: BLE001
                        pass
                    joined = (script_texts or "") + "\n" + html
                    summary["routes"]["static"] = extract_static_routes(joined)
                except Exception as e:                    # noqa: BLE001
                    summary["errors"].append(f"route-static: {e}")

                # Phase 2.5: names only. No browser credential can be
                # replayed from this observation or written into a report.
                try:
                    summary["auth_headers"] = {
                        row["name"]: True
                        for row in summary["header_observations"]
                        if row["present"]
                    }
                except Exception:                         # noqa: BLE001
                    summary["errors"].append("auth observation failed")
            except Exception as e:                        # noqa: BLE001
                summary["errors"].append(f"goto(): {e}")
            for ws in pending_websockets:
                try:
                    ws.close(code=1008,
                             reason="WebSocket unsupported by dxadom scope")
                except Exception:                         # noqa: BLE001
                    summary["network_events"].append({
                        "channel": "websocket", "kind": "error",
                        "reason": "websocket-mock-close-failed",
                        "origin": None,
                    })
        return summary


def summarize_availability() -> str:
    """One-line status suitable for `dxadyn --dom` startup output."""
    ok, reason = is_available()
    prefix = "[dxadom] OK" if ok else "[dxadom] UNAVAILABLE"
    return f"{prefix}: {reason}"
