"""Independent writer/admin login sessions for the bounded R4 scanner fixture."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import urllib.error
import urllib.request


@dataclass(frozen=True)
class ScannerSessions:
    writer_principal: str
    writer_token: str
    admin_principal: str
    admin_token: str

    @property
    def cookie_header(self) -> str:
        if not self.writer_token or not self.admin_token or self.writer_token == self.admin_token:
            raise ValueError("independent writer and reader-admin sessions required")
        return f"writer_session={self.writer_token}; admin_session={self.admin_token}"

    def public_record(self, checks: dict[str, dict]) -> dict:
        """Expose role proof while keeping cookie material out of evidence."""
        return {
            "writer": {"principal_sha256": hashlib.sha256(self.writer_principal.encode()).hexdigest(),
                       "role": "writer", "pre": checks.get("writer_pre", {}).get("passed", False),
                       "post": checks.get("writer_post", {}).get("passed", False)},
            "reader_admin": {
                "principal_sha256": hashlib.sha256(self.admin_principal.encode()).hexdigest(),
                "role": "reader-admin", "pre": checks.get("reader-admin_pre", {}).get("passed", False),
                "post": checks.get("reader-admin_post", {}).get("passed", False)},
            "independent_tokens": bool(self.writer_token and self.admin_token
                                        and self.writer_token != self.admin_token),
            "cookie_values_recorded": False,
        }


def provision_scanner_sessions(fixture) -> ScannerSessions:
    """Log in twice through the fixture and require distinct role credentials."""
    writer, writer_token = fixture.login("writer")
    admin, admin_token = fixture.login("reader-admin")
    sessions = ScannerSessions(writer, writer_token, admin, admin_token)
    # Force invariant validation before passing credentials to a scanner.
    sessions.cookie_header
    return sessions


def check_scanner_sessions(fixture, sessions: ScannerSessions, phase: str) -> dict:
    if phase not in {"pre", "post"}:
        raise ValueError("phase must be pre or post")
    return {
        f"writer_{phase}": fixture.session_check("writer", sessions.writer_token),
        f"reader-admin_{phase}": fixture.session_check("reader-admin", sessions.admin_token),
    }


def check_role_boundaries(fixture, sessions: ScannerSessions) -> dict:
    """Exercise four forbidden role uses; all requests count in the fixture budget."""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    checks = (
        ("writer_cannot_read_admin", "/admin/comments",
         f"writer_session={sessions.writer_token}", "GET", None),
        ("reader_admin_cannot_submit", "/comments",
         f"admin_session={sessions.admin_token}", "POST", b"comment=role-boundary-control"),
        ("admin_token_rejected_as_writer", "/session/writer",
         f"writer_session={sessions.admin_token}", "GET", None),
        ("writer_token_rejected_as_admin", "/session/reader-admin",
         f"admin_session={sessions.writer_token}", "GET", None),
    )
    results = {}
    for label, path, cookie, method, body in checks:
        request = urllib.request.Request(fixture.origin + path, data=body, method=method,
                                         headers={"Cookie": cookie})
        try:
            with opener.open(request, timeout=3) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
        except (urllib.error.URLError, TimeoutError):
            status = None
        expected = 401 if label.endswith(("read_admin", "cannot_submit")) else 403
        results[label] = {"status": status, "passed": status == expected,
                          "expected_status": expected}
    return results
