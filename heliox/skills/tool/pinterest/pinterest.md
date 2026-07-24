# Pinterest (`heliox tool pinterest -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Pinterest is a
**flat provider**: everything after `--` is the Pinterest tool's own CLI,
speaking Pinterest API v5 with the connected account's OAuth token.

```bash
heliox tool pinterest [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `account`, `board`, `pin`. Run `-- <resource> --help` for the full
flag surface. One connection is one Pinterest account — the token is scoped to
the single account that authorized it, so there is no account selector inside
the commands.

## Read the account, organize boards, publish pins

```bash
heliox tool pinterest -- account get                 # whose account, follower/pin counts
heliox tool pinterest -- board list                  # boards on the account
heliox tool pinterest -- board get <board_id>
heliox tool pinterest -- board create --name "Recipes" [--description "..."] \
    [--privacy PUBLIC|PROTECTED|SECRET]
heliox tool pinterest -- board delete <board_id>
heliox tool pinterest -- board sections <board_id>          # list a board's sections
heliox tool pinterest -- board add-section <board_id> --name "Desserts"
heliox tool pinterest -- board pins <board_id>              # pins on a board
```

## Pins

```bash
heliox tool pinterest -- pin list
heliox tool pinterest -- pin get <pin_id>
heliox tool pinterest -- pin create --board-id <board_id> \
    --image-url https://example.com/photo.jpg \
    [--title "..."] [--description "..."] [--link https://...] [--section-id <id>]
heliox tool pinterest -- pin delete <pin_id>
```

**Every pin needs a `--board-id`.** Create-pin is **image-URL-first**: the image
comes from a publicly reachable URL (`--image-url`). Video pins are not
supported by this tool yet.

## Pagination is an explicit cursor

List endpoints (`board list`, `board pins`, `pin list`, `board sections`) accept
`--page-size N` and `--bookmark <cursor>`, and the JSON response carries a
`bookmark` for the next page. To page, read the returned `bookmark` and pass it
back as `--bookmark` — there is no automatic follow, so you decide how far to
walk.

```bash
heliox tool pinterest -- board list --page-size 25
# → response includes "bookmark": "..."; next page:
heliox tool pinterest -- board list --page-size 25 --bookmark "<that value>"
```

## Footguns

- **A `--image-url` that Pinterest can't fetch is a 400** ("valid image url").
  The URL must be publicly reachable and a real image.
- **401 means reconnect** — the tool surfaces a distinct "token expired or
  revoked — reconnect the Pinterest connection" message. Don't retry the same
  call; re-auth the connection.
- **429 means back off** — the tool surfaces the rate-limit message. Wait and
  retry later rather than hammering; repeated writes to one object in a short
  window also trip this.
- **`board delete` / `pin delete` are irreversible** and return a
  `{"deleted":true}` receipt on success.
- **Board privacy** is one of `PUBLIC`, `PROTECTED`, `SECRET`; omit `--privacy`
  to take Pinterest's default.
