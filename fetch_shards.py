#!/usr/bin/env python3
"""fetch_shards.py -- the three weapon shards, fetched and PINNED.

WHY THIS EXISTS. On 31 Aug, the day master first carried this work, I cloned the
repository fresh and ran `check.sh`. It failed:

    FileNotFoundError: sh-PRIMARY.json

`.gitignore` excludes `sh-PRIMARY.json`, `sh-SECONDARY.json` and `sh-RANGE.json`
-- the three files EVERY weapon number in this repository rests on. Its comment
said they are "fetched on demand by model.py / model2c.py", and that is half
true: `model.py` fetches PRIMARY and SECONDARY only, and `model3.py`,
`model4.py`, `handmod.py` and `verify_upgrade.py` fetch nothing at all.

So `check.sh` had been passing for days on an untracked file that happened to sit
on one container's disk. **A container recycle would have turned every published
weapon figure into an unreproducible claim, and the check suite green the whole
time.** That is the same fault this repository has spent a week finding in other
people's instruments: a result read as clean from a state nobody established.

WHAT IT DOES. Fetches any missing shard, then verifies all three against the
sha256 recorded below -- the exact bytes every published figure was computed
from, confirmed identical to the live source on 31 Aug 2026.

A DIVERGENCE IS NOT AN ERROR TO PAPER OVER. If the upstream catalogue changes,
this fails and says so, and a human decides whether the published numbers move.
It must never silently accept new bytes, because `265 of 429`, `#1 NEC+PAL+RNG
551.9`, `Truwian Baton 11 vs 2` and every weapon row in the rankings are all
functions of these files.

    python3 fetch_shards.py             fetch what is missing, verify all three
    python3 fetch_shards.py --verify    verify only; never touch the network
    python3 fetch_shards.py --selftest  prove the verifier can FAIL
"""
import hashlib, os, sys, urllib.request

BASE = "https://samusmylove47-maker.github.io/EQL50ups/data/items/"
HERE = os.path.dirname(os.path.abspath(__file__))

# Measured 31 Aug 2026: local copy and live source byte-identical for all three.
PINNED = {
    "PRIMARY":   ("3dd16f76e4172097", 258942),
    "SECONDARY": ("5ffa23ff7e25980c", 192781),
    "RANGE":     ("657882cb6345d1d5",  42092),
}


def path(slot):
    return os.path.join(HERE, f"sh-{slot}.json")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()[:16]


def audit(reader):
    """reader(slot) -> bytes or None. Pure given its reader; no I/O of its own."""
    out = []
    for slot, (want_h, want_n) in PINNED.items():
        raw = reader(slot)
        if raw is None:
            out.append((slot, False, "absent -- run without --verify to fetch it"))
            continue
        got_h, got_n = digest(raw), len(raw)
        ok = (got_h, got_n) == (want_h, want_n)
        out.append((slot, ok,
                    f"sha256 {got_h} {got_n} b"
                    + ("" if ok else f"  != PINNED {want_h} {want_n} b")))
    return out


def on_disk(slot):
    p = path(slot)
    return open(p, "rb").read() if os.path.exists(p) else None


def fetch_missing():
    got = []
    for slot in PINNED:
        if not os.path.exists(path(slot)):
            print(f"  fetching sh-{slot}.json from {BASE}")
            urllib.request.urlretrieve(BASE + slot + ".json", path(slot))
            got.append(slot)
    return got


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("== fetch_shards self-test: the verifier must be able to FAIL ==")
        ok = True

        def probe(label, reader, slot_expected):
            global ok
            res = dict((s, o) for s, o, _ in audit(reader))
            if res.get(slot_expected) is not False:
                print(f"  {label:<44} BROKEN -- '{slot_expected}' did not fail"); ok = False
            else:
                print(f"  {label:<44} correctly fails on {slot_expected}")

        probe("one byte appended to a shard",
              lambda s: (on_disk(s) or b"") + (b"x" if s == "PRIMARY" else b""), "PRIMARY")
        probe("a shard truncated",
              lambda s: (on_disk(s) or b"")[:-1] if s == "RANGE" else on_disk(s), "RANGE")
        probe("a shard missing entirely",
              lambda s: None if s == "SECONDARY" else on_disk(s), "SECONDARY")
        if not all(o for _, o, _ in audit(on_disk)):
            print("  the real shards do not match their pins"); ok = False
        else:
            print("  the unmodified shards still verify against their pins")
        sys.exit(0 if ok else 1)

    if "--verify" not in sys.argv:
        fetch_missing()
    rs = audit(on_disk)
    for slot, o, d in rs:
        print(f"  sh-{slot+'.json':<20} {'ok' if o else 'FAILED'}   {d}")
    if not all(o for _, o, _ in rs):
        print("  The catalogue this repository's weapon numbers were computed from has"
              "\n  changed, or is absent. Do NOT re-pin without re-deriving the figures"
              "\n  that depend on it -- HANDOFF.md sections 35 and 41 name them.")
        sys.exit(1)
    print("  three shards verified against the bytes every weapon figure was computed from")
