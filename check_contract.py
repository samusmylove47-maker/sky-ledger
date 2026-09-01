#!/usr/bin/env python3
"""check_contract.py -- does EQLSGapEngine satisfy B's hand-written contract?

B wrote `web/src/engine/__fixtures__/gap-contract.json` stating what its
`measured` block needs. It is HAND-WRITTEN, not generated from my output, which is
the point: B says what it needs and I make it pass, rather than B describing what I
already do. Vendored here at B's `33b0c79` so this check cannot drift silently. Re-vendored
1 Sep 2026: B renamed the fixture to drop the version from its filename (a name that
must be renamed by hand is a name that will be wrong), re-pinned to engine 1.3.0, and
added `window` -- so B now asserts, against my real bundle, that `damage_dealt` is
filed under in_window and `spells_landed` under all_lines. Those two filings are the
division that gave 202%, and they are now a test on B's side and on mine.

This asserts TYPES AND SHAPES, never values -- B's numbers come from B's own
sample log and mine come from mine.

    python3 check_contract.py
    python3 check_contract.py --selftest
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "fixtures"))
# RE-VENDORED 1 Sep 2026 at B's 33b0c79, and THE FILENAME LOST ITS VERSION -- B's own
# fix, adopted. B renamed `gap-contract-1.2.0.json` to `gap-contract.json` because a
# name carrying a version goes stale the instant the pin moves, and a name that must
# be renamed by hand is a name that will be wrong. My copy carried the same defect
# twice over: `gap-contract-1.2.0.b-65e2f9e3.json` named a version AND a pin.
# The commit stays in the name -- it is the pin, and it is SUPPOSED to change when the
# content does. The version does not, because the file now states it in a field.
CONTRACT = os.path.join(ROOT, "handover", "gap-contract.b-33b0c79.json")

SPELL_KEYS = {"landings", "normalised_key", "damage_total", "damage_median", "damage_max"}


def _sv(v):
    return tuple(int(x) for x in v.split("."))


def audit(measured, version, contract, handoff=""):
    """SHAPE is asserted against B's fixture; VERSION is asserted as a RELATIONSHIP.

    This read `version == contract["assertedEngineVersion"]` until 1 Sep 2026, which was right while
    the engine sat at 1.2.0 and became a gate that could only be satisfied by never
    releasing again. Worse, it hid the thing the Director ruled on: TWO byte-sets
    shipped as 1.2.0 in one night, the second with a changed PARSER, and B's guard --
    exact equality -- could not tell them apart.

    So the checks are now: the engine is not BELOW the contract, the MAJOR matches
    (B's page refuses on a major mismatch), the SHAPE still satisfies every key B
    asked for, and -- the load-bearing one -- **a version divergence is DECLARED**.
    B asserts equality, so any divergence means B is reading its unknown band until B
    re-pins, and a divergence nobody wrote down is a consumer silently switched off.
    """
    want = contract["measured"]
    ev, cv = _sv(version), _sv(contract["assertedEngineVersion"])
    out = [
        ("engine is not BELOW the contract version", ev >= cv,
         f"engine {version}, contract {contract['assertedEngineVersion']}"),
        ("engine MAJOR matches the contract's", ev[0] == cv[0],
         f"{ev[0]} vs {cv[0]}; B's page refuses on a major mismatch"),
        # THE DETAIL MUST FOLLOW THE BRANCH THAT ACTUALLY HELD. The first version of
        # this line computed the failure text unconditionally, so a PASSING check
        # printed "HANDOFF.md carries no 'REPIN NEEDED: 1.3.0'" beside an `ok`. The
        # right answer in the wrong words -- the shape this repository has spent a
        # week finding in other people's instruments -- caught by reading the detail
        # column of a green run.
        ("a version divergence is DECLARED in HANDOFF.md",
         ev == cv or (f"REPIN NEEDED: {version}" in handoff),
         ("versions match, nothing to declare" if ev == cv
          else (f"engine {version} != contract {contract['assertedEngineVersion']}, and HANDOFF.md "
                f"DECLARES 'REPIN NEEDED: {version}' -- B is on its unknown band until "
                "it re-pins, and that is written down"
                if f"REPIN NEEDED: {version}" in handoff else
                f"engine {version} != contract {contract['assertedEngineVersion']} and HANDOFF.md "
                f"carries NO 'REPIN NEEDED: {version}' -- B is reading its unknown "
                "band and nobody said so"))),
    ]
    for k in ("engaged_seconds", "melee_seconds", "damage_dealt", "months_seen"):
        exp, got = want[k], measured.get(k, "<<ABSENT>>")
        ok = isinstance(got, type(exp)) and not isinstance(got, bool)
        out.append((f"measured.{k} is {type(exp).__name__}", ok,
                    f"got {type(got).__name__} {got!r}"))
    # ADDED AT 1.3.0. B's contract now asserts two FILINGS against my real bundle, in
    # its POPULATION_OF: `damage_dealt` under in_window and `spells_landed` under
    # all_lines. B's words: "If E re-files either, that test fails and a human re-reads
    # this contract instead of quietly dividing one population by another."
    # READ FROM THE CONTRACT, never typed here -- if B changes what it depends on, this
    # gate follows without an edit, which is the whole reason the contract is vendored.
    kbp = ((want.get("window") or {}).get("keys_by_population") or {})
    mine = ((measured.get("window") or {}).get("keys_by_population") or {})
    for pop in sorted(kbp):
        theirs = [k for k in kbp[pop] if not k.startswith("_")]
        out.append((f"population {pop!r} files exactly what B asserts",
                    sorted(mine.get(pop, [])) == sorted(theirs),
                    f"engine {sorted(mine.get(pop, []))} vs contract {sorted(theirs)}"))
    for key, pop in (("damage_dealt", "in_window"), ("spells_landed", "all_lines")):
        out.append((f"{key} is filed under {pop} (B divides on this)",
                    key in mine.get(pop, []), f"found under {[p for p in mine if key in mine[p]]}"))

    sl = measured.get("spells_landed")
    out.append(("measured.spells_landed is an object keyed by the RAW string",
                isinstance(sl, dict), f"got {type(sl).__name__}"))
    if isinstance(sl, dict) and sl:
        k0 = sorted(sl)[0]
        out.append((f"each entry carries {sorted(SPELL_KEYS)}",
                    SPELL_KEYS <= set(sl[k0]), f"'{k0}' has {sorted(sl[k0])}"))
        out.append(("normalised_key is a VALUE, not the key",
                    sl[k0].get("normalised_key") is not None
                    and isinstance(sl[k0]["normalised_key"], str), ""))
    return out


def load_contract():
    c = json.load(open(CONTRACT, encoding="utf-8"))
    # NO SILENT DEFAULT. B moved the version out of the filename and into
    # `assertedEngineVersion`; a `.get(..., "1.2.0")` here would have kept this gate
    # green against a contract that no longer says what it asserts.
    if "assertedEngineVersion" not in c:
        raise KeyError(f"{os.path.basename(CONTRACT)} carries no assertedEngineVersion; "
                       "the contract cannot say what it is asserted against")
    return c


# `real()` lived here and was never called. It returned the engine's `measured` block
# beside a HARD-CODED "1.2.0" -- a second, unsourced copy of a version the __main__
# path already reads out of the bundle. Deleted 1 Sep 2026 rather than updated: a
# duplicated constant is how two truths drift, and this one would have kept saying
# 1.2.0 through tonight's bump with nothing to notice.


if __name__ == "__main__":
    c = load_contract()
    from gapengine import gap_engine
    from synthetic_log import build
    import re as _re
    ver = _re.search(r'var VERSION = "([^"]+)"',
                     open(os.path.join(ROOT, "bundle", "eqls-gap-engine.js"),
                          encoding="utf-8").read()).group(1)
    m = gap_engine(build(), {})["measured"]
    handoff = open(os.path.join(ROOT, "HANDOFF.md"), encoding="utf-8").read()

    if "--selftest" in sys.argv:
        print("== check_contract self-test: it must be able to FAIL ==")
        ok = True
        bad = dict(m); bad["months_seen"] = ["Aug"]
        r = dict((n, o) for n, o, _ in audit(bad, ver, c))
        got = r.get("measured.months_seen is int")
        print(f"  a list where the contract wants an int   "
              f"{'correctly fails' if got is False else 'BROKEN'}")
        ok &= (got is False)
        bad2 = dict(m); bad2.pop("damage_dealt", None)
        r2 = dict((n, o) for n, o, _ in audit(bad2, ver, c))
        print(f"  an absent key                            "
              f"{'correctly fails' if r2.get('measured.damage_dealt is int') is False else 'BROKEN'}")
        ok &= (r2.get("measured.damage_dealt is int") is False)
        def arm(label, ver, hf, expect):
            global ok
            got = dict((n, o) for n, o, _ in audit(m, ver, c, hf)).get(expect)
            print(f"  {label:<40} {'correctly fails' if got is False else 'BROKEN'}")
            ok &= (got is False)

        arm("an engine BELOW the contract", "1.1.9", handoff,
            "engine is not BELOW the contract version")
        arm("a MAJOR bump", "2.0.0", handoff, "engine MAJOR matches the contract's")
        # DERIVE a diverging version from the contract rather than typing one. This
        # arm read "1.3.0" and BROKE the moment the contract was re-pinned to 1.3.0 --
        # there was no longer a divergence to leave undeclared, so the check could not
        # fire and the self-test reported BROKEN. A self-test constant that has to be
        # edited whenever the thing it tests moves is a self-test that will go stale.
        cv = _sv(c["assertedEngineVersion"])
        newer = f"{cv[0]}.{cv[1] + 1}.0"
        arm(f"a divergence nobody declared ({newer})", newer, "",
            "a version divergence is DECLARED in HANDOFF.md")
        # ...and the matched pair: the SAME divergence, declared, must PASS.
        got = dict((n, o) for n, o, _ in
                   audit(m, newer, c, f"REPIN NEEDED: {newer}")).get(
                       "a version divergence is DECLARED in HANDOFF.md")
        print(f"  {'the same divergence, DECLARED':<40} "
              f"{'correctly passes' if got is True else 'BROKEN'}")
        ok &= (got is True)
        sys.exit(0 if ok else 1)

    rs = audit(m, ver, c, handoff)
    for n, o, d in rs:
        print(f"  {n:<52} {'ok' if o else 'FAILED'}   {d}")
    if not all(o for _, o, _ in rs):
        print("  B's contract is NOT satisfied. B is never blocked on me and I am "
              f"never blocked on B, but a consumer asserting {c['assertedEngineVersion']} would read "
              "a shape it did not ask for.")
        sys.exit(1)
    # DERIVED FROM THE FILENAME, not typed. This line said "at 65e2f9e3" and would have
    # gone on saying it after tonight's re-vendor -- the same defect as the hard-coded
    # "1.2.0" deleted from this file an hour ago, in the sentence reporting success.
    pin = os.path.basename(CONTRACT).rsplit(".", 1)[0].split("b-")[-1]
    print(f"  {len(rs)} contract assertions, all satisfied, against B's fixture at {pin}, "
          f"asserted for engine {c['assertedEngineVersion']}")
