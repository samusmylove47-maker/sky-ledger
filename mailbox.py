#!/usr/bin/env python3
"""mailbox.py -- a polled mailbox between two sessions that cannot both call SendMessage.

THE PROBLEM, STATED FROM WHAT ACTUALLY HAPPENED RATHER THAN FROM WHAT I ASSUMED.
Session C and I exchanged two full rounds of high-quality findings in under an hour.
C reaches me by SendMessage; I reach C by pushing a file C fetches. CONTENT TRANSFER
DID NOT FAIL ONCE. Two things did:

  ADDRESSING   I told C its reply was on `master`. It was on a branch 60 commits
               ahead and master did not carry the file. C would have fetched, found
               nothing, and had NO WAY TO TELL THAT FROM MY NEVER HAVING WRITTEN IT.
  NOTIFICATION Neither of us learns that the other has written. C polls when it
               happens to; I poll when a tick fires.

So this is not a transport. Git is the transport and it works. This is an ADDRESS and
a POLL RECORD, and the poll record is the part that matters:

    LAST-POLLED-PEER: <when> <sha> <verdict>

with the verdict from a CLOSED SET -- NEW / NOTHING-NEW / UNREACHABLE. Never blank.
That is Session C's own sentence turned into a field: "'I checked and it was clean'
and 'I did not check' are different states and only one of them is reportable."
UNREACHABLE exists so that failing to look can never be recorded as looking and
finding nothing, which is the fault this repository has caught more than any other.

    python3 mailbox.py            validate MY mailbox (hermetic, no network)
    python3 mailbox.py --poll     fetch the peer's repo and read its mailbox
    python3 mailbox.py --selftest
"""
import datetime, io, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MAILBOX = os.path.join(ROOT, "MAILBOX.md")

# A message is open, answered, closed, or purely informational. Closed set, for the
# same reason every other state in this repository is one: a free-text status is one
# nobody can check.
STATES = ("AWAITING-REPLY", "ANSWERED", "CLOSED", "FYI")
# What a poll actually established. UNREACHABLE is the whole point of the field.
VERDICTS = ("NEW", "NOTHING-NEW", "UNREACHABLE")

HDR = re.compile(r"^([A-Z][A-Z-]+):[ \t]+(\S.*)$", re.M)
MSG = re.compile(r"^MSG:\s+(\S+)\s+\[([A-Z-]+)\]\s+to=(\S+)\s+re=(\S+)\s+--\s+(\S.*)$", re.M)
FILEREF = re.compile(r"^\s+file:\s+(\S+)\s*$", re.M)
# The verdict captures \S+, NOT [A-Z-]+, deliberately. A pattern that only matches
# VALID input turns an INVALID value into an ABSENT one: writing
# "LAST-POLLED-PEER: ... probably-fine" made the line fail to parse, so the gate
# reported "no poll record" -- a different diagnosis from "bad verdict", and the
# wrong one. Parse what a person would plausibly write; judge it afterwards.
POLL = re.compile(r"^LAST-POLLED-PEER:\s+(\S+)\s+(\S+)\s+(\S+)\s*$", re.M)

REQUIRED = ("MAILBOX-VERSION", "FROM", "REPO", "BRANCH", "PEER", "PEER-REPO",
            "PEER-BRANCH", "PEER-MAILBOX")


def audit(text, exists):
    """exists(path) -> bool. Returns [(name, ok, detail)]."""
    out = []
    hdr = dict(HDR.findall(text or ""))
    msgs = MSG.findall(text or "")

    # POSITIVE CONTROL FIRST. A pattern matching nothing passes every check below it.
    probe = MSG.search("MSG: E-000 [FYI] to=C re=probe -- a probe line\n")
    out.append(("the message pattern matches a known-good line", bool(probe),
                f"probe -> {probe.group(1) if probe else None}"))

    for k in REQUIRED:
        out.append((f"header {k} is present", k in hdr, f"headers {sorted(hdr)}"))

    # THE ADDRESSING FIX. I named a ref that did not carry the file. The mailbox
    # states the branch, and every open message names a file that must exist ON IT.
    out.append(("at least one message is declared", bool(msgs), f"{len(msgs)} found"))
    ids = [m[0] for m in msgs]
    out.append(("no message id is reused", len(ids) == len(set(ids)), f"ids {ids}"))
    for mid, state, to, re_, what in msgs:
        out.append((f"{mid}: state is one of {list(STATES)}", state in STATES,
                    f"got {state!r}"))
        out.append((f"{mid}: says what it is about", len(what.strip()) >= 15,
                    f"got {what[:40]!r}"))

    # Every file: line must point at something that is actually here.
    refs = FILEREF.findall(text or "")
    out.append(("every message names a file", len(refs) >= len(msgs),
                f"{len(refs)} file refs for {len(msgs)} messages"))
    missing = [r for r in refs if not exists(r)]
    out.append(("every named file EXISTS on this branch", not missing,
                f"missing {missing} -- this is the exact defect that sent C to an "
                f"empty ref"))

    # THE FIELD THIS FILE EXISTS FOR.
    p = POLL.search(text or "")
    out.append(("a poll record is present at all", bool(p),
                "absent -- silence with no poll record is indistinguishable from "
                "never having looked"))
    if p:
        out.append((f"the poll verdict is one of {list(VERDICTS)}",
                    p.group(3) in VERDICTS,
                    f"got {p.group(3)!r} -- a free-text verdict is one nobody can check"))
    return out


def here(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def record(sha, verdict, stamp):
    """Write the poll result back into MAILBOX.md.

    WHY THIS IS NOT LEFT TO THE AUTHOR. A poll record that must be hand-edited goes
    stale, and every hand-maintained field in this repository has: LAST CHANGE stood
    15 hours old under a header reading "update on EVERY push", and "0 commits ahead"
    stood through sixty commits and was then repeated to a peer as fact.
    A field whose whole purpose is to say WHEN I last looked cannot depend on my
    remembering to say it. Every exit path of --poll writes here, including the
    UNREACHABLE ones -- especially those, because a failed look is the reading most
    worth having a timestamp on."""
    try:
        t = io.open(MAILBOX, encoding="utf-8").read()
    except OSError:
        return False
    new, n = re.subn(r"^LAST-POLLED-PEER:.*$",
                     f"LAST-POLLED-PEER: {stamp} {sha or '-'} {verdict}",
                     t, count=1, flags=re.M)
    if not n:
        return False
    io.open(MAILBOX, "w", encoding="utf-8").write(new)
    return True


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("SELFTEST -- each check must fail when its own condition is broken")
        bad = 0

        def chk(name, ok, d=""):
            global bad
            print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1

        GOOD = ("\n".join(f"{k}: x" for k in REQUIRED) +
                "\nLAST-POLLED-PEER: 1-Sep-17:59Z abc1234 NOTHING-NEW\n"
                "MSG: E-001 [AWAITING-REPLY] to=C re=verb-counts -- the first-person split\n"
                "  file: handover/x.md\n")
        yes = lambda p: True

        def fired(t, e=yes):
            return [n for n, ok, _ in audit(t, e) if not ok]

        chk("a well-formed mailbox passes", not fired(GOOD), f"{fired(GOOD)}")
        chk("a state outside the closed set fires",
            any("state is one of" in x for x in
                fired(GOOD.replace("[AWAITING-REPLY]", "[PENDING]"))), "")
        chk("a free-text poll verdict fires",
            any("poll verdict" in x for x in
                fired(GOOD.replace("NOTHING-NEW", "probably-fine"))), "")
        # THE ONE THIS FILE EXISTS FOR, both halves.
        chk("NO poll record at all fires -- silence is not a report",
            any("poll record is present" in x for x in
                fired(re.sub(r"^LAST-POLLED-PEER:.*$", "", GOOD, flags=re.M))), "")
        chk("UNREACHABLE is a LEGAL verdict, not a failure",
            not fired(GOOD.replace("NOTHING-NEW", "UNREACHABLE")),
            "a gate that punishes an honest 'I could not look' teaches you to write "
            "NOTHING-NEW instead")
        # THE ADDRESSING FIX.
        chk("a named file that does NOT exist fires",
            any("EXISTS on this branch" in x for x in fired(GOOD, lambda p: False)), "")
        chk("a missing header fires",
            any("header BRANCH" in x for x in
                fired(GOOD.replace("BRANCH: x", "", 1))), "")
        chk("NO messages at all is caught, not read as clean",
            any("at least one message" in x for x in
                fired(re.sub(r"^MSG:.*$", "", GOOD, flags=re.M))), "")
        # record() is the piece that keeps the field honest, so it cannot be the one
        # piece with no test. Exercised on its SUBSTITUTION, hermetically -- the real
        # function writes MAILBOX.md and a self-test must not.
        import re as _re
        def _sub(t, stamp, sha, verdict):
            out, n = _re.subn(r"^LAST-POLLED-PEER:.*$",
                              f"LAST-POLLED-PEER: {stamp} {sha or '-'} {verdict}",
                              t, count=1, flags=_re.M)
            return out, n
        w, n = _sub(GOOD, "2026-09-01T19:39Z", "abc1234", "UNREACHABLE")
        chk("a recorded poll replaces the line and does not append a second",
            n == 1 and w.count("LAST-POLLED-PEER:") == 1, f"n={n}")
        chk("...and the rewritten mailbox still passes every check",
            not fired(w), f"{fired(w)}")
        chk("recording an UNREACHABLE poll with NO sha still yields a legal line",
            not fired(_sub(GOOD, "2026-09-01T19:39Z", "", "UNREACHABLE")[0]),
            "a failed fetch cannot be recorded, so it would go unrecorded")
        chk("a mailbox with no poll line is NOT silently given one",
            _sub("MAILBOX-VERSION: 1\n", "x", "y", "NEW")[1] == 0,
            "record() would fabricate a poll record where none was declared")
        chk("a duplicate message id fires",
            any("reused" in x for x in fired(
                GOOD + "MSG: E-001 [FYI] to=C re=dupe -- a second use of one id\n"
                       "  file: handover/x.md\n")), "")
        print(f"  {bad} self-test checks failed")
        sys.exit(1 if bad else 0)

    text = io.open(MAILBOX, encoding="utf-8").read() if os.path.exists(MAILBOX) else ""
    if "--poll" in sys.argv:
        hdr = dict(HDR.findall(text))
        repo, branch = hdr.get("PEER-REPO", ""), hdr.get("PEER-BRANCH", "main")
        box = hdr.get("PEER-MAILBOX", "MAILBOX.md")
        d = os.path.join("/home/user", *repo.split("/")) if repo else ""
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        print(f"peer {repo} @ {branch}, mailbox {box}")
        if not d or not os.path.isdir(os.path.join(d, ".git")):
            print(f"  VERDICT UNREACHABLE -- no checkout at {d}. NOT 'nothing new'.")
            print(f"  recorded: {record('', 'UNREACHABLE', stamp)}")
            sys.exit(0)
        r = subprocess.run(["git", "-C", d, "fetch", "origin", branch],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  VERDICT UNREACHABLE -- fetch failed: {r.stderr.strip()[:120]}")
            print(f"  recorded: {record('', 'UNREACHABLE', stamp)}")
            sys.exit(0)
        sha = subprocess.run(["git", "-C", d, "rev-parse", "--short",
                              f"origin/{branch}"], capture_output=True, text=True)
        cat = subprocess.run(["git", "-C", d, "show", f"origin/{branch}:{box}"],
                             capture_output=True, text=True)
        print(f"  peer head {sha.stdout.strip()}")
        prev = ""
        m = POLL.search(text)
        if m:
            prev = m.group(2)
        moved = sha.stdout.strip() != prev
        if cat.returncode != 0:
            # *** THIS BRANCH RETURNED `NOTHING-NEW` AND THAT WAS A FALSE NEGATIVE. ***
            # It established only that the peer has no MAILBOX.md. It never looked at
            # whether the peer had written anything. On the first tick that used it, C
            # had pushed a document answering a question I had open and this said
            # "nothing new" -- the exact fault this file exists to make unwriteable,
            # committed by this file.
            # A poll that cannot read the thing the protocol defines is UNREACHABLE.
            print(f"  peer has NO {box} -- the protocol is proposed, not adopted, so "
                  f"there is no mailbox to read.")
            print(f"  VERDICT UNREACHABLE. This is NOT 'nothing new': I could not "
                  f"perform the poll, only record the head.")
            if moved:
                print(f"  *** PEER HEAD MOVED {prev or '(none)'} -> "
                      f"{sha.stdout.strip()} AND I CANNOT SEE WHAT CHANGED. "
                      f"Read the peer's log by hand this tick. ***")
            else:
                print(f"  peer head unchanged at {sha.stdout.strip()} since the last "
                      f"recorded poll, which is the only negative I can honestly give.")
            print(f"  recorded: {record(sha.stdout.strip(), 'UNREACHABLE', stamp)}")
            sys.exit(0)
        pm = MSG.findall(cat.stdout)
        print(f"  peer mailbox: {len(pm)} message(s)")
        for mid, st, to, re_, what in pm:
            print(f"    {mid} [{st}] to={to} re={re_} -- {what[:60]}")
        # NEW only if the peer head actually moved since the last recorded poll; a
        # mailbox I have already read is not news because I read it again.
        v = "NEW" if sha.stdout.strip() != prev else "NOTHING-NEW"
        print(f"  VERDICT {v}")
        print(f"  recorded: {record(sha.stdout.strip(), v, stamp)}")
        sys.exit(0)

    print(f"read 1 file: MAILBOX.md ({len(text)} bytes)")
    rows = audit(text, here)
    bad = 0
    for n, ok, d in rows:
        print(f"  [{'ok' if ok else 'FAIL'}] {n}" + ("" if ok else f"  -- {d}"))
        bad += 0 if ok else 1
    print(f"  {len(rows)} checks, {bad} failing")
    sys.exit(1 if bad else 0)
