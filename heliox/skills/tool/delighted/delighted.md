# Delighted (`heliox tool delighted -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model.

> **UNAVAILABLE: provider sunset.** The Delighted product was fully shut down
> on 2026-06-30 and its REST API returns HTTP 410 Gone. This tool ships hidden
> and can never complete a live call: there is no account to connect and every
> command fails at the network. Do **not** offer it to the user or attempt a
> connect. Treat Delighted as retired. This page documents the intended
> surface for the record only; it exists because the tool is code-complete but
> permanently blocked, not because it can be used.

Delighted was an NPS/CSAT/CES customer-experience survey platform. It is a
**flat provider**: everything after `--` was the Delighted tool's own CLI,
speaking the Delighted v1 REST API with the connected project's API key
(HTTP Basic, key as username).

```bash
heliox tool delighted [--account <key>] -- <resource> <verb> [flags...]
```

Resources (were): `metrics`, `response`, `people`, `bounces`, `unsubscribes`,
`autopilot`. Run `-- <resource> --help` for the full flag surface.

- `metrics get`: read aggregate NPS/CSAT/CES scores over a window.
- `response list|get|create|update`: survey responses (verbatim feedback,
  scores, tags/notes).
- `people list|send|delete|cancel-pending`: survey recipients; `send`
  creates/updates a person and optionally schedules a survey.
- `bounces list`, `unsubscribes list|add`: deliverability / suppression.
- `autopilot memberships list|add|remove`, `autopilot config get`: Autopilot
  enrollment, scoped by `--platform email|sms`.

Output is the provider's JSON verbatim on stdout. Exit codes: `0` success,
`1` runtime/API failure (a `401` invalidates the stored key), `2` usage error.
