#!/usr/bin/env python3
# PARSER-ROLE: ENGINE -- this file is the gap engine. Exactly one file in this
# repository may say that line, and check_oneengine.py enforces it.
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
LANE_VERBS = {"kick", "bash", "strike", "backstab", "frenzy", "smite"}
AUTO_VERBS = {"crush", "slash", "pierce", "hit", "punch"}
# P-3 TIER 2. Verbs Session C measured in a 15-capture, 5,631,681-line corpus and I
# have never seen first-person outside a generated fixture. They are in MELEE so their
# damage is counted, and in NEITHER set above so they contribute nothing to
# `auto_attack_attempts`, `melee_seconds`, or any lane rate.
# FILING A VERB WITHOUT CADENCE EVIDENCE CORRUPTS A DENOMINATOR, WHICH IS WORSE THAN
# THE GAP IT CLOSES. C's count establishes that a verb exists, not what it is.
# `cleave` is here rather than in LANE_VERBS for the same reason on my own evidence:
# 10 usable inter-arrival gaps, below the 30-gap floor this engine already enforces on
# its own sensitivity figure. I am not applying a looser standard to a classification
# than to a sensitivity number.
UNCLASSIFIED_VERBS = {"cleave", "claw", "reave", "bite", "slice", "sting", "smash",
                      "shoot"}
# Cooldown ceilings, attempts per second, measured across 138 committed logs
# (model4.py LANE_RATE_MAX). These are the MAXIMUM observed, so a gap to them is
# a floor on what is available, not a promise.
LANE_CEILING = {"kick": 0.54, "bash": 0.54, "strike": 0.50, "backstab": 0.47,
                # model4.LANE_RATE_MAX: frenzy is the Berserker lane, smite the Paladin
                # lane. Filed on WITHIN-LOG cadence -- Kenkyo's auto runs 1.0s and its
                # lanes 4.0s, and both land at 6.0s. Cadence is NOT comparable across
                # characters (Shara's auto is slower than Kenkyo's lanes), which is a
                # correction to how the first version of this table was built.
                "frenzy": 0.72, "smite": 0.31}
MISS = re.compile(r"^You try to (\w+) .+?, but ")

SPELL = re.compile(r"^You hit (.+?) for (\d+) points of (\w+) damage by (.+?)\.(\s*\(Critical\))?$")
# `(?:on )?` IS LOAD-BEARING AND IS NOT COSMETIC. `frenzy` takes a preposition in 735
# of 735 first-person lines here, and Session C measures 57,733 occurrences across both
# persons with NONE in the direct-object form. Without this group the target captures as
# "on a wan ghoul knight" -- which splits target grouping AND makes "on yourself" fail
# `target.lower() in SELF_TARGETS`, silently REOPENING the bug the self-hit guard below
# exists to close. One missing group, two defects, one of them invisible.
_MELEE_VERBS = "|".join(sorted(LANE_VERBS | AUTO_VERBS | UNCLASSIFIED_VERBS))
MELEE = re.compile(r"^You (" + _MELEE_VERBS + r")(?:es)? (?:on )?(.+?) for (\d+) points of damage\.(\s*\(Critical\))?$")
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
# P-1. 0.93 was calibrated on EVERY melee line unfiltered; the classifier compares it
# against a population with crits and killing blows removed, where the same file gives
# 0.9932 (n=732) against 0.9387 (n=832). The constant was the unfiltered figure and the
# code the filtered one -- the 202% defect, inside the classifier.
# MEASURED CONSEQUENCE: none on either real capture. Shara 0.636 and Kenkyo 0.615 are
# further from 0.993 than from 0.93 and both still return null, correctly, until the
# owner supplies a stance screenshot alongside a log.
STANCE_EVEN_SHARE_OFFENSIVE = 0.993  # Offensive prints ~99.3% even damage
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
    # COUNT THE LINES HERE, where they are actually iterated. Counting them in
    # gap_engine with `sum(1 for _ in lines)` reads ZERO for a generator, because
    # _parse has already consumed it -- and an `isinstance(lines, list)` guard would
    # then report a real generator input as "empty", which is a THIRD wrong claim in
    # the block written to stop wrong claims. Caught before shipping by asking what a
    # caller other than my own __main__ would hand this.
    n_lines = 0
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
        # STRIP \r TOO. `rstrip("\n")` left a carriage return on every line of a CRLF
        # log, and `(.*)$` will not match past it, so the whole file parsed to ZERO
        # events. Python was saved only by universal-newline TEXT MODE in __main__;
        # a caller that reads bytes and splits itself -- which is exactly what the JS
        # driver does -- got `dps: None`. The JS engine had no such rescue and
        # returned an EMPTY measured block for a CRLF log.
        #
        # corpus/amp/eqlog_Shara_rivervale_20260829.txt IS CRLF. One of the two logs
        # committed to this repository could not be read by the bundle I ship, and
        # EverQuest runs on Windows, so CRLF is the NORMAL case and LF is the lucky one.
        # Found 1 Sep 2026 only because a JS run of that log returned `measured: {}`.
        #
        # bundle/check-integrity.py has guarded this bundle's OWN bytes against CRLF
        # since 31 Aug. I checked the artifact for carriage returns and never checked
        # the input for them.
        n_lines += 1
        raw = raw.rstrip("\r\n")
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
    return ev, kills, months, n_lines


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
    seen = set()
    for t, b in ev:
        m = MELEE.match(b)
        if m:
            v = m.group(1)
            # P-2. `hit` is in AUTO_VERBS and this function reads the RAW events, so
            # the self-target guard added to _hits never reached here: a
            # `You hit yourself` line was counted as an auto-attack attempt, inflating
            # the denominator every lane rate divides by. Measured impact: ZERO melee
            # self-hits across 139 unique logs. A real fix that never fires -- which is
            # why it is stated as measured-nil rather than as "conservative".
            if m.group(2).strip().lower() in SELF_TARGETS:
                continue
            seen.add(v)
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
    return lane_t, lane_dmg, melee_s, len(auto_t), sorted(seen & UNCLASSIFIED_VERBS)


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
    ev, kills, months, n_lines = _parse(lines)
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
    # R159: WHAT KIND OF CLAIM IS THIS EVIDENCE FOR?
    # Until 1.5.0 a file the engine could not read and a character who dealt no damage
    # produced the SAME output: `measured: {}` and "no outgoing damage lines matched;
    # nothing measured". That sentence is TRUE in both cases, and in one of them it is
    # a true statement about a file that was never read, sitting in the slot where a
    # measurement goes. The CRLF defect did its damage through exactly this: the parse
    # failed silently and the failure was indistinguishable from a legitimate zero.
    #
    # MEASURED, four real logs, 189,460 lines: 99.99%, 100%, 100%, 100% of lines carry
    # a timestamp. The 0.01% are wrapped chat lines. So a low share is not ambiguous --
    # it means the timestamp shape did not match, which is a READ failure, not a
    # finding about the player.
    #
    # The 0.50 boundary is deliberately far below the measured floor of 99.99%, so an
    # unusual but genuine log is never called unreadable. It is there to separate
    # "could not read this" from "read it, there was nothing", not to grade quality.
    stamped = len(ev)
    share = (stamped / n_lines) if n_lines else None
    verdict = ("empty" if not n_lines else
               "read" if share is not None and share >= 0.50 else "unreadable")
    report["coverage"]["parse"] = {
        "lines_in": n_lines,
        "lines_with_timestamp": stamped,
        "share_timestamped": round(share, 4) if share is not None else None,
        "verdict": verdict,
        "note": ("Every line of a real EverQuest log carries a timestamp: measured "
                 "99.99%-100% across 4 logs and 189,460 lines. A share below 50% means "
                 "the timestamp shape did not match, which is a fact about THIS "
                 "PARSER AND THIS FILE and not about the character. "
                 "`lines_in` COUNTS WHAT THE CALLER "
                 "SUPPLIED, not what the file contained: text.split() on a file "
                 "ending in a newline yields one more element than readlines() does. "
                 "A one-line difference between two callers over one file is that, "
                 "and is not an engine disagreement."),
    }
    report["coverage"]["self_damage_excluded"] = {
        "spell_lines": selfhit.get("spell", 0), "spell_damage": selfhit.get("spell_damage", 0),
        "melee_lines": selfhit.get("melee", 0), "melee_damage": selfhit.get("melee_damage", 0),
        "note": ("A first-person line whose target is the reflexive pronoun is an "
                 "HP-for-mana trade or self-inflicted damage, never output. Reported "
                 "rather than dropped silently: 92,822 points on the corpus log."),
    }
    if not hits:
        # THREE DIFFERENT CLAIMS, three different sentences. One sentence for all
        # three is what let a file that was never read report as a clean zero.
        report["coverage"]["note"] = {
            "empty": "NO INPUT. Zero lines were supplied. This is not a measurement.",
            "unreadable": (
                f"THIS FILE WAS NOT READ. Only {stamped} of {n_lines} lines matched the "
                "timestamp shape this parser requires, against 99.99%-100% in every "
                "real log measured. NOTHING HERE IS A MEASUREMENT ABOUT THE CHARACTER "
                "-- it is a statement about the parser and the file. Check the line "
                "endings and the timestamp format before reading anything below."),
            "read": (
                f"READ AND MEASURED: {stamped} timestamped lines, none of which were "
                "outgoing damage. THIS IS A REAL ZERO -- a support character's log, or "
                "a log for a different character. It is not a parse failure."),
        }[verdict]
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
                            "four denominators; a DPS figure without its window is not a measurement. "
                            "DAMAGE-SHIELD DAMAGE IS EXCLUDED. A player's own shield is never "
                            "written in the first person -- the form is "
                            "`<target> is pierced by <Owner>'s thorns`, naming the owner by "
                            "character name, with zero `by You` variants across 139 logs -- so "
                            "this engine cannot attribute it as a matter of the game's grammar, "
                            "not as an oversight. A meter that counts damage shields will report "
                            "a higher figure and both can be right.")
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
    lane_t, lane_dmg, melee_s, auto_n, unclassified = _lanes(ev, hits)
    m["time_in_melee_s"] = melee_s
    m["melee_seconds"] = melee_s   # E2: the same number under the contract name
    m["auto_attack_attempts"] = auto_n
    m["lanes"] = {v: {"attempts": len(ts), "landed": len(lane_dmg[v]),
                      "per_melee_second": round(len(ts) / melee_s, 4) if melee_s else None}
                  for v, ts in sorted(lane_t.items())}
    # THE POPULATIONS, stated. See POPULATIONS above for why. `all_lines` is the
    # denominator `spells_landed` and `resists` were always missing; `in_window` is
    # the one `dps` and `damage_dealt` already used without saying so.
    # THE ENDPOINT CONVENTION, AND WHAT IT COSTS. `engaged` is the sum of
    # (last hit - first hit) per run, so the time the FINAL SWING of each engagement
    # occupied is not in the denominator. That is a legitimate convention -- shipped
    # meters differ here, which is the whole point of dps_window_note -- but a
    # convention with an unstated size is how four meters end up 2.03x apart.
    #
    # MEASURED, 1 Sep 2026, four logs: the alternative convention (extend each run by
    # one mean inter-hit interval) moves DPS by 14.04%, 50.00%, 2.24% and 13.79%. It
    # is NOT a constant, it scales with engagements-per-second-of-combat, so it cannot
    # be a footnote either. It is computed per log and published.
    #
    # `dps` DOES NOT MOVE. Which convention is right is a mechanism claim about how
    # combat time works and I am not making one -- R74 is the standing rule. What is
    # measurable is the SENSITIVITY, and a reader entitled to the number is entitled
    # to how far it would move under the other choice.
    #
    # GATED. The interval is estimated from (distinct hit-seconds - runs) gaps. On the
    # 21s log that is 2 gaps and the "sensitivity" reads 50%, which is noise wearing a
    # measurement's clothes. Under 30 gaps it is refused with its reason, not emitted.
    hit_secs = sorted({h["t"] for h in in_window})
    n_gaps = len(hit_secs) - len(runs)
    if n_gaps >= 30 and engaged and dealt:
        ihi = engaged / n_gaps
        alt = dealt / (engaged + len(runs) * ihi)
        endpoint = {
            "convention": "first hit to last hit, per engagement",
            "interhit_seconds": round(ihi, 2),
            "gaps_measured": n_gaps,
            "dps_if_each_run_extended_by_one_interval": round(alt, 1),
            "sensitivity": round(m["dps"] / alt, 4) if alt else None,
            "note": ("The final swing of each engagement is outside this denominator. "
                     "`dps` is unchanged and this states what the other convention "
                     "would give -- not which is correct."),
        }
    else:
        endpoint = {
            "convention": "first hit to last hit, per engagement",
            "gaps_measured": n_gaps,
            "sensitivity": None,
            "note": (f"NOT CLAIMED: {n_gaps} inter-hit gaps is under the 30 needed to "
                     "estimate an interval. On a 21s log this figure read 50%, which "
                     "is noise, so it is refused rather than emitted."),
        }

    m["window"] = {
        "basis": "engaged",
        "endpoint": endpoint,
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
    # P-5. Verbs whose damage IS counted and which are filed as NEITHER auto-attack nor
    # lane. Without this, a log where every verb was classified and a log where a fifth
    # of the damage came from unfiled verbs emit an identical `lanes` block -- the
    # `measured: {}` shape, two situations producing one output. Everywhere else in this
    # engine a refusal is published; declining to file a verb is a refusal.
    # P-6. WHEN AN UNFILED VERB IS THE CHARACTER'S AUTO-ATTACK, EVERY LANE RATE DIES
    # AND NOTHING SAYS WHY. Session C established that which `You <verb>` forms appear
    # at all is a property of the LOGGING CHARACTER'S CLASSES -- its two characters emit
    # zero first-person `smite` where a genuine capture here emits 71. So a Beastlord
    # logging `You claw`, which this engine counts but does not file, produces
    # melee_seconds = 0, and every `per_melee_second` becomes null.
    # The null is CORRECT -- refusing beats dividing by zero -- and it is INDISTINGUISH-
    # ABLE from "this character had no melee time", which is a different fact. Two
    # situations, one output: the `measured: {}` shape, in the field P-5 added to stop it.
    _blocks = bool(unclassified) and not melee_s
    report["coverage"]["verbs_unclassified"] = {
        "verbs": unclassified,
        "blocks_lane_rates": _blocks,
        "blocks_lane_rates_note": (
            "TRUE means every per_melee_second below is null BECAUSE the only melee "
            "verbs this character used are ones this engine counts but does not file "
            "as auto-attacks -- not because the character had no melee time. The "
            "damage IS counted; the RATES are refused. Which `You <verb>` forms a log "
            "contains depends on the logging character's classes, so this is the "
            "expected shape for a class whose auto-attack verb is unfiled."
            if _blocks else
            "FALSE: lane rates, where null, are null for some other reason."),
        "note": ("Damage from these verbs IS in damage_dealt and dps. They contribute "
                 "NOTHING to auto_attack_attempts, melee_seconds or any lane rate, "
                 "because filing a verb without cadence evidence corrupts a denominator "
                 "and that is worse than the gap it closes. An empty list means no such "
                 "verb occurred, not that the check was skipped."),
    }
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
