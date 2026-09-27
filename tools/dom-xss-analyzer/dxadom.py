"""dxadom - the browser harness for dxa/dxadyn.

Phase 2.1: skeleton + graceful availability check + basic navigation.
Phase 2.2: DOM sink detection via a pre-user-JS init script that wraps
           Element.innerHTML/outerHTML setters, document.write/writeln,
           Range.createContextualFragment, eval, Function, Location.href.
Later phases build on this:
  2.3 - JS execution proof (alert dialog + console listener)
  2.4 - SPA hash-route discovery (history.pushState listener)
  2.5 - CSRF-in-header auto-detect (capture X-CSRF-Token from XHR/fetch)

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
#   window.eval (via reassignment)
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

  // eval - direct reassignment covers the window-scoped eval reference;
  // direct eval-in-scope calls still hit the original spec eval but the
  // window.eval wrapper catches the common `window.eval(x)` pattern.
  try {
    const origEval = window.eval;
    window.eval = function(s) { record('eval', s); return origEval(s); };
  } catch (_) {}

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
})();
"""


def sink_hits_for(sinks: List[dict], needle: str) -> List[dict]:
    """Filter a sinks list to only entries whose `arg` contains `needle`.
    Used to attribute DOM sink calls to an injected canary cid."""
    if not needle:
        return []
    return [s for s in (sinks or []) if needle in (s.get("arg") or "")]


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

    Later phases will extend this with:
      - init scripts that patch DOM sinks before user JS runs (2.2)
      - alert-dialog capture that promotes reflection -> proven-executable
        (2.3)
      - history.pushState listener for SPA route discovery (2.4)
    For 2.1 we ship only the basic visit + body+console capture so the
    scaffolding, install path, and error surface are settled first.
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
            'sinks': [ {sink, arg, stack, ts} ]     # Phase 2.2
          }

        The sink init script runs BEFORE any user JS, so every subsequent
        assignment to innerHTML/outerHTML, call to document.write /
        eval / Function / Range.createContextualFragment, or setter on
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
            "body_len": 0, "console": [], "errors": [], "sinks": [],
        }
        with self._page_scope() as page:
            page.on("console", lambda msg: summary["console"].append(
                f"{msg.type}: {msg.text}"))
            page.on("pageerror", lambda exc: summary["errors"].append(str(exc)))
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
            except Exception as e:                        # noqa: BLE001
                summary["errors"].append(f"goto(): {e}")
        return summary


def summarize_availability() -> str:
    """One-line status suitable for `dxadyn --dom` startup output."""
    ok, reason = is_available()
    prefix = "[dxadom] OK" if ok else "[dxadom] UNAVAILABLE"
    return f"{prefix}: {reason}"
