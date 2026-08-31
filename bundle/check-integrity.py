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


def audit(raw, hashed_name, hashed_raw):
    """Pure. Returns a list of (check_name, ok, detail). No I/O, no globals."""
    out = []
    digest = hashlib.sha256(raw).hexdigest()

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
    if len(names) != 1:
        return raw, (names[0] if names else None), b""
    return raw, names[0], open(os.path.join(HERE, names[0]), "rb").read()


def show(results):
    for n, ok, d in results:
        print(f"  {n:<38} {'ok' if ok else 'FAILED'}   {d}")
    return all(ok for _, ok, _ in results)


def selftest():
    raw, name, hraw = load()
    ok = True

    def mutate(label, r2, n2, h2, expect_failing):
        """Assert the mutation is real, then assert it breaks the named check."""
        nonlocal ok
        if (r2, n2, h2) == (raw, name, hraw):
            print(f"  {label:<44} BROKEN -- mutation was a no-op"); ok = False; return
        res = dict((n, o) for n, o, _ in audit(r2, n2, h2))
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

    # and the negative: the real bundle must pass every check
    if not all(o for _, o, _ in audit(raw, name, hraw)):
        print("  the real bundle does not pass its own checks"); ok = False
    else:
        print("  the unmutated bundle still passes all four")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("== check-integrity self-test: every check must be able to FAIL ==")
        sys.exit(0 if selftest() else 1)
    raw, name, hraw = load()
    good = show(audit(raw, name, hraw))
    print(f"\n  sha256 {hashlib.sha256(raw).hexdigest()}")
    if not good:
        print("  FAILED. The served bytes are not what this tree says they are.")
        sys.exit(1)
    print("  bundle integrity verified here, not only where it is served.")
