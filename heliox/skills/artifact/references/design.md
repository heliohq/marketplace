# Artifact design craft

Read this before authoring an HTML artifact by hand. The mechanics (verbs,
content contract, safety) are in `../SKILL.md`; this file is the **design
craft**. It follows Claude's artifact-design guidance, with the viewer-specific
differences collected below. Approach the work as the design lead at a small
studio known for versatility: give the artifact a visual identity pitched at
the treatment the task calls for, make subject-specific choices about palette,
typography, and layout, and avoid templated designs.

## Helio viewer specifics — read these first

A few facts about how the Helio viewer renders and stores an artifact shape the
guidance below; everything in *Fundamentals* and *When the request is editorial*
then applies:

- **The viewer has no theme toggle.** Only `@media (prefers-color-scheme: dark)`
  reaches the sandboxed iframe — there is no `data-theme` attribute to override.
  So the *Design both themes* rule below is replaced by: style both schemes
  through the media query, or deliberately commit to one visual world.
- **The document is stored verbatim.** Author a complete HTML file; its
  `<title>` **is** the artifact's title (no `<title>` and no `--title` fails the
  publish). Set the tab icon with the `--favicon` emoji flag, not a
  `<link rel="icon">`.
- **Prose → publish markdown, don't hand-author HTML.** A `.md` file renders
  server-side into a clean, theme-aware page that already satisfies the
  contract. Hand-built HTML for a plain document is wasted tokens.
- **Budget is 16 MiB**, but prefer SVG / HTML+CSS over raster `data:` URIs —
  inlined images are the usual size (and token) sink.

## Read the request first

Calibrate treatment, not whether to design. A doc deserves the same craft as a
landing page — what changes is the treatment that craft is delivered in.

Many requests call for a more utilitarian treatment: a plan, a memo, a
demo. Make it polished: include real typographic hierarchy, considered spacing,
and a proper palette, but avoid over-designing. Most pages do not need a flashy,
gigantic hero. Keep flourishes tasteful and limited.

Some requests call for an editorial treatment: a landing page, a game, an app,
or a tool the user will keep or share.

When unsure: a well-composed page is never the wrong answer; an over-designed
visual identity sometimes is. The fundamentals below apply to everything. The
editorial process runs only when the request calls for it.

## Fundamentals for every artifact

**Honor what's already there.** Look for an existing design system first:
project instructions, tokens or theme files, and existing component styles.
Apply it when it exists; the guidance below fills gaps and never overrides it.
Precedence is the user's words, then the project's existing system, then your
choices.

**Ground it in the subject.** If the subject is not already clear, pin one
concrete subject, its audience, and the page's single job. The subject's own
world — its materials, instruments, vernacular — is where distinctive choices
come from. Build with the real content throughout, never lorem.

**Pair typefaces.** Typography carries the page even when the page isn't about
typography. The sandbox CSP blocks font CDNs, so don't link a webfont URL and
risk a silent fallback. Instead inline the face as a `@font-face` `data:` URI
(or use the system stack). Keep running text near 65 characters wide; set a type
scale and stay on it; give headings `text-wrap: balance`, body text room to
breathe, and uppercase labels a touch of letter-spacing.

**Choose neutrals, don't default to them.** A pure mid-grey reads as
unconsidered; a grey with a slight hue bias toward the page's accent reads as
chosen. Pure white and near-black are fine grounds when they suit the subject —
the point is that the neutral was picked, not inherited.

**Design both themes — via the media query.** The page renders in the viewer's
theme through `@media (prefers-color-scheme: dark)`. Define the palette as
custom properties on `:root`, redefine only the tokens under the dark media
query, and style components through the tokens. Give the second theme the same
care as the first — don't naively invert; keep contrast legible and the accent
working on both grounds. A design that deliberately commits to one visual world
(a neon arcade screen, a letterpress invitation) may stay single-theme — make it
a choice, not an omission.

**Let layout do the spacing.** Lay out sibling groups with flex or grid and
`gap`, not per-element margins that silently collapse or double. Wide content —
tables, code, diagrams — gets `overflow-x: auto` on its own container so the
page body never scrolls sideways. Reach for `font-variant-numeric: tabular-nums`
wherever digits line up in columns.

**Avoid AI-generated design.** AI-generated design currently clusters around a
few looks: warm cream (#F4F1EA) with a serif display and terracotta accent;
near-black with a lone acid-green or vermilion pop; broadsheet hairline rules
with dense columns; a purple-to-blue gradient hero on white; Inter or Space
Grotesk as the "safe" face; emoji as section markers; everything centered;
`rounded-lg` everywhere; accent bar/rail on rounded cards. Where the user pins a
visual direction, follow it exactly — their words always win, including when
they ask for one of these looks. Where nothing is specified, don't spend that
freedom on one of these defaults.

**Build cleanly.** Be cognizant of overlapping elements, cascade collisions, and
silent font fallbacks; visual bugs hide in the gap between source and output.
Close every non-void element, double-quote attributes, give keyboard focus a
visible state, respect `prefers-reduced-motion`. For generative or decorative
graphics, reach for Canvas or WebGL rather than hand-authoring long SVG path
data.

**CSS rules.** When writing the CSS, watch selector specificities. It is easy to
generate classes that cancel each other out — a type-based selector like
`.section` fighting an element-based one like `.cta` over padding and margins
between sections. Structure the cascade so it doesn't silently undo spacing.

**Writing the copy.** Words are design material, not decoration. Write from the
user's side of the screen — name things by what people recognize, not how the
system is built (a person manages *notifications*, not *webhook config*). Active
voice; a control says exactly what happens ("Publish", then a toast that says
"Published"). Errors explain what went wrong and how to fix it — no apologies,
no vagueness. Specific beats clever.

**Structure is information.** Structural devices — numbering, eyebrows,
dividers, labels — should encode something true about the content, not decorate
it. Numbered markers (01 / 02 / 03) are only appropriate if the content actually
is a sequence — a real process or a typed timeline where order carries
information the reader needs. Question whether such choices actually make sense
before incorporating them.

**When it's a UI, not a document.** A dashboard or tool is scanned and operated,
not read top-to-bottom, so the craft shifts from typography to information
design. Surface the summary before the detail; encode state in form as well as
number — a pill, a chip, a severity stripe — so what needs attention reads at a
glance. Semantic color (good / warning / critical) is separate from the accent
hue and does not count as the accent. Give sparklines and charts the same care
as type: an area fill, a faint grid, an emphasized endpoint. What's interactive
should look interactive.

## Process

Before writing code, sketch a short design plan — a compact token system with
color, type, and layout:
- **Color**: describe the palette as 4–6 named hex values.
- **Type**: typefaces for 2+ roles — a characterful display face used with
  restraint, a complementary body face, and a utility face for captions or data
  if needed.
- **Layout**: the layout concept in one or two sentences.

Then build, following the plan and deriving every color and type decision from
it.

## When the request is editorial

The stance shifts: the client has already rejected proposals that felt
templated and is paying for a distinctive point of view. Make opinionated calls,
and take one real aesthetic risk where it serves the work.

Review the design plan against the subject before building. If any part reads
like the generic default you would produce for any similar page, revise it and
note what changed and why. Only after confirming the plan's uniqueness should
you write the code, following the revised plan exactly.

- **The hero is a thesis.** Open with the most characteristic thing in the
  subject's world — headline, image, live demo, or interactive moment.
- **Typography carries the personality of the page.** Pair the display and body
  faces deliberately, not the same families you would reach for on any other
  project, and set a clear type scale with intentional weights, widths, and
  spacing. Make the type treatment itself memorable, not a neutral delivery
  vehicle for the content.
- **Leverage motion deliberately.** Think about where and whether animation can
  serve the subject: a page-load sequence, a scroll-triggered reveal, hover
  micro-interactions, or ambient atmosphere. An orchestrated moment usually
  lands harder than scattered effects; choose what the direction calls for.
  Sometimes less is more, and extra animation contributes to the feeling that a
  design is AI-generated.
- **Match complexity to the vision.** Maximalist directions need elaborate
  execution; minimal directions need precision in spacing, type, and detail.
  Elegance is executing the chosen vision well.
- **Spend your boldness in one place; keep everything around it quiet.** If the
  accent fights the ground, shift it toward analogous or drop saturation rather
  than replacing it.
