#!/usr/bin/env python3
"""check_refclaims.py -- a claim about the distance between two moving git refs must be
recomputed, not remembered.

WHY. My STATUS block carried the line "my branch is an ancestor of master, 0 commits
ahead". It was true the day it was written. It went stale on my next push and nothing
recomputed it, so it kept asserting itself through sixty commits. Then I read it, and
on its authority told Session C that the reply I had written for C was on `master`.
It was not. C would have fetched master, found nothing, and had NO WAY TO DISTINGUISH
THAT FROM MY NEVER HAVING WRITTEN IT -- a false negative that reads exactly like
silence, which is the worst shape a wrong claim can take between two sessions.

The stale-fixture defect again, in the block whose own header says "update on EVERY
push". A number about a moving ref is a measurement with a shelf life.

FAIL-CLOSED ON PURPOSE. If `origin/master` cannot be resolved, this REFUSES rather
than passing. An instrument that reports "fine" when it could not look is the fault
this repository has caught more than any other.

    python3 check_refclaims.py
    python3 check_refclaims.py --selftest
"""
import io, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.path.join(ROOT, "HANDOFF.md")
BASE = "origin/master"

# The claim shape: "at least <N> COMMITS AHEAD", case-insensitive.
#
# IT IS A FLOOR, NOT AN EQUALITY, AND THAT IS FORCED BY ARITHMETIC. `origin/master..HEAD`
# counts the commit being written, so an exact claim is false the instant it is
# committed -- the number would have to predict its own commit. A floor cannot go
# false by pushing more work, and it fires exactly when it should: when master moves
# forward and swallows the branch, the real distance DROPS BELOW the floor.
# The direction that actually hurt someone -- claiming ZERO while sixty behind, which
# sent Session C to fetch an empty ref -- is caught either way.
AHEAD = re.compile(r"at least (\d+)\s+commits?\s+ahead\b", re.I)
# ...but a BARE claim with no floor is the stale shape and must not be writable.
BARE = re.compile(r"(?<!at least )\b(\d+)\s+commits?\s+ahead\b", re.I)


def git(*args):
    """(ok, output). Never raises -- a missing ref is a REFUSAL, not a crash."""
    try:
        r = subprocess.run(("git",) + args, cwd=ROOT, capture_output=True, text=True)
    except OSError as e:
        return False, str(e)
    return (r.returncode == 0), (r.stdout or r.stderr).strip()


def audit(text, actual):
    """actual: int, or None when the base ref could not be resolved."""
    out = []
    claims = [int(m.group(1)) for m in AHEAD.finditer(text)]
    out.append((f"a claim about the distance to {BASE} is present", bool(claims),
                f"found {claims}"))
    if actual is None:
        out.append((f"{BASE} resolves, so a verdict is possible at all", False,
                    "REFUSED -- cannot verify a claim against a ref I cannot read, "
                    "and a pass here would be an instrument reporting on a look it "
                    "never took"))
        return out
    for n in claims:
        out.append((f"the claimed floor of {n} still holds (git: {actual})",
                    actual >= n,
                    f"HANDOFF.md claims at least {n}, git says {actual}. If master "
                    f"merged the branch this is the line that must be rewritten -- "
                    f"it is the only moment the floor can go false"))
    bare = [int(m.group(1)) for m in BARE.finditer(text)]
    out.append(("no BARE distance claim stands without a floor", not bare,
                f"found {bare} -- an exact count about a moving ref is false one "
                f"commit later; write 'at least N commits ahead'"))
    return out


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("SELFTEST -- a stale distance must fire, a fresh one must not")
        bad = 0

        def chk(name, ok, d=""):
            global bad
            print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1

        def fired(rows):
            return [n for n, ok, _ in rows if not ok]

        # POSITIVE CONTROL FIRST: a pattern that matches nothing passes vacuously.
        chk("the claim pattern parses a known-good line",
            AHEAD.search("this branch is at least 60 commits ahead of master") is not None,
            "the pattern is dead")
        chk("a floor that still holds passes",
            not fired(audit("at least 60 commits ahead of master", 60)),
            f"{fired(audit('at least 60 commits ahead of master', 60))}")
        chk("...and keeps passing as the branch grows (the whole point of a floor)",
            not fired(audit("at least 60 commits ahead", 93)), "a floor expired")
        chk("a floor BROKEN by a merge fires",
            any("floor" in x for x in fired(audit("at least 60 commits ahead", 0))),
            f"{fired(audit('at least 60 commits ahead', 0))}")
        chk("THE ONE THAT MISLED C: a bare '0 commits ahead' fires",
            any("BARE" in x for x in fired(audit("0 commits ahead", 60))),
            f"{fired(audit('0 commits ahead', 60))}")
        chk("a bare exact claim fires even when it is momentarily TRUE",
            any("BARE" in x for x in fired(audit("60 commits ahead", 60))),
            "an exact claim was accepted; it is false one commit later")
        chk("NO claim at all is caught, not read as clean",
            any("is present" in x for x in fired(audit("nothing here", 60))),
            "an absent claim passed vacuously")
        chk("the floor pattern parses; the bare pattern does not double-count it",
            AHEAD.search("at least 60 commits ahead") is not None
            and BARE.search("at least 60 commits ahead") is None,
            "the two patterns overlap, so a correct line would report itself bare")
        # THE ONE THIS FILE IS SHAPED BY.
        chk("an unresolvable base ref REFUSES rather than passing",
            any("resolves" in x for x in fired(audit("at least 60 commits ahead", None))),
            "it passed while unable to look")
        chk("...and the refusal does not depend on the claim being wrong",
            any("resolves" in x for x in fired(audit("at least 0 commits ahead", None))),
            "the refusal only fires on some inputs")
        chk("singular 'commit ahead' parses too",
            AHEAD.search("at least 1 commit ahead") is not None, "plural-only pattern")
        print(f"  {bad} self-test checks failed")
        sys.exit(1 if bad else 0)

    ok, _ = git("rev-parse", "--verify", "--quiet", BASE)
    actual = None
    if ok:
        ok2, n = git("rev-list", "--count", f"{BASE}..HEAD")
        if ok2 and n.isdigit():
            actual = int(n)
    text = io.open(HANDOFF, encoding="utf-8").read()
    print(f"read 1 file: HANDOFF.md; {BASE} -> "
          + (f"{actual} commit(s) ahead" if actual is not None else "UNRESOLVED"))
    rows = audit(text, actual)
    bad = 0
    for n, good, d in rows:
        print(f"  [{'ok' if good else 'FAIL'}] {n}" + ("" if good else f"  -- {d}"))
        bad += 0 if good else 1
    print(f"  {len(rows)} checks, {bad} failing")
    sys.exit(1 if bad else 0)
