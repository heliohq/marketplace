#!/bin/bash
# Create the finished wiki page — ONE tool call, no shell-sensitive text on
# the command line (the safe-shell gate blocks `--content "$(...)"` shapes).
#
# Usage: bash <skill-dir>/scripts/create-doc.sh "<title>" <content-file> "@<owner handle>"
#
# The @handle scopes the document to your DM with your owner. That scope is
# what keeps the page private: DM members — the two of you — can read and
# edit it, other org members cannot. Never create the wiki without it.
# Prints the `document create --json` result; read the id from it.
set -eu
TITLE="${1:?title required}"
FILE="${2:?content file required}"
DM="${3:?owner DM required, e.g. @travis}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 - "$TITLE" "$FILE" "$DM" "$TMP/args.json" <<'PY'
import json, sys
content = open(sys.argv[2], encoding="utf-8").read()
json.dump(["document", "create", sys.argv[1], "--content", content,
           "--channel", sys.argv[3], "--json"],
          open(sys.argv[4], "w", encoding="utf-8"), ensure_ascii=False)
PY

cd "$TMP" && heliox --args-file args.json
