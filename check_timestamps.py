#!/usr/bin/env python3
"""check_timestamps.py -- every log-line timestamp pattern in this tree must accept a
SPACE-PADDED single-digit day.

WHY THIS IS A BEHAVIOURAL TEST AND NOT A GREP. Two hand-sweeps for this fault ran on
1 Sep 2026 and both were defective:

  - The Director's first sweep was a DEAD INSTRUMENT: it returned zero hits in every
    repository, which reads as "everyone is safe".
  - Mine matched on the literal `\\w{3} \\w{3} (\\d{2})` and therefore MISSED
    `amp.py:11`, which wrote the same fault as `(\\w{3} \\d{2})` -- the day inside the
    month-day capture. My probe for the fault had the same brittleness as the fault.

So this file does not look for a shape. **It extracts every timestamp-looking regex
in the tree and RUNS it against a space-padded line.** A pattern written any way at
all is caught, because the test is the input, not the spelling.

THE CLAIM UNDER TEST IS NOT THAT EQ LEGENDS SPACE-PADS. That is unverified -- see
gapengine.py's TS. The claim is that a parser should not CARE, because tolerance
costs one character and a fixed-width day silently discards the line before any
parse, where no instrument downstream can report it.

    python3 check_timestamps.py
    python3 check_timestamps.py --selftest
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "__pycache__", "node_modules", "corpus", ".github"}

PADDED = "[Sun Sep  1 00:00:00 2026] You slash a rat for 5 points of damage."
ZEROED = "[Sat Aug 29 00:00:00 2026] You slash a rat for 5 points of damage."

# A timestamp pattern, for this purpose, is a regex anchored at `^\[` that names a
# three-letter token -- the weekday. Deliberately loose: the point is to over-collect
# and then TEST, not to decide by inspection which ones matter.
PY_RE = re.compile(r're\.compile\(\s*r?"((?:[^"\\]|\\.)*)"', re.S)
JS_RE = re.compile(r'=\s*/((?:[^/\\\n]|\\.)+)/[gimsuy]*\s*;')


# A pattern may declare itself a deliberate control rather than a parser, by carrying
# this marker on its own line or the line above. ADDED because the sweep's FIRST RUN
# failed on its own known-bad control, which is a true positive on a false target:
# the extractor found a STRING and reported it as a PARSER. R80's shape again -- a
# lookup that succeeds on a name and returns a false answer about a role.
# The exemption is explicit, greppable, and counted, and `audit` asserts it stays
# rare rather than becoming a way to quiet the gate.
EXEMPT = "TIMESTAMP-EXEMPT"


def candidates(read, walk):
    """Return ([(path, pattern)], [(path, pattern)]) -- tested, and exempt."""
    out, exempt = [], []
    for path in walk():
        body = read(path)
        if body is None:
            continue
        lines = body.split("\n")
        pats = PY_RE.finditer(body) if path.endswith(".py") else JS_RE.finditer(body)
        for m in pats:
            p = m.group(1)
            if not (p.startswith(r"^\[") and r"\w{3}" in p):
                continue
            n = body[:m.start()].count("\n")           # 0-based line of the match
            near = "\n".join(lines[max(0, n - 1):n + 1])
            (exempt if EXEMPT in near else out).append((path, p))
    return out, exempt


def audit(cands, exempt=()):
    out = []
    # The exemption must stay a rarity that is read, not a switch that is used. Two
    # is the count today: the known-bad control below, and nothing else.
    out.append(("deliberate-control exemptions stay rare and named", len(exempt) <= 2,
                f"{len(exempt)} exempt: {[p for p, _ in exempt]}"))
    # POSITIVE CONTROL FIRST, because a sweep that finds nothing passes every check
    # below it vacuously -- which is exactly how the Director's first sweep read as a
    # clean bill of health for four repositories.
    out.append(("the sweep found timestamp patterns at all", len(cands) >= 3,
                f"{len(cands)} found: {sorted({p for p, _ in cands})}"))
    # ...and that the harness can tell a bad pattern from a good one.
    # TIMESTAMP-EXEMPT: a deliberate fixed-width pattern, the harness's own control.
    bad = re.compile(r"^\[\w{3} \w{3} (\d{2}) (\d{2}):(\d{2}):(\d{2}) \d{4}\] (.*)$")
    out.append(("the harness rejects a known-bad pattern",
                bool(bad.match(ZEROED)) and not bad.match(PADDED),
                "a fixed-width day matches the zero-padded line and not the padded one"))
    for path, src in sorted(cands):
        try:
            rx = re.compile(src)
        except re.error as e:
            out.append((f"{path}: pattern compiles", False, str(e))); continue
        out.append((f"{path}: accepts a SPACE-PADDED day", bool(rx.match(PADDED)),
                    f"pattern {src[:52]}"))
        out.append((f"{path}: still accepts a zero-padded day", bool(rx.match(ZEROED)),
                    f"pattern {src[:52]}"))
    return out


def walker():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith((".py", ".js")):
                yield os.path.relpath(os.path.join(base, f), ROOT)


def reader(path):
    p = os.path.join(ROOT, path)
    try:
        return io.open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def show(rows):
    bad = 0
    for n, ok, d in rows:
        print(f"  [{'ok' if ok else 'FAIL'}] {n}" + ("" if ok else f"  -- {d}"))
        bad += 0 if ok else 1
    return bad


if __name__ == "__main__":
    files = sorted(walker())
    # R73: the file set actually opened, not the one intended.
    print(f"read {len(files)} .py/.js file(s) under {os.path.basename(ROOT)}/ "
          f"(skipping {sorted(SKIP_DIRS)})")
    cands, exempt = candidates(reader, walker)

    if "--selftest" not in sys.argv:
        bad = show(audit(cands, exempt))
        print(f"  {len(audit(cands, exempt))} checks over {len(cands)} pattern(s), "
              f"{len(exempt)} exempt, {bad} failing")
        sys.exit(1 if bad else 0)

    print("SELFTEST -- the sweep must fail on a bad pattern and on its own blindness")
    if show(audit(cands, exempt)):
        print("  the real tree does not pass"); sys.exit(1)
    print(f"  the real tree passes, {len(cands)} patterns")
    bad = 0

    # 1. A file carrying the fixed-width day must be caught -- INCLUDING the shape my
    #    own hand-grep missed, where the day sits inside the month-day capture.
    for label, pat in (("plain fixed-width day",
                        r"^\[\\w{3} \\w{3} (\\d{2}) (\\d{2}):(\\d{2}):(\\d{2}) \\d{4}\\] (.*)$"),
                       ("day inside the month-day capture (amp.py's shape)",
                        r"^\[\\w{3} (\\w{3} \\d{2}) (\\d{2}):(\\d{2}):(\\d{2}) (\\d{4})\\] (.*)$")):
        injected = cands + [("INJECTED.py", pat.replace("\\\\", "\\"))]
        names = {n for n, ok, _ in audit(injected, exempt) if not ok}
        ok = "INJECTED.py: accepts a SPACE-PADDED day" in names
        print(f"  [{'ok' if ok else 'FAIL'}] a {label} is caught")
        bad += 0 if ok else 1

    # 2. A DEAD SWEEP must be caught. This is the Director's failure and the reason
    #    the control is the first check rather than a footnote.
    names = {n for n, ok, _ in audit([], exempt) if not ok}
    ok = "the sweep found timestamp patterns at all" in names
    print(f"  [{'ok' if ok else 'FAIL'}] a sweep that finds NOTHING is caught, not read as clean")
    bad += 0 if ok else 1

    # 3. The extractor must actually reach both languages, or a whole language could
    #    go unswept while the count still looks healthy.
    langs = {os.path.splitext(p)[1] for p, _ in cands}
    ok = {".py", ".js"} <= langs
    print(f"  [{'ok' if ok else 'FAIL'}] the extractor reaches both languages  -- found {sorted(langs)}")
    bad += 0 if ok else 1

    # 4. The exemption must not become a quiet switch.
    names = {n for n, ok, _ in audit(cands, exempt + [("X.py", "p"), ("Y.py", "p")]) if not ok}
    ok = "deliberate-control exemptions stay rare and named" in names
    print(f"  [{'ok' if ok else 'FAIL'}] a growing exemption list is caught, not absorbed")
    bad += 0 if ok else 1

    print(f"  {bad} self-test checks failed")
    sys.exit(1 if bad else 0)
