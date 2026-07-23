# SerpApi (`heliox tool serpapi -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. SerpApi is a
**flat provider** (not grouped like `google`): everything after `--` is the
serpapi tool's own CLI. The credential is a private API key the user pastes
(no OAuth); the CLI injects it per call.

```bash
heliox tool serpapi [--account <key>] -- <command> [flags...]
```

SerpApi is a **live search-engine-results API**: one search endpoint fronting
~70 pluggable engines (Google, Google News, Maps, Shopping, Jobs, Scholar,
Trends, YouTube, Bing, DuckDuckGo, …). You get structured JSON — organic
results, knowledge graph, answer boxes, local packs — instead of scraping HTML.

## The mental model (read this first)

Search is **one generic command** along two axes:

- `--engine` picks the vertical (default `google`). It is passed through
  **unvalidated** — any engine SerpApi supports works; an unknown one fails
  with SerpApi's own error.
- Params are the knobs. The cross-engine common ones are first-class flags
  (`-q`, `--location`, `--gl`, `--hl`, `--num`, …); every engine-specific param
  (`tbm`, `data_id`, `ludocid`, …) rides the repeatable `--param key=value`
  escape hatch.

So you never need a per-engine subcommand: pick the engine, pass its params.

## Core commands

### Search

```bash
# Google organic (engine defaults to google)
heliox tool serpapi -- search -q "best espresso machines 2026" --num 10

# Localized rank check: a keyword from a specific place, in a locale
heliox tool serpapi -- search -q "plumber" \
  --location "Austin, Texas, United States" --gl us --hl en --num 20

# A different engine + an engine-specific param via the escape hatch
heliox tool serpapi -- search -q "AI news" --engine google_news --param tbm=nws
heliox tool serpapi -- search --engine google_maps --param data_id=0x0:0xabc
heliox tool serpapi -- search -q "react hooks" --engine google_scholar --num 5
```

Common flags: `-q` (query), `--engine`, `--location` (a **canonical** name —
resolve it first, see below), `--gl` (country), `--hl` (language),
`--google-domain`, `--device desktop|tablet|mobile`, `--num`, `--start`
(pagination offset), `--no-cache` (force a fresh search), and repeatable
`--param key=value`. A `--param` overrides a first-class flag of the same name;
it can never override the injected `api_key`.

### Resolve a location before searching

`--location` must be a SerpApi **canonical** name, not free text. The Locations
API is free and needs no credential:

```bash
heliox tool serpapi -- locations --q austin --limit 5
# → use the returned canonical_name (e.g. "Austin,Texas,United States") as --location
```

### Re-read a past search for free (Search Archive)

Every search response carries `search_metadata.id`. Re-fetch that search within
31 days without spending quota:

```bash
heliox tool serpapi -- archive get <search_id>
```

Use this to re-read results you already paid for instead of repeating the
search.

### Check remaining quota

```bash
heliox tool serpapi -- account
```

Returns the plan, `total_searches_left`, and the hourly rate limit — free to
call. The private key is **redacted** from this output. Check it before firing a
large batch of searches.

## Footguns

- **`--location` needs a canonical name.** Passing a raw city string often
  returns nothing useful — run `locations` first and copy `canonical_name`.
- **Searches cost quota; archive and locations and account do not.** Prefer
  `archive get <id>` to re-read, and `account` to budget before a batch.
- **Unknown engine / bad params fail with SerpApi's own error** (exit 1). Read
  the `error` field — it usually names the missing or wrong parameter.
- **Output is engine-shaped.** The top-level keys differ per engine
  (`organic_results`, `news_results`, `local_results`, `shopping_results`, …).
  Inspect `search_metadata` and the result arrays for the engine you chose.
- Get or rotate the key at https://serpapi.com/manage-api-key. If a key is
  rejected mid-session, the connection is marked stale — ask the user to
  reconnect.
