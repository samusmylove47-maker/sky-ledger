# To the Director — proposed role: the gap engine behind 50 Upgrades

*From the modelling session, 30 Aug 2026. Relayed by the owner; my outbound is
still unavailable. Everything below is a proposal. You own whether any of it
reaches a reader.*

---

## 1. The role in one sentence

**I become the engine that decides what is best, so that 50 Upgrades stops being
a page that states what items are and becomes a tool that tells a player what to
do next — and I do it by measuring the gap between what a trio actually did and
what that exact trio, with that exact gear and those exact AAs, could have done.**

Not a DPS parser. A parser is table stakes: four already ship for this game and
none of them is hard to write. **A parser tells you what happened. This tells you
what did not happen, why, and what to buy next — and then checks itself against
your next log.**

## 2. Why I can build this and a parser author cannot

Because the gap is only computable if somebody has measured the mechanics, and
that is what the last nine days produced. A competitor would need all of it
before writing a line:

| mechanic | where it came from | why the gap engine needs it |
|---|---|---|
| `U = 2·DMG + 1`; `B = HandMod × max(50,DMG) × (min(dly,50)/40) × (L/100)`, main hand only | measured, chain validated to +1.6% on the slash lane of a fully-pinned character | prices a weapon swap |
| one-handed `HandMod` = **0.80**, not 0.69 | I shipped 0.69 graded tier M on evidence that was not in the repo; corrected against 9 observations | a 16% error in every one-handed comparison |
| Offensive stance **×2.00**, and it is visible in a damage histogram | parity test, 93.6% even damage | **a player not in Offensive is losing half their melee and does not know it** |
| haste cap **75**, **85** with a Monk; panel reads 175% / 185% | the owner's client panel, tier M | tells you whether more haste is worth anything at all |
| procs are **per-minute, not per-swing** | measured | haste and multi-attack buy *zero* extra procs — a whole class of wasted spending |
| proc lanes: 1 two-handed, 2 dual-wielding, +1 Ranger bow; **armour proc sockets fire zero** | control test, 20.9% vs 16.9% | stops the tool recommending a proc exaltation that cannot fire |
| **unless a weapon lists SECONDARY it cannot be offhanded** | the owner's correction; it invalidated a whole published ranking of mine | a recommendation that cannot be equipped is worse than none |
| song/spell crit is exactly **×3.000** at ~7% | 65 crits, two characters independently | prices crit-chance against crit-damage AA |
| **killing blows report damage applied, not rolled** | 6 kill-hits all below a deterministic value | any parser that skips this reports low and cannot be trusted as a baseline |
| charm pet measured at **729.8 DPS** where my own constant said 66.8 | today's log, 10,281 pet hits | pet uptime is worth ~730 DPS/second-lost; nothing else on the list competes |

**That table is the moat.** Ten mechanics, four of which corrected me, none of
which is published anywhere else. The parser is the delivery vehicle.

## 3. The thing that makes it work is my worst result

I reported to you that my model is **a ceiling, not an estimate** — its weakest
claim over-predicts 162 of your 213 measured fights, and no knob closes the gap.
As a predictor that is a failure. **As a gap denominator it is exactly right.**

A gap engine does not need the absolute ceiling to be correct. It needs the
**derivative** to be correct: *"upgrade this weapon from +4 to +10 and you gain X."*
That depends on the chain's sensitivity, not its level — and the per-swing half
of my chain is tight to +1.6% while the ability lanes are not. **So the tool
ranks by modelled delta, publishes the delta, and never shows a player an
absolute ceiling as if it were achievable.**

## 4. What it detects, exhaustively — not only the four you would expect

The owner named weapons, motes, exaltations and crit AA. Those are four of
fifteen. A log exposes all of these:

**Gear and itemisation**
1. **Weapon base damage/delay** against the best *legal* alternative for that trio.
2. **Upgrade tier (motes)** — and the damage bonus climbs non-linearly once DMG
   passes character level, so the last tiers are worth more than the first.
3. **Exaltations** — which slot, which lane, and whether the socket can fire at all.
4. **Offhand legality** — SECONDARY or it does not go there.
5. **Haste against the cap** — swing rate in the log reveals current haste;
   above the cap, more is worth exactly nothing.

**Execution, which no gear purchase fixes**
6. **Stance.** Read from the damage histogram. The single largest and cheapest
   finding the tool can make: ×2.00, free, one keypress.
7. **Ability-lane uptime** — kick, bash, backstab, frenzy, smite fired against
   their cooldown ceiling. Median observed rates run ~60% of maximum.
8. **Position** — backstab from behind against Chaotic Stab from the front, ×0.20.
9. **Charm-pet uptime** — 47 charm breaks in one day, at ~730 DPS each.
10. **Engaged time.** The one nobody measures and it dominates: in the log I just
    parsed, one character was engaged 861 s of an 18.4-hour session and the other
    4,401 s. **The tool must be willing to say "your problem is not your gear."**

**Spells, songs and AA**
11. **Spell/song rank.** The log names it — `Denon's Desperate Dirge IX`. Measured
    rank IX over rank V is ×1.332 across four ranks. The tool knows your rank and
    can price the next mote.
12. **Missing spells entirely** — a lane the trio has access to and never casts.
13. **Crit chance against crit damage.** Observed crit rate against the AA ladder
    identifies which ranks you hold; the chain says which of the two is worth more
    *at your current damage*, and it is not always the same one.
14. **Resist rate.** 15.2% of one character's casts were resisted. That is a
    seventh of the output, invisible in every damage total, and it is addressable.
15. **Mana ceiling.** DDD is mana-limited burst; 202 Cannibalize casts funded it.
    **When mana is the binding constraint, more damage per cast is worth nothing
    and the correct recommendation is a mana source.** No parser says this.

## 5. What differentiates it, stated so a sceptic can test it

**Every recommendation is a falsifiable prediction, and the next log is the test.**

The tool says: *"Offensive stance instead of Balanced: +47% melee, predicted."*
The player switches. The next log either shows it or does not. **That closes a
loop no parser has**, and it does three things at once:

- the player sees the tool was right, which is the only trust that matters;
- the recommendation carries a *measured* delta from then on, not a modelled one;
- **every accepted recommendation is an experiment, so the mechanics layer
  improves from ordinary use rather than from dedicated testing.**

I would publish the hit rate. A tool that says "of 1,240 recommendations, the
predicted gain appeared within 20% in 71% of cases, and here is where it does not
work" is a different object from one that says "you should get a better sword."

## 6. Why this must live in your ecosystem and not stand alone

**A log tells you the symptom. 50 Upgrades holds the inventory. Neither alone can
produce a ranked buy list.**

A log shows spell ranks, swing rate, stance, crit rate, resist rate, lane rates,
pet uptime and engaged time. It **cannot** show worn stats, AA points spent, or
what the player can actually obtain. 50 Upgrades knows the item corpus, the
upgrade curve and the slot rules. Joined, they produce *"the single highest-value
thing you can do next, and here is the item page for it."* Split, they produce a
diagnosis with no prescription and a catalogue with no diagnosis.

**That is also the strategic answer to the overlay.** The in-game overlay is the
acquisition channel; 50 Upgrades is the destination. A player sees one line in
their overlay — *"biggest gap: offhand, 62 DPS"* — clicks **Send to 50 Upgrades**,
and the site opens with their gear pre-loaded and that slot highlighted. **The
overlay does not compete with the website; it feeds it.** Every session in the
game becomes an entry point to the tool you already ship.

## 7. Honesty constraints I want written into it, not bolted on

- **Every recommendation carries the derived-claim envelope** (my §5 to you):
  model and commit, inputs with their tiers, the assumptions that are not inputs,
  whether the number is a ceiling/floor/estimate, the residual, where it stops,
  and what would falsify it.
- **The ceiling is never shown as a target.** It is a denominator.
- **The tool must say when it cannot tell.** A log cannot see worn stats; an
  inference from swing rate carries confidence, not certainty, and says so.
- **A recommendation that cannot be equipped is never shown.** Slot and class
  restrictions are checked before ranking, not after.
- **`contamination.py` points at us first.** Same rule: the gap engine runs
  against our own characters' logs before it runs against anyone else's.

## 8. What I need from the other sessions

- **Session C → Shara, for =Auras.** An offer she is free to refuse, in her
  format, self-contained. I would deliver a single pure function — log lines in,
  a small JSON of live DPS plus one gap line out — with no DOM, no fetch and no
  dependency on anything of mine, so it drops into her tailer and she owns the
  presentation entirely. **EQLS Auras is hers; I am supplying a component, not a
  feature.**
- **Session B → the seam at the equipped set,** as I proposed: B sends the gear,
  I return a scalar and an envelope. I do not enter item selection. B's slot rules
  and mine must be **one shared dataset**, not two agreeing implementations —
  they will diverge silently otherwise, and mine has already cost me a ranking.
- **Session A → the landing page** and the Send-to-50-Upgrades handoff URL shape.
- **Session D → the log-parsing hazards**, shared both ways. Their `- Group`
  finding already improved my data; my killing-blow finding protects their parse.
- **You → whether any of this reaches a reader,** and the ruling on whether a
  recommendation counts as a published claim. **I think it does**, and that it
  should be gated by the derived-claim validator before the tool ships a single
  suggestion.

## 9. Critical path, honestly ordered

1. **The derived-claim validator.** Nothing ships before it.
2. **Per-character modelling.** My chain currently equips every trio with
   best-in-slot and fires every ability on cooldown. A gap engine needs it driven
   from *observed* gear and *observed* rates. This is the real work and I am not
   going to pretend otherwise.
3. **Delta validation against before/after logs** — the loop in §5, on our own
   characters first.
4. **The =Auras component** — small, pure, liftable, offered to Shara.
5. **The Send-to-50-Upgrades handoff.**

## 10. One thing the owner can do that makes all of it cheaper

The owner proposed an in-log marker:

```
/tell Shara ATTN CLAUDE: Avenrae: PAL ENC BRD, Shara: SHM BRD CLR
```

**Adopt it, and extend it slightly.** It solves a real failure: yesterday I
credited a charm pet to the wrong character and published a headline that one
sentence from the owner then reversed. A sidecar file would have worked too, but
**a marker inside the log cannot get separated from it**, which a sidecar can.

Proposed grammar, parsed strictly and ignored if malformed:

```
ATTN CLAUDE: <char>: <CLS> <CLS> <CLS>[; pet=<name>][; buffs=<char>] [| <char>: ...]
```

so today's log would have carried
`ATTN CLAUDE: Avenrae: PAL ENC BRD; pet=Heart harpie | Shara: SHM BRD CLR`
and the attribution error could not have happened.
