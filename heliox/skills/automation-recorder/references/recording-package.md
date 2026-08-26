# Recording Package Format

## Fetch order

1. Download the zip attachment: `heliox blob get helio://attachment/<id> -o $REC/package.zip`.
2. Inspect BEFORE extracting — the archive is untrusted and this step is
   mandatory, exactly as SKILL.md's RECEIVED state specifies: `zipinfo`
   the archive and reject it on any symlink or non-regular entry (a
   single `img/` directory entry is the one allowed exception), more than
   100 entries, over 200 MB uncompressed, absolute or `..` paths, or
   entries outside the documented file set. Never extract first.
3. Extract: `unzip -o "$REC/package.zip" -d "$REC"`.
4. Read `$REC/manifest.json` first. It lists everything else.
5. Read `$REC/events.jsonl` (text; stdout is fine).
6. If `$REC/transcript.json` exists, read it (text; stdout is fine).
7. Read each image from `$REC/<path>` in manifest order (e.g. `$REC/img/0000.jpg`) to see what the screen looked like at each point.

## manifest.json

```json
{
  "version": 1,
  "id": "rec_abc123",
  "recordedAt": "2026-08-17T10:30:00Z",
  "durationMs": 120000,
  "audioStartT": 0,
  "display": { "width": 1470, "height": 956, "scale": 2 },
  "glowPresent": false,
  "secureInputMs": 0,
  "warnings": [],
  "images": [
    { "file": "img/0000.jpg", "t": 0, "kind": "keyframe", "rect": { "x": 0, "y": 0, "w": 1470, "h": 956 }, "display": { "w": 1470, "h": 956 }, "app": "Google Chrome", "title": "Inbox — Gmail" },
    { "file": "img/0001.jpg", "t": 3200, "kind": "crop", "rect": { "x": 100, "y": 200, "w": 400, "h": 300 }, "display": { "w": 1470, "h": 956 }, "app": "Google Chrome", "title": "Inbox — Gmail" }
  ],
  "events": "events.jsonl",
  "audio": null,
  "transcript": "transcript.json"
}
```

Fields: `t` is milliseconds from recording start. `kind` is `keyframe` (full window) or `crop` (changed region). `rect` is the image's region within its own frame's display; each image's `display` gives that display's logical size (a recording can cross monitors, so geometry is per-image — the top-level `display` is the primary display, informational only). Event coordinates are likewise local to the display the event occurred on; a drag's `from` AND `to` both use the START display's space (so the displacement vector is always true — a cross-display destination lands outside that display's bounds). `app` and `title` identify the foreground application. `audio` is always `null` in a delivered package — the ZIP carries the transcript, not the audio file. (The narration audio itself IS uploaded to Helio's servers for transcription and the server copy is retained; only the copy on the recording device is deleted after transcription succeeds. Do not tell users the audio never left their machine.) `audioStartT` is recording-clock ms when mic capture began (`null` when the recording has no audio); transcript timestamps can be aligned to the event timeline via this offset.

## events.jsonl

One JSON object per line, sorted by `t` ascending (guaranteed):
- `{ "t": 1200, "type": "click", "button": "left", "x": 450, "y": 320, "clicks": 1, "modifiers": ["shift"], "app": "Google Chrome", "title": "Inbox", "element": { "role": "AXLink", "title": "Daily logistics report", "value": null } }` — a click with the AX element identity. `button` is `"left"`, `"right"`, or `"other"`; `clicks` is the click count (1 = single, 2 = double); `element.value` is the AX value or `null`. `modifiers` (optional) lists held modifier keys from `["shift", "ctrl", "opt", "cmd"]` — note "opt", not "option".
- `{ "t": 1500, "type": "drag", "button": "left", "from": { "x": 100, "y": 200 }, "to": { "x": 300, "y": 400 }, "tEnd": 2000, "element": { "role": "AXImage", "title": "Photo", "value": null } }` — a drag (mousedown-to-mouseup displacement >6 px). `from`/`to` are start/end coordinates; `tEnd` is the mouseup timestamp. `element` is the accessibility FOCUSED element of the frontmost app at mousedown time — it may differ from the element under the cursor (AX hit-testing is not used).
- `{ "t": 2000, "type": "key", "shortcut": "cmd+c", "chars": null }` — a keyboard shortcut. `chars` is always `null` for shortcuts. `app` and `title` may appear as siblings.
- `{ "t": 2500, "type": "key", "shortcut": null, "chars": null, "text": "hello world", "count": 13, "tEnd": 3400 }` — typing. `text` approximates the field's FINAL content: consecutive chars within a 1 s gap are merged, and backspace/delete remove the previously typed character. Cursor-movement keys close the run (mid-string edits cannot be reconstructed), so a field edited with arrows appears as multiple `key` events. `count` is the number of keystrokes in the coalesced run (including backspace and other non-printable keys — it may exceed `text.length`). `tEnd` is the timestamp of the last keystroke (omitted when `count` is 1). When secure input is active, individual characters are replaced by the literal `[secure input]`; consecutive `[secure input]` chars collapse to a single occurrence in `text`.
- `{ "t": 5000, "type": "scroll", "x": 450, "y": 500, "dx": 0, "dy": -120, "tEnd": 5250, "app": "Google Chrome", "title": "Inbox" }` — scroll. When multiple scroll ticks occur within a 300 ms burst they are coalesced: `dx`/`dy` are the sums, `tEnd` is the last tick's timestamp (omitted for a single tick). `dx`/`dy` are macOS `scrollingDeltaX`/`scrollingDeltaY` in the user's configured scroll direction (positive `dy` = content scrolls toward the top; depends on the natural-scrolling system preference).
- `{ "t": 8000, "type": "app_switch", "app": "Google Sheets", "title": "Shipments" }` — app switch

The `element` field on clicks and drags is the accessibility FOCUSED element of the frontmost application at mousedown time. It identifies what the user targeted, though it may not correspond to the exact element under the cursor (AX hit-testing is not used). Use it to understand WHAT the user targeted, not just WHERE they clicked or dragged.

Typing events carry the typed text in the `text` field. When the user typed in a secure input field (e.g. a password manager), the text reads `[secure input]` — treat that as an opaque marker, not as literal content. Review the text alongside screenshots to understand what was entered and where.

## transcript.json

```json
{
  "text": "First I open Gmail and find the logistics email from ACME...",
  "words": [
    { "w": "First", "start": 0.1, "end": 0.3 },
    { "w": "I", "start": 0.32, "end": 0.4 },
    { "w": "open", "start": 0.42, "end": 0.7 }
  ]
}
```

The transcript is the narration: the user explaining what they are doing and WHY. Bind each utterance to the nearest preceding action by timestamp. Late corrections happen: "that one doesn't count" or "ignore that" refers back to a preceding action.

## Message

The hand-off message is a short human sentence in the sender's language — a summary of the recording (duration, action count, narration presence) and a request to automate. There is no machine-readable header; recognition is by the zip attachment: a single `automation-rec-*.zip` identifies the message as a recording package. The manifest inside the zip is the authoritative metadata source; its `version` field is the format version; all machine metadata (timing, image list, display geometry) lives in the manifest.

## Correlating sources

1. Images show WHAT the screen looked like.
2. Events show WHAT the user did (clicks, shortcuts, scrolls, app switches).
3. The transcript shows WHY they did it and what matters.

When sources disagree, the transcript (user's stated intent) wins over inferred intent from actions.
