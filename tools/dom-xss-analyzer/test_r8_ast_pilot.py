"""Small labeled corpus for the bounded Python AST pilot (R8)."""
import dxa
import pytest


CORPUS = [
    {
        "id": "py-tuple-unpack-source-positive",
        "label": "positive",
        "source": (
            'untrusted, label = (request.args.get("q"), "search")\n'
            'HTMLResponse(untrusted)\n'
        ),
        "expected_high": True,
    },
    {
        "id": "py-source-text-in-string-negative",
        "label": "negative",
        "source": (
            'literal = "request.args.get(\\\'q\\\')"\n'
            'HTMLResponse(literal)\n'
        ),
        "expected_high": False,
    },
]


def scan_corpus_case(tmp_path, case):
    path = tmp_path / (case["id"] + ".py")
    path.write_text(case["source"], encoding="utf-8")
    return [row for row in dxa.scan_file(str(path))
            if row["sink"] == "fastapi-html"]


@pytest.mark.parametrize("case", CORPUS, ids=lambda case: case["id"])
def test_labeled_python_ast_pilot_cases(tmp_path, case):
    """Each label asserts one narrow source-flow behavior, not general accuracy."""
    findings = scan_corpus_case(tmp_path, case)
    observed_high = any(row["confidence"] == "high" for row in findings)
    assert observed_high is case["expected_high"], case["id"]


def test_python_ast_pilot_labeled_corpus_measurement(tmp_path):
    """Report simple confusion counts for the declared two-case corpus."""
    outcomes = {case["id"]: any(row["confidence"] == "high"
                                for row in scan_corpus_case(tmp_path, case))
                for case in CORPUS}
    tp = sum(outcomes[case["id"]] for case in CORPUS if case["label"] == "positive")
    fp = sum(outcomes[case["id"]] for case in CORPUS if case["label"] == "negative")
    fn = sum(not outcomes[case["id"]] for case in CORPUS if case["label"] == "positive")
    tn = sum(not outcomes[case["id"]] for case in CORPUS if case["label"] == "negative")
    assert (tp, fp, fn, tn) == (1, 0, 0, 1)
