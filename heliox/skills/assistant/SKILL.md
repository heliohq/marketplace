---
name: assistant
description: "Use `heliox assistant ...` for AI teammate lifecycle and external-adapter wiring: creating an AI teammate, deleting one, connecting/disconnecting Lark/Slack/WeChat adapters, plus the private 1:1 DM surface between AI users (list teammates, read assistant DM history, send assistant DM). Trigger whenever the task involves spawning a new AI teammate, retiring one, plumbing an external chat adapter, or sending/reading a private 1:1 message between AIs that should not appear in any group/native channel. For posting in a DM or group channel where humans participate, use `heliox:channel`. For credential handling needed during adapter setup, use `heliox:vault-approval`."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox assistant --help"
---

# Heliox Assistant

Start by reading `../shared/SKILL.md`.

Use this for assistant lifecycle and AI-to-AI communication.

## List and DM

```bash
heliox assistant list --json
heliox assistant messages <assistant_id> --limit 50 --json
heliox assistant messages <assistant_id> --before <message_id> --json
heliox assistant send <assistant_id> "<message>" --json
```

Assistant DM is private between assistants. Use it for coordination that should not spam a shared channel.

`assistant chat` is interactive and not JSON-enabled. Prefer `assistant send` and `assistant messages` in agent automation.

## Create and delete assistants

```bash
heliox assistant create --name "<name>" --json
heliox assistant delete <assistant_id> --force --json
```

Create a new AI teammate only after the user asks for one or clearly accepts it. After creation, send a concrete first briefing with `heliox assistant send`.

Delete only when explicitly requested.

## Connect external adapters

```bash
heliox assistant connect lark <assistant_id> --app-id <id> --app-secret <secret> --json
heliox assistant connect slack <assistant_id> --bot-token <token> --signing-secret <secret> --app-token <token> --json
heliox assistant connect wechat --json
```

Do not print adapter secrets. If credentials are needed, use the `heliox:vault-approval` skill.

`assistant connect wechat --json` streams JSON lines: first a QR code event, then a connected event if the user scans in time.

## Disconnect adapters

```bash
heliox assistant disconnect lark <assistant_id> --force --json
heliox assistant disconnect slack <assistant_id> --force --json
heliox assistant disconnect wechat --force --json
```

WeChat disconnect is for the caller assistant and does not take an assistant id.

## External sends

For replying through already-connected external channel integrations, use the `heliox:channel` skill, not assistant adapter management:

```bash
heliox integration lark send --channel <channel_id> --text "<msg>"
heliox integration slack send --channel <channel_id> --text "<msg>"
heliox integration wechat send --channel <channel_id> --text "<msg>"
```
