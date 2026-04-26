# Subsystem #2 — Reference Vault

- **Date:** 2026-04-26
- **Status:** Approved (via Session A brainstorm)
- **Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md`
- **Master-spec sections referenced:** §1, §2 (target user — Ableton Lite, MPK Mini 4), §5.1 #2 (one-liner contract)
- **Session:** A (Scaffolding)
- **Build order:** Second in Session A (after #1, before #9)
- **Depends on:** #1 (folder shell + `.gitignore`)
- **Blocks:** #3 (Knowledge Base) and #9 (Companion Mode) reference `INDEX.md` when grounding answers

## One-liner contract

Acquires authoritative reference materials for Ableton Live 12 and the Akai MPK Mini 4, indexes them with a topic→page (or topic→URL) mapping in `reference/INDEX.md`, and curates a small set of authoritative online resources in `reference/ONLINE.md`.

## What this subsystem does

### 1. Manual acquisition (hybrid: try curl first, fall back to user-handoff per failed file)

For each manual:

1. Attempt download via PowerShell `Invoke-WebRequest` to `reference/`.
2. If the download succeeds AND the result is a valid PDF (verify by checking magic bytes — first four bytes are `%PDF`), keep it.
3. If the download fails or returns non-PDF content (e.g., HTML), fall through to "user-handoff": create or append to `reference/HOW-TO-FETCH.md` with the URL and an instruction for Destin to fetch it manually (browser → save as) into `reference/`.

#### Targets

| Manual | Expected outcome | Filename if downloaded |
|---|---|---|
| Akai MPK Mini 4 user guide | Likely succeeds (akaipro.com hosts a direct PDF link) | `reference/mpk-mini-4-user-guide.pdf` |
| MPK Mini 4 MIDI implementation chart | Often integrated into the user guide; may not exist as a separate file | `reference/mpk-mini-4-midi-chart.pdf` (if separate) |
| Ableton Live 12 reference manual | Expected to fail (Ableton serves the manual as HTML at `https://www.ableton.com/en/live-manual/12/`, with no official PDF) | (none — fall through to ONLINE.md) |

When a manual is not obtainable as a local PDF (i.e., the Ableton manual), `INDEX.md` maps topics to live URL anchors instead of page numbers, and `ONLINE.md` lists the live HTML manual as the authoritative source for that material.

### 2. `reference/INDEX.md`

Format:

```markdown
# Reference Index

> Topic → page (PDF) or URL anchor (online).

## Akai MPK Mini 4 user guide  (reference/mpk-mini-4-user-guide.pdf)
- Pads & MIDI mapping → p. 12
- Program editor → p. 24
- ...

## Ableton Live 12 reference manual  (online: https://www.ableton.com/en/live-manual/12/)
- Simpler instrument → https://www.ableton.com/en/live-manual/12/simpler/
- Mixer view → https://www.ableton.com/en/live-manual/12/mixer/
- ...
```

**Granularity:** chapter / major-topic level. One entry per major topic, not per section/subsection.

**Minimum:** 10 entries per source listed in `INDEX.md` — applies equally to PDF-acquired sources and to the HTML Ableton manual. Authored by Claude reading the actual materials (PDF text extraction for PDFs; the manual's table of contents for the HTML manual).

### 3. `reference/ONLINE.md`

Format (markdown table):

| Title | URL | What it's good for | Last verified |
|---|---|---|---|
| Ableton Live 12 reference manual | https://www.ableton.com/en/live-manual/12/ | Authoritative live manual (HTML, current) | 2026-04-26 |
| Ableton Learn Live | https://www.ableton.com/en/live/learn-live/ | Official video tutorials for beginners | 2026-04-26 |
| Akai MPK Mini 4 product page | https://www.akaipro.com/mpk-mini-4 | Product specs, downloads, support | 2026-04-26 |
| Camelot Wheel reference | https://mixedinkey.com/camelot-wheel/ | Standard Camelot notation reference | 2026-04-26 |
| Ableton Live 12 release notes | https://www.ableton.com/en/release-notes/live-12/ | What's in 12 vs prior versions | 2026-04-26 |

**Minimum:** 5 entries. Each URL verified via WebFetch at authoring time (returns 200 and content matches the title). The seed list above is the floor — Claude may add more if other authoritative sources are clearly relevant (e.g., Splice docs, Ableton certified-trainer resources).

## What this subsystem must NOT do

- Do not author any `knowledge/` content (that's Session B / Subsystem #3).
- Do not redistribute or host the manuals — local-only personal copies.
- Do not commit the PDFs to git (per `.gitignore` from #1).
- Do not write Python scripts.
- Do not write `taste/` or `teardowns/` content.

## Verification gates (must all pass before #9 starts)

- `reference/` contains the MPK manual(s) that downloaded successfully (or `reference/HOW-TO-FETCH.md` exists for any manual whose download failed).
- `reference/INDEX.md` exists with at least 10 entries per acquired source.
- `reference/ONLINE.md` exists with at least 5 entries; each URL verified to return 200 at authoring time.
- `git status` shows no `*.pdf` files staged (gitignore working).
- Spot-check: pick 3 INDEX.md entries that map to a PDF, open the PDF to the listed page, confirm the page actually covers the listed topic. Pick 3 entries that map to a URL anchor, fetch the URL, confirm the page covers the listed topic.
