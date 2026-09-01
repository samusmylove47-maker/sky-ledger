#!/usr/bin/env python3
"""check_unreported.py -- every row of docs/UNREPORTED-FINDINGS.md must still be true
of the tree it describes.

An index of findings is an artifact nothing produces, which is precisely the shape
that went stale in `fixtures/real-report-shara.json` and sat inside the drift gate
for a day. So this file's rows carry VERBATIM FRAGMENTS from the source, and this
gate fails when a fragment is gone -- the code moved and the index did not.

    python3 check_unreported.py
    python3 check_unreported.py --selftest
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(ROOT, "docs", "UNREPORTED-FINDINGS.md")

# (file, verbatim fragment that must appear in it). One per table row, in order.
ROWS = [
    ("gapengine.py",              "38% over-marked"),
    ("gapengine.py",              "3.7% of a character's apparent total until excluded"),
    ("bard.py",                   "92,822 points"),
    ("gapengine.py",              "the two differ by 2.3x and the reported gap by 3x"),
    ("gapengine.py",              "lands 46 times at 1864-1924"),
    ("gapengine.py",              "reported a 100% RESIST RATE"),
    ("model4.py",                 "cap is INERT"),
    ("bundle/check-integrity.py", "that mechanism does not fit THIS file"),
    ("bundle/check-integrity.py", "22403 vs 0 bytes"),
    ("gapengine.py",              "it labelled 64.2% as Balanced"),
]


def audit(read):
    """Pure but for the injected reader. Returns [(name, ok, detail)]."""
    out = []
    for i, (path, frag) in enumerate(ROWS, 1):
        body = read(path)
        if body is None:
            out.append((f"row {i}: {path}", False, "file does not exist")); continue
        n = body.count(frag)
        line = body[:body.index(frag)].count("\n") + 1 if n else None
        out.append((f"row {i}: {path}", n >= 1,
                    f"{path}:{line} carries it" if n else f"fragment absent: {frag!r}"))
    doc = read(os.path.relpath(DOC, ROOT))
    rows_in_doc = len(re.findall(r"^\| \d+ \|", doc or "", re.M))
    out.append(("the table has one row per checked fragment", rows_in_doc == len(ROWS),
                f"{rows_in_doc} table rows vs {len(ROWS)} fragments"))
    return out


def reader(path):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        return None
    return io.open(p, encoding="utf-8").read()


if __name__ == "__main__":
    # R73: state the file set actually opened.
    files = sorted({p for p, _ in ROWS} | {os.path.relpath(DOC, ROOT)})
    print(f"read {len(files)} file(s): {files}")

    if "--selftest" not in sys.argv:
        rows = audit(reader)
        bad = 0
        for n, ok, d in rows:
            print(f"  [{'ok' if ok else 'FAIL'}] {n:<34} {d}")
            bad += 0 if ok else 1
        print(f"  {len(rows)} checks, {bad} failing")
        sys.exit(1 if bad else 0)

    print("SELFTEST -- a fragment removed from the source must trip its own row")
    if any(not ok for _, ok, _ in audit(reader)):
        print("  the unmutated tree does not pass"); sys.exit(1)
    print("  unmutated tree passes")
    bad = 0
    for i, (path, frag) in enumerate(ROWS, 1):
        def r(p, _path=path, _frag=frag):
            b = reader(p)
            return b.replace(_frag, "") if (b and p == _path) else b
        names = {n for n, ok, _ in audit(r) if not ok}
        want = f"row {i}: {path}"
        ok = want in names
        print(f"  [{'ok' if ok else 'FAIL'}] removing {frag[:40]!r:<44} trips {want!r}")
        bad += 0 if ok else 1
    # and the doc's own row count
    def rdoc(p):
        b = reader(p)
        return re.sub(r"^\| 10 \|.*$", "", b, flags=re.M) if p.endswith("UNREPORTED-FINDINGS.md") else b
    ok = "the table has one row per checked fragment" in {n for n, o, _ in audit(rdoc) if not o}
    print(f"  [{'ok' if ok else 'FAIL'}] deleting a table row trips the row-count check")
    bad += 0 if ok else 1
    print(f"  {bad} mutations failed to trip their check")
    sys.exit(1 if bad else 0)
