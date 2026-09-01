#!/usr/bin/env python3
"""check_reachable.py -- every outbound document must be REACHABLE from the watched file.

WHY, AND IT IS NOT MY FINDING. Session 0 asked how to onboard a new cloud session onto
the file-watch relay, and described its failure: FIVE communications went into five NEW
files while the watched file sat untouched. A full day of output invisible to the
reader, and the session did not know -- it had been told a file was watched, never which
one.

I went to answer and found the same defect in this tree. `handover/TO-SESSION-C-mailbox.md`
and `handover/TO-SESSION-C-verb-census.md` were named ZERO times in HANDOFF.md. My
attempt to message C about them FAILED (this cloud session cannot message other
sessions), so they reached C only if C happened to browse. I wrote two documents for a
peer and left neither of them findable.

THE RULE. A watched file is an ADDRESS, not a container. Anything stored elsewhere is
fine -- and must be NAMED in the address, or it does not exist to a reader following the
only path they were given. That is the shape that gets both: one file to watch, many
files to write.

    python3 check_reachable.py
    python3 check_reachable.py --selftest
"""
import io, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WATCHED = "HANDOFF.md"
# Directories whose contents are OUTBOUND -- written for somebody else to read.
OUTBOUND = ("handover",)
SKIP = {".gitkeep"}


def audit(index, files):
    """index: text of the watched file. files: [relative path]. -> [(name, ok, detail)]"""
    out = []
    # POSITIVE CONTROL FIRST: an empty file list passes every check below it vacuously,
    # and "no outbound documents" and "no documents checked" look identical.
    out.append(("there are outbound documents to check at all", bool(files),
                f"{len(files)} found -- an empty sweep is not a clean one"))
    orphans = [f for f in files if os.path.basename(f) not in (index or "")]
    out.append(("every outbound document is NAMED in the watched file", not orphans,
                f"{len(orphans)} unreachable: {orphans} -- a reader following the only "
                f"path they were given never learns these exist"))
    return out


def outbound_files():
    out = []
    for d in OUTBOUND:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirs, names in os.walk(base):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for n in sorted(names):
                if n in SKIP or n.startswith("."):
                    continue
                out.append(os.path.relpath(os.path.join(dirpath, n), ROOT))
    return sorted(out)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("SELFTEST -- an unreachable document must fire")
        bad = 0

        def chk(name, ok, d=""):
            global bad
            print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1

        def fired(idx, fs):
            return [n for n, ok, _ in audit(idx, fs) if not ok]

        chk("a named document passes",
            not fired("see handover/a.md for detail", ["handover/a.md"]),
            f"{fired('see handover/a.md', ['handover/a.md'])}")
        # THE ONE THIS FILE EXISTS FOR.
        chk("an UNNAMED document fires",
            any("NAMED in the watched file" in x
                for x in fired("nothing here", ["handover/a.md"])), "")
        chk("one named and one not still fires",
            any("NAMED" in x for x in
                fired("see handover/a.md", ["handover/a.md", "handover/b.md"])), "")
        chk("NO documents at all is caught, not read as clean",
            any("to check at all" in x for x in fired("anything", [])),
            "an empty sweep passed as a clean one")
        # A bare mention anywhere counts: the point is that a reader can FIND it, not
        # that it is described well. A stricter rule would be a rule I break myself.
        chk("a mention inside prose counts, not only a link",
            not fired("I replied in handover/a.md this evening.", ["handover/a.md"]), "")
        print(f"  {bad} self-test checks failed")
        sys.exit(1 if bad else 0)

    idx = io.open(os.path.join(ROOT, WATCHED), encoding="utf-8").read()
    files = outbound_files()
    print(f"read {WATCHED} and {len(files)} outbound document(s) under "
          f"{'/, '.join(OUTBOUND)}/")
    rows = audit(idx, files)
    bad = 0
    for n, ok, d in rows:
        print(f"  [{'ok' if ok else 'FAIL'}] {n}" + ("" if ok else f"  -- {d}"))
        bad += 0 if ok else 1
    print(f"  {len(rows)} checks, {bad} failing")
    sys.exit(1 if bad else 0)
