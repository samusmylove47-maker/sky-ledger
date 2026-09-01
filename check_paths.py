#!/usr/bin/env python3
"""check_paths.py -- no committed file may hard-code an absolute path outside itself.

MEASURED, 1 Sep 2026, not reasoned about. `model4.py` carried
`REPO="/home/user/sky-ledger"`, and a fresh clone with ZERO shard files of its own
imported it successfully and loaded 515 weapons and 1,973 spells -- every one of them
from that absolute path, not from the clone.

THE PART THAT MATTERS IS NOT THE PORTABILITY. It is that `fetch_shards.py` fetches the
three shards INTO THE CLONE and verifies them against their pins, and `model4.py` then
read a different copy. **A gate that verifies bytes the consumer does not use.** Green
the whole time, on both machines, for days.

`verify_upgrade.py:20` has always used `os.path.dirname(os.path.abspath(__file__))`.
Two files, one repository, two conventions for the same constant -- and the hard-coded
one is the one every published weapon figure went through.

A path may be exempt when it is a genuine EXTERNAL dependency with no in-repo source,
and then it must say so on its own line or the line above. The exemption is counted and
capped, because an exemption nobody counts is a way to quiet a gate.

    python3 check_paths.py
    python3 check_paths.py --selftest
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "__pycache__", "node_modules", "corpus", "handover", "docs"}
EXEMPT = "ABSOLUTE-PATH-EXEMPT"
# TARGET AN ASSIGNMENT, NOT ANY LITERAL. The first version matched every string
# beginning with an absolute root, and its first run flagged four lines -- three of
# them its OWN docstring and control probe, and one a COMMENT in model4.py describing
# the value that had just been removed. It found STRINGS and reported them as
# behaviour, which is R80's fault and the third time tonight I have written it.
# The defect is a path BOUND TO A NAME AND USED, not a path mentioned in prose.
ROOTS = ("/tmp", "/home", "/root", "/var", "/opt", "/usr", "/etc")
_R = "|".join(re.escape(r) for r in ROOTS)
# TWO PATTERNS, because one was not enough and I proved it with a probe rather than
# reasoning about it. The single-line form missed a MULTI-LINE assignment entirely:
#     SNEAKY = (
#         "/home/user/sky-ledger"
#         "/spells.json")
# and the gate printed `ok` over a file that plainly contained one. Worse, residual.py
# had just been rewritten into exactly that shape, so the gate was passing my ONE KNOWN
# CASE BY BLINDNESS rather than by its declared exemption. A gate reading clean on the
# very fault it was written for -- caught by dropping a probe file into the tree and
# asking whether it fired.
LIT_ASSIGN = re.compile(
    r'^\s*(?:var\s+|let\s+|const\s+)?[A-Za-z_][\w.]*\s*=\s*[\(\s]*'
    r'["\']((?:' + _R + r')/[^"\'\n]*)["\']')
# A bare string-literal line: the continuation fragment of a multi-line assignment.
# Comment prose cannot match it, because a comment line starts with # or //.
LIT_FRAGMENT = re.compile(r'^\s*["\']((?:' + _R + r')/?[^"\'\n]*)["\']')
LIT_PATTERNS = (LIT_ASSIGN, LIT_FRAGMENT)


def scan(read, walk):
    """Return ([(path, line, literal)], [(path, line, literal)]) -- flagged, exempt."""
    bad, ok = [], []
    for rel in walk():
        body = read(rel)
        if body is None:
            continue
        lines = body.split("\n")
        for i, line in enumerate(lines):
            for m in [mm for pat in LIT_PATTERNS for mm in pat.finditer(line)]:
                near = "\n".join(lines[max(0, i - 1):i + 1])
                (ok if EXEMPT in near else bad).append((rel, i + 1, m.group(1)))
    return bad, ok


def audit(bad, ok):
    out = []
    # POSITIVE CONTROL FIRST. A scanner that matches nothing passes every check below
    # it vacuously -- and this repository has now caught two dead sweeps that read as
    # clean bills of health. The pattern must demonstrably match a known-bad literal.
    # ABSOLUTE-PATH-EXEMPT: the harness's own control literal, deliberate.
    probe = LIT_ASSIGN.search('REPO = "/home/user/sky-ledger"')
    frag = LIT_FRAGMENT.search('    "/home/user/sky-ledger"')
    out.append(("the pattern matches a known hard-coded repo root", bool(probe),
                f"probe -> {probe.group(1) if probe else None}"))
    out.append(("...and a MULTI-LINE continuation fragment, which it once missed",
                bool(frag), f"probe -> {frag.group(1) if frag else None}"))
    out.append(("no committed file hard-codes an absolute path", not bad,
                "; ".join(f"{p}:{n} {lit}" for p, n, lit in bad[:4])))
    # CAP TIGHTENED TO 0 on 1 Sep 2026. The one exemption this file ever carried was
    # residual.py's scratchpad path, and the dataset is committed now, so there is
    # nothing left to exempt. A cap left at 3 after the last exemption is spent is a
    # budget nobody is watching -- and the exemption mechanism has already, once,
    # passed a real defect by blindness rather than by declaration.
    out.append(("no exemptions are outstanding", len(ok) == 0,
                f"{len(ok)} exempt: {[(p, n) for p, n, _ in ok]}"))
    return out


def walker():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith((".py", ".js", ".sh")):
                yield os.path.relpath(os.path.join(base, f), ROOT)


def reader(rel):
    try:
        return io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
    except OSError:
        return None


if __name__ == "__main__":
    files = sorted(walker())
    # R73: the file set actually opened.
    print(f"read {len(files)} .py/.js/.sh file(s) under {os.path.basename(ROOT)}/ "
          f"(skipping {sorted(SKIP_DIRS)})")
    bad, ok = scan(reader, walker)
    for p, n, lit in ok:
        print(f"  exempt: {p}:{n}  {lit[:64]}")

    if "--selftest" not in sys.argv:
        fail = 0
        for name, good, detail in audit(bad, ok):
            print(f"  [{'ok' if good else 'FAIL'}] {name}" + ("" if good else f"  -- {detail}"))
            fail += 0 if good else 1
        sys.exit(1 if fail else 0)

    print("SELFTEST -- each check must fail when its own condition is broken")
    if any(not g for _, g, _ in audit(bad, ok)):
        print("  the real tree does not pass"); sys.exit(1)
    print("  the real tree passes")
    n = 0
    # The exact literal that was in model4.py until today.
    # ABSOLUTE-PATH-EXEMPT: the literal model4.py carried until today, injected.
    got = {x for x, g, _ in audit(bad + [("model4.py", 6, "/home/user/x")], ok) if not g}
    hit = "no committed file hard-codes an absolute path" in got
    print(f"  [{'ok' if hit else 'FAIL'}] the pre-fix model4.py literal is caught")
    n += 0 if hit else 1
    got = {x for x, g, _ in audit(bad, ok + [("a", 1, "/x")]) if not g}
    hit = "no exemptions are outstanding" in got
    print(f"  [{'ok' if hit else 'FAIL'}] a NEW exemption is caught the moment it appears")
    n += 0 if hit else 1
    # A dead scanner must be caught before its clean verdict is read.
    import re as _re
    # NEUTER WHAT audit() ACTUALLY PROBES WITH. My first version neutered
    # LIT_PATTERNS, which is what scan() uses -- while audit()'s controls probe
    # LIT_ASSIGN and LIT_FRAGMENT directly, so the "dead scanner" stayed alive and the
    # arm failed. The self-test caught it: a mutation aimed at the wrong global is a
    # mutation that cannot produce the defect.
    saved = (globals()["LIT_ASSIGN"], globals()["LIT_FRAGMENT"], globals()["LIT_PATTERNS"])
    try:
        dead = _re.compile(r"(?!x)x")                            # matches nothing at all
        globals()["LIT_ASSIGN"] = dead
        globals()["LIT_FRAGMENT"] = dead
        globals()["LIT_PATTERNS"] = (dead,)
        got = {x for x, g, _ in audit([], []) if not g}
        hit = "the pattern matches a known hard-coded repo root" in got
        print(f"  [{'ok' if hit else 'FAIL'}] a scanner that matches NOTHING is caught")
        n += 0 if hit else 1
    finally:
        (globals()["LIT_ASSIGN"], globals()["LIT_FRAGMENT"],
         globals()["LIT_PATTERNS"]) = saved
    print(f"  {n} self-test checks failed")
    sys.exit(1 if n else 0)
