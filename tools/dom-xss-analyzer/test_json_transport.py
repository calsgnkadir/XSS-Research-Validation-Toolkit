"""R2: JSON canaries survive encoding without mutating shared headers."""
from concurrent.futures import ThreadPoolExecutor
import json
import threading

import pytest

import dxadyn


def test_all_payload_shapes_round_trip_through_actual_submit(monkeypatch):
    captured = []

    def receive(url, body, method="POST"):
        captured.append(json.loads(body))
        return 200, url, "", "application/json"

    monkeypatch.setattr(dxadyn, "_fetch_json", receive)
    shapes = list(dxadyn.make_canaries_for(list(dxadyn.PAYLOAD_VARIANTS), waf_bypass=True))
    assert len(shapes) == 950
    for variant, cid, canary, marker in shapes:
        assert dxadyn._submit_json("http://127.0.0.1/test", '{"value":"{CANARY}"}', canary)[0] == 200
        assert captured[-1]["value"] == canary, variant


def test_nested_values_keys_and_control_characters_round_trip(monkeypatch):
    captured = []
    monkeypatch.setattr(dxadyn, "_fetch_json", lambda url, body, method:
                        (captured.append((json.loads(body), method)) or (200, url, "", "application/json")))
    canary = '\x00\t\r\n\b\f"\\ç😀'
    template = '{"nested":["prefix{CANARY}suffix",true,null,42],"{CANARY}":"{CANARY}"}'
    dxadyn._submit_json("http://127.0.0.1/test", template, canary, method="PATCH")
    payload, method = captured[0]
    assert payload == {"nested": ["prefix" + canary + "suffix", True, None, 42], canary: canary}
    assert method == "PATCH"


@pytest.mark.parametrize("template", ['{"value":{CANARY}}', '{"value":"unfinished}', '{"value":NaN}'])
def test_invalid_json_never_reaches_transport(monkeypatch, template):
    def unexpected(*args, **kwargs):
        pytest.fail("Invalid JSON was submitted")
    monkeypatch.setattr(dxadyn, "_fetch_json", unexpected)
    with pytest.raises(ValueError):
        dxadyn._submit_json("http://127.0.0.1/test", template, "canary")


def test_key_collision_is_rejected_before_submission(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("A key collision silently discarded data")
    monkeypatch.setattr(dxadyn, "_fetch_json", unexpected)
    with pytest.raises(ValueError, match="duplicate keys"):
        dxadyn._submit_json("http://127.0.0.1/test", '{"{CANARY}":1,"same":2}', "same")


def test_overlapping_json_requests_do_not_mutate_shared_headers(monkeypatch):
    shared = {"Content-Type": "text/plain", "Authorization": "test-placeholder"}
    monkeypatch.setattr(dxadyn, "EXTRA_HEADERS", shared.copy())
    both_running = threading.Barrier(2)

    def receive(url, data, method, extra=None):
        both_running.wait(timeout=5)
        assert dxadyn.EXTRA_HEADERS == shared
        assert extra == {"Content-Type": "application/json"}
        return 200, url, "", "application/json"

    monkeypatch.setattr(dxadyn, "fetch", receive)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(dxadyn._fetch_json, "http://127.0.0.1/test", b'{}') for _ in range(2)]
        assert all(future.result()[0] == 200 for future in futures)
    assert dxadyn.EXTRA_HEADERS == shared
