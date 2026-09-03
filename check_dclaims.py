#!/usr/bin/env python3
"""check_dclaims.py -- every item in my outbound Director channel must carry an END
CONDITION, and an item whose condition is MET must not still be open.

WHY. Asked for a status report on 3 Sep, I checked the list instead of recalling it and
found FOUR items still marked [OPEN] that were all closed -- one of them for eleven hours
after its substance was settled. That is the retirement-arm fault in my outbound channel,
on the day I built retirement arms for five other mechanisms and swept for exactly this
pattern. Section 79 enumerated six declaration mechanisms and DID NOT INCLUDE THE D-LIST,
which is my actual outbound. I checked the instruments and not the inbox.

THE DIRECTOR RULED FOR THIS and asked for the closed set so it can bind itself to the
vocabulary when it rules. So the set below is a CONTRACT, not a local convention.

A DATE IS NOT A CONDITION -- the Director's correction, already applied to the held
patches in check_holds.py, applied here one level up. Every condition is either something
an instrument evaluates, or explicitly one that nothing can: UNCHECKABLE is legal, honest,
and COUNTED, because a channel where every item is unverifiable satisfies every other
check and is worth nothing.

    python3 check_dclaims.py
    python3 check_dclaims.py --selftest
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.path.join(ROOT, "HANDOFF.md")

# What state an item is in. LIVE_STATES are the ones that must not outlive their condition.
STATES = ("OPEN", "RULED", "DONE", "CORRECTED", "ADVISORY")
LIVE_STATES = ("OPEN", "RULED")

DECL = re.compile(r"^\s*(D-\d+)\s+\[(\w+)[^\]]*\]\s+closes=(\S+)", re.M)


def _patch_ready(arg, text):
    """MET when the named patch has reached READY or SHIPPED. This is the condition that
    would have caught D-2 and D-6 -- both were 'ruling wanted' items whose substance had
    become a patch that was already built."""
    m = re.search(r"^HELD-PATCH:\s+" + re.escape(arg) + r"\s+\[(\w+)\]", text, re.M)
    if not m:
        return None, f"no declaration for {arg} -- cannot evaluate, REFUSING"
    return m.group(1) in ("READY", "SHIPPED"), f"{arg} is [{m.group(1)}]"


def _gate_exists(arg, text):
    """MET when a named gate file exists AND is wired into check.sh. Would have caught
    D-5, whose concern was answered by verbcensus.py being written and gated."""
    if not os.path.exists(os.path.join(ROOT, arg)):
        return False, f"{arg} does not exist"
    try:
        sh = io.open(os.path.join(ROOT, "check.sh"), encoding="utf-8").read()
    except OSError as e:
        return None, f"cannot read check.sh ({e}) -- REFUSING"
    return arg in sh, f"{arg} exists and is {'in' if arg in sh else 'NOT in'} check.sh"


# The contract. The Director binds itself to this vocabulary when it rules.
CONDITIONS = {
    "PATCH-READY": _patch_ready,      # closes=PATCH-READY:P-3
    "GATE-EXISTS": _gate_exists,      # closes=GATE-EXISTS:verbcensus.py
    # Uncheckable by me, legal, and COUNTED:
    "AWAITING-RULING": None,          # I cannot detect a ruling; the Director closes it
    "SEQUENCED": None,                # ruled, waiting on an event outside my instruments
    "ADVISORY": None,                 # a standing note, never closes, not a request
}


def audit(text):
    out, unverifiable = [], []
    decls = DECL.findall(text or "")

    # POSITIVE CONTROL FIRST: a pattern matching nothing passes every check below it.
    probe = DECL.search("                 D-9 [OPEN, 1 Jan] closes=ADVISORY  text\n")
    out.append(("the item pattern matches a known-good line", bool(probe),
                f"probe -> {probe.group(1) if probe else None}"))
    out.append(("at least one item is declared", bool(decls), f"{len(decls)} found"))

    # Every LIVE item must carry a condition. A closed item does not need an end
    # CONDITION -- it has an end. Requiring one everywhere would be ceremony, and
    # ceremony is what people stop doing.
    live = set(re.findall(r"^\s*(D-\d+)\s+\[(?:" + "|".join(LIVE_STATES) + r")\b",
                          text or "", re.M))
    with_cond = {d[0] for d in decls}
    out.append(("every LIVE item carries closes=", live <= with_cond,
                f"live without a condition: {sorted(live - with_cond)} -- an open item "
                f"with no end condition is one nobody can retire"))

    for did, state, cond in decls:
        out.append((f"{did}: state is one of {list(STATES)}", state in STATES,
                    f"got {state!r}"))
        key, _, arg = cond.partition(":")
        out.append((f"{did}: closes= names a known condition", key in CONDITIONS,
                    f"got {cond!r}. Legal: {sorted(CONDITIONS)}"))
        if key not in CONDITIONS:
            continue
        fn = CONDITIONS[key]
        if fn is None:
            unverifiable.append(did)
            continue
        met, why = fn(arg, text)
        out.append((f"{did}: its condition is evaluable at all", met is not None,
                    f"{why} -- an instrument that cannot look must REFUSE, not pass"))
        if met is None:
            continue
        out.append((f"{did}: its end condition has NOT been met",
                    not (state in LIVE_STATES and met),
                    f"{why}. This item is CLOSED and still marked [{state}]. Retire it "
                    f"with what closed it -- do not weaken the condition."))

    # Never silent: a channel where everything is unverifiable passes everything above.
    out.append((f"items with an UNVERIFIABLE end condition: {len(unverifiable)}", True,
                f"{unverifiable}"))
    return out


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("SELFTEST -- an item outliving its condition must fire")
        bad = 0

        def chk(name, ok, d=""):
            global bad
            print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1

        def fired(t):
            return [n for n, ok, _ in audit(t) if not ok]

        BASE = ("HELD-PATCH: P-1 [READY] ground=X until=Y -- a real patch declaration\n"
                "                 D-1 [ADVISORY, 1 Jan] closes=ADVISORY  a standing note\n")
        chk("a well-formed channel passes", not fired(BASE), f"{fired(BASE)}")
        # THE FOUR THAT WENT STALE WOULD HAVE BEEN CAUGHT. This is the retro-test.
        stale = BASE + "                 D-2 [OPEN, 1 Jan] closes=PATCH-READY:P-1  ruling wanted\n"
        chk("an OPEN item whose patch is READY fires -- the D-2 case",
            any("end condition has NOT been met" in x for x in fired(stale)), f"{fired(stale)}")
        live = BASE.replace("[READY]", "[HELD]") + \
            "                 D-2 [OPEN, 1 Jan] closes=PATCH-READY:P-1  ruling wanted\n"
        chk("...and does NOT fire while the patch is still HELD",
            not any("end condition has NOT been met" in x for x in fired(live)), f"{fired(live)}")
        chk("a DONE item does not fire even when its condition is met",
            not any("end condition has NOT been met" in x for x in
                    fired(BASE + "                 D-2 [DONE, 1 Jan] closes=PATCH-READY:P-1  x\n")), "")
        chk("a free-text condition is refused",
            any("names a known condition" in x for x in
                fired(BASE + "                 D-3 [OPEN, 1 Jan] closes=soon  x\n")), "")
        chk("a condition naming a patch that does not exist REFUSES, not passes",
            any("evaluable at all" in x for x in
                fired(BASE + "                 D-4 [OPEN, 1 Jan] closes=PATCH-READY:P-99  x\n")), "")
        chk("a LIVE item with NO closes= at all is caught",
            any("carries closes=" in x for x in
                fired(BASE + "                 D-5 [OPEN, 1 Jan]  no condition here\n")), "")
        chk("...but a DONE item needs no end CONDITION -- it has an end",
            not any("carries closes=" in x for x in
                    fired(BASE + "                 D-5 [DONE, 1 Jan]  closed already\n")), "")
        chk("NO items at all is caught, not read as clean",
            any("at least one item" in x for x in fired("nothing")), "")
        unc = BASE + "                 D-6 [OPEN, 1 Jan] closes=AWAITING-RULING  x\n"
        chk("UNCHECKABLE passes AND is counted",
            not fired(unc) and any("UNVERIFIABLE end condition: 2" in n
                                   for n, _, _ in audit(unc)), f"{fired(unc)}")
        print(f"  {bad} self-test checks failed")
        sys.exit(1 if bad else 0)

    text = io.open(HANDOFF, encoding="utf-8").read()
    print(f"read HANDOFF.md ({len(text):,} bytes)")
    rows = audit(text)
    bad = 0
    for n, ok, d in rows:
        print(f"  [{'ok' if ok else 'FAIL'}] {n}" + ("" if ok else f"  -- {d}"))
        bad += 0 if ok else 1
    print(f"  {len(rows)} checks, {bad} failing")
    sys.exit(1 if bad else 0)
