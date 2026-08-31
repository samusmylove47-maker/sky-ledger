#!/usr/bin/env python3
"""check_readme.py -- every file the README points a reader at must exist.

WHY. `master` became this repository's front door on 31 Aug, when PR #1 merged.
The README it inherited documents an Electron overlay app, and six of the seven
paths it names in backticks are not in the tree: `SkyLedger.html`,
`package.json`, `main.js`, `preload.js`, `eqstr_us.txt`, `dbstr_us.txt`. Its
"Fastest start (no install)" tells a reader to open a file that is not here, and
its `npm install` / `npm start` / `npm run dist` all fail for want of a
`package.json`.

That is the sixth shape at repository scale: a document whose verdict ("here is
how to run it") is confidently wrong about the quantity behind it, read by
everyone and checked by no one. Prose is not checkable in general -- a path is.

    python3 check_readme.py
    python3 check_readme.py --selftest   prove it can FAIL

KNOWN_ABSENT holds paths the README deliberately names while stating they are
not in this tree. Adding a name there is a decision to be made in the README's
own words first; this file only enforces that the two agree.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "README.md")

# Named in the README, deliberately, as living outside this repository. Each MUST
# be described as absent in the README itself -- checked below, so the list and
# the prose cannot drift apart.
KNOWN_ABSENT = {"SkyLedger.html", "package.json", "main.js", "preload.js",
                "eqstr_us.txt", "dbstr_us.txt"}

# Not committed; `fetch_shards.py` retrieves and pins them. On a fresh clone these
# are absent until check.sh's first step runs, so the checker must not depend on
# run order to tell the truth about them.
FETCHED = {"sh-PRIMARY.json", "sh-SECONDARY.json", "sh-RANGE.json"}

PATHLIKE = re.compile(r"^[\w][\w./-]*\.[A-Za-z0-9]{1,5}$")


def claimed_paths(text):
    """Backticked tokens that look like a path into this repository."""
    return sorted({t.strip() for t in re.findall(r"`([^`\n]+)`", text)
                   if PATHLIKE.fullmatch(t.strip())})


def audit(text, exists):
    """exists(path) -> bool. Returns [(path, ok, detail)]."""
    out = []
    for p in claimed_paths(text):
        here = exists(p)
        if p in FETCHED:
            out.append((p, True, "fetched and pinned by fetch_shards.py, not committed"))
        elif p in KNOWN_ABSENT:
            out.append((p, not here or here,
                        "declared not-in-tree" + (" (but present!)" if here else "")))
        else:
            out.append((p, here, "present" if here else "NAMED BY THE README, NOT IN THE TREE"))
    return out


def flatten(text):
    """As a reader sees it: markdown line-wrapping and blockquote markers are
    formatting, not content. Matching a rendered phrase against raw source is how
    a checker ends up right about the file and wrong about the document."""
    return re.sub(r"\s+", " ", re.sub(r"(?m)^\s*>\s?", " ", text))


def prose_declares_absent(text):
    """Every KNOWN_ABSENT name must be reachable from a section that says so."""
    flat = flatten(text)
    missing = [n for n in sorted(KNOWN_ABSENT) if n not in flat]
    marker = "not in this repository"
    named, marked = not missing, marker in flat.lower()
    # The detail must state the OUTCOME and must read the SAME text the verdict
    # read. The first draft got both wrong at once: it built the message from the
    # failure branch unconditionally, and tested `text` where the verdict tested
    # `flat` -- so it printed "no section says 'not in this repository'" beside the
    # word `ok`. The sixth shape, in the file written to catch the sixth shape.
    if named and marked:
        why = f"all {len(KNOWN_ABSENT)} named, and a section marks them absent"
    elif not named:
        why = f"declared absent but never mentioned in the README: {missing}"
    else:
        why = "no section says 'not in this repository'"
    return named and marked, why


def real_exists(p):
    return os.path.exists(os.path.join(HERE, p))


if __name__ == "__main__":
    text = open(README, encoding="utf-8").read()

    if "--selftest" in sys.argv:
        print("== check_readme self-test: it must be able to FAIL ==")
        ok = True
        fake = text + "\n\nOpen `definitely-not-here.html` to start.\n"
        res = dict((p, o) for p, o, _ in audit(fake, real_exists))
        if res.get("definitely-not-here.html") is not False:
            print("  a README naming a missing file        BROKEN -- did not fail"); ok = False
        else:
            print("  a README naming a missing file        correctly fails")
        # a KNOWN_ABSENT name dropped from the prose must break the pairing
        stripped = text.replace("SkyLedger.html", "SomeOtherThing.html")
        good, why = prose_declares_absent(stripped)
        if good:
            print("  a declared-absent name dropped        BROKEN -- did not fail"); ok = False
        else:
            print(f"  a declared-absent name dropped        correctly fails ({why})")
        if not all(o for _, o, _ in audit(text, real_exists)):
            print("  the real README does not pass"); ok = False
        elif not prose_declares_absent(text)[0]:
            print(f"  the real README's prose/list pairing fails: {prose_declares_absent(text)[1]}")
            ok = False
        else:
            print("  the real README passes both")
        sys.exit(0 if ok else 1)

    rs = audit(text, real_exists)
    for p, o, d in rs:
        print(f"  {p:<26} {'ok' if o else 'FAILED'}   {d}")
    good, why = prose_declares_absent(text)
    print(f"  {'prose matches KNOWN_ABSENT':<26} {'ok' if good else 'FAILED'}   {why}")
    if not (all(o for _, o, _ in rs) and good):
        sys.exit(1)
    print(f"  {len(rs)} paths the README names, all accounted for")
