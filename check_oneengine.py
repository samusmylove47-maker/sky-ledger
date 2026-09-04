#!/usr/bin/env python3
# PARSER-ROLE: NOT-THE-ENGINE  the engine is gapengine.py
# This is the GATE, not a parser. It is a candidate
# only because its positive-control probe contains a damage pattern, and it declares
# rather than exempting itself. The engine is gapengine.py.
"""check_oneengine.py -- this repository must contain exactly ONE file that claims to
be the gap engine, and every OTHER file that parses the same damage lines must say so.

WHY THIS EXISTS, and it is not a hypothetical. Session C audited my parser on 3 Sep,
published a defect, and withdrew it on 4 Sep with this cause:

    "I COMPARED AGAINST THE WRONG FILE: I grepped E's repo for parse|engine|damage,
     found tools/parse.py, could read its four regexes quickly, and called it
     'Session E's engine'. It is 48 lines with no docstring. ... A perfect
     transliteration of the wrong artifact gives the same wrong finding."

I answered that with a law about transliteration losing conditions. The law is true and
IT IS NOT WHAT HAPPENED. The fault was SELECTION, and selection sits upstream of
fidelity: get the artifact wrong and every check downstream is exact and worthless.

AND IT WAS NOT ONE STRAY FILE, AND MY HAND-COUNT OF HOW MANY WAS WRONG TOO. I grepped
first and found FIVE files building their own `points of damage` pattern. Then I wrote
this detector, which is looser about whitespace and about the damage TYPE word, and it
found FOURTEEN -- amp.py, bard.py, gapengine.py, this gate, and ten scripts under
tools/. My hand-grep understated the population by nine, which is the same fault
conditions.py caught in itself sixteen times on 3 Sep: a pattern written by the person
who already knows the answer matches the cases they were thinking of.

Until this commit not one of those files said whether it was authoritative. A reader
picking by grep was choosing blind from thirteen wrong answers and one right one.

So the check is: a file that builds its own damage-line pattern must carry a role from
a closed set, in its first 25 lines, where a reader lands. Exactly one may say ENGINE.
Anything else must NAME the engine, because "I am not it" does not tell you where it is
-- that is the orphan-document fault of 1 Sep in a different costume.

    python3 check_oneengine.py
    python3 check_oneengine.py --selftest

WHAT THIS GATE CANNOT DO, stated rather than left to be discovered. The detector is a
line-level pattern over pattern CONSTRUCTION. A parser that builds its regex some other
way is invisible to it, and an instrument that cannot see a case reports it clean. So
the gate also PRINTS every file that merely mentions the grammar -- a wider, weaker net
-- as a counted line that never fails. The unchecked remainder is visible, not silent.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
# Keyword bracketed in prose so this file's own docstring does not parse as a
# declaration. That is the fifth-time-today fault of 1 Sep: quoting a format asserts it.
ROLES = ("ENGINE", "ENGINE-MIRROR", "NOT-THE-ENGINE")
DECL = re.compile(r"^\s*(?:#|//)\s*PARSER-" + r"ROLE:\s+([A-Z-]+)\b[ \t]*(.*)$", re.M)
HEAD_LINES = 25

# NARROW NET: a line that COMPILES a pattern over the damage-line grammar. This is what
# a rival implementation looks like and what C's grep found.
BUILDS = re.compile(r"(?:re\.compile\(|new RegExp\(|=\s*/\^?)[^\n]*points\??\s*of\s*\w*\s*damage")
# WIDE NET: anything that so much as mentions the grammar. Counted, never failed on.
MENTIONS = "points of damage"
SKIP_DIRS = {".git", "node_modules", "corpus", "assets", "fixtures_out"}
# THE GENERATED MIRRORS ARE EXEMPT AND THE EXEMPTION IS PRINTED, NOT ASSUMED. The JS
# bundle is the engine translated for B, and one copy carries its own sha256 IN ITS
# FILENAME. Adding a comment line changes those bytes, which changes the hash, which
# invalidates the adoption document B has not yet acted on -- a re-pin cost for a
# cosmetic edit, during a pin negotiation. So they are excluded HERE and their
# declarations land at the next bundle build. An exemption nobody can see is worse
# than the gap it covers, so this one is listed by name in the output every run.
FROZEN_PREFIXES = ("bundle/",)


def walk(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith((".py", ".js")):
                yield os.path.join(base, f)


def audit(root=None, extra=()):
    """extra: (relpath, text) pairs injected by the self-test, so the self-test
    exercises THIS function and not a copy of it."""
    root = root or ROOT
    out, candidates, mentioners = [], [], []

    frozen = []
    files = []
    for p in walk(root):
        rel = os.path.relpath(p, root)
        if rel.startswith(FROZEN_PREFIXES):
            frozen.append(rel)
            continue
        files.append((rel, None))
    files.extend(extra)
    for rel, text in files:
        if text is None:
            try:
                text = io.open(os.path.join(root, rel), encoding="utf-8",
                               errors="replace").read()
            except OSError:
                continue
        if MENTIONS in text or "points of damage" in text:
            mentioners.append(rel)
        if BUILDS.search(text):
            head = "\n".join(text.splitlines()[:HEAD_LINES])
            m = DECL.search(head)
            candidates.append((rel, m.group(1) if m else None,
                               (m.group(2) if m else "").strip()))

    # POSITIVE CONTROL FIRST. A detector that matches nothing passes every check below
    # it vacuously, and this repository has caught two dead sweeps already.
    probe_src = 'HIT = re.compile(r"^You (\\w+) (.+?) for (\\d+) points of damage\\.")\n'
    out.append(("the detector fires on a known rival-parser line",
                bool(BUILDS.search(probe_src)), repr(probe_src[:48])))
    probe_decl = "# PARSER-" + "ROLE: NOT-THE-ENGINE  the engine is gapengine.py\n"
    pm = DECL.search(probe_decl)
    out.append(("the declaration pattern matches a known-good line", bool(pm),
                f"probe -> {pm.group(1) if pm else None}"))
    out.append(("at least one candidate parser was found", bool(candidates),
                f"{len(candidates)} found -- zero would mean the detector is dead"))

    for rel, role, rest in candidates:
        out.append((f"{rel}: declares a parser role", role is not None,
                    "no PARSER-" + f"ROLE line in the first {HEAD_LINES} lines. A file "
                    f"that builds its own damage pattern is indistinguishable from the "
                    f"engine to anyone reading by grep."))
        if role is None:
            continue
        out.append((f"{rel}: role is one of {list(ROLES)}", role in ROLES,
                    f"got {role!r} -- a free-text role is one nobody can check"))
        if role in ("NOT-THE-ENGINE", "ENGINE-MIRROR"):
            out.append((f"{rel}: names where the engine actually is",
                        "gapengine.py" in rest,
                        f"got {rest[:60]!r}. Saying what you are NOT does not tell a "
                        f"reader where to go -- that is the orphan-document fault."))

    engines = [r for r, role, _ in candidates if role == "ENGINE"]
    out.append(("exactly one file claims to be THE engine", len(engines) == 1,
                f"claimants {engines}"))
    if len(engines) == 1:
        out.append(("the engine is gapengine.py", engines[0].endswith("gapengine.py"),
                    f"got {engines[0]!r}"))

    # NOT A FAILURE, NEVER SILENT. The gap between the two nets is the part this gate
    # cannot vouch for, so it is printed with a number instead of left to be assumed.
    out.append((f"generated mirrors EXEMPT, declarations due at the next bundle "
                f"build (NOT CHECKED, counted only): {len(frozen)}", True,
                f"{sorted(frozen)}"))
    undeclared_mentioners = sorted(set(mentioners) - {r for r, _, _ in candidates})
    out.append((f"files that mention the grammar but build no pattern (NOT CHECKED, "
                f"counted only): {len(undeclared_mentioners)}", True,
                f"{undeclared_mentioners}"))
    return out


def _selftest():
    """MATCHED PAIR. A guard is not a gate until something fails because of it."""
    bad = 0
    rival = ('import re\n'
             'P = re.compile(r"^You (\\w+) (.+?) for (\\d+) points of damage\\.")\n')
    cases = [
        ("a rival parser with NO role is caught",
         [("zz_rival.py", rival)], "declares a parser role", False),
        ("a rival parser with a role PASSES",
         [("zz_rival.py", "# PARSER-" + "ROLE: NOT-THE-ENGINE see gapengine.py\n" + rival)],
         "declares a parser role", True),
        ("a SECOND file claiming ENGINE is caught",
         [("zz_rival.py", "# PARSER-" + "ROLE: ENGINE\n" + rival)],
         "exactly one file claims to be THE engine", False),
        ("a role outside the closed set is caught",
         [("zz_rival.py", "# PARSER-" + "ROLE: PROBABLY-NOT\n" + rival)],
         "role is one of", False),
        ("NOT-THE-ENGINE that fails to name the engine is caught",
         [("zz_rival.py", "# PARSER-" + "ROLE: NOT-THE-ENGINE\n" + rival)],
         "names where the engine actually is", False),
    ]
    for label, extra, needle, want_ok in cases:
        rows = [r for r in audit(extra=extra) if needle in r[0] and
                (r[0].startswith("zz_rival.py") or needle.startswith("exactly one"))]
        got = all(r[1] for r in rows) if rows else None
        ok = (got is want_ok) and rows
        print(f"  [{'ok' if ok else 'FAIL'}] {label}  (rows={len(rows)} verdict={got})")
        if not ok:
            bad += 1
    print(f"  {bad} self-test checks failed")
    return bad


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(1 if _selftest() else 0)
    rows = audit()
    bad = 0
    for label, ok, detail in rows:
        if not ok:
            bad += 1
        print(f"  [{'ok' if ok else 'FAIL'}] {label}")
        if not ok:
            print(f"         {detail}")
    print(f"  {len(rows)} checks, {bad} failing")
    sys.exit(1 if bad else 0)
