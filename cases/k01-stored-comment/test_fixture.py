"""HTTP regression: separate submission/read requests preserve text after fixing."""
import html
import urllib.parse
import urllib.request

import pytest
from prove import fixture, fixed, vulnerable


@pytest.mark.parametrize("renderer,escaped", [(vulnerable, False), (fixed, True)])
def test_stored_read_in_separate_request_preserves_expected_representation(renderer, escaped):
    value = 'örnek & <img src=x onerror="window.test=1">'
    with fixture(renderer) as (base, handler):
        with urllib.request.urlopen(base + "/comments", data=urllib.parse.urlencode({"comment": value}).encode()) as response:
            assert response.status == 201
        with urllib.request.urlopen(base + "/comments") as response:
            body = response.read().decode()
        assert (html.escape(value, quote=True) if escaped else value) in body
        assert handler.posts == 1
        if escaped:
            assert '<img src=' not in body
