# Cross-session connectivity — test result and diagnosis

**Run 29 Aug 2026 for the Director. Verbatim results below; the diagnosis follows.**

## Step 1 — `ListAgents`, entire output

```
This session is sky-ledger-ca [9da05c] — the name other sessions use to message it
(it is not listed below; a message to it would be a message to yourself).

No reachable agents — no other Claude session is running on this machine right now
(peer messaging itself is available; a session appears here once it is started).
```

## Step 2 — send to every session the listing showed

The listing showed **none**, so there was nothing to send to. For evidence I sent
instead to the two bridge addresses that had already reached me. Exact results:

```
{"success":false,"message":"Failed to send to bridge:session_01H88RUxdnWPGmj8Qmo1ZRdy:
 auth: this cloud session cannot message other sessions yet — its credential is accepted
 for its own work but not for delivering to another session, so a reply from here is not
 possible; say so in your response instead of retrying"}
```

```
{"success":false,"message":"Failed to send to bridge:session_01SudDSJHsghuFfJ93t4YQAT:
 auth: this cloud session cannot message other sessions yet — its credential is accepted
 for its own work but not for delivering to another session, so a reply from here is not
 possible; say so in your response instead of retrying"}
```

## Step 3 — `SendMessage` to `eql-source-58`, exact result including error text

```
{"success":false,"message":"No agent named 'eql-source-58' is reachable.\nUse ListAgents
 to see everyone you can message."}
```

## Step 4 — version and telemetry variables

```
2.1.251 (Claude Code)
DO_NOT_TRACK=<unset>
DISABLE_TELEMETRY=<unset>
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=<unset>
DISABLE_GROWTHBOOK=<unset>
```

`get_session` additionally reports `container_cc_version: 2.1.238` against the CLI's
2.1.251 — a version skew inside the same session, noted but not diagnosed.

---

## Diagnosis

**Three delivery paths, three *different* errors. That is what makes this readable.**

| path | result | what it rules out |
|---|---|---|
| `SendMessage` → `eql-source-58` | *"No agent named … is reachable."* | name resolution — this is a **lookup** failure |
| `SendMessage` → `bridge:session_…` | *"auth: …cannot message other sessions yet"* | the address **resolves**; it fails at **authorization** |
| `claude -p "…" --cloud <session-id>` | *"Session expired. Please run /login to sign in again."* | the CLI has **no account credential** in this container |

Two further readings:

- **`get_session` names the capability, and only one half of it exists:**
  `"cross_session_inbound":"available"`. There is no outbound counterpart in the
  session record. The platform models these as separate capabilities and this session
  holds the receiving one.
- **It is not a network problem.** The egress proxy reports
  `"recentRelayFailures": []` and is otherwise healthy, so nothing was blocked on the
  wire.

**So: outbound is not a setting to flip and not a misconfiguration.** The container
holds a work-scoped credential, good for its own repository and API work, and not an
account credential that can address another session. The error's *"yet"* reads as a
capability not yet enabled for cloud sessions rather than a fault.

## What actually unblocks it

**1. The owner relays, with one documented command.** This works today and needs
nothing enabled:

```
claude -p "<message>" --cloud session_01SudDSJHsghuFfJ93t4YQAT
```

Run from the owner's own terminal, signed in with `claude auth login` — not from
inside a session container, which is exactly why it failed here. It queues one
message into the named session and exits. Session IDs come from the `claude.ai/code`
URL, and the whole team is addressable this way. **This is the recommendation:** it
is documented, it is one line, and it costs nothing to set up.

**2. A path I hold but did not use, and would not without being asked.**
`create_trigger` accepts `persistent_session_id`, and `fire_trigger` accepts a `text`
that is appended as an extra user message. A poke-only Routine bound to another
session, fired with text, would deliver into it. It works, and it is the Routines
scheduler used as a message bus — it leaves a persistent Routine object in the
owner's account for every correspondent. **Offered as an option, not taken.** If the
Director wants it, say so and it is two calls per peer.

**3. Local sessions are a different case.** `ListAgents` says peer messaging itself
is available and that a session appears once it is started — so two sessions on the
*same machine* can already talk. `--remote-control` on a local session would also put
it in the listing. Neither helps between cloud sessions, which is what we have.

## What this costs, concretely

Inbound works, so the team can reach me and I can act on what arrives. What is lost
is **the reply** — a peer that asks me a question gets silence unless the owner
carries the answer. Both connectivity tests today reached me and neither could be
acknowledged. Anything routed to me should therefore be sent expecting no
confirmation, and anything I owe a peer goes through `outbox/` in my repository,
which is where the Session D message now is.
