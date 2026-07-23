# Gumroad (`heliox tool gumroad -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Gumroad is a
**flat provider**: everything after `--` is the Gumroad tool's own CLI, speaking
Gumroad API v2 with the connected creator account's OAuth token.

```bash
heliox tool gumroad [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `user`, `product`, `sale`, `subscriber`, `offer-code`, `license`.
Run `-- <resource> --help` for the full flag surface.

## What it is good for

Store operations on a Gumroad creator account: see what is selling, inspect and
toggle products, look at buyers and subscribers, run discount codes, and verify
software licenses.

```bash
heliox tool gumroad -- user get                    # whoami / sanity-check the connection
heliox tool gumroad -- product list                # the account's catalog
heliox tool gumroad -- product get --id <id>
heliox tool gumroad -- sale list --after 2026-01-01 --before 2026-02-01
heliox tool gumroad -- sale get --id <sale-id>
heliox tool gumroad -- subscriber list --product-id <id>
```

Sales list is the revenue-reporting surface — filter by `--after` / `--before`
(YYYY-MM-DD), `--email`, `--product-id`.

## Pagination (do not lose the cursor)

`sale list` returns at most one page plus a `next_page_key`. To read the next
page, pass it back as `--page-key`:

```bash
heliox tool gumroad -- sale list --page-key <next_page_key-from-the-previous-page>
```

The output is Gumroad's response verbatim, so read `next_page_key` off the JSON
and loop until it is absent. The older numeric `page` parameter is deprecated —
always page with `--page-key`.

## Fulfilment and refunds

```bash
heliox tool gumroad -- sale mark-shipped --id <sale-id> [--tracking-url <url>]
heliox tool gumroad -- sale refund --id <sale-id>                 # full refund
heliox tool gumroad -- sale refund --id <sale-id> --amount-cents 500   # partial
```

Omit `--amount-cents` for a full refund; pass it (in cents) for a partial.

## Products and discount codes

```bash
heliox tool gumroad -- product enable  --id <id>     # publish
heliox tool gumroad -- product disable --id <id>     # unpublish
heliox tool gumroad -- product delete  --id <id>

heliox tool gumroad -- offer-code list   --product-id <id>
heliox tool gumroad -- offer-code create --product-id <id> --name SALE10 --amount-off 1000            # $10 off (cents)
heliox tool gumroad -- offer-code create --product-id <id> --name HALF   --amount-off 50 --percent    # 50% off
heliox tool gumroad -- offer-code update --product-id <id> --id <id> --max-purchase-count 5
heliox tool gumroad -- offer-code delete --product-id <id> --id <id>
```

`--amount-off` is cents by default; add `--percent` to make it a percentage.

## Licenses

```bash
heliox tool gumroad -- license verify  --product-id <id> --license-key <key>   # read-only by default
heliox tool gumroad -- license verify  --product-id <id> --license-key <key> --increment-uses-count   # counts a use
heliox tool gumroad -- license enable  --product-id <id> --license-key <key>
heliox tool gumroad -- license disable --product-id <id> --license-key <key>
```

`license verify` does **not** consume a seat unless you pass
`--increment-uses-count` — leave it off for a plain check.

## Output and errors

Every command prints Gumroad's JSON on stdout. Gumroad wraps success as
`{"success":true, ...}`; the tool passes that through so list keys
(`products`, `sales`, `subscribers`, …) and the `next_page_key` cursor survive.
On failure the tool exits non-zero and prints Gumroad's message to stderr
(`--json` gives `{"error":{...}}`). Note the dialect: Gumroad can return HTTP 200
with `success:false` (e.g. a not-found product) — the tool treats that as an
error, not a silent empty result.

## Safety

Refunds, product enable/disable/delete, offer-code changes, and license
enable/disable are **real, outward-facing mutations** on the creator's live
store: follow the sensitive-operation rule from `../SKILL.md` — confirm
with the user before first-of-kind writes in a session, and never refund,
retire a product, or disable a license the user has not sanctioned.
