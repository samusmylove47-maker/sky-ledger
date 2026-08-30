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

TS    = re.compile(r"^\[\w{3} \w{3} (\d{2}) (\d{2}):(\d{2}):(\d{2}) \d{4}\] (.*)$")
SPELL = re.compile(r"^You hit (.+?) for (\d+) points of (\w+) damage by (.+?)\.(\s*\(Critical\))?$")
MELEE = re.compile(r"^You (slash|pierce|hit|crush|bash|kick|punch|backstab|strike)(?:es)? (.+?) for (\d+) points of damage\.(\s*\(Critical\))?$")
SLAIN = re.compile(r"^You have slain ")
RESIST= re.compile(r"^(.+?) resisted your (.+?)!$")
MARKER= re.compile(r"ATTN CLAUDE:\s*(.+)$")

GAP = 15          # seconds; a gap longer than this ends an engagement
MIN_ENGAGEMENT = 20

# Measured, tier M. DAMAGE-CHAIN.md carries the evidence and the residuals.
STANCE_OFFENSIVE_MULT = 2.00
STANCE_EVEN_SHARE_OFFENSIVE = 0.93   # Offensive prints ~93% even damage
STANCE_EVEN_SHARE_BALANCED  = 0.50


def _parse(lines):
    ev, kills = [], set()
    for raw in lines:
        m = TS.match(raw.rstrip("\n"))
        if not m:
            continue
        t = int(m.group(1))*86400 + int(m.group(2))*3600 + int(m.group(3))*60 + int(m.group(4))
        ev.append((t, m.group(5)))
        if SLAIN.match(m.group(5)):
            kills.add(t)
    return ev, kills


def _hits(ev, kills):
    out, resists = [], collections.Counter()
    for t, b in ev:
        m = SPELL.match(b)
        if m:
            # "You hit yourself ... by Cannibalize" is an HP-for-mana trade, not
            # output. It was 3.7% of a character's apparent total until excluded.
            if m.group(1).lower() != "yourself":
                out.append(dict(t=t, tgt=m.group(1), amt=int(m.group(2)), kind="spell",
                                verb=m.group(4), crit=bool(m.group(5)), kill=t in kills))
            continue
        m = MELEE.match(b)
        if m:
            out.append(dict(t=t, tgt=m.group(2), amt=int(m.group(3)), kind="melee",
                            verb=m.group(1), crit=bool(m.group(4)), kill=t in kills))
            continue
        m = RESIST.match(b)
        if m:
            resists[m.group(2)] += 1
    return out, resists


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


def gap_engine(lines, context=None):
    context = dict(context or {})
    ev, kills = _parse(lines)
    for _, b in ev:
        m = MARKER.search(b)
        if m:
            context.setdefault("marker_raw", m.group(1).strip())
    hits, resists = _hits(ev, kills)

    report = {"context": context, "measured": {}, "deltas": [], "refusals": [], "coverage": {}}
    if not hits:
        report["coverage"] = {"note": "no outgoing damage lines matched; nothing measured"}
        return report

    runs = _engagements(hits)
    engaged = sum(b - a for a, b in runs)
    dealt = sum(h["amt"] for h in hits for a, b in [(0, 0)] if True) if not runs else \
            sum(h["amt"] for h in hits if any(a <= h["t"] <= b for a, b in runs))

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
    m["engagements"] = len(runs)
    m["hits_counted"] = len(hits)
    m["killing_blows_excluded_from_rates"] = sum(1 for h in hits if h["kill"])
    m["crit_rate"] = round(len(crits) / len(nk), 4) if nk else None
    m["resists"] = dict(resists.most_common(5))
    m["stance_inferred"] = stance
    m["stance_evidence"] = evidence

    # --- deltas: modelled, always a difference against the observed baseline ---
    if stance == "Balanced" and melee:
        melee_dps = sum(h["amt"] for h in melee) / engaged if engaged else 0
        report["deltas"].append({
            "lane": "stance",
            "statement": "Offensive stance instead of Balanced",
            "value": round(melee_dps * (STANCE_OFFENSIVE_MULT - 1), 1),
            "unit": "dps_delta_vs_observed",
            "kind": "estimate",
            "requires": {"cost": "none — one keypress", "class_any": "the 9 martial classes"},
            "envelope_ref": "derived/stance-offensive.json",
            "falsifier": ("A following log at the same gear whose non-crit melee endpoint "
                          "does not approximately double."),
        })
    elif stance == "Offensive":
        report["coverage"].setdefault("no_delta_because", []).append(
            "stance: already Offensive, which is the largest free gain and it is taken")

    # --- refusals: output, never silence ---
    report["refusals"] = [
        {"lane": "item.selection", "reason": "computable_from_catalogue",
         "detail": "Which obtainable item meets a stat floor is a catalogue question.",
         "what_would_settle_it": "eqlegendstools.com holds this and does it well. Link, do not clone."},
        {"lane": "worn.stats", "reason": "no_log_evidence",
         "detail": "A log does not show worn stats. AC, resists and worn ATK were not seen.",
         "what_would_settle_it": "The 50 Upgrades gear input, or a character-panel reading."},
        {"lane": "engaged_time.comparison", "reason": "privacy",
         "detail": "Comparing how long two named characters were engaged is refused in all cases.",
         "what_would_settle_it": "Nothing. Hard refusal, ruled 30 August 2026."},
    ]
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
                                  "document, by design — HANDOFF.md §21.3.")
    return report


if __name__ == "__main__":
    import sys, json
    path = sys.argv[1] if len(sys.argv) > 1 else "corpus/amp/eqlog_Shara_rivervale_20260829_full.txt"
    with open(path, encoding="utf-8", errors="replace") as fh:
        rep = gap_engine(fh.readlines(), {"source": "local log, not transmitted"})
    print(json.dumps(rep, indent=1))
