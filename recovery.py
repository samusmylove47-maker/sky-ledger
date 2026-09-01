#!/usr/bin/env python3
"""recovery.py -- WHAT THE PUBLISHED NUMBERS WOULD LOSE IF THE VERB SET REGRESSED,
measured on real client-written logs by running the SAME engine twice: as shipped, and
narrowed in memory back to where it stood before the Tuesday bundle.

*** THIS FILE WAS INVERTED WHEN THE BUNDLE LANDED AND THAT IS DELIBERATE. *** It was
built to FORECAST what P-3 would recover, by widening a narrow engine. P-3 is applied,
so the forecast is spent; it now narrows the shipped engine instead and measures the
same delta from the other side. Identical number, different meaning: a forecast became
a REGRESSION GUARD. A tool whose premise is settled by the fix it measured has to be
re-pointed or retired -- leaving it aimed at a world that no longer exists is how a
green check stops meaning anything.

WHY IT IS BUILT THIS WAY. The obvious measurement -- "invisible damage over total
damage in the file" -- needs two populations to agree, and they do not: `damage_dealt`
is scoped to engaged runs and a file total is not. That mismatch is the 202% defect
this repository already shipped once. Running the engine twice makes the populations
identical BY CONSTRUCTION: same window logic, same exclusions, same everything except
the verb alternation. The delta between the two runs IS the cost, on the numbers a
reader actually sees.

NOTHING IS SHIPPED HERE. The widened patterns exist only inside this process, are
restored in a `finally`, and the file asserts the engine's own constants are back
before it prints. This measures what P-3 WOULD do; it does not do it.

AND THE SHARE THAT MATTERS IS NOT THE ONE I PUBLISHED. `19.66% of first-person melee
damage` is true and it is not the meter's error, because `damage_dealt` counts spells
too. For a caster the same missing verbs cost a rounding error; for a melee character
they cost a fifth of the number. Per-log, or it is not an answer.

    python3 recovery.py
    python3 recovery.py --selftest
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gapengine as G

# *** INVERTED WHEN THE TUESDAY BUNDLE LANDED. ***
# This file used to WIDEN a narrow shipped engine to measure what P-3 would recover.
# P-3 is now applied, so it NARROWS the shipped engine back to the pre-bundle verb set
# and measures the same delta from the other side. The number is identical and its
# meaning is not: it was a forecast and it is now a REGRESSION GUARD -- if someone
# removes the verbs, this reports the damage that goes missing, on real logs.
# A tool whose premise is fixed by the fix it measured is a tool that has to be
# re-pointed or retired, and silently leaving it pointing at the old world is how a
# passing test stops meaning anything.
REMOVE_LANE = ("frenzy", "smite")
REMOVE_UNCLASSIFIED = ("cleave", "claw", "reave", "bite", "slice", "sting", "smash",
                       "shoot")
# `frenzy` takes a preposition in 735 of 735 lines: `You frenzy ON a mob for N`.
# Without `(?:on )?` the target captures as "on a wan ghoul knight", which splits
# target grouping and -- worse -- slips past SELF_TARGETS, reopening P-2 on this verb.
PREPOSITION = r"(?:on )?"


def narrowed():
    """The MELEE pattern as it stood BEFORE the Tuesday bundle. Built by subtracting
    from the engine's own live constants rather than retyped, so it cannot silently
    disagree with what is deployed."""
    verbs = sorted((G.AUTO_VERBS | G.LANE_VERBS | G.UNCLASSIFIED_VERBS)
                   - set(REMOVE_LANE) - set(REMOVE_UNCLASSIFIED))
    return re.compile(r"^You (" + "|".join(verbs) + r")(?:es)? "
                      r"(.+?) for (\d+) points of damage\.(\s*\(Critical\))?$")


def run(lines, pre_bundle):
    """One engine run. `pre_bundle` narrows the verb set back to where it stood before
    the Tuesday bundle, for the duration, and puts every constant back whether or not
    the engine raises."""
    if not pre_bundle:
        return G.gap_engine(list(lines))
    old = (G.MELEE, G.LANE_VERBS, G.UNCLASSIFIED_VERBS)
    try:
        G.MELEE = narrowed()
        G.LANE_VERBS = G.LANE_VERBS - set(REMOVE_LANE)
        G.UNCLASSIFIED_VERBS = G.UNCLASSIFIED_VERBS - set(REMOVE_UNCLASSIFIED)
        return G.gap_engine(list(lines))
    finally:
        G.MELEE, G.LANE_VERBS, G.UNCLASSIFIED_VERBS = old


def measured(rep):
    m = getattr(rep, "measured", None)
    if m is None and isinstance(rep, dict):
        m = rep.get("measured")
    return m or {}


def client_logs():
    """Only logs carrying the name the EverQuest client writes. The 134 other files
    on this machine are other projects' generated fixtures; a recovery figure
    averaged over them measures a generator."""
    out = []
    for d, dirs, names in os.walk("/home/user"):
        dirs[:] = [x for x in dirs if x != ".git"]
        for n in names:
            if n.startswith("eqlog_") and n.endswith(".txt"):
                out.append(os.path.join(d, n))
    seen, uniq = set(), []
    for p in sorted(out):
        try:
            b = io.open(p, "rb").read()
        except OSError:
            continue
        import hashlib
        h = hashlib.sha256(b).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        uniq.append(p)
    return uniq


FIELDS = ("dps", "damage_dealt", "hits_counted", "engaged_seconds",
          "auto_attack_attempts", "melee_seconds")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("SELFTEST -- the SHIPPED engine must see what the pre-bundle one could not")
        bad = 0

        def chk(name, ok, d=""):
            global bad
            print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1

        S = "[Mon Aug 31 12:00:%02d 2026] "
        body = [S % i + "You slash a gnoll for 10 points of damage." for i in range(0, 40, 2)]
        body += [S % i + "You cleave a gnoll for 100 points of damage." for i in (5, 15, 25)]
        shipped, pre = run(body, False), run(body, True)
        w, b = measured(shipped), measured(pre)
        # POSITIVE CONTROL FIRST: if the widened run cannot differ from the shipped
        # one, every comparison below is vacuous and this file measures nothing.
        chk("THE SHIPPED ENGINE NOW SEES IT -- P-3 is live, not merely written up",
            w.get("damage_dealt", 0) > b.get("damage_dealt", 0),
            f"pre-bundle {b.get('damage_dealt')} -> shipped {w.get('damage_dealt')}")
        chk("the recovered amount is exactly the cleave damage",
            w.get("damage_dealt", 0) - b.get("damage_dealt", 0) == 300,
            f"delta {w.get('damage_dealt', 0) - b.get('damage_dealt', 0)}")
        chk("the PRE-BUNDLE engine was genuinely blind to it",
            b.get("damage_dealt") == 200, f"got {b.get('damage_dealt')}")
        # The engine's live constants must be exactly as they were.
        chk("engine constants restored after a narrowed run",
            "cleave" in G.MELEE.pattern and "cleave" in G.UNCLASSIFIED_VERBS
            and "frenzy" in G.LANE_VERBS,
            "the in-memory narrowing LEAKED and left the shipped engine crippled")
        boom = G.gap_engine
        try:
            G.gap_engine = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x"))
            try:
                run(body, True)
            except RuntimeError:
                pass
        finally:
            G.gap_engine = boom
        chk("constants intact after the engine RAISES mid-narrowing",
            "cleave" in G.MELEE.pattern and "cleave" in G.UNCLASSIFIED_VERBS
            and "frenzy" in G.LANE_VERBS,
            "a raising engine left the narrowing in place")
        # NEGATIVE CONTROL for the two restore checks above: they are string tests,
        # and a string test that can only pass proves nothing. Break it on purpose.
        _keep = G.MELEE
        G.MELEE = narrowed()
        chk("...and those two restore checks CAN fail",
            "cleave" not in G.MELEE.pattern, "the leak detector is blind")
        G.MELEE = _keep
        # frenzy's preposition must actually be handled
        fr = [S % i + "You slash a gnoll for 10 points of damage." for i in range(0, 40, 2)]
        fr += [S % i + "You frenzy on a gnoll for 50 points of damage." for i in (5, 15, 25)]
        chk("`You frenzy ON a mob` is read by the SHIPPED pattern",
            measured(run(fr, False)).get("damage_dealt", 0) == 350,
            f"got {measured(run(fr, False)).get('damage_dealt')}")
        chk("...and the pre-bundle pattern could NOT read it",
            measured(run(fr, True)).get("damage_dealt", 0) == 200,
            f"got {measured(run(fr, True)).get('damage_dealt')}")
        print(f"  {bad} self-test checks failed")
        sys.exit(1 if bad else 0)

    logs = client_logs()
    print(f"OPENED {len(logs)} unique client-written logs (eqlog_<Char>_<server>.txt).")
    print("Everything else on this machine is another project's generated fixture and")
    print("is deliberately excluded -- see HANDOFF.md section 69.\n")
    dps_moves = []
    for p in logs:
        _l = io.open(p, encoding="utf-8", errors="replace").read().splitlines()
        base = measured(run(_l, True))    # pre-bundle
        wide = measured(run(_l, False))   # shipped, with the bundle applied
        name = os.path.basename(p)
        moved = [(f, base.get(f), wide.get(f)) for f in FIELDS
                 if base.get(f) != wide.get(f)]
        fix = "fixture" in name.lower()
        print(f"  {name}" + ("   <-- A FIXTURE. Excluded from the range below."
                             if fix else ""))
        if not moved:
            print("    no published figure moves -- this log contains none of the "
                  "three verbs\n")
            continue
        for f, b, w in moved:
            try:
                pct = 100.0 * (w - b) / b if b else float("inf")
                print(f"    {f:<22} {b!s:>12} -> {w!s:>12}   {pct:+7.2f}%")
                if f == "dps" and not fix:
                    dps_moves.append((name, b, w, pct))
            except TypeError:
                print(f"    {f:<22} {b!s:>12} -> {w!s:>12}")
        print()

    print("THE PUBLISHED dps FIGURE, on client-written logs that contain these verbs:")
    if not dps_moves:
        print("  none moved.")
    else:
        lo = min(d[3] for d in dps_moves)
        hi = max(d[3] for d in dps_moves)
        for n, b, w, pct in sorted(dps_moves, key=lambda x: x[3]):
            print(f"  {pct:+7.2f}%   {b} -> {w}   {n}")
        print(f"\n  RANGE {lo:+.2f}% to {hi:+.2f}% across {len(dps_moves)} logs.")
    print("""
  READ THE SIGN. It is not all one direction, and that is the finding.
  A melee character's dps is UNDER-reported: the missing hits are damage.
  A caster's dps is OVER-reported: the missing hits contribute almost no damage
  but they DO mark engaged time, so recovering them grows the denominator faster
  than the numerator and the published dps FALLS.
  So "up to 20% more melee damage counted" -- which is what I told Session B --
  is not a statement about any number a reader sees. The share of first-person
  melee damage that is invisible (19.66%) and the error in the published dps are
  different quantities with different signs, and only the second one is the tool's
  accuracy.""")
