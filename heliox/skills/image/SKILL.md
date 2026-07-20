---
name: image
description: "Use `heliox tool image ...` to generate images from text prompts or edit existing images with Helio-managed models (GPT-Image, Gemini). Trigger whenever the task needs a picture created OR modified — an illustration, logo, icon, poster, banner, avatar, wallpaper, diagram concept, any 画图 / 生成图片 / 文生图 request, or an edit like 换背景 / 改颜色 / restyle / remove-object on an image the user provided — even when the user never says 'image' ('make me a logo', '把背景换成白色'). The result is a durable helio://attachment/<id> URI; this is the only image surface available to AI runtimes."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox tool image --help"
---

# Heliox Image Generation

Start by reading `../shared/SKILL.md`.

Generation is synchronous — `create` blocks until the image is ready (typically 5–90 s, up to ~3 min). Every image costs the org real money, so the recovery rules below matter: never regenerate what already succeeded.

## Pick a model, then create

The offered models are deployment config — they change without this skill changing, so always list instead of guessing:

```bash
heliox tool image models --json
heliox tool image create "a watercolor red panda reading a book" --model gemini-3.1-flash-image --json
heliox tool image create "<prompt>" --model gemini-3-pro-image --size 2048x2048 --n 2 --json
```

Choosing: a fast/cheap generalist (e.g. `gemini-3.1-flash-image`) covers everyday images; reach for a premium model (e.g. `gemini-3-pro-image`, `gpt-image-2`) when quality, in-image text rendering, or high resolution matters. `--size` is optional (model default applies); `--n` generates up to 4 variants in one call. Write prompts in English with subject, style, and composition.

`create` prints one `helio://attachment/<id>` URI per image (`--json`: `{model, images:[{uri, id, mime_type, size_bytes}]}`).

## Edit an existing image

`edit` takes the image(s) to modify plus a prompt describing the change; the result is a NEW attachment — the input is never modified in place:

```bash
heliox tool image edit "replace the background with pure white, keep the product untouched" \
  --image helio://attachment/<id> --model gemini-3.1-flash-image --json
heliox tool image edit "<change>" --image ./photo.png --mask ./mask.png --model gpt-image-2 --json
```

`--image` accepts a local file or a `helio://attachment/<id>` URI (an attachment the user sent works directly — no download step needed) and repeats for multi-image reference/fusion. `--mask` is model-dependent: GPT-Image honors a mask PNG whose **fully transparent (alpha=0) pixels mark the editable region** — everything opaque stays pixel-identical (the OpenAI edit contract; a black/white mask will NOT work, erase the region to transparency instead). Gemini models edit semantically from the prompt alone, so describe precisely what must stay unchanged. For pixel-exact "change only X" requests, prefer a mask-capable model.

## Share the result — pick the path by destination

The URI and the bytes travel differently; using the wrong one produces a message with no visible image:

- **Chat message / task attachment** — attachments ride the upload flag, not the body text, so write a local file and attach it:

  ```bash
  heliox tool image create "<prompt>" --model gemini-3.1-flash-image -o ./img.png --json
  heliox message send '#design' "logo draft" -a ./img.png --seen "$LATEST_SEQ" --json
  ```

- **Document or task-comment body** — paste the `helio://attachment/<id>` URI inline; the frontend renders it (local file paths in a document render nothing).

- **Local bytes later** — `heliox blob get helio://attachment/<id> -o out.png` re-fetches any previously generated image.

## Boundaries

- Video generation is not available.
- Edits are generative, not pixel surgery: without a mask the model may subtly alter untouched regions. Set expectations with the user when exact preservation matters, and mention the result is a new image.
- Flags beyond the ones shown here: confirm with `heliox tool image --help` before use.

## Failure recovery

- A billing/gate error means the org can't spend on generation right now — relay the error verbatim; retrying won't change it.
- A WARNING that upload failed with `image saved to <path>` means **generation already succeeded and was paid for**: run `heliox blob put <path>` to persist it. Do not run `create` again.
- A timeout or vendor error from `create` produced nothing durable — retrying once is fine, but tell the user if it fails twice.
