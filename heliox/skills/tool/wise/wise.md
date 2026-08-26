# Wise (`heliox tool wise`)

Wise is a **read / monitor + non-committal pricing** tool: check balances, watch
transfers land, read account activity, and price a hypothetical transfer. It
**cannot move money**: funding transfers and reading balance *statements* are
PSD2/SCA-gated and deliberately out of scope. If a task needs an actual payout,
that is a human action in the Wise app, not this tool.

Connect once (`heliox tool wise auth --json`); the user pastes a personal API
token. Everything after `--` goes to the tool.

## Resolve the profile first

Every balance / transfer-by-profile / activity / recipient call is scoped to a
Wise **profile id**. A token may see several profiles (personal + business), so
start by listing them and pick the right `--profile`:

```bash
heliox tool wise -- profile list                 # -> profiles with numeric ids + type (PERSONAL/BUSINESS)
```

`quote create` and `currency list` are **not** profile-scoped and take no
`--profile`.

## Verbs

```bash
heliox tool wise -- balance list --profile <id>            # multi-currency balances (STANDARD + SAVINGS/Jars by default; --types to narrow)
heliox tool wise -- balance get <balanceId> --profile <id>
heliox tool wise -- transfer list --profile <id> [--status <s>] [--created-date-start <iso>] [--created-date-end <iso>]
heliox tool wise -- transfer get <transferId>
heliox tool wise -- activity list --profile <id> [--size 1-100] [--next-cursor <cursor>]   # cursor-paginated feed
heliox tool wise -- recipient list --profile <id> [--currency EUR]
heliox tool wise -- quote create --source-currency USD --target-currency EUR --source-amount 5000   # or --target-amount
heliox tool wise -- currency list
```

Notes:
- `quote create` gives the mid-market rate + fee estimate and moves nothing;
  provide exactly one of `--source-amount` / `--target-amount`. Use it for
  "what would X→Y cost right now?" There is no separate rate command.
- `activity list` returns `{cursor, activities}`; pass the returned cursor back
  as `--next-cursor` to page.
- Amounts are exact decimals; read them as returned, do not round.
- `--base-url` selects a sandbox host (default is production
  `https://api.wise.com`); you normally never set it.
