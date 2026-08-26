# Lark / Feishu (`heliox tool lark -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model.

A **flat provider** wrapping the official `lark-cli`: everything after `--` is
its own CLI, speaking the Lark/Feishu Open Platform API.

```bash
heliox tool lark -- <domain> <command> [flags...]
heliox tool lark -- --help              # full command list, works before you connect
```

## Two identities, and the one that bites

Every call runs as one of two identities:

| | Reads / writes | How |
| --- | --- | --- |
| **bot** (default) | Only what the app itself owns or was invited into | nothing to pass |
| **user** | What that person can see: their calendar, chats, docs, mail | `--as user` **after** the `--` |

**The bot has its own empty calendar, empty chat list, empty drive.** So a
personal read that forgets `--as user` does not fail. It succeeds and returns
nothing:

```json
{ "ok": true, "identity": "bot", "data": [], "meta": {} }
```

Reported as-is, that becomes "you have nothing scheduled" about a person whose
day is full. Two rules, both checkable from output you already hold:

1. **A question about someone's own data is a `--as user` call.** Calendar,
   messages, documents, mail, drive: if the answer is *theirs*, the identity
   must be theirs.
2. **Read the identity the call reports, before you report anything.** The
   `+shortcut` results carry it as `"identity"` (the block above is a real
   `calendar +agenda` answer); `heliox tool lark -- whoami` asks outright and
   works for any command whose output does not say. If it is `bot` and you were
   asked about a person, you did not read their data. Say that, and do not report
   the empty result as their answer.

**Which** person `--as user` means is not something you choose: it is whoever
asked in the batch that started this turn, and Helio injects only that person's
token. So `--as user` is right when you are answering the person who asked, and
there is nothing to pass to aim it. When several people asked in one turn only
the first is represented. If you are working for one of the others, their data
is not reachable this turn; say so rather than reporting the first asker's.

```bash
heliox tool lark -- calendar +agenda --as user
```

## When `--as user` is refused

lark-cli reports `strict mode is "bot", only bot-identity commands are
available` and points at `lark-cli config strict-mode`. **That command is not
the remedy and cannot be run here**: the message is derived, not configured, and
it appears whenever no user token was injected for the acting person.

**heliox appends the real cause to the failure.** Read past lark-cli's own
message to the line that starts "This ran as the assistant". It names which of
these applies:

- that person has not completed **Connect as me** for this Lark connection, or
- their grant was revoked / expired, or
- the person whose identity Helio injected is not the one you meant; this
  turn represents whoever asked first; `-- whoami` tells you who that is.

The fix is a fresh identity authorization from that person, not a policy
switch. **heliox cannot mint that link**: authorizing your own identity is a
separate, optional step Helio offers on the connection itself, after it is
connected, and only that person can complete it. Ask them for it in one line,
saying what you need it for. `heliox tool lark auth` is a different thing: it
mints the *connection* link, and re-running it does not produce a user
identity.

Until they authorize, say the identity is unavailable, and do not silently answer
as the bot.

## Surface

Run `-- <domain> --help` for the full flags; `-- schema <service>.<resource>.<method>`
gives params, types and required scopes. Prefer the `+shortcut` commands over raw
API resources.

- `calendar`: `+agenda`, `+create`, `+freebusy`, `+rsvp`, plus raw `events` /
  `calendars` / `event.attendees` resources.
- `im`: messages and group chats. **Nothing stops a send.** Lark is a binary
  tool, and those run ungated; the approval gate in [../SKILL.md](../SKILL.md)
  covers service tools only. So `--as user` here posts under that person's name,
  to their colleagues, the moment you run it. Get their word for the actual text
  first; there is no card between you and the send.
  **A mirrored Helio channel is not this door**: your reply there already routes
  back to Lark on its own, so answer with `heliox message send`. Sending it
  through `im` instead double-posts it, ungated and under someone's name.
- `docs` / `drive` / `sheets` / `base` / `wiki`: documents, files, tables.
- `contact`, `task`, `approval`, `vc`, `minutes`, `mail`.

Output is the provider's JSON verbatim on stdout. Exit codes: `0` success,
`1` runtime/API failure, `2` usage error.
