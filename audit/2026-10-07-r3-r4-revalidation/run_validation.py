"""Reproduce this audit's tests with an explicitly selected local Chrome.

The dxadom module has Linux/macOS discovery hints. Add the operator's browser
to those hints for this test process before collection; do not change or mock
the browser, test expectations, or production discovery implementation.
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", required=True)
    parser.add_argument("--junit", default="acceptance.xml")
    args = parser.parse_args()
    browser = Path(args.browser)
    if not browser.is_file():
        parser.error("explicit browser executable does not exist")
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    os.chdir(repo)
    os.environ["DXA_BROWSER"] = str(browser)
    os.environ["DXA_REQUIRE_BROWSER"] = "1"
    os.environ.pop("BENCH_ENABLE_DOCKER", None)
    sys.path.insert(0, str(repo / "tools" / "dom-xss-analyzer"))
    import dxadom
    dxadom._CHROMIUM_HINTS.insert(0, str(browser))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        instance = pw.chromium.launch(headless=True, executable_path=str(browser))
        version = instance.version
        instance.close()
    environment = {
        "python": platform.python_version(), "platform": platform.platform(),
        "playwright": importlib.metadata.version("playwright"),
        "pytest": importlib.metadata.version("pytest"),
        "chrome_path": str(browser), "chrome_version": version,
        "browser_required": True, "docker_enabled": False,
        "dxadom_discovery": "explicit browser prepended to hints before collection",
    }
    (here / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    import pytest
    return pytest.main([
        "tools/dom-xss-analyzer", "bench", "-q", "-r", "a",
        "-p", "no:cacheprovider", "--tb=short", "--junitxml=" + str(here / args.junit),
    ])


if __name__ == "__main__":
    raise SystemExit(main())
