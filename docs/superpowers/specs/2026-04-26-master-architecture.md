# Crunchtronics Tutor — Master Architecture Spec

- **Date:** 2026-04-26
- **Status:** Approved (draft, pending implementation plan)
- **Author:** Destin + Claude (brainstorm session)

## 1. Purpose

Crunchtronics Tutor is a personal music-production learning system for **Destin**, a complete music-production beginner (brief junior-high piano background only) who has just acquired an **Akai MPK Mini 4** MIDI controller and the bundled **Ableton Live 12 Lite**. The system's job is to act as a long-running, taste-aware tutor that:

- Teaches music theory and software/hardware navigation in a top-down, genre-first way
- Personalizes lessons based on Destin's actual listening taste (sourced from Spotify)
- Walks through finished tracks Destin already loves and explains how they're built
- Sits alongside Destin during Ableton sessions and answers "how do I do X" questions by reading his screen
- Nudges him along a structured curriculum when he hasn't shown up in a while

The system is not a music generator, not an autonomous producer, and not a substitute for Destin actually doing the work — it is a tutor.

## 2. Target user profile

- **Background:** essentially zero music production; brief piano in junior high
- **Hardware:** Akai MPK Mini 4 (MIDI keys + 8 pads + knobs)
- **Software:** Ableton Live 12 Lite (bundled with the MPK), Windows 11 Home. Likely upgrade path: **Ableton Live 12 Intro** ($99). Standard/Suite are not on the near-term roadmap.
- **Taste anchor (working hypothesis, will be confirmed by Spotify pull):** EDM across multiple subgenres — confirmed reference points include Subtronics (riddim/dubstep), Wooli (melodic dubstep), John Summit (tech house), Jigitz (bass house)
- **Interaction model:** A + C — primarily on-demand chat sessions (open Claude Code in the project folder, ask questions, practice), supplemented by scheduled nudges that can suggest the next concept when stuck

## 3. Constraints (these shape the architecture)

1. **Spotify Web API deprecation (Nov 2024).** New apps no longer get `audio-features`, `audio-analysis`, `related-artists`, or recommendation endpoints. Only apps in extended quota mode prior to Nov 27, 2024 retain access. **Implication:** the Spotify subsystem can pull playlists and track lists, but BPM / key / Camelot / energy / danceability must come from a different source.
2. **Ableton Live 12 Lite/Intro limits.** Both editions share the architecturally significant constraints: **no Max for Live** (so no AbletonOSC), **no Sampler** (only Simpler), no Complex/Complex Pro warping. They differ in track count (Lite: 8 audio + 8 MIDI; Intro: 16 + 16) and send count (Lite: 2; Intro: 4) — neither difference affects this architecture. **Implications:** (a) no autonomous Ableton-control subsystem regardless of which edition the user runs; (b) teardowns produce step-by-step recipes designed to the **Lite floor** (8/8 tracks, Simpler-only) so they remain valid if the user upgrades to Intro, Standard, or Suite later; (c) only Suite — or Standard with a separately-purchased Max for Live — would unlock the deferred deep-OSC features in §12.
3. **Windows 11 host.** All tooling must run on Windows. PowerShell available, bash available via Git Bash.
4. **Beginner user.** The system must not short-circuit learning by doing the work for the user. Every artifact (curriculum, recipes, teardowns) is designed to make the user *do the production*, with Claude as guide.
5. **Audio asset reality for major commercial EDM.** Masters are obtainable (Beatport, Bandcamp, YouTube via yt-dlp); stems and multitracks effectively are not; Splice "Sounds of [artist]" packs and preset packs exist for many top-tier bass/dubstep artists and are the closest thing to studying actual production assets. **Implication:** teardown pipeline is master-first, with artist-specific resources surfaced as enhancement.

## 4. Top-level folder layout

Project root: `C:\Users\desti\crunchtronics-tutor\`

```
crunchtronics-tutor/
├── CLAUDE.md                    # how Claude operates inside this project
├── README.md                    # human-facing overview
├── curriculum.md                # state-tracked learning path (live document)
├── reference/                   # manuals + downloaded docs (Ableton, MPK)
├── knowledge/                   # structured cheat sheets Claude teaches from
│   ├── theory/                  # music theory primitives
│   ├── ableton/                 # software navigation
│   ├── mpk-mini-4/              # hardware navigation
│   ├── genres/                  # EDM-subgenre cheat sheets
│   └── artists/                 # per-artist resource pages (Splice packs, preset packs, signature techniques)
├── taste/                       # Spotify pull + enriched analysis
│   ├── playlists.json           # raw Spotify playlists payload
│   ├── tracks.csv               # enriched spreadsheet (BPM/key/Camelot/etc.)
│   └── profile.md               # narrative summary of taste, written by Claude
├── teardowns/                   # per-track teardown artifacts
│   └── <slug>/
│       ├── analysis.json        # librosa output
│       ├── teardown.md          # narrative explanation
│       └── recipe.md            # numbered build steps for Ableton Lite
├── sessions/                    # per-session logs
├── docs/superpowers/specs/      # this spec, plus per-subsystem specs
│   └── subsystems/              # 01-project-shell.md … 09-reactive-companion.md
└── scripts/                     # local CLI tools (spotify-pull, enrich, analyze, etc.)
```

Secrets live **outside** the project at `C:\Users\desti\.crunchtronics-tutor-secrets\`:

```
.crunchtronics-tutor-secrets/
├── spotify.json                 # OAuth client + refresh token
└── audio-enrichment.json        # GetSongBPM (or alternative) API key
```

## 5. Subsystem decomposition

Nine subsystems. Each gets its own brainstorm → spec → plan → implementation cycle. The dependencies column is the build-order constraint.

| # | Subsystem | Purpose | Depends on |
|---|---|---|---|
| 1 | **Project Shell** | CLAUDE.md, README, conventions, git init, folder bootstrap | — |
| 2 | **Reference Vault** | Acquire + index Ableton Lite manual, MPK Mini 4 manual, key online docs | #1 |
| 3 | **Knowledge Base** | Hand-authored structured guides (theory, software, hardware, genres, artists) | #1 |
| 4 | **Curriculum & Nudges** | Living `curriculum.md` + scheduled-agent nudges via `/schedule` | #3, #7 |
| 5 | **Spotify Integration** | OAuth, playlist pull, track-list extraction → `playlists.json` | #1 |
| 6 | **Audio Feature Enrichment** | Third-party API (GetSongBPM primary) → enrich `tracks.csv` | #5 |
| 7 | **Taste Profile** | Claude reads enriched spreadsheet → writes `taste/profile.md` | #6 |
| 8 | **Teardown Pipeline** | Local audio analysis (librosa) + Claude-authored teardown.md + recipe.md | #6 |
| 9 | **Reactive Companion** | windows-control MCP for screen reading + click guidance during sessions | #1 |

### 5.1 Per-subsystem responsibilities (one-liner contracts)

- **#1 Project Shell** — Bootstraps the folder, writes CLAUDE.md (the pedagogy + Claude conventions), README.md, initial empty curriculum.md, .gitignore, git init. Writes nothing in `taste/`, `teardowns/`, or `knowledge/` beyond folder skeletons.
- **#2 Reference Vault** — Acquires the Ableton Live 12 reference manual (downloadable PDF) and the Akai MPK Mini 4 user guide (PDF), indexes them with a `reference/INDEX.md` that maps topics to page numbers. Adds a small set of curated online docs (Ableton's official lessons URLs, MPK MIDI implementation chart).
- **#3 Knowledge Base** — Claude authors (under user direction) `knowledge/theory/`, `knowledge/ableton/`, `knowledge/mpk-mini-4/`, `knowledge/genres/`, `knowledge/artists/`. Each file is a structured cheat sheet Claude can read mid-session (consistent format: TL;DR → details → links into Reference Vault → "next concept"). Top-down framing: genre cheat sheets reference the theory primitives; theory primitives don't exist in isolation. Artist files are written incrementally — once the Taste Profile (#7) identifies which artists actually matter to the user, those artists get pages added.
- **#4 Curriculum & Nudges** — Designs the `curriculum.md` schema (lesson nodes, status tags, dependencies, "next" pointer). Writes the initial curriculum biased toward the user's taste profile. Sets up `/schedule` agents for M/W/F nudges. Defines the convention that Claude updates curriculum.md at the end of every session.
- **#5 Spotify Integration** — Registers the Spotify Developer app (manual user step, documented), implements OAuth refresh-token flow, writes a CLI script under `scripts/` (language to be chosen in this subsystem's spec) that dumps all user playlists + their track lists to `taste/playlists.json`. Idempotent. Re-runnable on a `/schedule` weekly.
- **#6 Audio Feature Enrichment** — Reads `playlists.json`, dedupes tracks, queries GetSongBPM (primary) for BPM + key, computes Camelot from key. Writes/updates `taste/tracks.csv` incrementally (only fetches rows missing data). Records `source` per row so the service is swappable. Rate-limit aware.
- **#7 Taste Profile** — Reads `tracks.csv`. Writes `taste/profile.md` — a prose narrative covering: dominant BPM clusters, dominant Camelot keys, energy/danceability biases, top artists, identified subgenres, and a "resources surface area" section (which top artists have known Splice packs / preset packs). Re-runs when csv row count changes ≥10%.
- **#8 Teardown Pipeline** — Workflow: user picks a track (from `tracks.csv` or arbitrary), system pulls audio (yt-dlp by default, manual file drop fallback), runs librosa to produce `analysis.json` (tempo, beat grid, sections, chroma), Claude writes `teardown.md` (what's happening when) + `recipe.md` (how to build a similar arrangement in Ableton, step by step). Recipes are written to the **Lite floor** (8 audio + 8 MIDI tracks, Simpler-only) so they remain valid on any edition; when a recipe is constrained by Lite limits, it includes a short "Intro+ note" describing what the user could do differently with more tracks/sends. Recipe references the artist's `knowledge/artists/<slug>.md` for resource enhancement when applicable.
- **#9 Reactive Companion** — On-demand only. User says "look at my Ableton" or similar; Claude uses `windows-control` MCP to capture the window, reads the state, and gives click-by-click guidance. No autonomous monitoring. Defines the conventions for when/how to invoke screen capture.

## 6. Data flow

```
                                                  ┌─────────────────┐
Spotify ──► (#5) ──► playlists.json ──► (#6) ──► tracks.csv ──► (#7) ──► taste/profile.md
                                                  │                       │
                                                  ▼                       ▼
                                              (#8) Teardown          (#4) Curriculum
                                              uses tracks.csv        reads profile,
                                              + user-provided        updates curriculum.md,
                                              audio file →           drives nudges
                                              analysis.json +
                                              teardown.md +
                                              recipe.md

(#3) Knowledge Base ──┐
(#2) Reference Vault ─┼──► read by Claude during all chat sessions
(#9) Companion ───────┘    (windows-control MCP, on-demand only)

Every session ──► sessions/YYYY-MM-DD-<topic>.md ──► feeds back into curriculum updates
```

## 7. Inter-subsystem contracts (data formats)

The whole point of the master architecture is that downstream sub-projects can be designed and built independently as long as they honor these formats.

### 7.1 `taste/playlists.json`

Raw Spotify Web API shape, stored verbatim. At minimum: a top-level `{ user_id, fetched_at, playlists: [...] }` where each playlist contains its `tracks: [...]` array as Spotify returns them. No transformation — keeps us robust to Spotify shape changes.

### 7.2 `taste/tracks.csv`

Flat CSV. Required columns (initial set; downstream subsystems can extend):

```
spotify_id, isrc, artist, title, album, duration_s, bpm, key_camelot, key_standard, energy, danceability, genre, source, fetched_at
```

- `source` = which enrichment service the row was fetched from (e.g., `getsongbpm`, `acousticbrainz`, `manual`)
- `fetched_at` = ISO 8601 timestamp
- Empty cells are valid — enrichment is best-effort

### 7.3 `curriculum.md`

Markdown with structured front matter and lesson nodes:

```markdown
---
last_updated: 2026-04-30T19:23:00Z
next: lesson-003
---

# Curriculum

## lesson-001: Setting up the MPK in Ableton Lite [done]
- [x] Install drivers
- [x] Map MPK pads to drum rack
- Notes: completed 2026-04-27, took ~30 min

## lesson-002: Four-on-the-floor drum pattern in tech house [done]
...

## lesson-003: Sidechain compression for that "pumping" feel [active]
- Why next: profile shows heavy melodic-techno bias; sidechain is foundational there
- Dependencies: lesson-002 (basic drum pattern)
- Practice task: ...
```

Status tags: `[active]`, `[blocked]`, `[done]`, `[skipped]`. Claude updates this file at the end of every session.

### 7.4 `taste/profile.md`

Prose, no schema. Sections (suggested):

```markdown
# Destin's taste profile (auto-generated 2026-04-30)

## TL;DR
You listen to {N} tracks across {M} playlists. Your taste centers on...

## BPM clusters
- 124-128 BPM: {count} tracks (tech house, melodic techno)
- 140-150 BPM: {count} tracks (dubstep / riddim)
- ...

## Key bias
Most common Camelot keys: ...

## Top artists & subgenres
...

## Resources surface area
- {N} artists with available Splice packs: ...
- {N} artists with preset packs: ...
- Cheapest leverage for buying study materials: ...
```

### 7.5 `teardowns/<slug>/`

Three files per teardown:

- `analysis.json` — librosa output: `{ tempo, beat_times, sections: [{start, duration, label}], chroma, mfcc_summary }`
- `teardown.md` — narrative ("0:00–0:16 intro: filtered piano + atmospheric pad + delayed drum hit at 0:08; the kick enters at 0:16 with a hard sidechained pluck...")
- `recipe.md` — numbered build steps written to the Lite floor (so they work on any edition) ("1. Set tempo to 126 BPM. 2. Create a Drum Rack on MIDI track 1. 3. Load a kick from your Splice library matching the punchy / short-decay character described in section 1..."). Sections that would benefit from Intro+ features get an inline "**Intro+ note:**" callout (e.g., "with a 9th MIDI track available, you could split the bass layers across two channels for independent processing")

### 7.6 `sessions/YYYY-MM-DD-<topic>.md`

Free-form markdown, written by Claude at the end of every session. Suggested sections: what we covered, blockers hit, links to curriculum nodes touched, what to do next session.

## 8. Refresh cadence

| Subsystem | Refresh trigger |
|---|---|
| Spotify pull (#5) | Weekly via `/schedule`, or on demand |
| Enrichment (#6) | Incremental — only rows missing data; rate-limited to GetSongBPM quota |
| Taste profile (#7) | When `tracks.csv` row count changes ≥10%, or on demand |
| Curriculum (#4) | End of every session (Claude updates inline) |
| Nudges (#4) | M/W/F mornings via `/schedule`, configurable |
| Teardowns (#8) | On demand only — user requests "teardown this track" |

## 9. Build order

```
Phase 1: Foundation              Phase 2: Learning surface          Phase 3: Personalization
─────────────────────            ──────────────────────             ────────────────────────
[#1] Project Shell      ──►      [#3] Knowledge Base        ──►    [#5] Spotify Integration
                                 [#2] Reference Vault        ║      [#6] Audio Enrichment
                                 [#9] Reactive Companion     ║      [#7] Taste Profile
                                          ║                  ║
                                          ▼                  ▼
                                          You can already learn      Personalizes everything
                                          + practice with Claude     downstream from here

Phase 4: Guided structure        Phase 5: Capstone
─────────────────────────        ─────────────────
[#4] Curriculum & Nudges  ──►    [#8] Teardown Pipeline
(depends on #3 + #7)             (depends on #6 + audio toolchain)
```

**Why this ordering:** the user can begin learning Ableton + theory after Phase 2 ships, before any Spotify or teardown infrastructure exists. Phase 3 personalizes everything downstream. Phase 4 (curriculum) intentionally waits for Phase 3 so the curriculum is taste-aware on first pass instead of being rebuilt later. Phase 5 is the capstone — most ambitious technically and most rewarding once everything else exists.

Within Phase 2 and Phase 3, subsystems are parallelizable — different sessions can build them concurrently as long as they honor the contracts in §7.

## 10. Sub-project hand-off pattern

Each subsystem becomes its own session: `superpowers:brainstorming` → spec → `superpowers:writing-plans` → `superpowers:executing-plans`. The master spec from this conversation is the **shared contract** every sub-project reads first.

Spec file naming:

```
docs/superpowers/specs/
├── 2026-04-26-master-architecture.md             ← this file
├── subsystems/
│   ├── 01-project-shell.md
│   ├── 02-reference-vault.md
│   ├── 03-knowledge-base.md
│   ├── 04-curriculum-and-nudges.md
│   ├── 05-spotify-integration.md
│   ├── 06-audio-enrichment.md
│   ├── 07-taste-profile.md
│   ├── 08-teardown-pipeline.md
│   └── 09-reactive-companion.md
```

Each sub-project's brainstorm should begin: "Read `docs/superpowers/specs/2026-04-26-master-architecture.md` first. You are designing subsystem #N — your inputs and outputs are defined in §5.1, §6, and §7. Stay within those boundaries."

## 11. Decisions (the 12 defaults)

| # | Decision | Default | Rationale |
|---|---|---|---|
| 1 | Spotify app registration | User registers a Spotify Developer app once; subsystem #5 documents the steps | Required, no automation around it |
| 2 | Audio enrichment service | **GetSongBPM** primary | Free, has API, BPM+key cover essentials; `source` column makes service swappable |
| 3 | Splice subscription | **Recommend but defer** until teardown ships (Phase 5) | No reason to pay before using it |
| 4 | Nudge cadence | **M/W/F mornings**, configurable in #4 | Frequent enough to engage, sparse enough not to pester |
| 5 | Git remote | **Local-only**, no remote until user decides | Zero risk of secrets leak by default |
| 6 | Audio analyzer | **librosa** (Python) | Maturest, easiest Windows install, best docs |
| 7 | Music theory framing | **Top-down** — genre patterns first, theory invoked as needed to explain them | User is learning to make music he likes, not pass a theory exam |
| 8 | Hardware/software ordering | **Together** — MPK mapped to Ableton defaults from day 1 of curriculum | Builds muscle memory while learning concepts |
| 9 | CLAUDE.md scope | Project description **+** Claude pedagogy conventions (always check curriculum, default to top-down framing, prefer reactive companion to verbal directions when Ableton is open) | The pedagogy *is* part of the project |
| 10 | Audio acquisition | **yt-dlp default**, manual file drop fallback | User selected this in brainstorm |
| 11 | Sessions log retention | **Keep all logs forever**, no rotation | Cheap; useful for "what did we cover 6 months ago" |
| 12 | Spotify pull frequency | **Weekly** scheduled + on-demand | Taste evolves slowly |

## 12. Out of scope

- Generating Ableton `.als` project files (Lite + no Max for Live)
- Autonomous companion mode (Claude watching the user produce in the background)
- Mobile or cloud access — this is a local-only Windows project
- Generative composition (Claude writing music for the user)
- Vocal-coaching or DJ-mixing modes (different disciplines, different specs)
- Deep Ableton OSC integration (AbletonOSC, real-time companion mode that watches the user produce, auto-generated `.als` tutorial projects) — requires Max for Live, which means **Ableton Suite** or **Standard + a separately-purchased Max for Live license**. Lite and Intro both lack Max for Live; an Intro upgrade alone does not unlock these features. Deferred indefinitely.

## 13. Next steps

1. User reviews this spec.
2. On approval, invoke `superpowers:writing-plans` to produce a **master implementation plan** that schedules each subsystem as its own brainstorm → spec → plan → implementation hand-off in the build order from §9.
3. Begin with subsystem #1 (Project Shell). Each subsequent subsystem is launched as its own session referencing this master spec.
