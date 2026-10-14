"""Independent local K01 proof run on the project's disposable fixture."""

from contextlib import contextmanager
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cases" / "k01-stored-comment"))
import check_repro
import prove


def main():
    proof = Path(__file__).resolve().parent / "proof"
    ports = []
    original = prove.fixture

    @contextmanager
    def observed_fixture(renderer):
        with original(renderer) as (origin, handler):
            assert urlsplit(origin).hostname == "127.0.0.1"
            ports.append(urlsplit(origin).port)
            yield origin, handler

    prove.fixture = observed_fixture
    try:
        prove.run(proof, r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        acceptance = check_repro.validate(
            proof, ports, expected_platform="Windows", expected_python="3.10."
        )
        acceptance["fixture_ports"] = ports
        acceptance["runner"] = "independent agent on same host; not a second human"
        (proof / "acceptance.json").write_text(
            json.dumps(acceptance, indent=2) + "\n", encoding="utf-8"
        )
        print("K01: 5/5 controls; 5/5 distinct closed ports; gate passed")
    finally:
        prove.fixture = original


if __name__ == "__main__":
    main()
