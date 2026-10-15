"""Budget and result-accounting regressions for the R4 comparator."""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from r4_compare_local import _classify_run


@pytest.mark.parametrize("args,expected", [
    ((0, False, False, [], 1), "completed"),
    ((0, True, True, [], 20), "timeout"),
    ((1, False, False, [], 1), "error"),
    ((1, False, False, [{"reflection": "unencoded"}], 1), "completed"),
    ((0, False, True, [], 2), "incomplete"),
    ((0, False, False, None, 1), "incomplete"),
])
def test_run_accounting_never_promotes_errors_or_budget_violations(args, expected):
    assert _classify_run(*args) == expected
