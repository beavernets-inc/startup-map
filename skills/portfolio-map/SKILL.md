---
name: portfolio-map
description: >-
  Map several parallel projects and the people attached to them as one
  self-contained HTML page: a card per project with its stage, next step
  (step / why / who), freshness (last contact, last commit, architecture-map
  status) and the people on it as chips coloured internal / customer / bizdev
  with urgency dots. Click a person to highlight them on every card. Use when
  the user wants to "map my projects", "show my portfolio", "see where
  everything is at", "who is connected to what", or a "startup map". Also the
  front door to architecture-map: it flags repos whose architecture map is
  missing or stale and offers to build them.
---

# Portfolio Map

One page that answers "where is everything, what is next on each, and who is
attached to it" for a person running several projects at once.

Two ideas make it worth building rather than reading the source files:

1. **One person can touch several projects.** A table hides that; this page
   lists them on every card they belong to, and clicking one lights them up
   everywhere.
2. **Progress is a stage, never a percentage.** A number nobody can defend is
   worse than no number.

Everything the map shows must trace to a file or to something the user told
you. Never invent a project, a person, a date or a stage.

**Privacy:** the user's data file lives in *their* project, never inside this
plugin. It usually holds real names and notes, so never copy it anywhere else.

## 0. Ask what they want (always first)

Ask the user, interactively (one short question, offer choices):

- **Where is the data file?** Default `./portfolio/map-data.json`. If it exists,
  read it; if not, this is a first build.
- **What to do this run:** build from scratch · refresh (re-read sources,
  update people/dates/next steps) · just rebuild the HTML from the current data
  · add a project or people.

Do only what they picked.

## 1. Find the real sources (build / refresh)

Look for whatever the user actually keeps:

- **People**: an outreach/contact log, a CRM export, `contacts.md`, a funnel
  sheet. Usually a markdown table with a person per row.
- **Projects**: a repo list, top-level directories, READMEs, a status board,
  a `TODO.md` (next steps come from here).
- **Repos**: the local path of each project's code repo, if it has one.

Read them yourself and emit JSON. Do **not** write a parser for someone's
markdown table: it breaks silently on the first stray `|` in a free-text cell.

## 2. Propose the projects, then stop

Show the user a table of projects, grouping, stage, repo path and next step,
and **wait for corrections**. Grouping is their mental model, not yours.

Stage ladder: `idea · building · live · in-use · paying`

| stage | means |
|---|---|
| `idea` | nothing built |
| `building` | being built, nobody outside has used it |
| `live` | it runs or is deployed, no real user yet |
| `in-use` | someone outside is actually using it |
| `paying` | someone is paying for it |

Any other stage word (e.g. `network` for a "General connections" card) is
shown as text with no progress bar.

## 3. Write the data file

Shape (see `examples/map-data.json` in the plugin for a complete fictional one):

```json
{
  "title": "Acme portfolio map", "org": "Acme",
  "sources": ["crm/outreach-log.md", "TODO.md"],
  "groups":   [{"id": "fintech", "label": "Finance", "color": "#60a5fa"}],
  "projects": [{"id": "ledger", "label": "Ledger", "group": "fintech", "stage": "in-use",
                "repo": "../ledger", "note": "one line",
                "next": {"step": "what happens next", "why": "why it matters now", "owner": "who does it"}}],
  "people":   [{"id": "Jane Doe", "internal": false, "status": "replied", "channel": "email",
                "last": "2026-01-15", "note": "context"}],
  "edges":    [{"s": "Jane Doe", "t": "ledger", "type": "pilot customer", "category": "customer"}]
}
```

- `repo`: absolute, `~/...`, or relative to the data file. Omit for a project
  with no code (e.g. "General connections").
- `group.color` is optional; groups get a palette colour by order otherwise.
- Card order = order in `projects`.
- `internal: true` puts a person in the Internal section on every card.
  Otherwise each **edge** sets `category`: `customer` or `bizdev` (default).
  The same person can be a customer on one project and a partner on another.
- `status` ranks `booked > warm > replied > sent > cold > closed`. A person on
  several rows keeps their furthest-along status and latest date.
- **Urgency is derived, not hand-tagged** (the build does it from `status` and
  `last`; set `urgency` only to override): `act` = booked or no reply after 14
  days (a nudge is due) · `warm` = warm/replied within 14 days · `wait` = sent
  within 14 days or no date · `cold` = closed or silent more than 21 days.
- Normalise aliases quietly, but **warn about any name you could not place**
  rather than inventing a node for it.

## 4. Build

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/portfolio-map/scripts/build.py" <data.json> [<out.html>]
```

(Standalone skill install: the script is `scripts/build.py` next to this file.)
Output defaults to `portfolio-map.html` next to the data file. The script reads
git for each repo's last commit and the last commit of
`<repo>/architecture-map.html`, fills `days` from `last`, derives urgency, and
warns about edges that name an unknown person or project. Stdlib only.

Prefer changing the data over editing `assets/template.html`. If you must edit
the template, rewrite a whole block rather than chaining small patches.

## 5. Architecture maps: offer, one at a time

After the build, list the projects whose card shows **arch map: not built** or
**stale** (map more than 30 days behind the last code commit). Ask the user
which, if any, to (re)build now. For each yes, run the `architecture-map`
skill on that repo; it saves `<repo>/architecture-map.html`. Remind the user
to commit it in that repo (freshness is read from git), then rebuild this map.
Never build them all unasked: each one is a real investigation of a codebase.

## 6. Check it by measuring, not by looking

Render it (Playwright, headless; serve the folder with
`python3 -m http.server` if `file://` is blocked) at **1440px and 390px**:

- `document.documentElement.scrollWidth <= clientWidth` (no sideways scroll)
- smallest text ≥ 10.5px; names never truncated
- clicking a person highlights their chip on every card they appear on
- zero console errors

Report where it saved, the projects flagged not built / stale, and anything in
the sources you could not place.
