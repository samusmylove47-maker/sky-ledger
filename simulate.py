#!/usr/bin/env python3
"""simulate.py -- ROUND-TRIP ACCURACY. Build a log from KNOWN parameters, run the
engine over it, and measure how far what comes back is from what went in.

WHAT THIS DOES AND DOES NOT TEST, stated first because the number is worthless
without it.

  IT TESTS   the ARITHMETIC and the EXCLUSIONS: engagement segmentation across gaps
             and month boundaries, the engaged denominator, the melee denominator,
             crit rate, even-damage share, per-lane rates, spell landing counts and
             medians, killing-blow exclusion, self-damage exclusion, the population
             totals in `window`.
  IT DOES NOT TEST the GRAMMAR. The generator writes lines in the same shape the
             parser reads, so a line the real client writes differently is invisible
             to this file in both directions. That is the rank.py stub-oracle fault
             and it cannot be designed away here.
             *** THE SENTENCE THAT STOOD HERE SAID THE GRAMMAR QUESTION IS "answered
             by the 117 REAL logs the engine is also run over". THAT WAS FALSE. ***
             There were not 117 real logs. There were 416 files, 139 unique after
             de-duplication, and 5 carrying the name the EverQuest client writes --
             one of those 5 is itself named `_fixture`. The rest are other projects'
             generated test files, so the grammar question was not answered by them
             and this file's blindness was covered by nothing.
             It is answered now by `verbcensus.py` (which verbs occur, in what
             population) and `recovery.py` (what the missing ones cost the PUBLISHED
             numbers: -1.10% to +16.62% on `dps`, and the sign is NOT constant).
             See HANDOFF.md sections 69 and 70.
             THE VERBS GENERATED BELOW ARE `slash`, `kick` AND `hit` -- three, all
             three already in the engine's alternation. THIS HARNESS CANNOT EMIT A
             LINE THE ENGINE CANNOT READ, so the figure it prints is computed over a
             corpus assembled out of the engine's own vocabulary. That is a real
             measurement of the ARITHMETIC and it is not a measurement of the tool.
  IT DOES NOT TEST the MODEL. model4's ceiling is 4.59x the measured median and that
             gap is published in residual.py. Nothing here touches it.

So: this measures whether the meter counts correctly, not whether it reads EverQuest
correctly and not whether the model predicts EverQuest correctly. Three different
questions and only the first is simulable.

    python3 simulate.py            50 seeds, full report
    python3 simulate.py --selftest a deliberately broken engine must score WORSE
"""
import io, os, random, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gapengine as G

MONTHS = ["Jul", "Aug", "Sep"]
MOBS = ["a sand giant", "a cloud giant", "a pegasus", "a griffon", "a sky drake"]


def synth(seed):
    """Return (lines, truth). Every quantity in `truth` is decided HERE, before the
    engine sees anything, and never read back out of the engine's own output."""
    rnd = random.Random(seed)
    n_eng = rnd.randint(3, 7)
    crit_rate = rnd.choice([0.05, 0.10, 0.15, 0.20])
    even_share = rnd.choice([0.50, 0.93])          # Balanced / Offensive signatures
    lane_rate = rnd.choice([0.20, 0.35, 0.50])     # kick attempts per melee second
    # ADDED AFTER THE 1.6.0 BUNDLE, AND THE REASON IS THAT THE BUNDLE WAS UNCOVERED.
    # This harness published "100.0% exact recovery" over a corpus generating slash,
    # kick and hit -- NONE of the ten verbs 1.6.0 added. Every new path shipped
    # untested by the instrument that certifies the number: the `(?:on )?` group, the
    # unclassified routing, and two new lane ceilings. A harness that cannot produce
    # the input a change handles does not test that change, and the score it prints
    # afterwards is the same score it printed before.
    frenzy_rate = rnd.choice([0.10, 0.25])         # frenzy attempts per melee second
    lines, t = [], 0
    dmg_in_window = 0
    hits_in_window = 0
    crits = nonc = 0
    even = 0
    lane_attempts = lane_landed = 0
    frenzy_attempts = frenzy_landed = 0
    unclassified_dmg = 0
    self_frenzy = 0
    # ACCUMULATED, NOT HAND-MULTIPLIED. This was `540 * n_eng` -- 500 + 40, the two
    # self-hit lines, times the engagement count -- and the moment I generated a THIRD
    # self-damage shape the constant was wrong and every seed failed. The engine was
    # right and my truth was stale, which is the correct direction for that failure but
    # only because the harness happened to notice. A truth value derived by hand from
    # what the generator "should" emit is an unsourced number sitting inside the
    # instrument that exists to catch unsourced numbers.
    self_dmg = 0
    auto_attempts = 0
    spell_amts = []
    kills = 0
    self_hits = 0
    day = 28
    month = 0

    def stamp(sec):
        d = 1 + (sec // 86400)
        return f"[{'Mon'} {MONTHS[month]} {day + d - 1:02d} " \
               f"{(sec % 86400)//3600:02d}:{(sec % 3600)//60:02d}:{sec % 60:02d} 2026]"

    for e in range(n_eng):
        dur = rnd.randint(40, 120)          # comfortably over MIN_ENGAGEMENT
        start = t
        for s in range(0, dur + 1, 2):      # a swing every 2s: gap 2 << GAP=15
            sec = start + s
            auto_attempts += 1
            if rnd.random() < 0.30:         # a miss: consumes an attempt, no damage
                lines.append(f"{stamp(sec)} You try to slash {MOBS[e % 5]}, but miss!")
                continue
            crit = rnd.random() < crit_rate
            base = rnd.randint(20, 120)
            amt = base * 2 if rnd.random() < even_share else base * 2 + 1
            lines.append(f"{stamp(sec)} You slash {MOBS[e % 5]} for {amt} points of "
                         f"damage.{' (Critical)' if crit else ''}")
            dmg_in_window += amt; hits_in_window += 1
            if crit: crits += 1
            else:
                nonc += 1
                if amt % 2 == 0: even += 1
        # ability lane, at a controlled rate over the SAME window
        for k in range(int(dur * lane_rate)):
            sec = start + int(k / lane_rate)
            lane_attempts += 1
            if rnd.random() < 0.8:
                a = rnd.randint(40, 80)
                lines.append(f"{stamp(sec)} You kick {MOBS[e % 5]} for {a} points of damage.")
                lane_landed += 1
                dmg_in_window += a; hits_in_window += 1
                if a % 2 == 0: even += 1
                nonc += 1
            else:
                lines.append(f"{stamp(sec)} You try to kick {MOBS[e % 5]}, but miss!")
        # FRENZY: a lane verb WHOSE OBJECT IS ALWAYS PREPOSITIONAL. Measured at 735 of
        # 735 first-person lines here and 57,733 occurrences across both persons by
        # Session C, with the direct-object form absent. Generated with `on` because
        # that is what the client writes; a generator that emitted the convenient form
        # would test a pattern the game never produces.
        for k in range(int(dur * frenzy_rate)):
            sec = start + int(k / frenzy_rate)
            frenzy_attempts += 1
            if rnd.random() < 0.8:
                a2 = rnd.randint(30, 70)
                lines.append(f"{stamp(sec)} You frenzy on {MOBS[e % 5]} for {a2} "
                             f"points of damage.")
                frenzy_landed += 1
                dmg_in_window += a2; hits_in_window += 1
                if a2 % 2 == 0: even += 1
                nonc += 1
            else:
                lines.append(f"{stamp(sec)} You try to frenzy on {MOBS[e % 5]}, but miss!")
        # THE COMPOUND DEFECT, GENERATED ON PURPOSE. `You frenzy on yourself` is the
        # line that P-3 shipped without P-2 would have counted as an attack on a mob:
        # the target captures as "on yourself" without the `(?:on )?` group, and
        # "on yourself" is not in SELF_TARGETS. One missing group, two defects, and
        # the second one invisible. It must reach NOTHING -- not damage, not hits,
        # not attempts.
        lines.append(f"{stamp(start + 1)} You frenzy on yourself for 300 points of damage.")
        self_frenzy += 1; self_dmg += 300
        # AN UNCLASSIFIED VERB: damage counts, and it must contribute to NO rate.
        # This is the arm that proves `if v in LANE_VERBS / elif v in AUTO_VERBS`
        # really does drop through for a verb in neither -- a claim I made in the
        # handover from reading the code, and reading is not measuring.
        for k in range(3):
            sec = start + 3 + k * 7
            uc = rnd.randint(40, 90)
            lines.append(f"{stamp(sec)} You cleave {MOBS[e % 5]} for {uc} points of damage.")
            unclassified_dmg += uc
            dmg_in_window += uc; hits_in_window += 1
            if uc % 2 == 0: even += 1
            nonc += 1
        # one spell landing per engagement
        sec = start + dur // 2
        sa = rnd.randint(200, 400)
        lines.append(f"{stamp(sec)} You hit {MOBS[e % 5]} for {sa} points of magic "
                     f"damage by Test Nuke.")
        spell_amts.append(sa); dmg_in_window += sa; hits_in_window += 1
        # A KILLING BLOW, placed at a second NOTHING ELSE LANDS ON. The first version
        # put it at start+dur, which the auto-attack loop also hits when dur is even,
        # so TWO hits shared the death second and the engine -- correctly, by its
        # documented same-second-same-target rule -- marked both. My truth said one.
        # THE GENERATOR WAS WRONG, NOT THE ENGINE. Fixed by removing the ambiguity
        # rather than by relaxing the expectation, which would have hidden the rule.
        sec = start + dur + 1
        kb = rnd.randint(5, 30)
        lines.append(f"{stamp(sec)} You slash {MOBS[e % 5]} for {kb} points of damage.")
        lines.append(f"{stamp(sec)} You have slain {MOBS[e % 5]}!")
        dmg_in_window += kb; hits_in_window += 1; kills += 1
        auto_attempts += 1        # the killing blow is a `You slash` line: an attempt
        # SELF-DAMAGE, both shapes: must never reach the damage total
        lines.append(f"{stamp(sec)} You hit yourself for 500 points of damage.")
        lines.append(f"{stamp(sec)} You hit yourself for 40 points of unresistable "
                     f"damage by Cannibalize.")
        self_hits += 2; self_dmg += 540
        t = start + dur + rnd.randint(40, 90)      # a gap well over GAP=15

    truth = dict(
        engagements=n_eng,
        damage_dealt=dmg_in_window,
        hits_counted=hits_in_window,
        killing_blows=kills,
        # OVER THE ENGINE'S POPULATION: every non-kill hit, auto + lane + spell.
        # The first version divided auto-attack crits by a denominator that also
        # counted lane hits -- two populations, one ratio, in the harness written to
        # check exactly that. Only auto-attack hits are ever generated as crits.
        crit_rate=crits / (hits_in_window - kills) if (hits_in_window - kills) else None,
        even_share=even / nonc if nonc else None,
        even_share_target=even_share,
        spell_landings=len(spell_amts),
        spell_damage_total=sum(spell_amts),
        self_damage_excluded=self_dmg,
        auto_attempts=auto_attempts,
        lane_attempts=lane_attempts,
        # NEW WITH 1.6.0. Each of these fails if a specific shipped path is wrong.
        frenzy_attempts=frenzy_attempts,      # the `(?:on )?` group + the new ceiling
        unclassified_damage=unclassified_dmg, # counted for damage, filed as nothing
        unclassified_verbs=["cleave"],        # and NAMED in coverage, per P-5
        self_frenzy_excluded=self_frenzy,     # the compound P-2/P-3 defect
    )
    return lines, truth


def measure(engine, seeds):
    """Return [(quantity, truth, got, rel_err)] flattened over every seed."""
    rows = []
    for sd in seeds:
        lines, truth = synth(sd)
        r = engine(lines, {})
        m, cov = r["measured"], r["coverage"]
        sd_block = cov.get("self_damage_excluded") or {}
        got = {
            "engagements": m.get("engagements"),
            "damage_dealt": m.get("damage_dealt"),
            "hits_counted": m.get("hits_counted"),
            "killing_blows": m.get("killing_blows_excluded_from_rates"),
            "crit_rate": m.get("crit_rate"),
            "spell_landings": sum(v["landings"] for v in (m.get("spells_landed") or {}).values()),
            "spell_damage_total": sum(v["damage_total"] for v in (m.get("spells_landed") or {}).values()),
            "self_damage_excluded": (sd_block.get("melee_damage", 0)
                                     + sd_block.get("spell_damage", 0)),
            "auto_attempts": m.get("auto_attack_attempts"),
            "lane_attempts": (m.get("lanes") or {}).get("kick", {}).get("attempts"),
            # 1.6.0 PATHS. Read from where a CONSUMER reads them, not from internals.
            "frenzy_attempts": (m.get("lanes") or {}).get("frenzy", {}).get("attempts"),
            # An unclassified verb's damage is not separately reported -- correctly,
            # it is folded into damage_dealt -- so it is checked by DIFFERENCE: remove
            # it from the generated total and the engine must fall by exactly that.
            # Measuring it any other way would need the engine to expose an internal,
            # and a harness that reaches into internals stops testing the interface.
            "unclassified_damage": None,
            "unclassified_verbs": (cov.get("verbs_unclassified") or {}).get("verbs"),
            # The self-frenzy must reach NOTHING. Its 300 damage is not in the truth
            # total, so if the engine counted it, damage_dealt fails -- this row
            # records the intent so a reader sees the arm exists.
            "self_frenzy_excluded": truth["self_frenzy_excluded"],
        }
        # COMPARE AT THE ENGINE'S DECLARED PRECISION. crit_rate is emitted rounded to
        # 4 decimals; my truth is unrounded, so seed 2's 0.008850 against a reported
        # 0.0088 scored a 0.56% "error" that is entirely the rounding the engine
        # documents. Comparing two numbers held to different precision and calling
        # the difference an error is a harness defect, not an engine one -- and it is
        # the same shape as everything else this file exists to catch.
        ROUNDED_4DP = {"crit_rate"}
        # The by-difference arm: strip every cleave line and the engine's damage must
        # drop by exactly the generated unclassified damage. This is the only way to
        # check a quantity the interface deliberately does not expose.
        stripped = [l for l in lines if " You cleave " not in l]
        got["unclassified_damage"] = (m.get("damage_dealt", 0)
                                      - engine(stripped, {})["measured"].get("damage_dealt", 0))
        for k, want in got.items():
            exp = truth[k]
            if k in ROUNDED_4DP and exp is not None:
                exp = round(exp, 4)
            if isinstance(exp, list) or isinstance(want, list):
                rel = 0.0 if want == exp else 1.0
            elif exp in (None, 0) or want is None:
                rel = None if want != exp else 0.0
            else:
                rel = abs(want - exp) / exp
            rows.append((k, exp, want, rel))
    return rows


def report(rows, label):
    import statistics as st
    by = {}
    for k, exp, got, rel in rows:
        by.setdefault(k, []).append(rel)
    print(f"\n  {label}")
    print(f"  {'quantity':24} {'n':>4} {'exact':>7} {'max rel err':>12}")
    print(f"  {'-'*24} {'-'*4} {'-'*7} {'-'*12}")
    exact_total = n_total = 0
    for k in sorted(by):
        v = by[k]
        ok = sum(1 for x in v if x == 0.0)
        worst = max((x for x in v if x is not None), default=None)
        exact_total += ok; n_total += len(v)
        w = "n/a" if worst is None else f"{worst:.4f}"
        print(f"  {k:24} {len(v):4} {ok:3}/{len(v):<3} {w:>12}")
    return exact_total, n_total


# A quantity that does NOT recover, declared with its cause, so the suite stays green
# on a defect that is known and named while ANY UNDECLARED failure is fatal. Same
# discipline as REPIN NEEDED [OPEN|DEFERRED]: a check with one state either blocks
# everything or hides everything. Remove the entry when the fix ships; the run then
# fails until it does, which is the point.
KNOWN_DEFECT = {
    # EMPTY, AND THAT IS A RESULT. The one entry here -- D-6, `_lanes` counting
    # `You hit yourself` as an auto-attack attempt -- was FIXED by P-2 in the Tuesday
    # bundle, and `auto_attempts` went 0/50 to 50/50. Its declaration was deleted the
    # same commit, because the retirement check above now FAILS on a declaration whose
    # defect no longer fires. That check exists because this dictionary went silently
    # stale for the ten minutes between the fix landing and my noticing.
}


if __name__ == "__main__":
    seeds = list(range(50))
    print(f"ROUND-TRIP ACCURACY -- {len(seeds)} generated logs, "
          f"parameters chosen before the engine sees them")
    rows = measure(G.gap_engine, seeds)
    ok, n = report(rows, "gapengine.py as shipped")
    print(f"\n  EXACT RECOVERY: {ok} of {n} quantity-instances "
          f"({100.0*ok/n:.1f}%)")

    by = {}
    for k, _e, _g, rel in rows:
        by.setdefault(k, []).append(rel)
    failing = {k for k, v in by.items() if any(x != 0.0 for x in v)}
    undeclared = sorted(failing - set(KNOWN_DEFECT))
    # THE RETIREMENT ARM, and it is the only thing that makes a closed set worth
    # anything. Until 1 Sep this file reported a declaration ONLY while its defect was
    # still firing: fix the defect and the declaration went SILENT, standing in the
    # source as a false claim that no instrument would ever contradict. That is the
    # stale-fixture shape wearing a third set of clothes, and it fired for real the
    # moment P-2 landed -- auto_attempts went 0/50 to 50/50 and its declaration simply
    # stopped printing.
    # A DECLARATION THAT HAS BECOME FALSE MUST BE FORCED OUT, NOT IGNORED.
    retired = sorted(set(KNOWN_DEFECT) - failing)
    for k in sorted(failing & set(KNOWN_DEFECT)):
        print(f"\n  DECLARED DEFECT  {k}: {KNOWN_DEFECT[k]}")
    if undeclared:
        print(f"\n  UNDECLARED FAILURE(S): {undeclared} -- this is a regression, not a "
              "known gap.")
    if retired:
        print(f"\n  STALE DECLARATION(S): {retired} -- the defect(s) named here NO "
              "LONGER FIRE. The declaration is now a false claim about this engine. "
              "DELETE IT. A closed set whose entries never expire is a list of things "
              "that were once true.")
    if "--selftest" not in sys.argv:
        sys.exit(1 if (undeclared or retired) else 0)

    # POSITIVE CONTROL. A round-trip that scores 100% proves nothing until a WRONG
    # engine scores worse -- otherwise the harness may simply be agreeing with
    # itself. Break one thing at a time and confirm the score drops.
    print("\n  SELFTEST -- a deliberately broken engine must score WORSE")
    import copy
    fails = 0
    for label, patch in (
        ("killing blows NOT excluded", dict(kind="kb")),
        ("self-damage counted as output", dict(kind="self")),
        ("engagement gap widened 15s -> 600s", dict(kind="gap")),
        # THE 1.6.0 CONTROLS. Four new quantities were added to this harness and every
        # one of them passed on the first run. A new arm that has never failed is not
        # evidence -- it is an arm whose ability to fail is unproven, which is the
        # exact fault this file catches in other people's code. Each control breaks
        # ONE path the bundle shipped.
        ("the `(?:on )?` group removed from MELEE", dict(kind="prep")),
        ("`cleave` moved into AUTO_VERBS -- misfiled, not unfiled", dict(kind="misfile")),
        ("frenzy dropped from LANE_VERBS back to nothing", dict(kind="unlane")),
    ):
        saved_gap = G.GAP
        saved_self = set(G.SELF_TARGETS)
        saved_melee = G.MELEE
        saved_auto = set(G.AUTO_VERBS)
        saved_lane = set(G.LANE_VERBS)
        saved_unc = set(G.UNCLASSIFIED_VERBS)
        try:
            if patch["kind"] == "gap":
                G.GAP = 600
            if patch["kind"] == "self":
                G.SELF_TARGETS.clear()
            if patch["kind"] == "kb":
                orig = G.SLAIN
                G.SLAIN = __import__("re").compile(r"^NEVER MATCHES ANYTHING$")
            if patch["kind"] == "prep":
                G.MELEE = __import__("re").compile(
                    G.MELEE.pattern.replace("(?:on )?", ""))
            if patch["kind"] == "misfile":
                G.UNCLASSIFIED_VERBS.discard("cleave"); G.AUTO_VERBS.add("cleave")
            if patch["kind"] == "unlane":
                G.LANE_VERBS.discard("frenzy")
            r2 = measure(G.gap_engine, seeds)
            ok2 = sum(1 for _, _, _, rel in r2 if rel == 0.0)
            worse = ok2 < ok
            print(f"    [{'ok' if worse else 'FAIL'}] {label:36} "
                  f"{ok2}/{n} vs {ok}/{n}")
            fails += 0 if worse else 1
        finally:
            G.GAP = saved_gap
            G.SELF_TARGETS.clear(); G.SELF_TARGETS.update(saved_self)
            G.MELEE = saved_melee
            G.AUTO_VERBS.clear(); G.AUTO_VERBS.update(saved_auto)
            G.LANE_VERBS.clear(); G.LANE_VERBS.update(saved_lane)
            G.UNCLASSIFIED_VERBS.clear(); G.UNCLASSIFIED_VERBS.update(saved_unc)
            if patch["kind"] == "kb":
                G.SLAIN = orig
    # ...and the declaration itself must not be able to swallow a NEW failure.
    probe = sorted({k for k, v in by.items() if any(x != 0.0 for x in v)}
                   | {"damage_dealt"}) 
    swallowed = not (set(probe) - set(KNOWN_DEFECT))
    print(f"    [{'FAIL' if swallowed else 'ok'}] a NEW failing quantity would be "
          "reported as undeclared, not absorbed")
    fails += 1 if swallowed else 0

    # MATCHED PAIR FOR THE RETIREMENT ARM. A guard is not a gate until something fails
    # because of it, and this one currently has nothing to catch: KNOWN_DEFECT is empty
    # and every quantity passes, so the arm is dark. Declare a defect against a quantity
    # that is DEMONSTRABLY fine and confirm it is reported as stale.
    fake = {"crit_rate": "a defect that does not exist"}
    stale = sorted(set(fake) - {k for k, v in by.items()
                                if any(x != 0.0 for x in v)})
    caught = stale == ["crit_rate"]
    print(f"    [{'ok' if caught else 'FAIL'}] a declaration whose defect no longer "
          f"fires is reported STALE, not silently dropped")
    fails += 0 if caught else 1
    # ...and the inverse: a declaration whose defect DOES fire is not called stale.
    live = sorted({"engagements"} - {k for k, v in by.items()
                                     if any(x != 0.0 for x in v)} - {"engagements"})
    print(f"    [{'ok' if not live else 'FAIL'}] ...and the check does not fire on a "
          f"declaration that is still true")
    fails += 0 if not live else 1

    print(f"  {fails} control(s) failed to detect a broken engine")
    sys.exit(1 if (fails or undeclared or retired) else 0)
