#!/usr/bin/env python3
"""rank.py -- MAKE ME BIS: the ordering half. Session E (EQLS Residual).

    rank(candidates, character, actionability, now) -> Plan

I own ONE question: *how much would that actually matter, and in what order.*
B owns which items are candidates; D owns whether a raid can be run this week.

THE THREE RULINGS THIS IS BUILT TO, 31 Aug 2026
-----------------------------------------------
1. ACTIONABILITY IS THREE-WAY AND THE NOT-KNOWING VALUE IS LOUD. An upgrade whose
   actionability is unknown is NOT ranked as actionable and is NOT dropped. It
   goes in its own band and says why. A boolean would force two not-knowing states
   to collapse into a knowing one, and whichever way it collapses is a claim
   nobody can source.
2. THE TOKEN CAP DECIDES, NOT THE LOCKOUT GRID. Measured by D: 18 roster boss
   kills in one character-week yielded 3 tokens. A boss can read `open` on the
   grid while the cap is spent. So this file NEVER reads a grid -- it calls the
   injected `actionability(state, now, {raid, difficulty})` and takes its answer.
3. THE LIST MUST BE SPENDABLE, NOT MERELY ORDERED. "I have three tokens, where do
   they go" is the player's real question. Rank, then allocate against the cap,
   then say what the rest are waiting on.

AND THE ONE THAT SHAPES EVERYTHING: NO MANUFACTURED COMMON UNIT. Where a damage
delta is computable it is computed. Where it is not, the row is flagged
qualitatively and ranked in a SEPARATE BAND. A feature that ranks two things it
cannot compare is worse than one that ranks fewer things honestly.
"""
import math

# ---------------------------------------------------------------------------
# The cap. A BOUND, NOT A MEASUREMENT, and the caveat travels with the number.
# ---------------------------------------------------------------------------
TOKEN_CAP = 3
TOKEN_CAP_BASIS = "D, 3 character-weeks: Avenrae wk 11 Aug 18 kills/3 tokens; Shara wk 11 Aug 16/3; both wk 4 Aug 7/3."
TOKEN_CAP_CAVEAT = ("n=3, all three reaching exactly 3. Consistent with a cap of 3 AND with any "
                    "higher cap never reached. This is a BOUND, not a measurement. Never print it "
                    "as a settled rule.")

# ---------------------------------------------------------------------------
# What this project can and cannot convert into damage. Measured, not assumed.
# ---------------------------------------------------------------------------
# CONVERTIBLE: weapon damage and delay, through the validated damage chain --
#   U = 2*DMG + 1, B = HandMod * max(L, DMG) * (min(delay,50)/40) * (L/100)
# NOT CONVERTIBLE: everything driven by the ATK coefficient. BUILDS.md:281 records
#   it as DEV-REFUSED -- "We aren't going to spoil the exact formula" -- and
#   model.py:22 carries K only as an environment knob whose default is explicitly
#   not measured. So STR, ATK and the attributes that feed them CANNOT be turned
#   into a DPS number by anything this project has sourced.
# NOT DAMAGE AT ALL: ac, hp, mana, saves.
CONVERTIBLE_KEYS = {"weaponDamage", "weaponDelay"}
DEV_REFUSED_KEYS = {"atk", "str", "dex", "agi"}
NOT_DAMAGE_KEYS = {"ac", "hp", "mana", "wis", "int", "sta", "cha",
                   "svFire", "svCold", "svMagic", "svPoison", "svDisease", "svVoid"}

BANDS = ("modelled", "unknown_impact", "unknown_actionability", "unsourced_impact")


class SeamError(TypeError):
    """Raised when this module is asked to do another session's job."""


# ---------------------------------------------------------------------------
def _damage_delta(cand, character):
    """DPS delta for a weapon swap, or (None, reason) when not computable.

    Returns (value, basis) or (None, why_not). Never guesses.
    """
    d = cand.get("statDelta") or {}
    hit = CONVERTIBLE_KEYS & set(d)
    if not hit:
        touched = set(d)
        if touched & DEV_REFUSED_KEYS:
            return None, ("impact_not_computable: the ATK coefficient is DEV-REFUSED "
                          "(BUILDS.md:281). No sourced conversion from "
                          f"{sorted(touched & DEV_REFUSED_KEYS)} to DPS exists.")
        if touched and touched <= NOT_DAMAGE_KEYS:
            return None, (f"not_a_damage_stat: {sorted(touched)} do not enter the damage "
                          "chain. Survivability and utility are not ranked here.")
        return None, "no_stat_delta_recorded"

    dmg_now, dly_now = cand.get("currentDamage"), cand.get("currentDelay")
    dd, ddly = d.get("weaponDamage", 0), d.get("weaponDelay", 0)
    if dmg_now is None or dly_now is None:
        return None, ("impact_not_computable: a weapon delta needs the CURRENT weapon's "
                      "damage and delay to compute against; neither was supplied.")
    lvl = character.get("level")
    hand = character.get("handMod")
    haste = character.get("hastePercent")
    if lvl is None or hand is None or haste is None:
        return None, ("impact_not_computable: needs level, handMod and hastePercent from "
                      "the character; missing "
                      f"{[k for k,v in (('level',lvl),('handMod',hand),('hastePercent',haste)) if v is None]}.")

    def swing(dmg, dly):
        if dly <= 0:
            return None
        u = 2 * dmg + 1
        b = hand * max(lvl, dmg) * (min(dly, 50) / 40.0) * (lvl / 100.0)
        rate = (1 + haste / 100.0) / (dly / 10.0)
        return ((u + 1) / 2.0 + b) * rate      # mean roll on [1,U] plus the bonus

    a = swing(dmg_now, dly_now)
    b_ = swing(dmg_now + dd, dly_now + ddly)
    if a is None or b_ is None:
        return None, "impact_not_computable: a delay of zero or less has no swing rate."
    return round(b_ - a, 2), ("damage chain on mean roll: U=2*DMG+1, "
                              "B=HandMod*max(L,DMG)*(min(delay,50)/40)*(L/100)")


# ---------------------------------------------------------------------------
def _actionable(cand, character, actionability, now):
    """Ask D. Never read a grid, never infer, never pass an item id."""
    obt = cand.get("obtainable")
    if obt in (None, "not recorded"):
        return {"answer": "unknown", "why": "obtainable_not_recorded",
                "doesNotAnswer": None}
    if not isinstance(obt, dict):
        raise SeamError("obtainable must be {boss, zone, difficulty}; "
                        f"got {type(obt).__name__}. Item ids belong to B, not here.")
    missing = [k for k in ("boss", "zone", "difficulty") if obt.get(k) in (None, "")]
    if missing:
        return {"answer": "unknown", "why": f"obtainable_incomplete: missing {missing}",
                "doesNotAnswer": None}
    if actionability is None:
        return {"answer": "not_looked", "why": "no actionability oracle was supplied",
                "doesNotAnswer": None}
    r = actionability(character.get("state"), now,
                      {"raid": obt["boss"], "difficulty": obt["difficulty"]})
    ans = r.get("answer") if isinstance(r, dict) else r
    if ans not in ("yes", "no", "unknown", "not_looked", "completed"):
        return {"answer": "unknown", "why": f"oracle returned an unrecognised state {ans!r}",
                "doesNotAnswer": None}
    return {"answer": ans,
            "why": (r.get("why") if isinstance(r, dict) else None),
            # RULING 2, BOUND 1: `yes` means "may run it and spend a token" and NEVER
            # "the item will drop". The loot lockout is not observable from a log,
            # ever. This field is carried through verbatim and never collapsed.
            "doesNotAnswer": (r.get("doesNotAnswer") if isinstance(r, dict) else None)}


# `completed` is ACTIONABLE, deliberately: a locked-out kill still pays a
# guaranteed drop per the 28 Jul 2026 patch note. Filtering it out deletes real
# upgrades -- the opposite error to the one the three-way rule guards against,
# and just as costly.
ACTIONABLE = {"yes", "completed"}
UNKNOWN = {"unknown", "not_looked"}


def rank(candidates, character, actionability=None, now=None):
    """Order upgrades, then allocate them against the weekly token cap."""
    if not isinstance(candidates, (list, tuple)):
        raise SeamError("candidates must be B's list of candidate rows.")
    rows, refusals = [], []
    for c in candidates:
        if not c.get("eligible", True):
            refusals.append({"lane": "candidate.ineligible",
                             "item": c.get("candidateName"),
                             "reason": c.get("eligibilityReason") or "not stated by B"})
            continue
        act = _actionable(c, character, actionability, now)
        val, basis = _damage_delta(c, character)
        # BAND PRECEDENCE, and the order is load-bearing. The first draft put
        # actionability ahead of impact, and a row that could NEVER be scored --
        # `ac`/`hp`, which do not enter the damage chain at all -- came out labelled
        # "unknown_actionability", i.e. blamed on a lookup we had not done rather
        # than on a conversion that does not exist. The band is what a reader sees;
        # it must carry the BINDING reason, not the first one tested.
        #   unsourced_impact      the figures exist but are tier 4/5
        #   unknown_impact        no sourced conversion -- about the world, permanent
        #   unknown_actionability impact IS computable, we just have not looked
        if c.get("impactSourceTier") in (4, 5):
            band = "unsourced_impact"
        elif val is None:
            band = "unknown_impact"
        elif act["answer"] in UNKNOWN:
            band = "unknown_actionability"
        else:
            band = "modelled"
        rows.append({"item": c.get("candidateName"), "slot": c.get("slot"),
                     "replaces": c.get("replacesItemId"),
                     "dps_delta": val, "basis": basis if val is not None else None,
                     "why_no_number": None if val is not None else basis,
                     "actionability": act, "band": band,
                     "impactSourceTier": c.get("impactSourceTier")})

    for r in rows:
        if r["band"] == "modelled" and r["dps_delta"] is not None and r["dps_delta"] <= 0:
            r["band"] = "unknown_impact"
            r["why_no_number"] = "the computed delta is not positive; this is not an upgrade"

    banded = {b: [r for r in rows if r["band"] == b] for b in BANDS}
    banded["modelled"].sort(key=lambda r: -r["dps_delta"])

    spendable = [r for r in banded["modelled"] if r["actionability"]["answer"] in ACTIONABLE]
    allocate, deferred = spendable[:TOKEN_CAP], spendable[TOKEN_CAP:]
    blocked = [r for r in banded["modelled"] if r["actionability"]["answer"] == "no"]

    return {
        "spend": {
            "cap": TOKEN_CAP, "cap_basis": TOKEN_CAP_BASIS, "cap_caveat": TOKEN_CAP_CAVEAT,
            "allocate": allocate,
            "deferred_cap_reached": deferred,
            "blocked_this_week": blocked,
            "doesNotAnswer": ("Actionable means you MAY run it and spend a token. It never "
                              "means the item will drop. The loot lockout is not observable "
                              "from a log."),
        },
        "bands": {b: banded[b] for b in BANDS},
        "refusals": refusals + [
            {"lane": "impact.attributes", "reason": "dev_refused",
             "detail": "STR/ATK deltas cannot be converted to DPS: the ATK coefficient is "
                       "dev-refused (BUILDS.md:281).",
             "what_would_settle_it": "A measured %DPS-per-100-ATK from paired logs at one "
                                     "known ATK difference."},
            {"lane": "impact.survivability", "reason": "out_of_scope",
             "detail": "AC, HP, mana and saves are not ranked here. They do not enter the "
                       "damage chain and this ranker only orders damage.",
             "what_would_settle_it": "Nothing. A different ranker, deliberately."},
        ],
        "coverage": {
            "candidates_in": len(candidates),
            "ranked_on_a_number": len(banded["modelled"]),
            "held_back_no_number": len(banded["unknown_impact"]),
            "held_back_unknown_actionability": len(banded["unknown_actionability"]),
            "held_back_unsourced": len(banded["unsourced_impact"]),
            "note": "A row in a held-back band is NOT a row we scored zero. It is a row we "
                    "declined to score, and the reason is on it.",
        },
    }


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys, json

    CHAR = {"level": 50, "handMod": 0.80, "hastePercent": 75, "state": {}}

    def oracle(state, now, key):
        assert set(key) == {"raid", "difficulty"}, "the seam passes raid+difficulty only"
        if key["raid"] == "Vox":
            return {"answer": "no", "why": "token cap spent this week",
                    "doesNotAnswer": "may-run, never will-drop"}
        if key["raid"] == "Trak":
            return {"answer": "completed", "why": "locked out, still pays a guaranteed drop",
                    "doesNotAnswer": "may-run, never will-drop"}
        return {"answer": "yes", "why": "open and cap available",
                "doesNotAnswer": "may-run, never will-drop"}

    def W(name, dmg, dly, boss, tier=None):
        return {"slot": "PRIMARY", "candidateName": name, "replacesItemId": "cur",
                "statDelta": {"weaponDamage": dmg, "weaponDelay": dly},
                "currentDamage": 50, "currentDelay": 70, "eligible": True,
                "impactSourceTier": tier,
                "obtainable": {"boss": boss, "zone": "z", "difficulty": "normal"}}

    if "--selftest" in sys.argv:
        print("== rank self-test: every ruling must be enforced, and each check must FAIL on its inverse ==")
        ok = True

        def check(label, cond, detail=""):
            global ok
            print(f"  {label:<56} {'ok' if cond else 'FAILED'}   {detail}")
            if not cond: ok = False

        # RULING 1 -- unknown is neither ranked as actionable nor dropped
        c = W("Unknown Source", 20, -10, "x"); c["obtainable"] = "not recorded"
        p = rank([c], CHAR, oracle, "now")
        check("unknown actionability is NOT allocated", not p["spend"]["allocate"])
        check("unknown actionability is NOT dropped",
              len(p["bands"]["unknown_actionability"]) == 1,
              p["bands"]["unknown_actionability"][0]["actionability"]["why"] if p["bands"]["unknown_actionability"] else "MISSING")

        # RULING 2 -- `completed` is actionable, deliberately
        p = rank([W("Trak Blade", 20, -10, "Trak")], CHAR, oracle, "now")
        check("`completed` IS allocated (guaranteed drop)", len(p["spend"]["allocate"]) == 1)

        # ...and its inverse: `no` is not
        p = rank([W("Vox Blade", 20, -10, "Vox")], CHAR, oracle, "now")
        check("`no` is NOT allocated but IS reported",
              not p["spend"]["allocate"] and len(p["spend"]["blocked_this_week"]) == 1)

        # RULING 3 -- spendable: the cap bounds the allocation, the rest is deferred not lost
        many = [W(f"Blade {i}", 30 - i, -10, "open") for i in range(6)]
        p = rank(many, CHAR, oracle, "now")
        check("allocation is capped at TOKEN_CAP", len(p["spend"]["allocate"]) == TOKEN_CAP,
              f"{len(p['spend']['allocate'])} of {len(many)}")
        check("the rest are DEFERRED, not discarded",
              len(p["spend"]["deferred_cap_reached"]) == len(many) - TOKEN_CAP)
        check("allocation is in descending impact order",
              [r["dps_delta"] for r in p["spend"]["allocate"]] ==
              sorted([r["dps_delta"] for r in p["spend"]["allocate"]], reverse=True))

        # NO MANUFACTURED UNIT -- dev-refused stats never get a number
        c = {"slot": "EAR", "candidateName": "Band", "statDelta": {"str": 20, "atk": 40},
             "eligible": True, "obtainable": {"boss": "open", "zone": "z", "difficulty": "normal"}}
        p = rank([c], CHAR, oracle, "now")
        r = (p["bands"]["unknown_impact"] or [{}])[0]
        check("dev-refused ATK/STR gets NO number",
              r.get("dps_delta") is None and "DEV-REFUSED" in (r.get("why_no_number") or ""))
        check("...and it is the BINDING reason, not the actionability one",
              r.get("band") == "unknown_impact")

        # BOUND 1 -- doesNotAnswer survives to the output
        p = rank([W("Blade", 20, -10, "open")], CHAR, oracle, "now")
        check("doesNotAnswer is carried, not collapsed",
              "never" in p["spend"]["doesNotAnswer"].lower() and
              p["spend"]["allocate"][0]["actionability"]["doesNotAnswer"] is not None)

        # THE SEAM -- item ids are another session's job
        try:
            rank([{"candidateName": "x", "eligible": True, "obtainable": "itemid:1234"}],
                 CHAR, oracle, "now")
            check("an item id in `obtainable` raises SeamError", False, "it did not raise")
        except SeamError as e:
            check("an item id in `obtainable` raises SeamError", True, str(e)[:44])

        # the cap caveat travels with the cap
        check("TOKEN_CAP carries its n=3 caveat",
              "BOUND, not a measurement" in rank([], CHAR, oracle, "now")["spend"]["cap_caveat"])

        sys.exit(0 if ok else 1)

    print(json.dumps(rank([W("Earthshaker", 24, -5, "open"),
                           W("Trak Blade", 12, 0, "Trak"),
                           W("Vox Blade", 30, -20, "Vox")], CHAR, oracle, "now"),
                     indent=1)[:900])
