#!/usr/bin/env python3
"""handmod.py -- settle the main-hand damage-bonus Hand Modifier.

This repo shipped HAND_1H = 0.69, graded tier M in SOURCING.md on the strength
of "two client windows (Garduk, Arydryidriyorn) solving to 0.680 and 0.686".
Neither window's readings are anywhere in this repository. A tier-M grade on a
measurement whose parse is not committed is not a tier-M grade; it is a typed
number, which is the exact fault this project keeps finding in other people's
work. So the constant is re-derived here, from evidence anyone can re-fetch.

Source: eqlwiki `Game_Mechanics`, sections "Confirmed Legends Observations" and
"Working Legends Damage Bonus Formula", added 2026-08-11 by Maergoth, re-fetched
raw on 2026-08-29 (43,724 bytes, matching the stated revision size).

  curl -sS "https://eqlwiki.com/index.php?title=Game_Mechanics&action=raw"

TIER: this is wiki PROSE, tier 5 by our own hierarchy, and the page says of
itself "It should not yet be described as the exact server formula." Nothing
below trusts its formula. What is used is its OBSERVATION TABLE, tested against
candidate constants, plus one independent tier-2 statblock we already held.
"""
import math

# The 14 rows the wiki labels "directly observed in-game". DMG was not recorded
# for any of them, which the page states, and which matters: the formula's
# max(Level, Damage) branch is invisible while DMG <= Level and dominant above it.
OBS = [(32,'1H',24,5),(48,'1H',24,12),(49,'1H',22,10),(49,'1H',23,11),
       (49,'1H',24,12),(49,'1H',30,14),(49,'1H',36,17),(49,'1H',40,19),
       (50,'1H',24,13),
       (49,'2H',30,19),(49,'2H',42,27),(49,'2H',44,29),(49,'2H',58,33),
       (49,'2H',70,38)]

def raw(hand, L, dly, dmg=0):
    return hand * max(L, dmg) * (min(dly, 50) / 40.0) * (L / 100.0)

def residuals(hand, kind):
    """observed - predicted, at floor rounding, assuming DMG <= level."""
    return [o - math.floor(raw(hand, L, dly)) for L, k, dly, o in OBS if k == kind]

if __name__ == "__main__":
    print("ONE-HANDED  (9 observations)")
    print(f"{'hand':>6} {'exact':>6}  {'over-predicts':>14}  residuals (observed - predicted)")
    for h in (0.69, 0.75, 0.78, 0.80, 0.82, 0.85, 0.90):
        r = residuals(h, '1H')
        print(f"{h:6.2f} {sum(1 for x in r if x == 0):6d}  {sum(1 for x in r if x < 0):14d}  {r}")
    print()
    print("0.69 is refuted: 0 of 9 exact, and every miss is LOW, by 1 to 3.")
    print("0.80 is the largest modifier that NEVER over-predicts, at 5 of 9 exact.")
    print("Its four remaining misses are all +1 -- the direction an unrecorded DMG above")
    print("the character's level produces through max(Level, Damage). Above 0.82 the")
    print("residuals change sign, which no unrecorded-DMG story can explain.")
    print()
    print("INDEPENDENT CHECK -- one tier-2 statblock this repo already held:")
    print("  Efreeti Standard, 3 dmg / 10 delay, 1H Blunt (sh-SECONDARY.json), prints Dmg Bon 5.")
    lo = 5 / 6.25; hi = 6 / 6.25
    print(f"  At level 50: floor(hand * 6.25) == 5  =>  hand in [{lo:.2f}, {hi:.2f}).")
    print(f"  0.69 gives {math.floor(raw(0.69,50,10)):d}. 0.80 gives {math.floor(raw(0.80,50,10)):d}.")
    print("  DAMAGE-CHAIN.md called this 'one open conflict' and kept 0.69 on the tier-M")
    print("  claim above. With that claim's data absent from the repo, the conflict resolves")
    print("  against 0.69 on both lines of evidence at once.")
    print()
    print("TWO-HANDED  (5 observations, at the published 1.10)")
    r = residuals(1.10, '2H')
    print(f"  residuals {r}  -- 4 of 5 exact.")
    print("  The miss is dly 70 -> observed 38, predicted 33. Delay 58 and delay 70 both")
    print("  hit the 50-delay cap, so the capped formula predicts the SAME 33.01 for both")
    print("  while the observations differ by 5. Either the cap is wrong or that weapon's")
    print("  DMG exceeds the character's level; DMG 57 reproduces 38 exactly. NOT SETTLED,")
    print("  and it does not touch 1.10, which the other four rows fix.")
    print()
    print("WHAT THIS COSTS US: on the one fully-pinned character (validate_jos437.py) the")
    print("slash lane moves from +1.6% to +3.4% against measurement -- 0.69 fits that ONE")
    print("character marginally better. 1.8 points on one lane of one parse does not")
    print("outweigh 9 observations and a printed statblock. Recorded, not hidden.")
