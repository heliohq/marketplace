# heliox tool billcom — BILL (Bill.com) AP/AR

Read `../SKILL.md` first for the connect + call model shared by every tool.

BILL (formerly Bill.com) is an accounts-payable (AP — money owed to vendors)
and accounts-receivable (AR — money owed by customers) platform. Use it to
answer questions about bills, vendors, invoices, customers, and payments, and
to draft new bills / vendors / invoices / customers.

Credentials are injected automatically — you never see the developer key,
password, or sync token. Each call signs in to BILL, runs the operation, and
returns provider-neutral JSON.

## Command surface

```bash
heliox tool billcom -- bill     list [--max N] [--page TOKEN] [--filter f:op:v] [--sort field:asc]
heliox tool billcom -- bill     get <id>
heliox tool billcom -- bill     create --data '{ ...bill fields... }'
heliox tool billcom -- vendor   list|get <id>|create --data '{...}'
heliox tool billcom -- invoice  list|get <id>|create --data '{...}'
heliox tool billcom -- customer list|get <id>|create --data '{...}'
heliox tool billcom -- payment  list|get <id>          # READ-ONLY (see below)
heliox tool billcom -- org      list                   # organizations for this login
heliox tool billcom -- whoami                          # session info: org id, user id, MFA status
```

`list` returns a provider-neutral envelope `{"items":[...],"next_page":"..."}`.
Pass the `next_page` value back as `--page` to fetch the next page. `get` and
`create` emit the provider's raw JSON.

## Money-movement carve-out — IMPORTANT

**Payments are read-only.** You can `payment list` and `payment get`, but there
is deliberately no `payment create`, no bank-account setup, and no bulk
money endpoints. Creating or scheduling a payment in BILL requires an elevated,
MFA-trusted session that this integration does not hold (and that is
intrinsically unavailable on the recommended sync-token credential). Do not
attempt to move money, add a funding source, or approve a payment through this
tool — it cannot, and you should tell the user to do that in the BILL web app.

Drafting a **bill** or **invoice** (a record of what is owed) is fine and
supported; that is not money movement.

## Failure modes

- If a call reports the credential was rejected, the stored BILL credential is
  wrong or expired — ask the user to reconnect (`heliox tool billcom auth`).
  BILL sessions expire after inactivity and are re-minted automatically on the
  next call, so a one-off expiry is not something you handle.
- A `4xx` error surfaces BILL's own code + message; a bad `--data` payload is a
  usage error (exit 2) — fix the JSON and retry.
