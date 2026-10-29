# C4 visual system — how the model maps to HTML/CSS/SVG

This is the visual language for the architecture map. The working skeleton is `assets/template.html` — copy it and fill **only its `MODEL` object**; the engine renders everything from it. This file explains the *rules* so the diagram stays consistent and on the Stage house palette.

It is the **C4 Container level** (Context → **Container** → Component → Code). You draw containers (deployable/runnable things: a web app, an API, a worker, a DB) and show their components (modules/responsibilities) nested inside, with labeled edges between them. Clicking drills one level deeper (Model D, below) — the Component level — without leaving the page.

## The MODEL (the only thing you edit)
The template is **data-driven**: a single `MODEL = { repo, brand, date, legend, layout, nodes, edges }` object drives the render — the topbar (document title, wordmark, date) is filled from `repo`/`brand`/`date` at runtime, so there are no `{{placeholders}}` to hand-edit (`date:''` auto-fills today). Schema (full version in the template's top comment):
- `legend` — `[['layer','Name'], …]`, only the layers you use.
- `layout` — array of rows of node ids, laid out top→down (clients/edge → server → data/external). Center a much-called hub (a DB) in its row.
- `nodes` — `{ id: {label, tech, layer, kind, summary, entry[], net?, talksTo?[], components?[]} }`. `kind:'container'` shows component pills; `kind:'node'` is a bare box. `entry[0]` also renders **in the card header** (small mono under the tech line) — the file that *is* this container.
- `components` — `[{id, label, one, summary, whatHowWhy?, ports?, flow?, anatomy?, files[], kids?[{label,txt}], talksTo?[{to,via}], net?}]`.
- `edges` — `[{from, to, label, net?}]` where `from`/`to` are **node ids** (container-level).

The detail fields (`summary`/`files`/`kids`/`talksTo`/`entry`/`net`) come from the Stage 3.5 enrichment pass and power the drill-down + networking toggle. Never hand-write boxes or edit the engine.

### The richer component fields (all optional — use where they carry real signal)
Every one of these is additive: a component with only `summary`/`files`/`kids`/`talksTo` still renders exactly as before. Add the richer fields to the components that matter (the ones with real logic / the files a reader will study), not to every box.

**`whatHowWhy: {what, how, why}`** — three short labeled lines that *lead* the drill-down: what it is, how it works, why it's necessary. When present it replaces the flat `summary` as the lead content (keep `summary` anyway as the fallback).

**`ports: {in:[{label, from}], out:[{label, to}]}`** — Blender-node style I/O. Rendered as small labeled dots on the **left edge** (inputs: callers, injected/imported services, data read) and the **right edge** (outputs: data written, network calls, return values) of the expanded component's detail row. Label each port with the **payload and its purpose** — `'SOAP text → billing codes'`, not `'HTTP'`. `from`/`to` is the other end (a component, a file, a service). A `talksTo` that is really request **and** response gets a port on *both* sides.

**`flow: [step]`** — the ordered chain of functions the data passes through inside this component; opens the **Data flow** tab of the drawer (slides in from the left, vertical, scrollable — the lane is capped with an IN row at the top and an OUT row at the bottom, derived from `ports` when present).
```js
step = {label, fn?, file?, external?, in, does, out, branch?, children?:[step]}
```
- `fn` — the function/symbol that runs (`extract_codes()`).
- `file` + `external:true` — the step's main function is **imported from another file**: the node renders visually differentiated (dashed, accent-tinted) and shows `imported from <path>`, so the reader knows where to zoom in next.
- `children` — **nested sub-cards**: the helper functions this step calls, rendered smaller inside the parent, each with its own in/does/out, stacked vertically with arrows in call order.
- `branch` — a lane name. **Consecutive** steps carrying `branch` form one parallel group: each distinct value becomes a side-by-side lane, and the first following step without `branch` is where the lanes re-merge. Omit it for a straight single lane (the normal case) — only use it for a genuine branch.
- `out` of one step should read as the `in` of the next: a reader must be able to follow one piece of data from entry to exit.

**`anatomy: [{section, lines, runsWhen, summary}]`** — the **Code anatomy** tab of the same drawer: the file as it sits on disk, top to bottom, for big files worth studying. Usual sections: `Imports` · `Module-level setup` (runs once at import) · `Definitions` (registered but dormant) · `Entry points` (run per request/event). `lines` is the real line range (`'190–232'`), `runsWhen` is when that section executes. Skip it for small files.

**File paths** render with the shared directory prefix dim and the last one or two segments bold, and they **wrap** — a long path never clips or overflows a card.

## Non-negotiables (inherited from the Stage house style)
- **Single self-contained HTML file.** Inline all CSS and JS. Inline images as base64 / inline SVG. The ONLY allowed external reference is the one Google Fonts link for Inter (or inline the woff2 to go fully offline). Never link a local `assets/` path that can break.
- **CSS variables only for theming.** Rebrand by changing `--accent` (and optionally `--accent-dark` / `--accent-soft`). Do not hand-color elements.
- **Inter** font (400–800), system fallback. Same `--ink` / `--muted` / `--surface` / `--divider` neutrals as the deck template.
- This is **one canvas**, not slides: no 1536×864 scene system. Instead the diagram is **responsive / fit-to-width / zoomable** (the template's `fit()` + zoom buttons). Keep it readable at "Fit".

## Accent (override beats auto-pick)
Same rule as presentation-maker: if the user names a color or "neutral", that wins. Otherwise a brand hex found in the repo (Tailwind/CSS config, logo) → `--accent`; else keep the neutral slate-blue `#2563EB`. Dark theme: `<html data-theme="dark">` for developer/technical-toned subjects or on request.

## Layer tints — the one place we use more than one hue
A C4 diagram needs tiers to read apart, so each **layer** gets its own muted tint. This is a *controlled* exception to "one hue", not a license for rainbow slop: the tints are **equal-lightness, desaturated**, and fixed. Defined as variables in the template:

| Layer | line var | soft-fill var | hue |
|---|---|---|---|
| frontend | `--l-frontend` | `--l-frontend-soft` | blue |
| backend | `--l-backend` | `--l-backend-soft` | violet |
| data | `--l-data` | `--l-data-soft` | teal |
| external | `--l-external` | `--l-external-soft` | amber |
| mcp | `--l-mcp` | `--l-mcp-soft` | rose |
| infra | `--l-infra` | `--l-infra-soft` | neutral gray |

The engine tints each box from its `layer` (it sets `--layer`/`--layer-soft` for you). The box border, header tech-label, tag, component left-borders, and hover state all derive from `--layer`. **Infra/edge** (nginx, a reverse proxy, a sidecar, an actor like a browser) uses the neutral gray so it doesn't compete with the real tiers. **Only list the layers you use** in `MODEL.legend`.

## The box vocabulary
- **Container** (`kind:'container'`) — a tier/app box: a header (title + tech + tag + caret) over a wrap of component **pills**. Use for anything with internal parts (frontend, backend, a worker, an MCP server, a DB you want to show tables in).
- **Component** (a `components[]` entry → a pill) — a labeled chip inside a container. Group files by directory/responsibility — don't make one pill per file. Its detail fields (summary/files/kids/talksTo) power the drill-down.
- **Node** (`kind:'node'`) — a bare box with a title + sublabel, no pills. Use for a cache/queue, a single external API, or an **actor** (a browser, an MCP client). Clicking a node reveals its overview inline.

## Layout by tier
```
┌─ FRONTEND ─┐   ┌─ BACKEND ─┐   ┌─ EXTERNAL ─┐
│ [pills...] │──▶│ [pills...] │──▶│ [pills...] │
└────────────┘   └─────┬──────┘   └────────────┘
                       ▼   ▼
            [AI]  [Email]  [Postgres]  [Sources]   ← data + external, hub centered
```
- `MODEL.layout` is a column of flex rows. First row = clients/edge; then the server tier; then data + external. Rows wrap on narrow viewports.
- Keep the **reading direction** top→down: requests flow from clients into the server tier, then down into data and out to external/MCP. **Center a hub everything calls** (a DB) in its row so callers reach it without crossing a whole tier — this was the single biggest readability win on the real maps.
- Boxes are laid out by **flex only**; only the SVG edge layer is absolutely positioned.

## The SVG arrow technique (the core trick)
Arrows are **not** drawn in the HTML — they're computed so they stay attached when the layout reflows (resize, zoom, **and when a card expands via the drill-down**). The engine does this; don't touch it:
1. An `<svg id="edges">` and an HTML `#edge-labels` layer sit **inside `#diagram`** (sharing its un-zoomed coordinate space), absolutely positioned, `pointer-events:none`.
2. `MODEL.edges` is the only data the renderer reads: `{from, to, label, net?}` where `from`/`to` are **node ids**.
3. `drawEdges()` runs on load, `resize`, zoom, pan, and every inline expand/collapse. For each edge it reads both endpoints' rects via **`getBoundingClientRect()`** (converted to `#diagram` coords / current `zoom` in `relRect()`), picks exit/entry points (`anchors()`: different rows → exit top/bottom and route vertically; same row → exit sides and route horizontally), draws an **orthogonal `path` whose cross-travel runs in the empty gutter between rows/columns** (`bezier()` — a 3-segment Manhattan path, so a line never cuts through a box), with `marker-end`, and places an `.edge-label` pill at the midpoint.
4. **Never hard-code arrow coordinates.** Add/remove an arrow by editing `MODEL.edges` only.

Edge label = the **protocol** (`HTTP`, `HTTPS`, `REST`, `SQL`, `query`, `gRPC`, `cache`, `import`, `calls`, `MCP`, `WebSocket`, `IMAP/SMTP`). Keep labels short; the pill has a background so it stays legible in a narrow gap — but prefer enough gap that labels sit in open space.

## Model D — the drill-down (in-card inline reveal)
The map's signature interaction. **No side panel** — clicking reveals detail *inside the card itself*; the card grows, neighbours reflow, arrows recompute.
- **Click a pill** → that component's detail appends inline, in this order: **what / how / why** (or the flat `summary`) → **ports** (labeled dots on the row's left and right edges) → the **Data flow / Code anatomy** buttons → **files** (each with a copy button) → **kids** (the flat one-liner list) → **talks-to** chips → networking facts. The pill highlights; an **×** (or re-click) collapses it. Multiple can be open at once (they stack).
- **Click a card title or a node** → the tier/node **overview** (summary · entry point · talks-to) reveals the same way. The container title is styled as a **clickable chip** (same visual language as the pills) so it's obvious it opens the overview.
- **The drawer** (a real overlay, not an inline row) slides in **from the left** for `flow` / `anatomy`: full-height, vertically scrollable, dismissed by the ×, the scrim, or `Esc`. Its two tabs appear only when the component defines the matching field. It sits above the canvas and doesn't disturb the layout, so arrows never move when it opens.
- It's **2 levels only** (card → component, with flat children); children don't drill further.
- Driven entirely by the Stage 3.5 detail fields — `toggleInline()` builds the row and calls `drawEdges()` so the arrows follow the grown card.

## Networking toggle
A topbar switch (`#net`, **default off**) that surfaces the network layer at a glance:
- **On** → each edge label swaps to its `net` string (port/protocol, e.g. `127.0.0.1:8000`), styled in the accent; and each box shows its `net` address line (domain · listen port · upstream · TLS).
- Source `net` facts from `nginx/*.conf`, `docker-compose.yml`, systemd units, `wrangler.toml`. **Flag env-only facts** (a public VPS IP not in the repo) rather than invent them; loopback addresses from the config are fine to show.

## Files & copy
File paths render as monospace chips with a small **copy** button (copies the full path; a toast confirms). No editor deep-links — copy is universal and machine-independent.

## Navigate like a map
Hold **left-click + drag to pan**; **scroll-wheel to zoom** (anchored on the cursor); plus **Fit / ±** buttons. Default to "Fit" on load. `#canvas{cursor:grab}` + a `mousedown→mousemove→mouseup` pan driving `scrollLeft/scrollTop`, and a non-passive `wheel` handler that re-anchors scroll after `applyZoom()`. `user-select:none` on `#diagram` so dragging doesn't select text.

## Self-contained checklist (part of the Done bar)
- [ ] All CSS in one `<style>`, all JS in one `<script>`. Images base64 / inline SVG.
- [ ] At most one external link (Google Fonts). Nothing else loaded at view time.
- [ ] You edited **only `MODEL`** — the engine is untouched; example nodes/edges are deleted.
- [ ] `MODEL.legend` lists exactly the layers shown.
- [ ] Drill-down works (pill → what/how/why · ports · files/kids/talks-to), the network toggle lights up, copy buttons copy.
- [ ] Where you added `flow`/`anatomy`, the drawer opens from the left, scrolls to the end with nothing clipped, and both themes (`data-theme="dark"`) still read cleanly.
