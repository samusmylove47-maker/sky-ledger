#!/usr/bin/env python3
"""check_selfhits.py -- a self-hit must never reach `damage_dealt`, in either engine.

RELAYED BY SESSION D, 1 Sep 2026, and checked against this engine rather than
accepted: a self-hit written WITHOUT a `by <spell>` clause cannot match the SPELL
shape (which requires that clause), falls through to the MELEE shape, and is emitted
as ordinary OUTGOING damage against a target named `yourself`.

THE HOLE WAS REAL HERE. The `yourself` guard existed only on the SPELL branch.

D also warned that the obvious fix -- dropping rows where actor equals target --
SILENTLY DROPS REAL DAMAGE, because a log cannot tell one entity hitting itself from
two entities sharing a name. Correct, and it does not apply to this engine: every
regex is anchored `^You`, so the string compared is the client's REFLEXIVE PRONOUN,
not a mob name. Two entities cannot both be called `yourself`. `Heart harpie` can be
two entities -- 10,383 lines of it, and it is a charm pet -- and that is exactly why
the same filter would be wrong in a third-person parser and is right in this one.

WHY THIS FILE EXISTS AT ALL, rather than a corpus measurement:

    SPELL branch, target `yourself`   202 lines, 92,822 damage   already excluded
    MELEE branch, target `yourself`     0 lines,      0 damage   the hole

Zero instances in 189,460 lines. **A corpus cannot test a guard for a shape it does
not contain** -- HANDOFF section 20. So the input here is CRAFTED, and the file
carries its own positive control: the non-self line in the same log MUST be counted,
or a zero total would be indistinguishable from a broken harness.

    python3 check_selfhits.py
    python3 check_selfhits.py --selftest   remove the guard; every check must flip
"""
import io, json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# CRAFTED. Both self shapes, plus one real hit as the positive control.
# The date is deliberately a SPACE-PADDED single-digit day: ctime() writes
# `Sun Sep  1`, `\d{2}` never matched it, and until 1 Sep 2026 both engines dropped
# every line on days 1-9 of any month. If that widening is ever reverted, every
# assertion below goes to zero at once and this file says so.
LINES = [
    "[Sun Sep  1 00:00:00 2026] You hit yourself for 500 points of damage.",
    "[Sun Sep  1 00:00:01 2026] You hit yourself for 40 points of unresistable damage by Cannibalize.",
    "[Sun Sep  1 00:00:02 2026] You slash a rat for 60 points of damage.",
    "[Sun Sep  1 00:00:40 2026] You slash a rat for 60 points of damage.",
]
SELF_MELEE, SELF_SPELL, REAL = 500, 40, 120


def audit(rep, label):
    m, cov = rep.get("measured", {}), rep.get("coverage", {})
    sd = cov.get("self_damage_excluded") or {}
    all_dmg = (m.get("window") or {}).get("all_lines", {}).get("damage")
    out = [
        # POSITIVE CONTROL FIRST, and it must be INDEPENDENT OF THE GUARD -- which
        # my first version was not. It asserted `all_dmg == REAL`, which is the same
        # sentence as the exclusion check one line down, so removing the guard
        # "failed the control" and the control proved nothing the check did not.
        # A control that moves with the thing it is controlling for is not a control.
        # Caught by the self-test, which is what the self-test is for.
        (f"{label}: positive control -- the harness can see damage at all",
         all_dmg is not None and all_dmg >= REAL,
         f"all_lines.damage {all_dmg}, needs at least {REAL}"),
        (f"{label}: the melee-shape self-hit is NOT in the damage total",
         all_dmg == REAL, f"all_lines.damage {all_dmg}, expected exactly {REAL}"),
        (f"{label}: it is REPORTED, not silently dropped",
         sd.get("melee_lines") == 1 and sd.get("melee_damage") == SELF_MELEE,
         f"melee_lines {sd.get('melee_lines')}, melee_damage {sd.get('melee_damage')}"),
        (f"{label}: the spell-shape self-hit is reported too",
         sd.get("spell_lines") == 1 and sd.get("spell_damage") == SELF_SPELL,
         f"spell_lines {sd.get('spell_lines')}, spell_damage {sd.get('spell_damage')}"),
        (f"{label}: no spell named for a self-hit reaches spells_landed",
         "Cannibalize" not in (m.get("spells_landed") or {}),
         f"spells_landed keys {sorted(m.get('spells_landed') or {})}"),
    ]
    return out


def js_report(lines):
    drv = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False)
    drv.write("var fs=require('fs');require(process.argv[2]);"
              "var l=fs.readFileSync(process.argv[3],'utf8').split('\\n');"
              "process.stdout.write(JSON.stringify(EQLSGapEngine.gapEngine(l,{})));")
    drv.close()
    lf = tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8")
    lf.write("\n".join(lines)); lf.close()
    try:
        r = subprocess.run(["node", drv.name, os.path.join(ROOT, "bundle", "eqls-gap-engine.js"),
                            lf.name], capture_output=True, text=True, check=True)
        return json.loads(r.stdout)
    finally:
        os.unlink(drv.name); os.unlink(lf.name)


def show(rows):
    bad = 0
    for n, ok, d in rows:
        print(f"  [{'ok' if ok else 'FAIL'}] {n}" + ("" if ok else f"  -- {d}"))
        bad += 0 if ok else 1
    return bad


if __name__ == "__main__":
    from gapengine import gap_engine
    import gapengine
    # R73: state the input actually used. It is crafted, not read, and saying so is
    # the point -- a corpus cannot test a guard for a shape it does not contain.
    print(f"read 0 files: {len(LINES)} CRAFTED lines, "
          f"{SELF_MELEE + SELF_SPELL} self damage, {REAL} real damage")

    if "--selftest" not in sys.argv:
        bad = show(audit(gap_engine(LINES, {}), "PY"))
        bad += show(audit(js_report(LINES), "JS"))
        print(f"  10 checks across both engines, {bad} failing")
        sys.exit(1 if bad else 0)

    print("SELFTEST -- with the guard removed, every check must flip")
    if show(audit(gap_engine(LINES, {}), "PY")):
        print("  the unmutated engine does not pass"); sys.exit(1)
    print("  unmutated engine passes")
    saved = gapengine.SELF_TARGETS
    try:
        gapengine.SELF_TARGETS = set()          # the pre-fix behaviour, exactly
        rows = audit(gap_engine(LINES, {}), "PY-no-guard")
        fired = {n for n, ok, _ in rows if not ok}
        must = [n for n, _, _ in rows if "positive control" not in n]
        bad = 0
        for n in must:
            ok = n in fired
            print(f"  [{'ok' if ok else 'FAIL'}] guard removed trips: {n}")
            bad += 0 if ok else 1
        ctrl = [n for n, ok, _ in rows if "positive control" in n and ok]
        print(f"  [{'ok' if ctrl else 'FAIL'}] the positive control STILL passes without "
              "the guard -- it measures the harness, not the guard")
        bad += 0 if ctrl else 1
    finally:
        gapengine.SELF_TARGETS = saved
    print(f"  {bad} checks failed to behave as required")
    sys.exit(1 if bad else 0)
