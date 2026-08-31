# The Concordance — bounded investigation, not a plan

**Session E (EQLS Residual), 31 August 2026, 19:45Z.**
Authorised by the Director as a **bounded investigation**: produce a proposal,
commit nothing to the site, build no pipeline. **No competitor was sampled. Nobody
was contacted. Nothing was published.** This document is the analysis that lets
the owner decide, and the decision is theirs.

The audit's §06, verbatim as it reached me:

> *"Publish a falsification rate — The Concordance: sample n entries per rival,
> check against the game, publish disagreement rates and methodology, monthly.
> GUARDRAILS: include your own error rate; give right of reply before publishing;
> credit self-disclosure. Without all three it is a hit piece and backfires."*

---

## 0 · The binding principle, verified rather than quoted from memory

The Director cited `scripts/contamination.py`. I fetched it from `eql-source`
`main` at `e6039020` and read lines 15–18 rather than accept the citation:

> *"A scanner that only finds other people's contamination is an attack ad. This
> one runs against eqlsource and publishes what it finds here. **If it is ever
> pointed outward, it is pointed here first and the results go up either way.**"*

**Verbatim, and there is more above it than was quoted, which changes the
analysis.** Lines 10–13:

> *"On 14 August 2026 an outside audit found six classic haste figures sitting
> inside our own **verified** tier."*

And lines 23–25, which govern the whole method:

> *"A hit is **not** proof of an error. Legends kept a great deal of classic
> EverQuest intact, and several of these patterns are perfectly current."*

**That third quote is the one nobody carried forward and it is the most
important.** A disagreement between us and a rival is not an error by either of
us until something outside both of us adjudicates it.

---

## 1 · What we would have to hold per entry for a rate to be refutable

A published rate is a claim. Under this project's own gate a claim ships only if
someone can attack it. **A disagreement rate is refutable only if a reader can
re-derive any single row without us.** That means per sampled entry:

| field | why it is load-bearing |
|---|---|
| **entry id and rival URL, plus retrieval timestamp** | Rival pages change. An identifier without a timestamp is indistinguishable from a contradiction — the rule that has already caught us twice today. |
| **the rival's value, quoted verbatim, and the byte-range or selector it came from** | So a reader can check we read the page correctly rather than a summary of it. Most "errors" in comparisons of this kind are parsing errors. |
| **our value, with its tier and its own source** | Publishing our number without its provenance makes the comparison us-versus-them rather than both-versus-the-game. |
| **the ADJUDICATOR: what settled it, when, and by whom** | The game client, a log line, a patch note. **Not us.** |
| **the classification, from a closed vocabulary** | `rival_wrong` · `we_were_wrong` · `both_wrong` · `era_difference` · `ambiguous_source` · `unadjudicated`. |
| **`unadjudicated` must be a first-class outcome and must be published** | It is the `<28% · 0/9` of this instrument: the honest answer when nothing settled it. A rate that silently drops unadjudicated rows is measuring our sampling, not their accuracy. |

**The refutability test, stated so it can fail:** hand a stranger one row and the
adjudicator's evidence, with our conclusion removed. If they cannot reach the same
classification, the row is not evidence and must not enter the numerator.

**And the denominator discipline this project already learned the hard way:** four
shipped DPS meters use four different denominators, a 2.03× spread. *Disagreements
÷ what?* Entries sampled, entries where both sides make a claim, or entries where
an adjudicator exists? **Those are three different numbers and only the third can
honestly be called a disagreement rate.**

---

## 2 · Our own error rate — and this is where I stop

**The guardrail says publish it. My answer is that we cannot compute it today, and
therefore the Concordance is a hit piece by construction today.** Stating that and
stopping is what I was asked to do if this was the finding.

### 2.1 The one historical instance is a count, not a rate

*"Six classic haste figures sitting inside our own verified tier."* **Six of how
many?** `contamination.py` records the numerator and I can find no denominator for
it. This project's own rule — *"a resist count with no denominator is not a rate"*
— applies to us exactly as written. **We have one measured instance of our own
error and it is unusable as a rate.**

### 2.2 Ground truth costs owner-hours, and I have measured the rate

Our error rate against *the game* can only be established where something outside
us adjudicates, and for anything the log does not show, that is **the owner, in
game, with a client window.**

**I have a live measurement of what that costs, and it is my own blocked item.**
`35.5` needs *one* client window of *one* weapon at any tier ≥ 1 to settle the
`+1/tier` upgrade floor. It was raised at roughly 04:00Z and is **still blocked at
19:45Z** — **~16 hours for one reading**, and it is the cheapest open question in
my tree.

**Extrapolate honestly: a self-error rate needs the same n as the rival rate.** §3
puts the useful n in the hundreds. At the capture rate we can actually demonstrate,
**a self-error denominator in the hundreds is not months away, it is not on the
roadmap at all.**

### 2.3 The instrument we do have cannot return one of its two answers

Session 0 found this in the falsification ledger and it applies here directly:

> *"The ledger is a book of reversals. A claim that was made, checked, and held
> never enters it. So it can report how often a **disputed** claim failed. It can
> never report how often a claim was right."*

**A self-error rate built from our retraction history has the same shape.** My own
tree would supply a rich numerator — I have published several retractions today
alone — and **no denominator whatsoever**, because claims that were right and never
disputed leave no record. Publishing that number would understate or overstate our
error rate by an unknown factor in an unknown direction.

### 2.4 So the finding

**All three guardrails are load-bearing and we can satisfy two.** Right of reply is
a process choice; crediting self-disclosure is a policy choice. **Our own error
rate is a measurement, we cannot make it, and the audit says that without it the
thing backfires.**

**Recommendation: do not build the Concordance as specified.** Not "not yet" —
*not as specified*, because the missing piece is not effort, it is a denominator
that does not exist and has no path to existing at the sampling rate the project
can sustain.

---

## 3 · What n makes a rate publishable at all

Computed, not asserted. Wilson 95% intervals, observed disagreement 10%:

```
    n    k    point      95% interval    width   verdict
   10    1    10.0%   [ 1.8%, 40.4%]    38.6%   cannot distinguish 10% from 30%
   30    3    10.0%   [ 3.5%, 25.6%]    22.2%   cannot distinguish 10% from 30%
  100   10    10.0%   [ 5.5%, 17.4%]    11.9%   cannot distinguish 10% from 20%
  200   20    10.0%   [ 6.6%, 14.9%]     8.4%   distinguishes 10% from 15%
 1000  100    10.0%   [ 8.3%, 12.0%]     3.7%   tight enough to name a rival
```

**Below n ≈ 200 a published rate cannot separate "they are somewhat wrong" from
"they are three times worse than us", which is the only distinction a reader would
act on.** The project's rule — *one session is a sample and not a rate* — is the
same statement at n = 1.

**And the case that decides the ethics, not just the statistics:** what we may
print when we find *nothing* wrong.

```
    0/9     ->  under 30%, never 0%
   0/50     ->  under 7%,  never 0%
  0/300     ->  under 1%,  never 0%
```

**This is the site's own dry-streak rule — `<28% · 0/9` — pointed at a rival, and
it binds in the direction that flatters them.** We could never publish *"0%
disagreement, they are clean"* on a small sample; we would have to publish *"under
30%"*, which reads as an accusation. **A small honest sample is worse for a rival
than a large one, and worse than saying nothing.** That asymmetry is a reason for
caution that has nothing to do with malice.

---

## 4 · What it costs when we are wrong in public

The principle at `contamination.py:15–18` already binds: **point it at ourselves
first and publish either way.** Starting from there rather than rediscovering it,
what the order does *not* cover:

1. **A retraction never travels as far as the claim.** Measured, today, inside this
   project: *"the engine reads nothing from context"* went from one session to
   three trees in about an hour and took four commits and a direct message from the
   Director to correct. **That was three cooperating sessions who all wanted to be
   right.** A rival has no such incentive and no such channel.
2. **The failure mode is a parsing error, not a lie.** Every self-inflicted wound
   in this project's record is an instrument that could not return one of its two
   answers — a grep that counts mentions, a tooltip that could not reach base
   damage below 10, a fixture gate that compared two of five structures. **Pointed
   at our own tree those cost a retraction. Pointed at a named competitor, the same
   class of bug is a public accusation of incompetence that we cannot fully
   withdraw.**
3. **We would be asserting about people, not data.** `eqlegendstools.com`,
   `loadoutlegends.com` and `eqltools.com` are named in our own credits, and
   `sowoky`'s log-line edge cases are credited in `README.md` as *"the difference
   between a tracker that works and one that quietly lies."* **We are proposing to
   publish a disagreement rate about people we have already thanked in print.**
4. **The asymmetry in §3 is not neutral.** With a sample we can afford, a clean
   rival still reads as "under 30% wrong".

---

## 5 · What I recommend, and the falsifier for it

**Recommendation: do not publish rival disagreement rates. Publish the
adjudications instead.**

Same work, same discipline, none of the statistics we cannot support:

- **Where two sources disagree, print the disagreement and what settled it** — the
  site already does this. `README.md` carries two contradictory-source items
  marked ⚑ and three marked ✧ as resolved, naming `eqlsource` and
  `eqlegendstools` on each side. **That is the Concordance at n = 5, without a
  rate, and it is already shipping.**
- **A per-entry adjudication is refutable on its own.** A rate is only refutable
  with its denominator, its interval and its unadjudicated count — three things a
  reader will not check and we currently cannot supply.
- **It satisfies the audit's actual insight.** The auditor's reason for calling
  this a moat was our *refusal behaviour* — *"printing `<28% · 0/9` instead of
  `0%`"*. **That is a per-claim honesty property, not a rate.** Publishing a rate
  we cannot bound would be abandoning the exact thing the auditor praised.

**The falsifier, since I am proposing nothing without one:** if the owner can
establish an adjudication path that does not cost owner-hours per entry — a
Legends-authored data export, a patch-note corpus, anything outside us that
settles entries in bulk — **then §2 collapses, a self-error denominator becomes
computable, and the Concordance as specified becomes buildable.** That is the one
thing that would reverse this recommendation, and it is a question about the world,
not about our effort.

---

## 6 · Bounds honoured

- **No competitor sampled.** No rival page was fetched for this document.
- **Nobody contacted.** No right-of-reply approach made or drafted.
- **Nothing published.** This file is in my own repository.
- **No pipeline built.** No code was written for the Concordance.
- **`35.5` untouched.** Still BLOCKED on the owner's in-game capture, not worked
  around, not estimated past — and it appears in §2.2 as *evidence about capture
  cost*, which is the only use of it that does not require the answer.
