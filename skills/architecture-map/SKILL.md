---
name: architecture-map
description: Map a code repo's architecture as a single self-contained HTML C4-style container diagram — labeled tier boxes (frontend/backend/data/external/MCP) with components nested inside and labeled arrows showing how they talk. Use when the user wants to "map the architecture", "visualize the codebase", "show me how this app is wired", "draw the stack", or "make an architecture diagram" of a repo.
---

# Architecture Map

Works standalone on any repo. It is also called by the `portfolio-map` skill for projects whose card shows "arch map: not built" or "stale".

Map a code repo as one self-contained, interactive HTML **C4 container diagram**. Every box, pill, and arrow must trace to code that actually runs — never invent one. Use your own judgement for anything not spelled out here.

## Investigate
**Study the code, never the prose.** Do not trust README/markdown/docs — or even code comments — to decide what exists; they drift and describe things that were removed or never shipped. Read the actual source: imports, call sites, config, and the dependency manifests. A box or edge is real only if running code backs it (a file, an import, a wired call, a declared dependency), not because a doc or comment claims it.

Read the repo enough to understand how it's actually wired — cheaply, not file-by-file. Look at: the file tree, manifests, frameworks, config, entry points, routes/wiring. For a large repo, fan out `Explore` subagents (one per area) and keep the conclusions, not the file dumps.

Sort what you find into tiers — **frontend · backend · data · external · infra · mcp**, plus any other tier the repo genuinely has. Name only the tiers that exist.

## Model, then gate
Build the structure first: tiers as boxes, modules grouped by responsibility as pills inside them, arrows for real relationships (label each with its protocol). Stay at the container level — a readable handful of boxes and edges, not a call graph. Show the user a short outline + the detected stack and **wait for approval** before building. (Headless caller: print it, then proceed.)

## Build
Copy `assets/template.html` and fill the `MODEL` object — the engine draws everything (orthogonal non-overlapping arrows, drill-down, network toggle, pan/zoom, draggable cards). Prefer filling `MODEL` over touching the engine; extend the engine only when a required outcome below isn't rendered yet. Match the **"Stage" house style** (Inter font, `--accent` theming, neutral palette, no rainbow slop) — `references/c4-style.md` has the full `MODEL` schema + visual system. Save as `<repo>/architecture-map.html` (that exact name at the repo root: `portfolio-map` looks for it there and reads its last commit date to tell whether it is stale, so suggest the user commits it).

What goes in each card (per node in `MODEL`):
- **box** — label, tech, layer, kind (`container` has pills · `node` is a bare box). A container's header also shows its **entry file path** (e.g. `backend/src/app/main.py`), so the file that *is* the container is always visible in the title area. The container **title itself is styled as a clickable chip** (same visual language as the pills) so it's obvious it opens the overview.
- **pills** — the modules/responsibilities inside a container.
- **drill-down detail** (read the real code for these) — in this order:
  - **What / How / Why** — three short labeled lines: what it is, how it works, why it's necessary.
  - **Inputs and outputs as ports** — Blender-node style: dots on the card's **left edge = inputs** (what comes in and from where — callers, imported services, data read), dots on the **right edge = outputs** (what goes out and to where — data written, network calls, return values). Each port is labeled with the payload *and its purpose* ("SOAP text → billing codes"), not just a protocol name. A `talksTo` that is really request+response appears on both sides.
  - **Data-flow drawer** — every component with real logic also gets a `flow`: the ordered chain of functions the data passes through inside it. A "data flow" affordance next to the ports slides in a panel from the left, laid out **vertically, top to bottom, scrollable**: inputs at the top, outputs at the bottom, function nodes stacked between them — each showing what comes in, how the data is transformed, and what goes out (which is the next node's input). Everything must be visible by scrolling; nothing may clip off-screen. If a flow genuinely branches, show the branches as parallel side-by-side lanes that re-merge; otherwise keep one straight lane. A step whose main function is **imported from another file** must be visually differentiated from local steps and show that source file's path on the node, so the reader knows where to zoom in next. A step (a stage's main function) may contain **nested sub-cards** — the helper functions it calls — rendered smaller inside the parent card, each with its own in/does/out, sequenced vertically with arrows when they run in order, so the reader sees which input maps to which helper and how data hands off between them. A reader should be able to follow one piece of data from entry to exit.
  - **Code anatomy view** — big files a person will actually study also get an `anatomy`: a second tab in the same drawer showing the file as it sits on disk, top to bottom — imports, module-level setup (runs once at import), definitions (registered but dormant), and entry points (run per request/event) — each section with its line range, when it runs, and what's in it. Optional per component, like `flow`; skip it for small files.
  - the real file paths, a short flat list of sub-items if any (cap ~8), and any networking facts (ports/domains/TLS).
- **file paths** — render the shared directory prefix small/dim and the last one or two path segments prominent. Long paths must never clip or overflow the card: wrap or scroll them.

## Outcome
One self-contained HTML file: labeled tier boxes with nested components, protocol-labeled arrows, click-to-drill-in detail, a networking toggle, and pan/zoom/drag — something a person can open and actually understand how the app is wired.

## Double-check (correctness above all)
Render it (Playwright MCP, headless, screenshot) and confirm it is a **correct and complete** representation:
- Account for **every** manifest dependency and **every** top-level dir — each is on the map, folded into a component, or deliberately out of scope. Anything unaccounted for is a miss; fix it.
- Nothing is fabricated: a doc or comment claim is **not** evidence. If no running code uses something, it's out of scope even if a stale dir or file lingers (e.g. an unreferenced data dir for a dependency that isn't installed).
- Arrows connect the right boxes, labels are legible, and drill-down + the network toggle work.

Report the stack, what you drew, the saved path, and anything you couldn't resolve.
