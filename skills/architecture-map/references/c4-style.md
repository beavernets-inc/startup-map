# C4 visual system — how the model maps to HTML/CSS/SVG

This is the visual language for the architecture map. The working skeleton is `assets/template.html` — copy it and fill **only its `MODEL` object**; the engine renders everything from it. This file explains the *rules* so the diagram stays consistent and on the Stage house palette.

It is the **C4 Container level** (Context → **Container** → Component → Code). You draw containers (deployable/runnable things: a web app, an API, a worker, a DB) and show their components (modules/responsibilities) nested inside, with labeled edges between them. Clicking drills one level deeper (Model D, below) — the Component level — without leaving the page.

## The MODEL (the only thing you edit)
The template is **data-driven**: a single `MODEL = { repo, brand, date, legend, layout, nodes, edges }` object drives the render — the topbar (document title, wordmark, date) is filled from `repo`/`brand`/`date` at runtime, so there are no `{{placeholders}}` to hand-edit (`date:''` auto-fills today). Schema (full version in the template's top comment):
- `legend` — `[['layer','Name'], …]`, only the layers you use.
- `layout` — array of rows of node ids, laid out top→down (clients/edge → server → data/external). Center a much-called hub (a DB) in its row.
- `nodes` — `{ id: {label, tech, layer, kind, summary, entry[], net?, talksTo?[], components?[]} }`. `kind:'container'` shows component pills; `kind:'node'` is a bare box.
- `components` — `[{id, label, one, summary, files[], kids?[{label,txt}], talksTo?[{to,via}], net?}]`.
- `edges` — `[{from, to, label, net?}]` where `from`/`to` are **node ids** (container-level).

The detail fields (`summary`/`files`/`kids`/`talksTo`/`entry`/`net`) come from the Stage 3.5 enrichment pass and power the drill-down + networking toggle. Never hand-write boxes or edit the engine.

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
- **Click a pill** → that component's detail appends inline: **summary** → **files** (each with a copy button) → **kids** (the flat one-liner list) → **talks-to** chips. The pill highlights; an **×** (or re-click) collapses it. Multiple can be open at once (they stack).
- **Click a card title or a node** → the tier/node **overview** (summary · entry point · talks-to) reveals the same way.
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
- [ ] Drill-down works (pill → summary/files/kids/talks-to), the network toggle lights up, copy buttons copy.
