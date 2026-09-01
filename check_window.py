#!/usr/bin/env python3
"""check_window.py -- every number in `measured` must name the population it is over.

WHY THIS EXISTS. `measured` carried three populations in one block with no labels:

  in_window   damage over engagement runs        dps, damage_dealt, engaged_seconds
  all_lines   every matched line in the file     spells_landed, resists, crit_rate
  melee_time  auto-attack runs                   lanes, melee_seconds

A consumer that combined two of them got a number that is a share of nothing, and
B's own contract names the exact division that does it: `damage_dealt` is "the
denominator for share-of-output" and `spells_landed[*].damage_total` is what a
consumer attributes with. Measured 1 Sep 2026, four logs, engine unchanged:

  corpus/amp/..._full.txt   sum(damage_total)/damage_dealt = 202%
  corpus/amp/....txt                                         324%
  eql-meter Kenkyo sample                                     34%
  EQBuddy Testchar fixture                                     0%

Not a constant a reader could learn to subtract, and 202% is on the log this
engine was built against. Against the RIGHT denominator the same figure is 99.8%.

WHAT IT GATES. Not the arithmetic -- the LABELLING. A key added to `measured`
without a declared population fails here, because the next such key is the next
share of nothing.

    python3 check_window.py             run against the committed log
    python3 check_window.py --selftest  mutate the report, every check must flip
"""
import io, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
LOG = os.path.join(ROOT, "corpus", "amp", "eqlog_Shara_rivervale_20260829_full.txt")


def checks(measured):
    """Return [(name, ok, detail)]. Pure: takes a `measured` block, reads no file."""
    out = []
    w = measured.get("window")
    if not isinstance(w, dict):
        return [("measured.window is present and an object", False, f"got {type(w).__name__}")]
    kbp = w.get("keys_by_population")
    if not isinstance(kbp, dict):
        return [("window.keys_by_population is an object", False, f"got {type(kbp).__name__}")]

    declared, dupes = set(), []
    for pop, keys in sorted(kbp.items()):
        for k in keys:
            if k in declared:
                dupes.append(k)
            declared.add(k)
    out.append(("no key is declared in two populations", not dupes, f"duplicated: {sorted(dupes)}"))

    unassigned = sorted(set(measured) - declared)
    out.append(("every measured key names its population", not unassigned,
                f"undeclared: {unassigned}"))

    missing = sorted(declared - set(measured))
    out.append(("every declared key is actually emitted", not missing,
                f"declared but absent: {missing}"))

    iw, al = w.get("in_window", {}), w.get("all_lines", {})
    out.append(("window.in_window.damage == measured.damage_dealt",
                iw.get("damage") == measured.get("damage_dealt"),
                f"{iw.get('damage')} vs {measured.get('damage_dealt')}"))
    out.append(("window.melee_time.seconds == measured.melee_seconds",
                w.get("melee_time", {}).get("seconds") == measured.get("melee_seconds"),
                f"{w.get('melee_time', {}).get('seconds')} vs {measured.get('melee_seconds')}"))
    out.append(("all_lines contains in_window (damage and hits)",
                (al.get("damage") or 0) >= (iw.get("damage") or 0)
                and (al.get("hits") or 0) >= (iw.get("hits") or 0),
                f"all {al} vs in {iw}"))

    # THE ENDPOINT CONVENTION, added 1.4.0. The engaged window runs first hit to last
    # hit, so the final swing's time is outside the denominator. The size of that
    # choice is 14.04% on the corpus log and is NOT a constant -- 2.24% to 13.79% on
    # three others -- so it is computed per log, and REFUSED when the sample cannot
    # support it rather than emitted as noise.
    ep = w.get("endpoint") or {}
    out.append(("window.endpoint states its convention",
                bool(isinstance(ep.get("convention"), str) and ep.get("convention")),
                f"got {ep.get('convention')!r}"))
    sens, gaps = ep.get("sensitivity"), ep.get("gaps_measured")
    if isinstance(gaps, int) and gaps >= 30:
        out.append(("a sufficient sample yields a sensitivity",
                    isinstance(sens, float) and sens >= 1.0,
                    f"{gaps} gaps, sensitivity {sens!r}; must be >= 1.0 because a "
                    "LONGER denominator can only LOWER dps"))
    else:
        out.append(("an insufficient sample REFUSES, and says why",
                    sens is None and "NOT CLAIMED" in (ep.get("note") or ""),
                    f"{gaps} gaps, sensitivity {sens!r}"))

    sl = measured.get("spells_landed") or {}
    sp = sum(v.get("damage_total", 0) for v in sl.values())
    out.append(("sum(spells_landed.damage_total) fits inside its OWN population",
                sp <= (al.get("damage") or 0),
                f"{sp} of {al.get('damage')} = "
                f"{sp / al['damage']:.4f}" if al.get("damage") else f"{sp} of 0"))
    return out


def trap_is_reachable(measured):
    """THE PRECONDITION (HANDOFF section 20). The check above reads clean whether or
    not the fault it guards can occur. Establish that it CAN on this log before
    reading a clean result as evidence of anything: if the wrong denominator ever
    stops producing an impossible share here, the 202% in every header is stale and
    somebody must be told, not quietly passed."""
    sl = measured.get("spells_landed") or {}
    sp = sum(v.get("damage_total", 0) for v in sl.values())
    dd = measured.get("damage_dealt") or 0
    right = measured["window"]["all_lines"]["damage"]
    return sp / dd if dd else None, sp / right if right else None


def run(measured, label):
    rows = checks(measured)
    bad = 0
    for name, ok, detail in rows:
        print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {detail}"))
        bad += 0 if ok else 1
    print(f"  {len(rows)} checks on {label}, {bad} failing")
    return bad


if __name__ == "__main__":
    from gapengine import gap_engine
    # R73, adopted 1 Sep 2026: a command that reads a file set states the count it
    # actually opened. One file here, named, and its byte count printed -- so a
    # truncated or substituted log cannot pass as the log the 202% was measured on.
    with io.open(LOG, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    print(f"read 1 file: {os.path.relpath(LOG, ROOT)}  "
          f"{os.path.getsize(LOG)} bytes, {len(lines)} lines")
    measured = gap_engine(lines, {})["measured"]

    if "--selftest" not in sys.argv:
        wrong, right = trap_is_reachable(measured)
        print(f"  precondition: the WRONG denominator gives {wrong:.1%}, "
              f"the right one {right:.1%}")
        if wrong is None or wrong <= 1.0:
            print("  FAIL -- the trap this gate exists for is NOT reachable on this log. "
                  "Every header claiming 202% is now unsourced.")
            sys.exit(1)
        sys.exit(1 if run(measured, "the committed log") else 0)

    # --- self-test: each check must FAIL when its own condition is broken --------
    print("SELFTEST -- a mutated report must trip exactly the check that owns it")
    base = run(measured, "unmutated (must be 0 failing)")
    if base:
        print("SELFTEST FAILED: the unmutated report does not pass."); sys.exit(1)

    def mutate(fn, expect):
        import copy
        m = copy.deepcopy(measured)
        fn(m)
        names = {n for n, ok, _ in checks(m) if not ok}
        ok = expect in names
        print(f"  [{'ok' if ok else 'FAIL'}] {expect!r}" +
              ("" if ok else f"  -- did not fire; fired: {sorted(names)}"))
        return 0 if ok else 1

    bad = 0
    bad += mutate(lambda m: m.__setitem__("brand_new_number", 7),
                  "every measured key names its population")
    bad += mutate(lambda m: m["window"]["keys_by_population"]["in_window"].append("no_such_key"),
                  "every declared key is actually emitted")
    bad += mutate(lambda m: m["window"]["keys_by_population"]["annotation"].append("dps"),
                  "no key is declared in two populations")
    bad += mutate(lambda m: m["window"]["in_window"].__setitem__("damage", 1),
                  "window.in_window.damage == measured.damage_dealt")
    bad += mutate(lambda m: m["window"]["melee_time"].__setitem__("seconds", 1),
                  "window.melee_time.seconds == measured.melee_seconds")
    bad += mutate(lambda m: m["window"]["all_lines"].__setitem__("damage", 0),
                  "all_lines contains in_window (damage and hits)")
    # The one that reproduces the original defect: all_lines set to what
    # damage_dealt is, i.e. the report claiming the window population IS the whole
    # log. The spell total then overflows its own denominator -- 202%.
    bad += mutate(lambda m: m["window"]["all_lines"].__setitem__("damage", m["damage_dealt"]),
                  "sum(spells_landed.damage_total) fits inside its OWN population")
    bad += mutate(lambda m: m["window"]["endpoint"].__setitem__("convention", ""),
                  "window.endpoint states its convention")
    # A sensitivity BELOW 1.0 is arithmetically impossible -- a longer denominator can
    # only LOWER dps -- so it would mean the two figures came from different
    # numerators, which is the population defect this whole file exists for.
    bad += mutate(lambda m: m["window"]["endpoint"].__setitem__("sensitivity", 0.5),
                  "a sufficient sample yields a sensitivity")
    bad += mutate(lambda m: m["window"]["endpoint"].__setitem__("sensitivity", None),
                  "a sufficient sample yields a sensitivity")
    bad += mutate(lambda m: m.__setitem__("window", None),
                  "measured.window is present and an object")
    print(f"  {bad} self-test mutations failed to trip their check")
    sys.exit(1 if bad else 0)
