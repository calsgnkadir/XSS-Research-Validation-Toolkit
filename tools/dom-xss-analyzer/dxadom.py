"""dxadom - the browser harness for dxa/dxadyn.

Phase 2.1: skeleton + graceful availability check + basic navigation.
Later phases build on this:
  2.2 - DOM sink detection (patch Element.innerHTML, eval, jQuery.html)
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
            'body_len': int, 'console': [str], 'errors': [str]
          }

        Never raises for network errors; those land in `errors`. Timeout
        is `self.timeout_ms`."""
        summary: dict = {
            "url": url, "status": None, "title": "",
            "body_len": 0, "console": [], "errors": [],
        }
        with self._page_scope() as page:
            page.on("console", lambda msg: summary["console"].append(
                f"{msg.type}: {msg.text}"))
            page.on("pageerror", lambda exc: summary["errors"].append(str(exc)))
            try:
                resp = page.goto(url, timeout=self.timeout_ms,
                                 wait_until="load")
                summary["status"] = resp.status if resp else None
                summary["title"] = page.title() or ""
                # Guard body access - about:blank / very early failures
                # can leave content() raising a TargetClosedError.
                try:
                    summary["body_len"] = len(page.content())
                except Exception as e:                    # noqa: BLE001
                    summary["errors"].append(f"content(): {e}")
            except Exception as e:                        # noqa: BLE001
                summary["errors"].append(f"goto(): {e}")
        return summary


def summarize_availability() -> str:
    """One-line status suitable for `dxadyn --dom` startup output."""
    ok, reason = is_available()
    prefix = "[dxadom] OK" if ok else "[dxadom] UNAVAILABLE"
    return f"{prefix}: {reason}"
