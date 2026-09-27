"""pytest bootstrap for the tools/dom-xss-analyzer test suite.

CI runs `pytest -q` from THIS directory, which puts the current
directory on sys.path but NOT the repo root. A couple of integration
tests reach out to the top-level `bench` package (the shared benchmark
harness) - without this shim they hit ModuleNotFoundError.

Adding the repo root to sys.path is scoped to test collection; the
runtime tool code (dxadyn.py, dxadom.py) never depends on this shim
because it doesn't import `bench`.
"""
from __future__ import annotations
import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_ROOT_STR = str(_REPO_ROOT)
if _ROOT_STR not in sys.path:
    sys.path.insert(0, _ROOT_STR)
