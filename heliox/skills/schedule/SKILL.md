---
name: schedule
description: "Use `heliox schedule ...` for durable user-visible future work: reminders, one-shot follow-ups, recurring briefs/check-ins, calendar-like events, and schedules the user must be able to list, update, disable, or delete. Trigger whenever the user says remind me, check later, every day/week, morning brief, follow up at a time, or asks to manage scheduled work. Do NOT use session-native cron / wakeup / sleep-loop tools for any user-visible deferred work — those run only inside the current session and the user cannot see, list, cancel, or observe them; `heliox schedule` lives in schedule-service and survives pod restarts, which is what users expect when they say 'remind me'."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox schedule --help"
---

# Heliox Schedule

Start by reading `../shared/SKILL.md`.

Use Helio schedules for user-visible future work. They live in schedule-service and survive pod restarts.

Do not use session-native cron or wakeup tools for user-visible Helio work. The user cannot see, cancel, or observe those reliably.

## Create

```bash
heliox schedule create "<name>" --start "<rfc3339>" --type one-shot --channel <channel_id> --description "<prompt>" --json
```

```bash
heliox schedule create "<name>" --cron "<five-field-cron>" --tz <iana_timezone> --channel <channel_id> --description "<prompt>" --json
```

```bash
heliox schedule create "<name>" --start "<rfc3339>" --end "<rfc3339>" --channel <channel_id> [--location "<text>"] [--attendees "user_a,user_b"] --json
```

Important fields:

- `--channel` is where the AI reply lands when the schedule fires.
- `--description` is the instruction for the future turn, not merely display text.
- Use RFC3339 timestamps for `--start` and `--end`.
- Use IANA timezones for `--tz`, for example `Asia/Shanghai` or `America/Los_Angeles`.
- Use five-field cron expressions.
- Add `--disabled` to create without enabling.

## Types

The server derives type from field shape unless `--type` is supplied:

| Shape | Meaning |
| --- | --- |
| `--cron` without `--start` | recurring runtime cron |
| `--start --type one-shot` | fire once, then disable |
| `--start --end` | calendar interval |
| `--start --cron` | recurring calendar event |

For reminders and future assistant work, prefer explicit `--type one-shot` for one-time work and `--cron --tz` for recurring work.

## Manage

```bash
heliox schedule list --json
heliox schedule list --enabled --json
heliox schedule list --disabled --json
heliox schedule list --sort next_run_at_asc --limit 20 --json
heliox schedule show <id> --json
heliox schedule update <id> --enable --json
heliox schedule update <id> --disable --json
heliox schedule delete <id> --force --json
```

Use `schedule update --disable` when the user may want the schedule back. Use
delete only when they ask to remove it.

## Update

```bash
heliox schedule update <id> --name "<name>" --json
heliox schedule update <id> --description "<prompt>" --json
heliox schedule update <id> --start "<rfc3339>" --json
heliox schedule update <id> --end "<rfc3339>" --json
heliox schedule update <id> --end "" --json
heliox schedule update <id> --cron "<five-field-cron>" --tz <iana_timezone> --json
heliox schedule update <id> --attendees "user_a,user_b" --json
heliox schedule update <id> --add-attendee user_c --remove-attendee user_a --json
heliox schedule update <id> --enable --json
heliox schedule update <id> --disable --json
```

`--attendees` replaces the whole list. `--add-attendee` and `--remove-attendee` can be repeated and cannot be combined with `--attendees`.
