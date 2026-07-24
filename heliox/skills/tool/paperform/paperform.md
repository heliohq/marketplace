# Paperform (`heliox tool paperform -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Paperform is a
**flat provider** (not grouped): everything after `--` is the paperform tool's
own CLI.

```bash
heliox tool paperform [--account <key>] -- <resource> <verb> [flags...]
```

It is a **read-only** wrapper over the Paperform v1 API (`api.paperform.co/v1`,
Bearer auth). Use it to triage and summarize form responses, inspect a form's
questions, and read commerce config. It does not create, edit, or delete
anything. API access needs a Standard or Business Paperform plan.

Every command prints the provider's JSON to stdout verbatim. Errors go to
stderr as `{"error":{"message","status"}}` under `--json`. Exit codes: `0` ok,
`1` API/runtime failure (a `429` surfaces the retry delay), `2` usage error.

## The core loop

The most common task is **read a form's responses**:

```bash
# 1. find the form (slug or id)
heliox tool paperform -- form list
# 2. (optional) understand its questions before reading answers
heliox tool paperform -- field list --form <slug_or_id>
# 3. read the responses — this is the payload you summarize/triage
heliox tool paperform -- submission list --form <slug_or_id> --limit 50
# 4. pull one response in full
heliox tool paperform -- submission get --id <submission_id> --form <slug_or_id>
```

## Commands

| Command | What it reads |
|---|---|
| `form list [pagination]` | Forms accessible by the key |
| `form get --form <slug_or_id>` | One form |
| `field list --form <id>` | A form's fields (questions) |
| `field get --form <id> --key <k>` | One field |
| `submission list --form <id> [pagination]` | Responses to a form |
| `submission get --id <id> [--form <id>]` | One response |
| `partial-submission list --form <id> [pagination]` | Abandoned responses |
| `partial-submission get --id <id> [--form <id>]` | One partial response |
| `space list` / `space get --id <id>` / `space forms --id <id>` | Workspace tree |
| `product list --form <id>` | A form's products/order config |
| `coupon list --form <id>` / `coupon get --form <id> --code <c>` | Discount coupons |

## Pagination (list commands)

Passed straight through to Paperform, omitted when unset:

`--limit <n>` (default 20, max 100), `--skip <n>`, `--sort ASC|DESC` (default
DESC by created_at), `--after-id <id>` / `--before-id <id>`, `--after-date` /
`--before-date` (UTC), and for `form list`: `--search <text>` +
`--search-fields title,slug,custom_slug`.

## Footguns

- **A form is identified by its slug OR its id** — either works for `--form`.
- **A submission's answers live in the submission object**, keyed by field. Read
  `field list` first when you need to map answers back to their questions.
- **`partial-submission`** is for responses the user started but did not submit;
  most triage uses `submission`, not this.
- **Rate limited (`429`)**: back off using the retry delay in the error message.
