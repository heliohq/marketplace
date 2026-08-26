# Plaid (`heliox tool plaid -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Plaid is a
**flat provider** (not grouped like `google`): everything after `--` is the
plaid tool's own CLI.

```bash
heliox tool plaid [--account <key>] -- <resource> <verb> [flags...]
```

## The mental model (read this first: it prevents the #1 footgun)

Plaid has **two separate credential kinds**, and Helio only stores one of them:

- **App credentials**: the `client_id` + `secret` for one environment. These
  are what the user connected; Helio injects them automatically on every call.
  A connection is **one Plaid app in one environment** (sandbox or production),
  never one bank account.
- **An Item `access_token`**: per **linked bank** (one "Item"). This is **not**
  stored by Helio. You supply it **per call** with `--access-token`. It comes
  from the user's own Plaid **Link** integration, or (in sandbox) from the
  `item exchange-public-token` command below.

So: **institution lookups need no `--access-token`**; anything that reads a
specific bank's data (accounts, balances, transactions, identity, auth) needs
one, and the user (or the sandbox loop) has to give it to you.

`PLAID_ENV` (set when the user connected) selects sandbox vs production. The
`sandbox …` commands only exist in the sandbox environment.

## Always-available: institution reference (no access_token)

```bash
heliox tool plaid -- institutions get --count 10 --country-codes US
heliox tool plaid -- institutions get-by-id --institution-id ins_109508 --country-codes US
```

Use these to resolve an institution id, list supported banks, or check product
support. They work the moment the app is approved, the safest surface.

## Reading a linked bank Item (needs --access-token)

```bash
heliox tool plaid -- accounts get       --access-token <token>
heliox tool plaid -- accounts balance   --access-token <token>
heliox tool plaid -- auth get           --access-token <token>   # account + routing numbers
heliox tool plaid -- identity get       --access-token <token>
heliox tool plaid -- item get           --access-token <token>
heliox tool plaid -- transactions sync  --access-token <token> [--cursor <c>] [--count 100]
heliox tool plaid -- transactions get   --access-token <token> --start-date 2026-01-01 --end-date 2026-02-01
heliox tool plaid -- item remove        --access-token <token>   # unlinks the Item
```

`transactions sync` is the preferred way to read transactions: pass no
`--cursor` for full history, then re-run with the returned `next_cursor` to get
only new changes.

If you have a `public_token` (from the user's Link flow), exchange it once for
an `access_token`:

```bash
heliox tool plaid -- item exchange-public-token --public-token <public_token>
```

## Sandbox: stand up a full test Item with no browser (sandbox env only)

```bash
# 1. mint a sandbox public_token for a test institution
heliox tool plaid -- sandbox public-token-create --institution-id ins_109508 --products transactions
# 2. exchange it for an access_token
heliox tool plaid -- item exchange-public-token --public-token <public_token>
# 3. read from the Item
heliox tool plaid -- transactions sync --access-token <access_token>
```

`sandbox public-token-create` **refuses when the connection is production**:
the endpoint does not exist there.

## Footguns

- **No `--access-token`?** Only the two `institutions` commands will work.
  Everything else needs a per-Item token you must obtain first.
- **Production Item reads** require an `access_token` minted by the user's own
  Link widget. Helio's connect flow does not host Link. Institution lookups are
  the only always-on production surface without a token.
- **Errors carry Plaid's own codes.** A failure surfaces `error_type` /
  `error_code` / `error_message` (e.g. `INVALID_ACCESS_TOKEN`,
  `ITEM_LOGIN_REQUIRED`, `PRODUCT_NOT_READY`). Read `error_code` and act on it
  (re-link the Item, wait for the product, fix the token) rather than retrying
  blindly. `INVALID_ACCESS_TOKEN` is an Item-token problem, not the connection.
- **`--json`** is accepted for uniformity; Plaid responses are already JSON and
  emitted verbatim.
