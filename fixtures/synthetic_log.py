#!/usr/bin/env python3
"""synthetic_log.py -- the invented log the fixture and the parity harness share.

Lifted verbatim out of make_fixture.py on 31 Aug so that bundle/parity.py could
stop depending on a real player log.

WHY IT MOVED. parity.py read `corpus/corpus/.../jos437-finishing-blow.log`, and
`corpus/corpus` was a COMMITTED SYMLINK to an absolute path carrying this
session's own UUID. It resolved on exactly one container and nowhere else -- so a
fresh clone appeared to verify parity while in fact borrowing a file from the
machine that wrote it, and CI would have gone red on its first run for a reason
that had nothing to do with the code.

A synthetic log is the better default anyway: parity tests the PORT, not the
mechanic, and it should not need a real player's log to do that. Nothing here is
measured. The numbers are invented because the log is invented.
"""
import random


def build():
    """The 523-line synthetic log. Deterministic: same bytes every call."""
    # Deterministic, so the fixture is reproducible and a diff means a real change.
    rng = random.Random(20260830)
    LINES, t = [], 0

    def stamp(body):
        nonlocal t
        h, m, s = 20 + t // 3600, (t // 60) % 60, t % 60
        LINES.append(f"[Sat Aug 30 {h:02d}:{m:02d}:{s:02d} 2026] {body}")

    MOBS = ["a rock golem", "a sand giant", "a dune tarantula"]
    stamp("ATTN CLAUDE: EXAMPLE: WAR MNK SHM")
    for wave in range(6):
        mob = MOBS[wave % len(MOBS)]
        for beat in range(38):
            t += 1
            # auto-attack: two swings most seconds
            for _ in range(2):
                if rng.random() < 0.62:
                    stamp(f"You slash {mob} for {rng.randint(38, 96)} points of damage.")
                else:
                    stamp(f"You try to slash {mob}, but miss!")
            # ability lanes, deliberately fired well under their cooldown
            if rng.random() < 0.09:
                stamp(f"You kick {mob} for {rng.randint(14, 34)} points of damage."
                      if rng.random() < 0.65 else f"You try to kick {mob}, but miss!")
            if rng.random() < 0.11:
                stamp(f"You bash {mob} for {rng.randint(16, 40)} points of damage."
                      if rng.random() < 0.6 else f"You try to bash {mob}, but miss!")
            if rng.random() < 0.05:
                stamp(f"You hit {mob} for {rng.randint(180, 240)} points of magic damage "
                      f"by Example Nuke III." + (" (Critical)" if rng.random() < 0.07 else ""))
            if rng.random() < 0.012:
                stamp(f"{mob.capitalize()} resisted your Example Nuke III!")
        stamp(f"You slash {mob} for {rng.randint(38, 96)} points of damage.")
        stamp(f"You have slain {mob}!")
        t += 25   # a gap, so engagements are real runs rather than one block

    return LINES
