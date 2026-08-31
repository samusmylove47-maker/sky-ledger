#!/usr/bin/env python3
"""attribute.py -- bard.py's totals, re-attributed to BUILDS rather than to
whichever name the log printed.

Two corrections the owner supplied, both of which the log alone cannot infer:

  1. `Heart harpie` is Avenrae's CHARM PET and the primary output of the
     PAL/ENC/BRD build under test. Its damage belongs to Avenrae.
     Corroborated in the log: "heart harpie has been charmed" x47.
  2. `Puma Maw` is a proc from a Shaman buff cast by Shara's trio (SHM/BRD/CLR).
     It is BUFF-GRANTED and belongs to neither build's own kit. The standing rule
     on this project is that classes are not credited for buffs, so it is broken
     out rather than assigned.
"""
import re, collections, statistics as st
import bard as B   # reuse the parse

hits = B.hits
PET = "Heart harpie"
OWN = {"Avenrae", "Shara"}

pet_out, pet_friendly = 0, 0
for h in hits:
    if h["actor"].lower().startswith("heart harpie"):
        if h["tgt"] in ("Avenrae", "YOU", "you") or "Shara" in h["tgt"]:
            pet_friendly += h["amt"]
        else:
            pet_out += h["amt"]

def puma(actor):
    return sum(h["amt"] for h in hits if h["actor"] == actor and h["spell"].startswith("Puma"))
pet_puma = sum(h["amt"] for h in hits if h["actor"].lower().startswith("heart harpie")
               and h["spell"].startswith("Puma") and h["tgt"] not in ("Avenrae","YOU","you"))

av_own  = sum(h["amt"] for h in hits if h["actor"] == "Avenrae")
sh_own  = sum(h["amt"] for h in hits if h["actor"] == "Shara")

print("=" * 92); print("RE-ATTRIBUTED TOTALS — by build, not by log name"); print("=" * 92)
rows = [
    ("Avenrae PAL/ENC/BRD", "own lines",              av_own - puma("Avenrae")),
    ("",                    "charm pet, on enemies",  pet_out - pet_puma),
    ("",                    "-- buff-granted (Puma Maw), NOT the build's kit",
                            puma("Avenrae") + pet_puma),
    ("Shara SHM/BRD/CLR",   "own lines",              sh_own - puma("Shara")),
    ("",                    "-- buff-granted (Puma Maw)", puma("Shara")),
]
for a, b_, v in rows:
    print(f"  {a:<22} {b_:<48} {v:12,d}")
av_kit  = (av_own - puma("Avenrae")) + (pet_out - pet_puma)
sh_kit  = sh_own - puma("Shara")
av_buff = puma("Avenrae") + pet_puma
print()
print(f"  {'Avenrae build, kit only':<40} {av_kit:12,d}")
print(f"  {'Shara build, kit only':<40} {sh_kit:12,d}   -> Avenrae/Shara = {av_kit/sh_kit:.2f}x")
print(f"  {'buff-granted, credited to neither':<40} {av_buff + puma('Shara'):12,d}")
print(f"  {'pet damage that hit US on a charm break':<40} {pet_friendly:12,d}  (excluded from output)")

print()
print("=" * 92); print("ENGAGED DPS, with the pet folded into Avenrae"); print("=" * 92)
def attribute(h):
    if h["spell"].startswith("Puma"): return None          # buff, neither build
    if h["actor"].lower().startswith("heart harpie"):
        return None if h["tgt"] in ("Avenrae","YOU","you") else "Avenrae"
    return h["actor"] if h["actor"] in OWN else None

pool = collections.defaultdict(list)
for h in hits:
    a = attribute(h)
    if a: pool[a].append(h)

for actor in ("Shara", "Avenrae"):
    hs = pool[actor]
    w = [(a, b_) for a, b_ in B.windows(hs) if b_ - a >= 20]
    rows = sorted(((sum(h["amt"] for h in hs if a <= h["t"] <= b_) / (b_ - a), b_ - a,
                    sum(h["amt"] for h in hs if a <= h["t"] <= b_)) for a, b_ in w), reverse=True)
    eng = sum(r[1] for r in rows); d = sum(r[2] for r in rows)
    print(f"\n  {actor:<8} {len(rows):3d} engagements >=20s, {eng:5d}s engaged, {d:11,d} damage")
    print(f"           aggregate {d/eng:8.1f} DPS   median engagement {st.median([r[0] for r in rows]):8.1f}"
          f"   best {rows[0][0]:8.1f} over {rows[0][1]}s")

print()
print("=" * 92); print("THE CHARM PET ON ITS OWN — and what it does to CHARM_PET = 66.8"); print("=" * 92)
ph = [h for h in hits if h["actor"].lower().startswith("heart harpie")
      and h["tgt"] not in ("Avenrae","YOU","you") and not h["spell"].startswith("Puma")]
w = [(a, b_) for a, b_ in B.windows(ph) if b_ - a >= 20]
rows = sorted(((sum(h["amt"] for h in ph if a <= h["t"] <= b_) / (b_ - a), b_ - a) for a, b_ in w), reverse=True)
eng = sum(r[1] for r in rows)
d = sum(h["amt"] for h in ph)
print(f"  {len(ph):,d} pet hits, {d:,d} damage, {len(rows)} engagements, {eng:,d}s engaged")
print(f"  aggregate {sum(r[0]*r[1] for r in rows)/eng:.1f} DPS   median engagement {st.median([r[0] for r in rows]):.1f}"
      f"   best {rows[0][0]:.1f}")
print(f"  model4.py carries CHARM_PET = {66.8}. Measured here: "
      f"{sum(r[0]*r[1] for r in rows)/eng/66.8:.1f}x that.")
print(f"  charm events in the log: 47 ('heart harpie has been charmed'), and "
      f"{pet_friendly:,d} damage landed on us across the breaks.")
