"""Sharing copies redact known credentials without promoting or mutating evidence."""
from copy import deepcopy
import html
import json

import pytest

import dxa_evidence as evidence


@pytest.mark.parametrize("key", [
    "api_key", "API-KEY", "apiKey", "X-API-Key", "access_token",
    "refresh_token", "id_token", "client_secret", "csrf_token",
    "csrfmiddlewaretoken", "authenticity_token", "_token", "tokenCSRF",
    "X-CSRF-Token", "X-XSRF-Token", "Set-Cookie", "Proxy-Authorization",
    "Authorization", "cookies", "password",
])
def test_known_credential_fields_are_redacted_in_sharing_copies(key):
    secret = "FAKE-PRIVATE-VALUE-DO-NOT-EXPORT"
    row = {"finding_id": "privacy-one", "evidence_level": "reflection",
           "observations": [{"response": {key: {"nested": [secret]}}}]}
    before = deepcopy(row)
    document = evidence.report([row], "fixture", meta={key: secret})
    exported = json.dumps(document)
    page = evidence.render_report(document)
    assert secret not in exported
    assert secret not in page
    assert document["findings"][0]["observations"][0]["response"][key] == "[redacted]"
    assert document["meta"][key] == "[redacted]"
    assert document["findings"][0]["evidence_level"] == "reflection"
    assert document["findings"][0]["triage"] == "unreviewed"
    assert document["findings"][0]["role_verified"] is False
    assert row == before


def test_evidence_links_preserve_location_but_remove_url_credentials():
    links = ["https://alice:FAKE_PASS@lab.test/proof?token=FAKE_QUERY#FAKE_FRAGMENT",
             "http://[::1]:8080/proof?empty=&q=FAKE_SECOND",
             "cases/local-proof.json"]
    row = {"finding_id": "privacy-links", "evidence_links": links}
    before = deepcopy(row)
    document = evidence.report([row], "fixture")
    expected = ["https://lab.test/proof?token=%5Bredacted%5D",
                "http://[::1]:8080/proof?empty=%5Bredacted%5D&q=%5Bredacted%5D",
                "cases/local-proof.json"]
    assert document["findings"][0]["evidence_links"] == expected
    assert document["findings"][0]["observations"][0]["evidence_links"] == expected
    for output in (json.dumps(document), evidence.render_report(document)):
        for secret in ("alice", "FAKE_PASS", "FAKE_QUERY", "FAKE_FRAGMENT", "FAKE_SECOND"):
            assert secret not in output
    assert row == before


def test_url_field_case_and_event_url_are_consistently_redacted():
    url = "https://u:FAKE_PASS@lab.test/a?auth=FAKE_QUERY#FAKE_FRAGMENT"
    row = {"finding_id": "privacy-urls", "observations": [{"URL": url, "Read_URL": url}]}
    event = evidence.ReportEvent("http", "error", "request-failed", url=url, status=403)
    document = evidence.report([row], "fixture", events=[event])
    expected = "https://lab.test/a?auth=%5Bredacted%5D"
    assert document["findings"][0]["observations"] == [{"URL": expected, "Read_URL": expected}]
    assert document["events"][0]["url"] == expected
    assert document["events"][0]["kind"] == "error"
    assert document["events"][0]["status"] == 403
    assert event.url == url


def test_noncredential_metadata_and_html_escaping_are_preserved():
    row = {"finding_id": "<script>fixture</script>", "canary_id": "cid-one",
           "observations": [{"csrf_field": "csrf_token", "token_count": 2,
                             "api_key_name": "X-API-Key", "session_check": "passed"}]}
    document = evidence.report([row], "fixture")
    assert document["findings"][0]["observations"] == row["observations"]
    page = evidence.render_report(document)
    assert "<script>fixture</script>" not in page
    assert html.escape(row["finding_id"]) in page
    assert document["findings"][0]["canary_id"] == "cid-one"
    assert evidence.clean(document) == document
