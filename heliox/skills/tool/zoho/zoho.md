# Zoho tools (`heliox tool zoho ...`)

Read [../SKILL.md](../SKILL.md) first for the general connect/use model. Zoho
products are connected **per app** — each app is its own connection with its
own consent and its own OAuth scopes. Per-app details live in this directory;
run `heliox tool zoho --help` for the current app list.

## Auth (per app)

```bash
heliox tool zoho auth books --json    # mint the authorize link, relay to the user
heliox tool zoho auth crm --json
```

Connecting one app grants nothing for the others — Books and CRM are separate
scope families / client registrations, so each needs its own auth link and
user consent.

## Accounts

One connection acts as the user's own Zoho account for that app. The user may
connect several accounts of the same app; disambiguate calls with
`--account <key>` (keys come from `heliox tool list` or the 409 candidate
list). `--account` goes **before** the `--` separator:

```bash
heliox tool zoho books --account acme@corp.com -- org list --json
```

## Apps

| App | Reference | What it does |
| --- | --- | --- |
| books | [books.md](./books.md) | Zoho Books: invoices, contacts, estimates, items, bills, payments, expenses (org-scoped) |
| crm | [crm.md](./crm.md) | Zoho CRM: records, COQL queries, notes, module/field metadata |
