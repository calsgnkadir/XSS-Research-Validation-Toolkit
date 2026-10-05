"""Persistent stored blind attempts; callbacks are network evidence, never JS proof."""
import argparse
import dxa_evidence as evidence
import json
import math
from pathlib import Path
import sqlite3
import time
import urllib.parse
import urllib.request
import uuid


def callback_base(url):
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme not in ("http", "https") or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError("callback must be an HTTP(S) base URL without credentials, query or fragment")
    return url.rstrip("/")


def private_url(url):
    """Keep the route, omit credentials, query values and fragments."""
    p = urllib.parse.urlsplit(url)
    host = p.netloc.rsplit("@", 1)[-1]
    query = urllib.parse.urlencode([(k, "[redacted]") for k, _ in
                                   urllib.parse.parse_qsl(p.query, keep_blank_values=True)])
    return urllib.parse.urlunsplit((p.scheme, host, p.path, query, ""))


def candidate(cid, variant, target, field, method, role="unspecified"):
    return {"schema_version": 1, "attempt_id": uuid.uuid4().hex,
            "canary_id": cid, "variant": variant, "target": private_url(target),
            "field": field, "method": method.upper(), "session_role": role,
            "created_at": time.time(), "submission_state": "prepared",
            "sub_status": None, "check_status": None, "check_url": "",
            "reflection": "not-observed", "context": "unknown",
            "severity": "candidate", "evidence_level": "candidate",
            "triage": "unreviewed", "callback_state": "not-queried"}


class AttemptJournal:
    """A committed pre-send record survives process exit. No payload/auth storage.

    Connections are short-lived: worker threads never share a connection.
    A unique cid constraint prevents ambiguous correlation within one journal.
    """
    def __init__(self, path, callback, role="unspecified", *, existing=False):
        self.path = Path(path)
        self.callback = callback_base(callback)
        self.role = role
        self.run_id = uuid.uuid4().hex
        if existing and not self.path.is_file():
            raise ValueError("blind journal does not exist")
        if not existing:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ValueError("unsupported blind journal schema")
            if existing and version != 1:
                raise ValueError("not a version 1 blind journal")
            db.execute("CREATE TABLE IF NOT EXISTS attempts "
                       "(cid TEXT PRIMARY KEY, run_id TEXT NOT NULL, "
                       "callback TEXT NOT NULL, record TEXT NOT NULL)")
            db.execute("PRAGMA user_version=1")

    def _connect(self):
        # sqlite Connection's context manager commits but does not close.
        from contextlib import contextmanager

        @contextmanager
        def connection():
            db = sqlite3.connect(self.path, timeout=30)
            try:
                with db:
                    yield db
            finally:
                db.close()
        return connection()

    def begin(self, row):
        row.update(run_id=self.run_id, session_role=self.role)
        with self._connect() as db:
            db.execute("INSERT INTO attempts VALUES (?,?,?,?)",
                       (row["canary_id"], self.run_id, self.callback, json.dumps(row)))

    def submission(self, row, status, state):
        row.update(sub_status=status, submission_state=state, submitted_at=time.time())
        # Merge only submission metadata: don't erase a concurrent reconciliation.
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            saved = json.loads(db.execute("SELECT record FROM attempts WHERE cid=?",
                                          (row["canary_id"],)).fetchone()[0])
            for key in ("sub_status", "submission_state", "submitted_at"):
                saved[key] = row[key]
            db.execute("UPDATE attempts SET record=? WHERE cid=?",
                       (json.dumps(saved), row["canary_id"]))

    def records(self, run_id=None):
        with self._connect() as db:
            rows = db.execute("SELECT record FROM attempts WHERE callback=? "
                              "AND (? IS NULL OR run_id=?) ORDER BY rowid",
                              (self.callback, run_id, run_id)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def observe(self, cid, hit):
        """Persist a scan-time hit only when identity and time match this attempt."""
        if not isinstance(hit, dict) or hit.get("cid") != cid:
            return False
        ts = hit.get("ts")
        if not isinstance(ts, (int, float)) or not math.isfinite(ts):
            return False
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            result = db.execute("SELECT record FROM attempts WHERE cid=? AND callback=?",
                                (cid, self.callback)).fetchone()
            if not result:
                return False
            row = json.loads(result[0])
            if not row["created_at"] <= ts <= time.time() + 5:
                return False
            row.update(evidence_level="resource-callback", severity="resource-callback",
                       callback_state="matched", hit_at=ts, last_checked_at=time.time())
            db.execute("UPDATE attempts SET record=? WHERE cid=?", (json.dumps(row), cid))
        return True

    def reconcile(self, run_id=None, timeout=2):
        """One bounded lookup per cid, no target visits or resubmission.

        HTTP and malformed responses remain query-error, distinct from no-hit.
        Timestamps use the callback server clock; synchronized clocks required.
        """
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("lookup timeout must be finite and positive")
        for row in self.records(run_id):
            state, observed = "no-hit", None
            try:
                cid = row["canary_id"]
                url = self.callback + "/hits/" + urllib.parse.quote(cid, safe="")
                with urllib.request.urlopen(url, timeout=timeout) as response:
                    payload = json.load(response)
                hits = payload["hits"]
                if not isinstance(hits, list) or any(not isinstance(h, dict) for h in hits):
                    raise ValueError("malformed hits")
                matches = [h for h in hits if h.get("cid") == cid
                           and isinstance(h.get("ts"), (int, float))
                           and math.isfinite(h["ts"])
                           and row["created_at"] <= h["ts"] <= time.time() + 5]
                if matches:
                    observed = min(matches, key=lambda h: h["ts"])
                    state = "matched"
            except (OSError, ValueError, KeyError, TypeError):
                state = "query-error"
            with self._connect() as db:
                # Re-read to preserve submission updates and previous evidence.
                db.execute("BEGIN IMMEDIATE")
                saved = json.loads(db.execute("SELECT record FROM attempts WHERE cid=?",
                                              (row["canary_id"],)).fetchone()[0])
                saved.update(callback_state=state, last_checked_at=time.time())
                if observed:
                    saved.update(evidence_level="resource-callback",
                                 severity="resource-callback", hit_at=observed["ts"])
                db.execute("UPDATE attempts SET record=? WHERE cid=?",
                           (json.dumps(saved), row["canary_id"]))
        return self.records(run_id)


def render_report(records):
    return evidence.render_report(journal_report(records))


def journal_report(records):
    events = []
    for record in records:
        state = record.get("callback_state", "not-queried")
        events.append(evidence.ReportEvent("callback", "error" if state == "query-error" else "info",
                                           state, canary_id=record["canary_id"]))
        status = record.get("sub_status")
        if record.get("submission_state") in ("error", "prepared") or (status and status >= 400):
            events.append(evidence.ReportEvent("submission", "error" if not status or status >= 500 else "skip",
                                               record["submission_state"], record.get("target", ""),
                                               status, record["canary_id"]))
    return evidence.report(records, "blind-reconcile", events)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal", required=True)
    parser.add_argument("--blind-callback", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--timeout", type=float, default=2)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--html")
    args = parser.parse_args(argv)
    try:
        paths = [Path(p).resolve() for p in (args.journal, args.json_out, args.html) if p]
        if len(set(paths)) != len(paths):
            raise ValueError("journal and report paths must be distinct")
        journal = AttemptJournal(args.journal, args.blind_callback, existing=True)
        records = journal.reconcile(args.run_id, args.timeout)
        document = journal_report(records)
        document["attempts"] = document["findings"]  # compatibility alias, same objects
        Path(args.json_out).write_text(json.dumps(document,
                                                indent=2), encoding="utf-8")
        if args.html:
            Path(args.html).write_text(evidence.render_report(document), encoding="utf-8")
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.error(str(exc))
    print(f"{len(records)} attempt(s); "
          f"{sum(r['evidence_level'] == 'resource-callback' for r in records)} callback(s); "
          "JavaScript execution not established")
    return 2 if any(r["callback_state"] == "query-error" for r in records) else 0


if __name__ == "__main__":
    raise SystemExit(main())
