#!/usr/bin/env python3
"""percharacter.py -- WHICH of model4's inputs can a single character's LOG supply?

CRITICAL-PATH TASK 2, and this is deliberately NOT the fitted per-character model I
declared in HANDOFF section 39.5. It is the audit that has to come first, because the
first thing I did when I pointed the model at a real log was discover the log does not
carry most of what the model needs:

    stance      the classifier REFUSED on the corpus log, and stance is a factor of
                TWO on melee output
    auto-attack 86 non-crit landed swings against a measured 1,372.9 dps, because the
                character is a Bard doing almost all of it through one song

Fitting a per-character model on top of that would have produced a number whose
uncertainty nobody could see. So this file answers the prior question and states its
own surface: for each input `model4.evaluate` consumes, is it OBSERVED from the log,
REFUSED (observable in principle, not supportable by THIS log), or ASSUMED (no log can
supply it)? And where an input is both observed AND carries a model constant, the two
are printed side by side with the sample size, because that comparison is the whole
point of having a measured baseline.

NOTHING HERE NAMES AN ITEM AND NOTHING READS WORN STATS. Both are standing refusals in
gapengine.py and they are not relaxed by being asked from a different file.

NO COMPARISON IS CLAIMED BELOW n = 30. That is the same floor `_stance` uses for its
even-damage share and `window.endpoint` uses for its inter-hit interval; reusing it
rather than inventing a third is deliberate.

    python3 percharacter.py [log]
    python3 percharacter.py --selftest
"""
import io, os, statistics as st, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import gapengine as G
import model4 as M

N_FLOOR = 30
AUTO = {"crush", "slash", "pierce", "hit", "punch"}
DEFAULT_LOG = os.path.join(ROOT, "corpus", "amp", "eqlog_Shara_rivervale_20260829_full.txt")

# HOW each input model4.evaluate consumes can be obtained. The CLASSIFICATION is
# typed; every VALUE below is derived at run time. A row here that no measurement
# reaches is caught by the self-test, not by my memory of having written one.
#   observed  a log supplies it directly
#   refusable a log supplies it WHEN the sample is large enough; this log may not
#   assumed   no log can supply it -- it needs the client, a catalogue, or the fight
# The 5th field is the ROW PREFIX that satisfies this input. It exists because the
# first version matched by `name.split()[0]`, so "ability lane rates" went looking for
# a row starting "ability" while the rows are named "lane rate: bash". The check fired
# and it was right to: a reach-test that guesses at a name is R80's fault exactly -- a
# lookup that succeeds or fails on a STRING and reports it as a fact about coverage.
INPUTS = [
    ("swing land rate",   "refusable", "P_LAND_BAL",  "landed / attempted auto-attack",     "swing land rate"),
    ("crit rate",         "refusable", "CRIT_RATE",   "crit / (crit + non-crit) swings",    "crit rate"),
    ("crit multiplier",   "refusable", "CRIT_MULT",   "mean crit / mean non-crit hit",      "crit multiplier"),
    ("stance",            "refusable", "STANCE_DMG",  "even-damage share of non-crit melee","stance"),
    ("ability lane rates","refusable", "LANE_RATE_MAX","lane attempts per melee second",    "lane rate:"),
    ("class set",         "refusable", "OFFENSE",     "which classes own the observed lanes","class set"),
    ("weapon damage",     "assumed",   None,          "a log does not show worn stats",     "weapon damage"),
    ("weapon delay",      "assumed",   None,          "a log does not show worn stats",     "weapon delay"),
    ("haste",             "assumed",   "HASTE_CAP",   "swing rate confounds haste with delay","haste"),
    ("target mitigation", "assumed",   "MITF",        "a property of the fight, not the log","target mitigation"),
    ("wrath / ATK",       "assumed",   "STR_MOD",     "worn ATK is not in a log",           "wrath / ATK"),
    ("strikethrough",     "assumed",   "STRIKETHROUGH","class-conditional, needs the class","strikethrough"),
    ("buff uptime",       "assumed",   None,          "not emitted as a line this parser reads","buff uptime"),
]

# A constant is only comparable to an observation when the CONDITIONS it was measured
# under are established. model4's CRIT_RATE, P_LAND_BAL and the lane ceilings are all
# level-50 OFFENSIVE-stance figures. If the stance is not identified, printing
# `observed / model` beside them is a number in the wrong column -- the exact fault
# this repository has spent a week finding in other instruments. So the ratio is
# SUPPRESSED, with its reason, until its precondition holds. HANDOFF section 20.
NEEDS_STANCE = {"swing land rate", "crit rate", "crit multiplier", "lane rate:"}


def observe(lines):
    """Everything this file measures, in one pass over the parsed events."""
    ev, kills, months, n_lines = G._parse(lines)
    hits, resists, selfhit = G._hits(ev, kills)
    lane_t, lane_dmg, melee_s, auto_n = G._lanes(ev, hits)
    rep = G.gap_engine(lines, {})

    mel = [h for h in hits if h["kind"] == "melee" and h["verb"] in AUTO and not h["kill"]]
    nc = [h["amt"] for h in mel if not h["crit"]]
    cr = [h["amt"] for h in mel if h["crit"]]
    lanes_seen = sorted(set(lane_t) & set(M.LANE_OWNER))
    # The log narrows the class set: a lane appears only if somebody in the trio owns
    # it. Intersection over observed lanes, union within a lane. This is a DERIVATION
    # FROM THE LOG, not a catalogue lookup, and it never names an item.
    classes = None
    for v in lanes_seen:
        owners = M.LANE_OWNER[v]
        classes = set(owners) if classes is None else (classes | set(owners))
    return dict(
        n_lines=n_lines, parse=rep["coverage"].get("parse", {}),
        swings_landed=len(mel), swings_attempted=auto_n, melee_s=melee_s,
        nc=nc, cr=cr, lanes=lane_t, lanes_seen=lanes_seen,
        class_candidates=sorted(classes) if classes else [],
        stance=rep["measured"].get("stance_inferred"),
        stance_evidence=rep["measured"].get("stance_evidence"),
        dps=rep["measured"].get("dps"),
    )


def rows(o):
    """[(input, verdict, n, observed, model, note)] -- verdict is derived, never typed."""
    out = []

    def add(name, kind, n, obs, model, note):
        if kind == "assumed":
            v = "ASSUMED"
        elif n is None or n < N_FLOOR:
            v = "REFUSED"
        else:
            v = "OBSERVED"
        out.append((name, v, n, obs, model, note))

    n_sw = o["swings_attempted"]
    add("swing land rate", "refusable", n_sw,
        (o["swings_landed"] / n_sw) if n_sw else None, M.P_LAND_BAL,
        "attempts include misses; model figure is the BALANCED baseline")
    n_c = len(o["nc"]) + len(o["cr"])
    add("crit rate", "refusable", n_c,
        (len(o["cr"]) / n_c) if n_c else None, M.CRIT_RATE,
        "auto-attack swings only, killing blows excluded")
    add("crit multiplier", "refusable", len(o["cr"]),
        (st.mean(o["cr"]) / st.mean(o["nc"])) if o["cr"] and o["nc"] else None,
        M.CRIT_MULT, "ratio of two means; n is the CRIT count, the scarcer side")
    add("stance", "refusable", len(o["nc"]) if o["stance"] else 0,
        o["stance"], M.STANCE_DMG, "engine's own classifier; None means NOT identified")
    for v in o["lanes_seen"]:
        n_l = len(o["lanes"][v])
        add(f"lane rate: {v}", "refusable", n_l,
            (n_l / o["melee_s"]) if o["melee_s"] else None, M.LANE_RATE_MAX.get(v),
            "attempts per MELEE second, not engaged second")
    add("class set", "refusable", len(o["lanes_seen"]) and n_sw,
        ",".join(o["class_candidates"]) or None, None,
        f"from lanes {o['lanes_seen']}; a UNION, so it narrows and never identifies")
    for name, kind, const, how, _pref in INPUTS:
        if kind == "assumed":
            add(name, "assumed", None, None, getattr(M, const, None) if const else None, how)
    return out


def audit(o, r=None):
    """Checks over the audit itself. Returns [(name, ok, detail)].

    Takes an optional pre-built row list so the self-test can INJECT a bad row
    directly. The first version could only mutate the observations and hope the
    derivation produced the row it wanted -- which is a mutation that may not
    produce the defect, D's own harness fault, and it left two of these four
    checks with no proof they could fire at all."""
    r = rows(o) if r is None else r
    out = []
    names = {x[0] for x in r}
    declared = {n for n, k, _, _, _ in INPUTS if k == "assumed"}
    out.append(("every ASSUMED input in the table is reported", declared <= names,
                f"missing {sorted(declared - names)}"))
    refusable = [(n, p) for n, k, _, _, p in INPUTS if k == "refusable"]
    # Matched on the DECLARED prefix, not a guessed one. See the note on INPUTS.
    unreached = {n for n, p in refusable if not any(x[0].startswith(p) for x in r)}
    out.append(("every REFUSABLE input is reached by a measurement", not unreached,
                f"unreached {sorted(unreached)}"))
    below = [x for x in r if x[1] == "REFUSED" and x[2] is not None and x[2] >= N_FLOOR]
    out.append((f"nothing is REFUSED while its n is at or above {N_FLOOR}", not below,
                f"{[(x[0], x[2]) for x in below]}"))
    above = [x for x in r if x[1] == "OBSERVED" and (x[2] is None or x[2] < N_FLOOR)]
    out.append((f"nothing is OBSERVED on fewer than {N_FLOOR} samples", not above,
                f"{[(x[0], x[2]) for x in above]}"))
    # THE PRECONDITION. A run where nothing is observable proves nothing about the
    # audit -- it reads identically to an audit that cannot observe anything at all.
    out.append(("at least one input IS observed on this log",
                any(x[1] == "OBSERVED" for x in r),
                f"{sum(1 for x in r if x[1] == 'OBSERVED')} observed"))
    return out


def report(o):
    print(f"  parse: {o['parse'].get('verdict')}  {o['parse'].get('lines_in')} lines, "
          f"{o['parse'].get('lines_with_timestamp')} timestamped   dps={o['dps']}")
    print()
    stance_known = o["stance"] is not None
    print(f"  {'model4 input':<22} {'verdict':<9} {'n':>6}  {'observed':>12}  {'model':>10}")
    print(f"  {'-'*22} {'-'*9} {'-'*6}  {'-'*12}  {'-'*10}")
    for name, v, n, obs, model, note in rows(o):
        fo = f"{obs:12.4f}" if isinstance(obs, float) else f"{str(obs):>12}"
        fm = f"{model:10.4f}" if isinstance(model, float) else f"{str(model):>10}"
        print(f"  {name:<22} {v:<9} {str(n if n is not None else '-'):>6}  {fo}  {fm}")
        if v == "OBSERVED" and isinstance(obs, float) and isinstance(model, float) and model:
            needs = any(name.startswith(p) for p in NEEDS_STANCE)
            if needs and not stance_known:
                print(f"  {'':22} RATIO SUPPRESSED: this model constant is a level-50 "
                      "OFFENSIVE figure and the stance is NOT identified on this log, "
                      "so observed/model would compare two different conditions.")
            else:
                print(f"  {'':22} {'':9} {'':6}  ratio observed/model = {obs/model:.3f}")
        if v == "REFUSED":
            print(f"  {'':22} NOT CLAIMED: {note}")


if __name__ == "__main__":
    path = DEFAULT_LOG
    for a in sys.argv[1:]:
        if not a.startswith("--"):
            path = a
    # R73: state the file set actually opened.
    print(f"read 1 file: {os.path.relpath(path, ROOT)}  {os.path.getsize(path)} bytes")
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        o = observe(fh.readlines())

    if "--selftest" not in sys.argv:
        report(o)
        print()
        bad = 0
        for n, ok, d in audit(o):
            print(f"  [{'ok' if ok else 'FAIL'}] {n}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1
        sys.exit(1 if bad else 0)

    print("SELFTEST -- each check must fail when its own condition is broken")
    if any(not ok for _, ok, _ in audit(o)):
        print("  the real log does not pass"); sys.exit(1)
    print("  the real log passes")
    import copy
    base = rows(o)
    bad = 0

    def inject(label, fn, expect):
        global bad
        r = [list(x) for x in base]
        fn(r)
        r = [tuple(x) for x in r]
        fired = {n for n, ok, _ in audit(o, r) if not ok}
        ok = expect in fired
        print(f"  [{'ok' if ok else 'FAIL'}] {label}"
              + ("" if ok else f"  -- fired {sorted(fired)}"))
        bad += 0 if ok else 1

    inject(f"an OBSERVED row on fewer than {N_FLOOR} samples is caught",
           lambda r: r.__setitem__(0, [r[0][0], "OBSERVED", 3, r[0][3], r[0][4], r[0][5]]),
           f"nothing is OBSERVED on fewer than {N_FLOOR} samples")
    inject(f"a REFUSED row whose n is at or above {N_FLOOR} is caught",
           lambda r: r.__setitem__(0, [r[0][0], "REFUSED", 999, r[0][3], r[0][4], r[0][5]]),
           f"nothing is REFUSED while its n is at or above {N_FLOOR}")
    inject("an ASSUMED input dropped from the report is caught",
           lambda r: [r.remove(x) for x in list(r) if x[0] == "target mitigation"],
           "every ASSUMED input in the table is reported")
    inject("a REFUSABLE input no measurement reaches is caught",
           lambda r: [r.remove(x) for x in list(r) if x[0].startswith("lane rate:")],
           "every REFUSABLE input is reached by a measurement")
    inject("a run where NOTHING is observed is caught, not read as clean",
           lambda r: [x.__setitem__(1, "REFUSED") for x in r if x[1] == "OBSERVED"],
           "at least one input IS observed on this log")
    print(f"  {bad} self-test checks failed")
    sys.exit(1 if bad else 0)
