# Postmark (`heliox tool postmark`)

Postmark is a transactional + broadcast email delivery service. Use it to send
email on the user's behalf, look up what was sent or received, and diagnose
deliverability. Read the top-level [../SKILL.md](../SKILL.md) first for the
connect/list/use model — this page is the command surface.

The connection is scoped to **one Postmark server** (the account key is that
server's link). A user with multiple servers connects each Server API Token
separately; pass `--account <key>` when more than one is connected.

Everything after `--` goes to the tool. Add `--json` on any leaf for structured
output. Run `heliox tool postmark -- <group> <cmd> --help` for the full flag list.

## Send

```bash
# Plain transactional send. --from must be a CONFIRMED Sender Signature.
heliox tool postmark -- email send \
  --from you@yourdomain.com --to person@example.com \
  --subject "Your report" --text "Here it is." [--html "<p>Here it is.</p>"]

# Optional: --cc --bcc --reply-to --tag --stream --track-opens \
#           --track-links None|HtmlAndText|HtmlOnly|TextOnly \
#           --metadata '{"order":"123"}' --header "X-Thing: value" --attachment ./file.pdf

# Template send: exactly one of --template-id or --template-alias, plus --model.
heliox tool postmark -- email send-template \
  --from you@yourdomain.com --to person@example.com \
  --template-alias welcome --model '{"name":"Ada"}'
```

A successful send returns the provider JSON with a `MessageID` and `ErrorCode`
`0`. A validation failure (unconfirmed sender, inactive recipient, malformed
request) is a non-zero exit with the provider's `Message` on stderr.

## Look up activity

```bash
heliox tool postmark -- message list-outbound [--count 100 --offset 0 \
  --recipient a@b.com --from-email you@d.com --tag welcome --subject Hi \
  --status sent --stream outbound]
heliox tool postmark -- message get-outbound <message-id>   # detail + delivery events
heliox tool postmark -- message list-inbound  [--count --offset --recipient \
  --from-email --subject --status]
heliox tool postmark -- message get-inbound   <message-id>
```

## Templates & diagnostics

```bash
heliox tool postmark -- template list [--count --offset]
heliox tool postmark -- template get  <id-or-alias>
heliox tool postmark -- stats delivery                      # delivery / bounce summary
heliox tool postmark -- bounce list [--count --offset --type HardBounce \
  --email a@b.com --tag welcome --message-id <id> --inactive]
heliox tool postmark -- bounce get      <bounce-id>
heliox tool postmark -- bounce activate <bounce-id>         # reactivate a deactivated recipient
```

## Server

```bash
heliox tool postmark -- server get   # server metadata (name, link, streams) — API tokens are redacted
```

## Safety

- Sending email is an outward-facing action — follow the sensitive-operation
  rule in `../SKILL.md`. Confirm the recipient, subject, and body with
  the user before sending anything non-trivial, and prefer the sandbox test
  token for dry runs when the user offers one.
- `bounce activate` re-enables delivery to an address Postmark deactivated for
  hard-bouncing or complaining; only do it when the user confirms the address is
  valid, or you risk sender-reputation damage.
- Never echo the Server API Token; `server get` deliberately redacts it.
