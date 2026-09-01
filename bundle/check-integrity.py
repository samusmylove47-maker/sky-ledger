#!/usr/bin/env python3
"""check-integrity.py -- the bundle's bytes, verified in MY tree.

Session A caught a corruption of this bundle in A's tree, by verifying the
served hash. Nothing here verified it: the hash lived in a filename and in a
sentence in HANDOFF.md -- both assertions, neither a check. This closes that.
The integrity of the artifact I hand to A is now checked where I build it, not
only where A serves it.

    python3 bundle/check-integrity.py             check the real bundle
    python3 bundle/check-integrity.py --selftest  prove each check can FAIL

The self-test is the point. A's finding tonight was a check branch that fired
and reported nothing (scripts/check.py:151), and my first attempt at proving
this file works was itself a silent no-op -- a shell `bytes.replace()` on a
needle that was not in the file, which mutates nothing and reports success.
So the mutations below are asserted to have actually changed the input before
their effect on the checks is read. A test that cannot mutate is a test that
cannot fail.
"""
import hashlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAME_RE = re.compile(r"eqls-gap-engine\.([0-9a-f]{8})\.js")


def audit(raw, hashed_name, hashed_raw, found=None):
    """Pure. Returns a list of (check_name, ok, detail). No I/O, no globals.

    `found` is the FULL list of hashed copies the directory holds. Added 1 Sep 2026
    under R73 -- a command that reads a file set states the count it opened.
    Reproduced before it was written: with two hashed copies present this file
    printed

        hashed copy is byte-identical  FAILED   22403 vs 0 bytes
        FAILED. The served bytes are not what this tree says they are.

    The bytes were fine. There were TWO hashed copies, `load()` silently took the
    first sorted one and handed b"" alongside it, and the gate reported a corruption
    that had not happened. The right answer in the wrong words -- and the wrong words
    send you to debug the bundle instead of the directory.

    The real fault it was hiding is the one BUNDLE-CONTRACT section 6 exists for: a
    stale hashed copy left behind is a valid-looking hashed URL serving YESTERDAY'S
    ENGINE, which is the exact scar that section records."""
    out = []
    digest = hashlib.sha256(raw).hexdigest()

    if found is None:
        found = [hashed_name] if hashed_name else []
    out.append(("exactly one hashed copy in the directory", len(found) == 1,
                f"found {len(found)}: {sorted(found)}"))

    m = NAME_RE.fullmatch(hashed_name or "")
    out.append(("hashed copy is named correctly", bool(m),
                hashed_name or "no hashed copy found"))
    if m:
        claimed = m.group(1)
        out.append(("filename hash matches the bytes", digest.startswith(claimed),
                    f"sha256[:8] {digest[:8]}, filename claims {claimed}"))
        out.append(("hashed copy is byte-identical", hashed_raw == raw,
                    f"{len(raw)} vs {len(hashed_raw)} bytes"))

    # Would a text round-trip touch this file? A's note says its harness
    # corrupted this bundle "because the harness restores through a text
    # round-trip". Measured, that mechanism does not fit THIS file: it is pure
    # ASCII, LF-only, no tabs, no BOM, no trailing whitespace, final newline --
    # every normalising round-trip returns it unchanged. Kept anyway, so that if
    # the bundle ever GAINS a byte a round-trip could touch, this tree says so
    # before A's does.
    bad = []
    if raw and max(raw) > 0x7E:      bad.append("non-ASCII")
    if b"\r" in raw:                 bad.append("CR")
    if b"\t" in raw:                 bad.append("TAB")
    if raw[:3] == b"\xef\xbb\xbf":   bad.append("BOM")
    if not raw.endswith(b"\n"):      bad.append("no final newline")
    if any(l != l.rstrip() for l in raw.split(b"\n")): bad.append("trailing whitespace")
    try:
        rt = raw.decode("utf-8").replace("\r\n", "\n").rstrip("\n").encode() + b"\n"
        if rt != raw: bad.append("normalising round-trip alters bytes")
    except UnicodeDecodeError:
        bad.append("not decodable as UTF-8")
    out.append(("round-trip stable (ASCII/LF/final NL)", not bad,
                ", ".join(bad) if bad else "no byte a text round-trip can touch"))
    return out


def load():
    raw = open(os.path.join(HERE, "eqls-gap-engine.js"), "rb").read()
    names = [f for f in sorted(os.listdir(HERE)) if NAME_RE.fullmatch(f)]
    # READ THE COPY IT NAMES, whatever the count. This used to hand back b"" as soon
    # as the count was not 1, so with two copies present the byte-identical check
    # reported "22403 vs 0 bytes" -- a corruption that had not happened, sitting
    # beside the count check that names the real fault. Two true statements are worth
    # more than one true and one false: the count check owns the extra copy, and this
    # one now tells the truth about the copy it named.
    if not names:
        return raw, None, b"", names
    return raw, names[0], open(os.path.join(HERE, names[0]), "rb").read(), names


def show(results):
    for n, ok, d in results:
        print(f"  {n:<38} {'ok' if ok else 'FAILED'}   {d}")
    return all(ok for _, ok, _ in results)


def selftest():
    raw, name, hraw, found = load()
    ok = True

    def mutate(label, r2, n2, h2, expect_failing, f2=None):
        """Assert the mutation is real, then assert it breaks the named check."""
        nonlocal ok
        if (r2, n2, h2, f2) == (raw, name, hraw, None):
            print(f"  {label:<44} BROKEN -- mutation was a no-op"); ok = False; return
        res = dict((n, o) for n, o, _ in audit(r2, n2, h2, f2))
        got = res.get(expect_failing)
        if got is None:
            print(f"  {label:<44} BROKEN -- '{expect_failing}' not reported"); ok = False
        elif got:
            print(f"  {label:<44} BROKEN -- '{expect_failing}' still passed"); ok = False
        else:
            print(f"  {label:<44} correctly fails '{expect_failing}'")

    mutate("one byte appended to the served copy", raw, name, hraw + b"\n",
           "hashed copy is byte-identical")
    mutate("the source bytes change, filename does not", raw + b"//x\n", name, hraw + b"//x\n",
           "filename hash matches the bytes")
    mutate("an em dash reaches the bundle", raw[:-1] + "// —\n".encode(), name, hraw,
           "round-trip stable (ASCII/LF/final NL)")
    mutate("CRLF line endings", raw.replace(b"\n", b"\r\n"), name, hraw,
           "round-trip stable (ASCII/LF/final NL)")
    mutate("final newline stripped", raw.rstrip(b"\n"), name, hraw,
           "round-trip stable (ASCII/LF/final NL)")
    mutate("hashed copy missing", raw, None, b"",
           "hashed copy is named correctly")
    # The one this file used to misreport. A stale hashed copy left beside the new
    # one is a valid-looking URL serving yesterday's engine, and until tonight it
    # surfaced as "the served bytes are not what this tree says they are".
    mutate("a stale hashed copy left behind", raw, name, hraw,
           "exactly one hashed copy in the directory",
           f2=sorted(set(found) | {"eqls-gap-engine.deadbeef.js"}))
    mutate("no hashed copy at all", raw, None, b"",
           "exactly one hashed copy in the directory", f2=[])

    # and the negative: the real bundle must pass every check
    if not all(o for _, o, _ in audit(raw, name, hraw, found)):
        print("  the real bundle does not pass its own checks"); ok = False
    else:
        print(f"  the unmutated bundle still passes all {len(audit(raw, name, hraw, found))}")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("== check-integrity self-test: every check must be able to FAIL ==")
        sys.exit(0 if selftest() else 1)
    raw, name, hraw, found = load()
    # R73: state the file set actually opened, not the one intended.
    print(f"  read {len(found) + 1} file(s) in {os.path.relpath(HERE)}/: "
          f"eqls-gap-engine.js + {len(found)} hashed cop(y/ies) {sorted(found)}")
    good = show(audit(raw, name, hraw, found))
    print(f"\n  sha256 {hashlib.sha256(raw).hexdigest()}")
    if not good:
        # NAME THE FAULT THAT FIRED. One sentence for every failure read as "the
        # bytes are corrupt" is the shape this file spent tonight fixing elsewhere.
        failed = [n for n, o, _ in audit(raw, name, hraw, found) if not o]
        if failed == ["exactly one hashed copy in the directory"]:
            print(f"  FAILED. The bytes are fine. This directory holds {len(found)} hashed "
                  "copies, so a hashed URL can serve an engine that is not this one -- "
                  "the stale-asset scar BUNDLE-CONTRACT section 6 records. Delete the "
                  "copies that are not the current hash.")
        else:
            print(f"  FAILED: {failed}. The served bytes are not what this tree says "
                  "they are.")
        sys.exit(1)
    print("  bundle integrity verified here, not only where it is served.")
