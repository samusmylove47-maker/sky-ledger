#!/usr/bin/env python3
"""gapengine.py -- gapEngine(lines, context) -> Report. Session E.

THE ENGINE, not the shape of its output. HANDOFF.md §21 is the contract;
fixtures/sample-report.json was hand-written and the Director named that gap
correctly. This produces the same structure from a real log.

PURE by construction: no DOM, no fetch, no network, no filesystem, no clock.
Lines in, a dict out. Egress: none. Self-containment: total. Answered
separately, as ruled.

What it does NOT do, deliberately (§21.6): name an item, emit a modelled
absolute, answer anything computable from a catalogue, or compare two
characters' engaged time. Those are `refusals`, which are output rather than
silence, because a short list reads as "nothing to improve".
"""
import re, collections, statistics as st

# DAY OF MONTH: `[ \d]\d`, NOT `\d{2}`. WIDENED 1 Sep 2026, AND THE EVIDENCE IS
# INCOMPLETE -- STATED HERE RATHER THAN LEFT AS A CLEAN-LOOKING PATTERN.
# EverQuest timestamps have the layout C's ctime() produces, and ctime SPACE-PADS a
# single-digit day: `Sun Sep  1 00:00:00 2026`. Against that, `\d{2}` matches nothing,
# so BOTH ENGINES WOULD SILENTLY DROP EVERY LINE LOGGED ON DAYS 1-9 OF ANY MONTH --
# a third of the calendar, and today is the 1st.
# WHAT I CAN AND CANNOT ESTABLISH:
#   MEASURED   no log in this corpus contains a single-digit day. 4 logs, 189,460
#              lines, zero instances. So a "0 lines dropped" reading is worth
#              nothing here: the shape has not occurred, which is not the same as
#              the parser handling it (HANDOFF section 20).
#   MEASURED   widening is INERT on this corpus: the full report over
#              corpus/amp/..._full.txt is byte-identical before and after.
#   NOT MEASURED  what EQ Legends actually writes for a single-digit day. That is a
#              MECHANISM claim about a client I cannot run, and R74 is the standing
#              rule on mechanism claims. ONE LOG FROM A DAY 1-9 SETTLES IT.
# The class accepts both forms, so it is right either way and costs one character.
TS    = re.compile(r"^\[\w{3} \w{3} ([ \d]\d) (\d{2}):(\d{2}):(\d{2}) \d{4}\] (.*)$")
LANE_VERBS = {"kick", "bash", "strike", "backstab"}
AUTO_VERBS = {"crush", "slash", "pierce", "hit", "punch"}
# Cooldown ceilings, attempts per second, measured across 138 committed logs
# (model4.py LANE_RATE_MAX). These are the MAXIMUM observed, so a gap to them is
# a floor on what is available, not a promise.
LANE_CEILING = {"kick": 0.54, "bash": 0.54, "strike": 0.50, "backstab": 0.47}
MISS = re.compile(r"^You try to (\w+) .+?, but ")

SPELL = re.compile(r"^You hit (.+?) for (\d+) points of (\w+) damage by (.+?)\.(\s*\(Critical\))?$")
MELEE = re.compile(r"^You (slash|pierce|hit|crush|bash|kick|punch|backstab|strike)(?:es)? (.+?) for (\d+) points of damage\.(\s*\(Critical\))?$")
# SELF-DAMAGE, and why a name-equality filter is safe HERE and is not safe in a
# third-person parser. Session D relayed 1 Sep 2026 that a self-hit with NO
# `by <spell>` clause falls through to the melee shape and is emitted as ordinary
# OUTGOING damage, and warned that the obvious fix -- dropping rows where actor
# equals target -- SILENTLY DROPS REAL DAMAGE, because a log cannot tell one entity
# hitting itself from two entities sharing a name. That warning is correct and it
# does not apply to this engine, for a reason worth stating rather than assuming:
# every regex here is anchored `^You`, so the string being compared is the client's
# REFLEXIVE PRONOUN, not a mob name. Two entities cannot both be called `yourself`.
# `Heart harpie` can be two entities -- 10,383 lines of it, and it is a charm pet --
# and `yourself` cannot.
#
# MEASURED before the guard was written, 4 logs, 189,460 lines:
#   SPELL branch, target `yourself`   202 lines, 92,822 damage   already excluded
#   MELEE branch, target `yourself`     0 lines,      0 damage   NOT excluded
# So the hole was real in the code and had no instances in this corpus. A zero is not
# a guard; it is a shape that has not occurred yet. check_selfhits.py supplies the
# positive control the corpus cannot.
SELF_TARGETS = {"yourself"}

SLAIN = re.compile(r"^You have slain (.+?)!$")
# R79 HAZARD, MEASURED ON THIS CORPUS 1 Sep 2026 RATHER THAN ASSUMED AWAY.
# Session C found that EQ capitalises a mob's leading article LINE-INITIALLY and not
# mid-sentence, so "A vis ghoul knight" and "a vis ghoul knight" key as two mobs.
# C's decidable set went 133 -> 385 and agreement 72.2% -> 86.8% on that one fix.
# Measured here across 4 logs, 189,460 lines, this engine's own regexes:
#   targets of MY damage         65 distinct, 0 case-paired keys
#   targets of `You have slain`  46 distinct, 0 case-paired keys
#   slain names matching a hit target ONLY under a case flip: 0
#   names on `X resisted your`   13 distinct, 13 of 13 LEADING-CAPITAL
# The kill join -- (t, target) against hit targets -- is IMMUNE, because both line
# shapes put the name mid-sentence. THE RESIST LINE IS NOT: its name is line-initial
# and therefore capitalised, and SIX of those 13 are the same mob as a damage target
# under a case flip. The only reason it does not bite is that this regex's group(1)
# IS DISCARDED -- resists are keyed by the SPELL, group(2).
# IMMUNE BY DISCARD, NOT BY DESIGN. The moment anyone joins group(1) to a damage
# target, it splits, and the measurement above says by how much.
RESIST= re.compile(r"^(.+?) resisted your (.+?)!$")
MARKER= re.compile(r"ATTN CLAUDE:\s*(.+)$")

GAP = 15          # seconds; a gap longer than this ends an engagement
MIN_ENGAGEMENT = 20

# Measured, tier M. DAMAGE-CHAIN.md carries the evidence and the residuals.
STANCE_OFFENSIVE_MULT = 2.00
STANCE_EVEN_SHARE_OFFENSIVE = 0.93   # Offensive prints ~93% even damage
STANCE_EVEN_SHARE_BALANCED  = 0.50


def _parse(lines):
    """Kills are keyed on (timestamp, TARGET), not timestamp alone.

    Corrected 30 Aug 2026 after Session D published its parser interface and
    asked, without asserting an answer, whether my killing-blow exclusions came
    from a windowed join or a per-line judgement. Reading my own code: neither.
    They came from a same-second join with no target, so ANY hit landing in a
    second when ANYTHING died was marked a killing blow. On the log this was
    built against that marked 194 hits where the target-aware join marks 120 --
    **38% over-marked**, and in AE combat it is systematic rather than rare:
    'a deathly usher' was marked because 'a glyphed sentry' died that second.

    D's interface is what makes the fix possible: the damage row and the kill
    row are separate events that both carry the target, precisely so the join
    is the consumer's to make. It was mine to make and I had made it wrong."""
    ev, kills, months = [], set(), set()
    # A MONOTONIC DAY INDEX, not the day-of-month. `t` was day_of_month*86400 +
    # h*3600 + m*60 + s, which RUNS BACKWARDS at a month boundary: 31 Aug 23:59
    # is t=2764740 and 1 Sep 00:00 is t=86400. Found 31 Aug 2026 by Session C
    # asking what my segmentation rule was -- a continuous 38s fight across that
    # boundary reported TWO engagements and 76 engaged seconds, halving DPS.
    #
    # The log is append-only and chronological, so counting DISTINCT (month, day)
    # pairs in file order gives a monotonic index without a calendar, and it
    # survives the December-January rollover the year field would also need.
    day_idx, prev_key = -1, None
    for raw in lines:
        raw = raw.rstrip("\n")
        m = TS.match(raw)
        if not m:
            continue
        key = (raw[5:8], m.group(1))
        if key != prev_key:
            day_idx += 1
            prev_key = key
        # TS anchors on ^\[\w{3} \w{3} , so for any line it matched, raw[5:8] IS
        # the month token. Sliced rather than captured: adding a group to TS would
        # shift every numeric group below, and the bound tonight is no new regex.
        months.add(raw[5:8])
        t = day_idx*86400 + int(m.group(2))*3600 + int(m.group(3))*60 + int(m.group(4))
        body = m.group(5)
        ev.append((t, body))
        k = SLAIN.match(body)
        if k:
            kills.add((t, k.group(1)))
    return ev, kills, months


def _hits(ev, kills):
    # An exclusion of 92,822 points should not be silent. Counted and surfaced in
    # coverage.self_damage_excluded rather than dropped where no reader can see it.
    out, resists, selfhit = [], collections.Counter(), {}
    for t, b in ev:
        m = SPELL.match(b)
        if m:
            # "You hit yourself ... by Cannibalize" is an HP-for-mana trade, not
            # output. It was 3.7% of a character's apparent total until excluded.
            if m.group(1).lower() in SELF_TARGETS:
                selfhit["spell"] = selfhit.get("spell", 0) + 1
                selfhit["spell_damage"] = selfhit.get("spell_damage", 0) + int(m.group(2))
            else:
                out.append(dict(t=t, tgt=m.group(1), amt=int(m.group(2)), kind="spell",
                                verb=m.group(4), crit=bool(m.group(5)),
                                kill=(t, m.group(1)) in kills))
            continue
        m = MELEE.match(b)
        if m:
            # THE HOLE D FOUND. This branch had no self-target guard, so a self-hit
            # written without a `by <spell>` clause -- which cannot match SPELL, since
            # SPELL requires that clause -- landed here and was counted as OUTGOING.
            # Measured: 0 instances in 189,460 lines, and 0 lines in this corpus match
            # both patterns, so MATCH ORDER was never protecting anything either. D
            # relayed the same correction about its own parser the same night.
            if m.group(2).lower() in SELF_TARGETS:
                selfhit["melee"] = selfhit.get("melee", 0) + 1
                selfhit["melee_damage"] = selfhit.get("melee_damage", 0) + int(m.group(3))
                continue
            out.append(dict(t=t, tgt=m.group(2), amt=int(m.group(3)), kind="melee",
                            verb=m.group(1), crit=bool(m.group(4)),
                            kill=(t, m.group(2)) in kills))
            continue
        m = RESIST.match(b)
        if m:
            resists[m.group(2)] += 1
    return out, resists, selfhit


def _runs(ts, gap=GAP):
    ts = sorted(set(ts))
    if not ts:
        return []
    out, start, prev = [], ts[0], ts[0]
    for t in ts[1:]:
        if t - prev > gap:
            out.append((start, prev)); start = t
        prev = t
    out.append((start, prev))
    return [(a, b) for a, b in out if b > a]


def _lanes(ev, hits):
    """Attempts per lane, INCLUDING MISSES -- a kick that misses still consumed
    its cooldown, so hits alone understate the rate and overstate the gap.

    The denominator is TIME IN MELEE, not engaged time. On the log this was built
    against the two differ by 2.3x and the reported gap by 3x: 5x under ceiling
    against 14x. A caster who never closes has no lane gap to close, and engaged
    time would tell them they had an enormous one."""
    lane_t = collections.defaultdict(list)
    lane_dmg = collections.defaultdict(list)
    auto_t = []
    for t, b in ev:
        m = MELEE.match(b)
        if m:
            v = m.group(1)
            if v in LANE_VERBS:
                lane_t[v].append(t); lane_dmg[v].append(int(m.group(3)))
            elif v in AUTO_VERBS:
                auto_t.append(t)
            continue
        m = MISS.match(b)
        if m:
            v = m.group(1)
            if v in LANE_VERBS: lane_t[v].append(t)
            elif v in AUTO_VERBS: auto_t.append(t)
    melee_s = sum(b - a for a, b in _runs(auto_t))
    return lane_t, lane_dmg, melee_s, len(auto_t)


def _engagements(hits):
    ts = sorted({h["t"] for h in hits})
    if not ts:
        return []
    runs, start, prev = [], ts[0], ts[0]
    for t in ts[1:]:
        if t - prev > GAP:
            runs.append((start, prev)); start = t
        prev = t
    runs.append((start, prev))
    return [(a, b) for a, b in runs if b - a >= MIN_ENGAGEMENT]


def _materiality(share):
    """A delta without a sense of its own scale sends readers chasing rounding
    errors. Every delta carries this, not just the small ones."""
    if share is None:
        return "unknown - no observed baseline to compare against"
    if share < 0.02:
        return "negligible - under 2% of this character's output"
    if share < 0.10:
        return "modest - a few percent of this character's output"
    return "material"


def _stance(hits):
    """Offensive doubles damage, so it prints ~93% even values; Balanced ~50%.
    Killing blows truncate to remaining hit points and are excluded."""
    v = [h["amt"] for h in hits if h["kind"] == "melee" and not h["crit"] and not h["kill"]]
    if len(v) < 30:
        return None, f"only {len(v)} usable non-crit melee hits; need 30", None
    even = sum(1 for x in v if x % 2 == 0) / len(v)
    # A classifier that always returns a label fails open. Distance to each
    # signature, in standard errors, decides -- and "neither" is a real answer.
    # Caught 30 Aug by running the engine: it labelled 64.2% as Balanced on a
    # <=0.65 threshold, when 64.2% over n=120 is 3.1 SE from Balanced's 50% and
    # nowhere near Offensive's 93%. The data said neither and the code said one.
    se = (0.25 / len(v)) ** 0.5
    d_bal = abs(even - STANCE_EVEN_SHARE_BALANCED) / se
    d_off = abs(even - STANCE_EVEN_SHARE_OFFENSIVE) / se
    detail = (f"{even:.1%} even damage across {len(v)} non-crit melee hits "
              f"(killing blows excluded). Balanced prints ~{STANCE_EVEN_SHARE_BALANCED:.0%}, "
              f"Offensive ~{STANCE_EVEN_SHARE_OFFENSIVE:.0%}. "
              f"Distance: {d_bal:.1f} SE from Balanced, {d_off:.1f} SE from Offensive.")
    if d_bal <= 2.0 and d_off > 2.0:
        return "Balanced", detail, even
    if d_off <= 2.0 and d_bal > 2.0:
        return "Offensive", detail, even
    return None, detail + " Neither signature is within 2 SE, so the stance is NOT identified.", even


# Every numeric key in `measured` is computed over ONE of three populations, and
# until 1 Sep 2026 the report did not say which one. THREE populations, one block,
# no labels -- so a consumer that combined two of them got a number that is a share
# of nothing. Measured on the log this engine was built against
# (corpus/amp/eqlog_Shara_rivervale_20260829_full.txt):
#
#   sum(spells_landed[*].damage_total) / damage_dealt  =  2,388,509 / 1,182,027
#                                                      =  202%
#
# and B's own contract names that exact division: `damage_dealt` is "the denominator
# for share-of-output" and `spells_landed.damage_total` is the numerator a consumer
# attributes with. Both are in `measured`, side by side, and they are over different
# populations. 324% on the short log; 34% and 0% on two outside logs, so the error is
# not a constant a reader could learn to subtract.
#
# THE FIX IS NOT TO RESCOPE THE FIELDS. Scoping `spells_landed` to the engagement
# window would delete a spell that landed only outside it -- `Puma Maw`, 5 landings,
# would vanish -- and B's contract says in as many words that a spell ABSENT from
# this object is unmeasured, and must not be read as unused. Deleting it would
# manufacture the exact false reading B wrote that clause to prevent.
#
# So: no existing value moves. The report states its populations and publishes the
# totals, and every share becomes computable against the right denominator.
# check_window.py is the gate; it fails if a key here belongs to no population.
POPULATIONS = {
    # damage over runs of hits with no gap above GAP, lasting MIN_ENGAGEMENT or more
    "in_window": ("dps", "engaged_seconds", "damage_dealt", "engagements"),
    # every matched line in the file, whatever window it fell in
    "all_lines": ("hits_counted", "killing_blows_excluded_from_rates", "crit_rate",
                  "spells_landed", "resists", "months_seen", "stance_inferred"),
    # auto-attack runs; deliberately NOT engaged time, and documented in _lanes
    "melee_time": ("time_in_melee_s", "melee_seconds", "auto_attack_attempts", "lanes"),
    # not measurements: labels and prose about the measurements
    "annotation": ("dps_window", "dps_window_note", "stance_evidence", "window"),
}


# Refusals that hold for ANY input, including no input. Emitted before the
# engine looks at a single line, because each is a fact about what a log can
# never show -- not a finding about this log.
ALWAYS_REFUSED = (
    {"lane": "item.selection", "reason": "computable_from_catalogue",
     "detail": "Which obtainable item meets a stat floor is a catalogue question.",
     "what_would_settle_it": "eqlegendstools.com holds this and does it well. Link, do not clone."},
    # RULED 31 Aug 2026 by the Director, Option 1, implementation mine. This read
    # "The 50 Upgrades gear input, or a character-panel reading." That named an
    # integration which does not exist and was never scoped, and a definite article
    # in a documentation field is indistinguishable from a commitment: it sent
    # Session B looking for a seam for ~7 hours and produced a false missing-seam
    # ruling that had to be retracted to two sessions. It now names a KIND of
    # source, which stays true whatever the owner decides about a gear path.
    # The RULING IS TEXT ONLY. It does not authorise a gear input, does not settle
    # whether one should exist, and does not touch the refusal -- which is correct
    # and was never in question: a log does not show worn stats. B measured that
    # this refusal still fires when handed worn stats, because no code path could
    # notice them.
    {"lane": "worn.stats", "reason": "no_log_evidence",
     "detail": "A log does not show worn stats. AC, resists and worn ATK were not seen.",
     "what_would_settle_it": "Worn stats from a source the reader trusts -- a gear planner's export, or a character-panel reading."},
    {"lane": "engaged_time.comparison", "reason": "privacy",
     "detail": "Comparing how long two named characters were engaged is refused in all cases.",
     "what_would_settle_it": "Nothing. Hard refusal, ruled 30 August 2026."},
)


def gap_engine(lines, context=None):
    # WHAT THIS ENGINE DOES WITH `context`, stated precisely because two sessions
    # got it wrong in opposite directions on 31 Aug 2026:
    #   - it CONSUMES NO VALUE from it. No branch, rate, denominator or refusal
    #     depends on anything a caller supplies. `slot`, `equip`, `weapon`,
    #     `armor` appear zero times in this file and in the bundle.
    #   - it does READ the object, to copy it. This line. The caller's dict is
    #     never mutated -- the same aliasing property the refusals now have.
    #   - it reads ONE field's PRESENCE, `marker_raw`, to guard a write below.
    #     A presence test is not a consumed value.
    # "The engine reads nothing from context" is close but too strong; "the engine
    # consumes no context value" is the sentence that survives reading the lines.
    context = dict(context or {})
    ev, kills, months = _parse(lines)
    for _, b in ev:
        m = MARKER.search(b)
        if m:
            context.setdefault("marker_raw", m.group(1).strip())
    hits, resists, selfhit = _hits(ev, kills)

    # The unconditional refusals are attached HERE, before any early return.
    # FIXED 31 Aug 2026: they used to be built at the end of the function, after
    # `if not hits: return report`. So a log with no outgoing damage -- a support
    # character's log, a log for the wrong character, a file that failed to
    # decode, an empty file -- produced a Report with `refusals: []`. The engine
    # went silent about what it refuses exactly when it knew least, and a page
    # rendering `refusals` would have shown nothing.
    #
    # The worst of the three is `engaged_time.comparison`, whose own detail says
    # "refused in all cases" and which was therefore not. `worn.stats` is the one
    # the Director asked about. Neither depends on the log at all.
    report = {"context": context, "measured": {}, "deltas": [],
              "refusals": [dict(r) for r in ALWAYS_REFUSED], "coverage": {}}
    report["coverage"]["self_damage_excluded"] = {
        "spell_lines": selfhit.get("spell", 0), "spell_damage": selfhit.get("spell_damage", 0),
        "melee_lines": selfhit.get("melee", 0), "melee_damage": selfhit.get("melee_damage", 0),
        "note": ("A first-person line whose target is the reflexive pronoun is an "
                 "HP-for-mana trade or self-inflicted damage, never output. Reported "
                 "rather than dropped silently: 92,822 points on the corpus log."),
    }
    if not hits:
        report["coverage"]["note"] = "no outgoing damage lines matched; nothing measured"
        return report

    runs = _engagements(hits)
    engaged = sum(b - a for a, b in runs)
    dealt = sum(h["amt"] for h in hits for a, b in [(0, 0)] if True) if not runs else \
            sum(h["amt"] for h in hits if any(a <= h["t"] <= b for a, b in runs))

    # The hits `dealt` was summed over, named rather than recomputed, so
    # window.in_window.hits and damage_dealt can never describe different sets.
    in_window = [h for h in hits if any(a <= h["t"] <= b for a, b in runs)]

    nk = [h for h in hits if not h["kill"]]
    crits = [h for h in nk if h["crit"]]
    melee = [h for h in nk if h["kind"] == "melee" and not h["crit"]]
    stance, evidence, even = _stance(hits)

    m = report["measured"]
    m["dps"] = round(dealt / engaged, 1) if engaged else None
    m["dps_window"] = "engaged"
    m["dps_window_note"] = ("Engaged = damage over runs of hits with no gap above "
                            f"{GAP}s, lasting {MIN_ENGAGEMENT}s or more. Four shipped meters use "
                            "four denominators; a DPS figure without its window is not a measurement.")
    # E2. These were all computed and thrown away. `melee_seconds` in particular
    # survived only as ENGLISH inside basis.denominator, and a consumer cannot
    # compute against a sentence.
    m["engaged_seconds"] = engaged
    m["damage_dealt"] = dealt
    # A COUNT, not the tokens. B's contract calls it "int, distinct calendar months
    # the log covers. Not a duration -- a STALENESS SIGNAL." The Director's spec said
    # "count of distinct month tokens" and I emitted the set. My error, not a relay
    # error: I read the word `count` and shipped the thing being counted.
    m["months_seen"] = len(months)
    m["engagements"] = len(runs)
    m["hits_counted"] = len(hits)
    m["killing_blows_excluded_from_rates"] = sum(1 for h in hits if h["kill"])
    m["crit_rate"] = round(len(crits) / len(nk), 4) if nk else None
    # A resist count with no denominator is not a rate. Landings and resists are
    # both per-target, so they share one.
    landed = collections.Counter()
    for h in hits:
        if h["kind"] == "spell":
            landed[h["verb"]] += 1
    # E1. Raw key AND normalised_key, NEVER merged. Measured on the corpus:
    # `Cannibalize` lands 156 times at damage 41-51 while `Cannibalization I`
    # lands 46 times at 1864-1924 -- FORTY TIMES APART. Merging them yields a
    # median that describes neither. `landings` counts LANDING LINES, one per
    # target, and is NOT a cast count.
    by_raw = collections.defaultdict(list)
    for h in hits:
        if h["kind"] == "spell":
            by_raw[h["verb"]].append(h["amt"])
    m["spells_landed"] = {
        name: {"landings": len(v),                      # landing lines, one per target; NOT casts
               "normalised_key": re.sub(r" [IVX]+$", "", name),
               "damage_total": sum(v),
               "damage_median": round(st.median(v), 1),
               "damage_max": max(v)}
        for name, v in sorted(by_raw.items())}

    m["resists"] = []
    for name, n in resists.most_common(6):
        base = re.sub(r" [IVX]+$", "", name)
        hit_n = landed.get(base, 0)
        m["resists"].append({
            "spell": name, "resisted": n, "landed": hit_n,
            # The guard is on hit_n, NOT on (n + hit_n). Caught 30 Aug by reading
            # the output: with hit_n == 0 the sum is still truthy, so a DoT whose
            # landings are not "You hit" lines reported a 100% RESIST RATE. That is
            # a fail-open default -- it would tell a reader their spell never lands
            # when the truth is that this parser cannot see it land.
            "rate": round(n / (n + hit_n), 4) if hit_n else None,
            "note": "landed and resisted are both per-target, so they share a denominator"
                    if hit_n else ("no landings of this spell appear as direct-damage lines "
                                   "(a damage-over-time effect reports differently), so the "
                                   "denominator is unknown and NO RATE IS CLAIMED"),
        })
    m["stance_inferred"] = stance
    m["stance_evidence"] = evidence

    # --- deltas: modelled, always a difference against the observed baseline ---
    if stance == "Balanced" and melee:
        melee_dps = sum(h["amt"] for h in melee) / engaged if engaged else 0
        val = melee_dps * (STANCE_OFFENSIVE_MULT - 1)
        share = val / m["dps"] if m["dps"] else None
        report["deltas"].append({
            "lane": "stance",
            "statement": "Offensive stance instead of Balanced",
            "value": round(val, 1),
            "unit": "dps_delta_vs_observed",
            # Every delta carries the same keys. The stance delta lacked `share`
            # and `materiality` until 30 Aug -- so the LARGEST delta was the one
            # with no sense of scale attached, which is the reader most likely to
            # be sent chasing. Found by generating the fixture from the engine and
            # diffing its keys against a real run.
            "share_of_observed_dps": round(share, 4) if share else None,
            "materiality": _materiality(share),
            "kind": "estimate",
            "requires": {"cost": "none - one keypress", "class_any": "the 9 martial classes"},
            "basis": {"melee_dps_observed": round(melee_dps, 1),
                      "stance_multiplier": STANCE_OFFENSIVE_MULT,
                      "denominator": f"{engaged}s engaged"},
            "falsifier": ("A following log at the same gear whose non-crit melee endpoint "
                          "does not approximately double."),
        })
    elif stance == "Offensive":
        report["coverage"].setdefault("no_delta_because", []).append(
            "stance: already Offensive, which is the largest free gain and it is taken")

    # --- ability lanes: the delta that needs no catalogue and no worn stats ---
    lane_t, lane_dmg, melee_s, auto_n = _lanes(ev, hits)
    m["time_in_melee_s"] = melee_s
    m["melee_seconds"] = melee_s   # E2: the same number under the contract name
    m["auto_attack_attempts"] = auto_n
    m["lanes"] = {v: {"attempts": len(ts), "landed": len(lane_dmg[v]),
                      "per_melee_second": round(len(ts) / melee_s, 4) if melee_s else None}
                  for v, ts in sorted(lane_t.items())}
    # THE POPULATIONS, stated. See POPULATIONS above for why. `all_lines` is the
    # denominator `spells_landed` and `resists` were always missing; `in_window` is
    # the one `dps` and `damage_dealt` already used without saying so.
    m["window"] = {
        "basis": "engaged",
        "in_window": {"hits": len(in_window), "damage": dealt},
        "all_lines": {"hits": len(hits), "damage": sum(h["amt"] for h in hits)},
        "melee_time": {"seconds": melee_s, "auto_attack_attempts": auto_n},
        "keys_by_population": {k: sorted(v) for k, v in sorted(POPULATIONS.items())},
        "note": ("Three populations in one block. A share is only a share against the "
                 "population its numerator came from: sum(spells_landed[*].damage_total) "
                 "divides by window.all_lines.damage, NOT by damage_dealt. Dividing it by "
                 "damage_dealt on the log this engine was built against gives 202%."),
    }

    if melee_s >= 60:
        for v, ts in sorted(lane_t.items()):
            ceil = LANE_CEILING.get(v)
            if not ceil or not lane_dmg[v]:
                continue
            rate = len(ts) / melee_s
            gap = ceil - rate
            if gap <= 0:
                # E-record. This was `continue` -- a silent skip. A player who
                # EXCEEDS a ceiling is the only evidence that the ceiling is wrong,
                # and the ceilings come from a corpus BRIEF-eqlsource.md:589 calls
                # "essentially one player across class swaps". Discarding the one
                # signal that could ever correct them is the expensive silence.
                report["coverage"].setdefault("ceiling_exceeded", []).append(
                    {"lane": v, "observed_rate": round(rate, 4),
                     "ceiling": ceil, "melee_s": melee_s})
                continue
            land = len(lane_dmg[v]) / len(ts)
            value = gap * st.mean(lane_dmg[v]) * land
            # UNIT BUG, FIXED 31 Aug 2026. This read `value / m["dps"]`, which
            # divided a per-MELEE-second quantity by a per-ENGAGED-second one and
            # produced a number that was a share of nothing. The `basis` field one
            # line below has said `"{melee_s}s in melee, NOT {engaged}s engaged"`
            # the whole time -- the code documented the mismatch directly beneath
            # the line that committed it.
            #
            # The delta yields `value` extra damage for each MELEE second, over
            # melee_s of them. Observed output is dps * engaged. So the share is
            # total-extra over total-observed, which is dimensionless:
            share = ((value * melee_s) / (m["dps"] * engaged)
                     if m["dps"] and engaged else None)
            report["deltas"].append({
                "lane": f"lane.{v}",
                "statement": f"fire {v} at its cooldown rather than the observed "
                             f"{rate:.2f}/s while in melee",
                "value": round(value, 1),
                "unit": "dps_delta_vs_observed",
                "share_of_observed_dps": round(share, 4) if share else None,
                "materiality": _materiality(share),
                "kind": "floor",
                "requires": {"cost": "none - rotation only"},
                    "basis": {"observed_per_melee_second": round(rate, 4),
                          "ceiling_per_second": ceil,
                          "denominator": f"{melee_s}s in melee, NOT {engaged}s engaged",
                          "attempts_include_misses": True,
                          "landed_share": round(land, 3)},
                "falsifier": f"A following log at a measured {v} rate above "
                             f"{ceil * 0.8:.2f}/s in melee showing no lane gain.",
            })
    elif melee_s:
        report["coverage"].setdefault("no_delta_because", []).append(
            f"ability lanes: only {melee_s}s in melee, below the 60s floor for a rate")

    # --- refusals: the CONDITIONAL two. The unconditional three are emitted at
    # construction, above, because they do not depend on the log. See ALWAYS_REFUSED.
    if not melee_s:
        report["refusals"].append(
            {"lane": "ability.uptime", "reason": "no_log_evidence",
             "detail": "no auto-attack lines, so there is no time-in-melee denominator",
             "what_would_settle_it": "a log with melee engagement"})
    if stance is None:
        report["refusals"].append(
            {"lane": "stance", "reason": "no_log_evidence", "detail": evidence,
             "what_would_settle_it": "A longer sample, or a client screenshot of the stance."})

    report["coverage"]["inputs_observed"] = sorted(
        {"engaged time", "crit rate", "resist counts"} |
        ({"stance"} if stance else set()))
    report["coverage"]["inputs_assumed"] = ["haste at cap", "target mitigation", "buff uptime"]
    report["coverage"]["note"] = ("Every delta is a difference against this character's own "
                                  "observed baseline. No absolute modelled figure appears in this "
                                  "document, by design - HANDOFF.md 21.3.")
    return report


if __name__ == "__main__":
    import sys, json
    path = sys.argv[1] if len(sys.argv) > 1 else "corpus/amp/eqlog_Shara_rivervale_20260829_full.txt"
    with open(path, encoding="utf-8", errors="replace") as fh:
        rep = gap_engine(fh.readlines(), {"source": "local log, not transmitted"})
    print(json.dumps(rep, indent=1))
