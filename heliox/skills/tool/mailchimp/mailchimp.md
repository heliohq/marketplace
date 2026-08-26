# Mailchimp (`heliox tool mailchimp -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Mailchimp is
a **flat provider**: everything after `--` is the Mailchimp tool's own CLI,
speaking Mailchimp Marketing API v3.0 with the connected account's token.

```bash
heliox tool mailchimp [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `ping`, `audience`, `member`, `segment`, `campaign`, `report`,
`template`, `search`. Run `-- <resource> --help` for the full flag surface.

Output is the provider's JSON on stdout (verbatim). Action verbs that the API
answers with `204 No Content` (send/test/schedule/unschedule/archive/delete/
tag) instead print a small receipt: `{"ok":true,"action":"send","id":"..."}`.
Exit codes: `0` success, `1` API/runtime error (Mailchimp problem-detail on
stderr; `401` also hints to reconnect), `2` usage error. Add `--json` to get
errors as `{"error":{"message":…,"kind":"usage|api","status":…}}`.

## The mental model (audiences, members, campaigns)

- An **audience** (a.k.a. list) holds **members** (subscribers). Almost every
  member/segment/campaign call needs a `<list_id>`. Get it from
  `audience list`.
- A **member** is addressed by the MD5 of its lowercase email. The CLI does the
  hashing for you: pass `--email you@example.com`. `--hash <md5>` is a
  passthrough alternative when you already have it.
- A **campaign** is created empty, then given content, then sent/scheduled.
  Reporting lives under `report`, keyed by the campaign id.

## Audiences and members

```bash
heliox tool mailchimp -- audience list                       # find list ids
heliox tool mailchimp -- audience get <list_id>
heliox tool mailchimp -- member list <list_id> [--status subscribed]
heliox tool mailchimp -- member get <list_id> --email you@example.com
```

Add or update a subscriber (upsert, safe to re-run):

```bash
heliox tool mailchimp -- member upsert <list_id> --email you@example.com \
  --status subscribed --merge '{"FNAME":"Ada","LNAME":"Lovelace"}' --tags vip,beta
```

`--status-if-new` (default `subscribed`) is the status applied only when the
member is newly created; `--status` sets the status of an existing member.
`--merge` is a JSON object of merge fields.

Tag / untag and archive:

```bash
heliox tool mailchimp -- member tag <list_id> --email you@example.com --add vip --remove trial
heliox tool mailchimp -- member archive <list_id> --email you@example.com
```

Segments:

```bash
heliox tool mailchimp -- segment list <list_id>
heliox tool mailchimp -- segment members <list_id> <segment_id>
```

## Campaigns (create → content → send)

```bash
heliox tool mailchimp -- campaign create --list <list_id> \
  --subject "Launch day" --from-name "Ada" --reply-to ada@example.com [--segment <seg_id>] [--title "internal name"]
# returns the new campaign id

heliox tool mailchimp -- campaign set-content <id> --html-file ./email.html   # or --html "..." or --template <template_id>
heliox tool mailchimp -- campaign test <id> --emails a@x.com,b@y.com          # send a test first
heliox tool mailchimp -- campaign send <id>
heliox tool mailchimp -- campaign schedule <id> --at 2026-08-01T15:00:00Z     # RFC3339; unschedule with `campaign unschedule <id>`
heliox tool mailchimp -- campaign list [--status sent]
heliox tool mailchimp -- campaign get <id>
heliox tool mailchimp -- campaign delete <id>
```

## Reports, templates, search

```bash
heliox tool mailchimp -- report list                 # per-campaign performance
heliox tool mailchimp -- report get <campaign_id>
heliox tool mailchimp -- template list
heliox tool mailchimp -- search members --query "ada@"
heliox tool mailchimp -- search campaigns --query "launch"
```

## Footguns

- **Always resolve `<list_id>` first** with `audience list`. Member, segment,
  and campaign-create calls all need it, and it is not the audience *name*.
- **Send is irreversible.** Prefer `campaign test --emails ...` before
  `campaign send`. `schedule` can be undone with `unschedule`; a real send
  cannot.
- **Content before send.** A campaign created with `campaign create` has no
  body until `campaign set-content`; sending an empty campaign fails.
- **Schedule times are RFC3339 and must be in the future**; Mailchimp also
  rounds to :00/:15/:30/:45 minutes. Pass a quarter-hour boundary.
- **Pagination**: list verbs take `--count` / `--offset`; add `--fields` (e.g.
  `--fields lists.id,lists.name`) to trim large responses to what you need.
