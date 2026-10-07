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
Phase 2.5: CSRF-in-header auto-detect - page.on('request') captures
           every XHR/fetch header, extract_auth_headers() pulls the
           documented CSRF/session/auth families out of the observed
           set so downstream reflected/stored probes can replay them
           without manual --csrf-refresh + --csrf-header config.

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
import os
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
# Modern SPAs (Angular, React with axios interceptors, any XHR wrapper
# that self-installs) attach anti-CSRF / session / API-key headers to
# every stateful request without any HTML meta-tag or hidden form input.
# Phase 1.4's --csrf-refresh + --csrf-header pair requires the operator
# to know that URL and header name up front. Phase 2.5 removes that
# knowledge burden: the browser session watches its own XHR/fetch
# traffic, records the outgoing headers, and callers can pick out the
# canonical CSRF / auth families with extract_auth_headers().
#
# Names recognized (case-insensitive; the extractor normalises keys).
# Split into families so a caller can pick "just CSRF" or "all auth"
# without walking the whole set.

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
    """Walk a captured requests list, return a dict of every CSRF / session /
    metadata header that appeared, keyed by canonical lower-case name and
    valued by the MOST RECENT observed value.

    Empty/None input returns {}. Requests without headers are skipped.
    Header names not in the documented families are ignored - a random
    `X-Custom-Foo` from user code does not get promoted to auth on its
    own, but the operator can extend the families via the module-level
    sets if a target needs it.

    Returns {} when no known family matched; never raises."""
    if not requests:
        return {}
    known = _CSRF_HEADER_NAMES | _SESSION_HEADER_NAMES | _METADATA_HEADER_NAMES
    out: dict = {}
    for req in requests:
        headers = req.get("headers") or {}
        for name, value in headers.items():
            key = name.lower()
            if key in known and value:
                out[key] = value
    return out


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
        page = self._browser.new_page()
        try:
            yield page
        finally:
            page.close()

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
            'requests': [ {method, url, headers} ],    # Phase 2.5 - every
                                                        # XHR/fetch made during
                                                        # load, headers included
            'auth_headers': { name_lower: value },     # Phase 2.5 - subset of
                                                        # requests[].headers that
                                                        # matched CSRF/session/
                                                        # metadata families
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
            "requests": [], "auth_headers": {},
            "limitations": ["eval-not-instrumented-to-preserve-lexical-scope"],
        }
        with self._page_scope() as page:
            page.on("console", lambda msg: summary["console"].append(
                f"{msg.type}: {msg.text}"))
            page.on("pageerror", lambda exc: summary["errors"].append(str(exc)))

            # Phase 2.3: capture + auto-dismiss window.alert/confirm/prompt/
            # beforeunload dialogs. Recording happens BEFORE dismissal so
            # the message is always preserved. Every dialog MUST be
            # dismissed or the page hangs waiting for a response - even
            # if the recorder throws.
            # Phase 2.5: capture every outgoing XHR/fetch request. We
            # keep method + url + headers (small footprint, no body).
            # `request` fires for the initial navigation too - we filter
            # on resource_type so only script-initiated requests land in
            # the auth-detection pool. Main-document nav doesn't set
            # anti-CSRF headers itself, only the SPA's XHR/fetch do.
            def _on_request(req):
                try:
                    if req.resource_type in ("document", "stylesheet",
                                              "image", "font", "media"):
                        return
                    summary["requests"].append({
                        "method": req.method,
                        "url": req.url,
                        "headers": dict(req.headers),
                    })
                except Exception as e:                    # noqa: BLE001
                    summary["errors"].append(f"request record: {e}")
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

                # Phase 2.5: post-process the captured requests list to
                # extract the canonical CSRF / auth / metadata headers.
                # Callers can install these into dxadyn.EXTRA_HEADERS to
                # authenticate subsequent probes without --csrf-refresh.
                try:
                    summary["auth_headers"] = extract_auth_headers(
                        summary["requests"])
                except Exception as e:                    # noqa: BLE001
                    summary["errors"].append(f"auth-extract: {e}")
            except Exception as e:                        # noqa: BLE001
                summary["errors"].append(f"goto(): {e}")
        return summary


def summarize_availability() -> str:
    """One-line status suitable for `dxadyn --dom` startup output."""
    ok, reason = is_available()
    prefix = "[dxadom] OK" if ok else "[dxadom] UNAVAILABLE"
    return f"{prefix}: {reason}"
