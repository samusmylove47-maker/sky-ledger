#!/usr/bin/env python3
"""make_real.py -- regenerate fixtures/real-report-shara.json BY RUNNING THE ENGINE.

WHY THIS EXISTS. `real-report-shara.json` was a committed artifact that no tool
produced. `make_fixture.py` regenerates the SYNTHETIC fixture on every run of the
drift gate; its real-log counterpart was written once, by hand, from a run that
was current that day.

Measured 1 Sep 2026: the committed file still carried

    "months_seen": ["Aug"]

-- the LIST. That is the exact defect B's hand-written contract caught on 31 Aug
("int, distinct calendar months... a STALENESS SIGNAL"), which I fixed in both
engines the same night. The fix never reached this file, and `check_drift.py`
compares KEY SETS, so `months_seen` was present in both and the gate read clean
for a day while the artifact carried the shape the contract rejects.

A staleness signal that is itself stale. The fix is the same one make_fixture.py
already applies to the synthetic side and for the same reason: there is one
producer, so there is nothing to drift from.

    python3 fixtures/make_real.py
"""
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
LOG = os.path.join(ROOT, "corpus", "amp", "eqlog_Shara_rivervale_20260829_full.txt")
OUT = os.path.join(ROOT, "fixtures", "real-report-shara.json")

from gapengine import gap_engine

if __name__ == "__main__":
    # R73, adopted 1 Sep 2026 from the Director: a command that reads a file set
    # states the count it actually opened. One file, named, with its size -- so a
    # truncated or substituted log cannot regenerate this artifact unnoticed.
    with io.open(LOG, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    print(f"read 1 file: {os.path.relpath(LOG, ROOT)}  "
          f"{os.path.getsize(LOG)} bytes, {len(lines)} lines")
    rep = gap_engine(lines, {"source": "local log, not transmitted"})
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1); fh.write("\n")
    m = rep["measured"]
    print(f"wrote {os.path.relpath(OUT, ROOT)}  dps={m['dps']} engaged={m['engaged_seconds']}s "
          f"months_seen={m['months_seen']!r} deltas={len(rep['deltas'])} "
          f"refusals={len(rep['refusals'])}")
