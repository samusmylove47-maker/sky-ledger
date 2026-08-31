#!/usr/bin/env python3
"""check-contract.py -- does my scanner still cover the contract I ship against?

Until 04:19Z on 31 Aug this repository DID NOT HOLD A COPY of
`docs/BUNDLE-CONTRACT.md`. I built to it by reading it on a branch and kept
nothing, so when Session 0 asked whether the merged version still matched what I
built to, I could not answer from my own tree. A copy is now vendored beside the
bundle, named by the commit it came from -- the same convention as the bundle
itself.

Two checks, and the second is the one with teeth:

  1. The vendored contract is intact (sha256 recorded here, matched on every run).
  2. EVERY construct §3 names in backticks appears in check-bundle.js's BANNED
     list. This is the fail-open that vendoring alone does not close: A can add a
     clause to §3, my scanner keeps reporting "18 constructs, 0 present", and the
     green means only that I did not look. A scanner is not compliance with a
     contract it has not read.

Run:  python3 bundle/check-contract.py
      python3 bundle/check-contract.py --selftest    prove both checks can FAIL
"""
import hashlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VENDORED = os.path.join(ROOT, "handover", "BUNDLE-CONTRACT.d5c2b4a4.md")
SCANNER = os.path.join(HERE, "check-bundle.js")

# sha256 of docs/BUNDLE-CONTRACT.md at eql-source d5c2b4a4 (PR #155 merge),
# verified equal to `git show d5c2b4a4:docs/BUNDLE-CONTRACT.md | sha256sum`.
# I built to 2bd70807. Diffed: ONE hunk, entirely inside §4 (WHO DECODES),
# additive -- it constrains A's decode ordering and adds a U+FFFD count, both
# host-side. §3, the section this bundle is bound by, is BYTE-IDENTICAL across
# the two commits (22 lines, verified with awk + diff, not by reading).
EXPECTED = "9b8bee429ac7efa9ae301ec84aa016ff26f40a4770e3f37a3cd252aac789a041"

# Constructs §3 states as prohibitions. Extracted by hand from the vendored text
# and re-derived below, so a clause A adds cannot slip past unnoticed.
ALIASES = {
    "window": None,            # §3 permits window for the bundle's own registration
    "XMLHttpRequest": "XMLHttpRequest",
}

def clause_tokens(text):
    """Backticked identifiers inside §3, minus prose and permitted names."""
    sec = re.search(r"^## 3\..*?(?=^## )", text, re.S | re.M)
    if not sec:
        return None
    toks = set()
    for t in re.findall(r"`([^`]+)`", sec.group(0)):
        t = t.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\(\))?|new Function", t):
            continue           # paths, versions, prose fragments
        toks.add(t.rstrip("()"))
    return toks

def banned_list(js):
    m = re.search(r"const BANNED = \[(.*?)\];", js, re.S)
    return {s.strip() for s in re.findall(r"'([^']*)'", m.group(1))} if m else set()

# Names §3 mentions that are NOT prohibitions: permitted, or prose subjects.
NOT_PROHIBITIONS = {"window", "Report", "E", "cookies"}

def audit(contract_text, contract_bytes, scanner_js):
    out = []
    digest = hashlib.sha256(contract_bytes).hexdigest()
    out.append(("vendored contract is intact", digest == EXPECTED,
                f"sha256 {digest[:16]}..."))
    toks = clause_tokens(contract_text)
    if toks is None:
        out.append(("section 3 is present in the vendored copy", False,
                    "no '## 3.' heading -- the contract was restructured"))
        return out
    banned = banned_list(scanner_js)
    required = {t for t in toks if t not in NOT_PROHIBITIONS}
    missing = sorted(t for t in required
                     if t not in banned and t.lower() not in {b.lower() for b in banned})
    out.append(("scanner covers every construct section 3 names", not missing,
                f"{len(required)} named, {len(banned)} scanned"
                + (f" -- NOT COVERED: {missing}" if missing else "")))
    return out

def load():
    b = open(VENDORED, "rb").read()
    return b.decode("utf-8"), b, open(SCANNER, encoding="utf-8").read()

def show(rs):
    for n, ok, d in rs:
        print(f"  {n:<48} {'ok' if ok else 'FAILED'}   {d}")
    return all(o for _, o, _ in rs)

if __name__ == "__main__":
    text, raw, js = load()
    if "--selftest" in sys.argv:
        print("== check-contract self-test: both checks must be able to FAIL ==")
        ok = True
        def mut(label, t, b, j, expect):
            global ok
            if (t, b, j) == (text, raw, js):
                print(f"  {label:<46} BROKEN -- mutation was a no-op"); ok = False; return
            got = dict((n, o) for n, o, _ in audit(t, b, j)).get(expect)
            if got is None:
                print(f"  {label:<46} BROKEN -- '{expect}' not reported"); ok = False
            elif got:
                print(f"  {label:<46} BROKEN -- '{expect}' still passed"); ok = False
            else:
                print(f"  {label:<46} correctly fails '{expect}'")
        mut("contract edited under us", text + "\n", raw + b"\n", js,
            "vendored contract is intact")
        mut("A adds a clause my scanner misses",
            text.replace("- **No `eval`", "- **No `SharedWorker`.** New clause.\n- **No `eval`"),
            raw, js, "scanner covers every construct section 3 names")
        mut("a construct dropped from the scanner", text, raw,
            js.replace("'fetch',", ""),
            "scanner covers every construct section 3 names")
        if not all(o for _, o, _ in audit(text, raw, js)):
            print("  the real pair does not pass"); ok = False
        else:
            print("  the unmutated contract and scanner still pass both")
        sys.exit(0 if ok else 1)
    sys.exit(0 if show(audit(text, raw, js)) else 1)
