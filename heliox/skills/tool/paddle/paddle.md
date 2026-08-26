# Paddle (`heliox tool paddle`)

Paddle Billing, the merchant-of-record subscription platform. Use it for
billing/support and revenue ops on the seller's **own** account: look up a
customer's plan and payment history, run subscription lifecycle actions, pull an
invoice, manage the catalog, issue refunds/credits, and export revenue reports.

This wraps **Paddle Billing** (the current product), not the legacy Paddle
Classic vendor API.

Read `../SKILL.md` and the portal model in `../SKILL.md` first. Connect
is api-key: the user pastes a Paddle Billing API key (Paddle dashboard →
Developer Tools → Authentication). You never see the key. The CLI injects it
per call.

## Environments (no base URL to pick)

The key prefix decides live vs sandbox automatically:

- `pdl_live_apikey_…` → live (`api.paddle.com`)
- `pdl_sdbx_apikey_…` → sandbox (`sandbox-api.paddle.com`)

Live and sandbox are **separate accounts with separate data**. A sandbox key
cannot see live customers and vice-versa. Whatever key the user connected is the
account you operate on.

## Output & pagination

- Default output prints the resource `data`. Add `--json` to get the full
  `{ "data": …, "meta": … }` envelope.
- List endpoints are cursor-paged. With `--json`, read `meta.pagination.next`
  and pass it back as `--after <cursor>` to get the next page. `--per-page <n>`
  sets the page size.
- Filter lists with `--status <s>`, the convenience `--customer-id ctm_…` /
  `--subscription-id sub_…` where shown, or a generic repeatable
  `--filter key=value`.

## Preview before you write

Money-moving actions have dry-run twins: run the preview, show the user the
resulting proration/charge, then do the real action:

- `subscription preview-update <id> --data '…'` before `subscription update`
- `subscription preview-charge <id> --data '…'` before `subscription charge`
- `transaction preview --data '…'` before `transaction create`

Financial records are never deleted; cancel / pause / archive-via-status are the
mutation surface.

## Command surface

```
paddle customer      list | get <id> | create | update <id>
                     credit-balances <id> | addresses <id> | businesses <id>
paddle subscription  list | get <id> | update <id>
                     cancel <id> | pause <id> | resume <id> | activate <id>
                     charge <id> | preview-charge <id> | preview-update <id>
paddle transaction   list | get <id> | create | invoice <id> | preview
paddle product       list | get <id> | create | update <id>
paddle price         list | get <id> | create | update <id>
paddle discount      list | get <id> | create | update <id>
paddle adjustment    list | create
paddle report        create | list | get <id> | download-url <id>
paddle event         list | types | notification-settings
```

Write verbs (`create`, `update`, lifecycle actions, previews) take the full
Paddle request body via `--data '<json>'`. Use `paddle <group> <verb> --help`
(after `--` at the shell) for the exact body fields of any endpoint.

## Common jobs

- **"What plan is this customer on and did their last payment go through?"**
  `paddle customer get <ctm_id>`, then
  `paddle subscription list --customer-id <ctm_id>` and
  `paddle transaction list --customer-id <ctm_id>`.
- **"Send them their invoice."** `paddle transaction invoice <txn_id>` returns
  the invoice PDF URL.
- **"Pause / cancel this subscription."** `paddle subscription pause|cancel <id>`
  (add `--data` for `effective_from` if the user wants end-of-term vs immediate).
- **"Refund this charge."** `paddle adjustment create --data '…'` (type
  `refund`/`credit`, referencing the transaction).
- **"What's the catalog?" / "Make a discount code."** `paddle product list`,
  `paddle price list`, `paddle discount create --data '…'`.

## Errors

Failures print Paddle's error object (`code`, `detail`, `documentation_url`) and
exit non-zero. A rejected key (401/403) means the user must paste a fresh key.
Ask them to reconnect. `429` is a rate-limit (per IP, ~240 req/min general);
back off and retry.
