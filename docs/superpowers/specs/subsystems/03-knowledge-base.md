# Subsystem #3 — Knowledge Base

- **Date:** 2026-04-26
- **Status:** Approved (via Session B brainstorm)
- **Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md`
- **Master-spec sections referenced:** §1 + §2 (target user — beginner, EDM, MPK Mini 4, Ableton Lite/Intro), §5.1 #3 (one-liner contract — Claude authors cheat sheets under user direction), §11 default decisions #7 (top-down framing), #8 (hardware/software learned together), #9 (CLAUDE.md pedagogy already written by #1)
- **Session:** B (Knowledge Base)
- **Build order:** Sole subsystem in Session B (after Session A complete)
- **Depends on:** #1 (folder skeleton), #2 (`reference/INDEX.md` — cheat sheets cite into it by topic name)
- **Blocks:** #4 (Curriculum reads `knowledge/` + `taste/profile.md`), #7 (Taste Profile authors `knowledge/artists/*` once taste data exists), #8 (Teardowns reference `knowledge/genres/*` and `knowledge/artists/*`)

## One-liner contract

Authors a structured library of beginner-friendly cheat sheets across theory, Ableton, MPK Mini 4, and EDM subgenres, each following a fixed template (front matter + TL;DR + Cheat block + Read-this-yourself + See also), indexed by `knowledge/INDEX.md`. Top-down framing: genre cheat sheets reference theory primitives only when load-bearing.

## What this subsystem does

### 1. The cheat-sheet template (every file under `knowledge/{theory,ableton,mpk-mini-4,genres,artists}/` follows this shape)

```markdown
---
slug: tech-house
category: genres
tldr: Four-on-the-floor club music at 124-128 BPM with rolling basslines and tight, punchy drums.
prerequisites: [rhythm-basics, the-mixer]
references:
  - "Ableton Manual: Mixing (mixer view, sends, returns)"
  - "Ableton Manual: Live Audio Effect Reference"
next: sidechain-compression
---

# Tech house

## TL;DR
<2-4 sentences expanding the front-matter tldr — what it is, why it sounds the way it does,
and where it sits in the EDM landscape.>

## Cheat block
<Dense bullets. Claude scans this mid-session. Subheadings allowed.>
- **BPM:** 124-128
- **Structure:** intro 16 bars -> drop A 32 bars -> break 16 -> drop B 32 -> outro 16
- **Drums:** four-on-the-floor kick, off-beat open hat, tight clap on 2/4
- ...

## Read this yourself
<Conversational prose. Second person. For Destin to read standalone.>

## See also
- `theory/rhythm-basics.md` — four-on-the-floor anatomy
- `ableton/the-mixer.md` — for the sidechained-bass setup
- Reference: *Mixing (mixer view, sends, returns)* in `reference/INDEX.md`
```

#### Front-matter rules

| Field | Type | Constraint |
|---|---|---|
| `slug` | string | Kebab-case, matches filename without `.md`, unique across all of `knowledge/` |
| `category` | enum | One of `theory`, `ableton`, `mpk-mini-4`, `genres`, `artists` |
| `tldr` | string | One sentence, ≤25 words. The body's `## TL;DR` opens with this exact sentence, then expands. |
| `prerequisites` | list of slugs | Bare slugs (no path, no extension). Empty list `[]` for foundational primitives. Each slug must resolve to a cheat sheet that exists. |
| `references` | list of strings | Human-readable topic names of the form `"<Source>: <topic>"` where `<Source>` is `Ableton Manual` or `MPK Manual`, and `<topic>` semantically corresponds to a bullet in the matching section of `reference/INDEX.md`. Reference Vault is the canonical source for URLs/page numbers; cheat sheets cite by topic, never by URL or page number directly. The match is semantic (Claude can find the corresponding INDEX entry), not a verbatim string match. Empty list allowed when no Reference Vault entry applies. |
| `next` | slug or null | Single forward pointer used by Subsystem #4 Curriculum. `null` for terminal/leaf concepts. |

#### Body rules

- `## TL;DR` — opens with the front-matter `tldr` sentence verbatim, then 1-3 sentences of expansion.
- `## Cheat block` — bullet-heavy, dense, fast to scan. Subheadings allowed (`### Drums`, `### Structure`). This is the layer Claude reads mid-session.
- `## Read this yourself` — prose, second person, friendly, no jargon without a one-line definition. Aimed at Destin reading on the couch. Length scales with topic complexity (~100-300 words typical).
- `## See also` — bullet list of (a) other cheat-sheet relative-path links with one-line "why", and (b) Reference Vault citations of the form `Reference: *<topic>* in reference/INDEX.md`. Body cross-links to other cheat sheets use **relative markdown paths** (`../theory/rhythm-basics.md`), never bare slugs.
- "Next concept" lives in front matter only — no body section needed. The `## See also` is for lateral/related concepts, not the curriculum forward-pointer.

### 2. Seed content authored this session

19 cheat sheets total. (Plus `companion-mode.md` from Session A, untouched.)

#### `knowledge/theory/` (5 files)

| File | Covers |
|---|---|
| `rhythm-basics.md` | Beats, bars, time signatures, four-on-the-floor anatomy |
| `intervals.md` | Semitones, scale steps, interval naming |
| `scales-and-keys.md` | Major/minor scales, key signatures, modes invoked only when load-bearing |
| `chord-construction.md` | Triads, 7th chords, building from scale degrees |
| `the-camelot-wheel.md` | Camelot notation, harmonic mixing intuition |

#### `knowledge/ableton/` (6 new files; companion-mode.md from Session A is **not modified**)

| File | Covers |
|---|---|
| `session-vs-arrangement-view.md` | When to use each; Lite's 8/8 track floor called out |
| `the-browser.md` | Finding instruments/samples/devices; search; tags |
| `midi-vs-audio-tracks.md` | What each holds; when to pick which |
| `the-mixer.md` | Channel strip; sends/returns; Lite's 2-send floor called out |
| `simpler-basics.md` | Loading a sample; Classic/One-Shot/Slice modes; envelopes |
| `drum-rack-basics.md` | Chains; pads; cross-link to MPK pad mapping |

#### `knowledge/mpk-mini-4/` (4 files)

| File | Covers |
|---|---|
| `pads-vs-keys-vs-knobs.md` | What each surface does; default mappings |
| `mapping-pads-to-drum-rack.md` | End-to-end recipe; cross-links to `ableton/drum-rack-basics.md` |
| `mpk-program-editor.md` | Akai Program Editor app; custom presets |
| `transport-controls.md` | Play/stop/record bindings to Ableton transport |

#### `knowledge/genres/` (4 files)

| File | Anchor artist | Notes |
|---|---|---|
| `dubstep.md` | Subtronics | Covers the riddim/heavy-dubstep cluster as one cheat sheet |
| `melodic-dubstep.md` | Wooli | Separate from `dubstep.md` — distinct production aesthetic |
| `tech-house.md` | John Summit | — |
| `bass-house.md` | Jigitz | — |

Each genre cheat sheet covers: typical BPM range, typical song structure, signature drum/bass/synth aesthetics, key reference artists, and links to the theory primitives it depends on (top-down framing per master spec §11 #7).

#### `knowledge/artists/` (empty this session)

Populated by Session D / Subsystem #7 (Taste Profile) once Spotify pull + enrichment data identify which specific artists matter to Destin. Do not preempt.

### 3. `knowledge/INDEX.md`

Format: grouped by subdirectory, mirrors the shape of `reference/INDEX.md`.

```markdown
# Knowledge Index

> One entry per cheat sheet. TL;DR pulled from each file's front matter.

## theory
- [chord-construction](theory/chord-construction.md) — How triads and seventh chords are built from scale degrees.
- [intervals](theory/intervals.md) — Distances between two notes, named in semitones and scale steps.
- [rhythm-basics](theory/rhythm-basics.md) — Beats, bars, time signatures, and the four-on-the-floor pulse EDM is built on.
- [scales-and-keys](theory/scales-and-keys.md) — Major and minor scales, key signatures, and how a track's key shapes its mood.
- [the-camelot-wheel](theory/the-camelot-wheel.md) — Camelot notation: a DJ-friendly map of which keys mix harmonically.

## ableton
- [companion-mode](ableton/companion-mode.md) — On-demand screen-reading policy for Ableton sessions. *(authored Session A — do not modify)*
- [drum-rack-basics](ableton/drum-rack-basics.md) — ...
- ...

## mpk-mini-4
- ...

## genres
- ...

## artists
*(empty — populated by Session D / Subsystem #7 once the taste profile lands.)*
```

**Maintenance discipline:** whenever a cheat sheet is added, removed, renamed, or has its `tldr` field changed, `knowledge/INDEX.md` is regenerated by hand and committed in the same commit as the cheat-sheet change. No script — the regen is small enough to do reliably.

**Special case — `companion-mode.md`:** Session A's policy doc has no front matter (it is a policy, not a cheat sheet, and its content is preserved byte-identical). Its `INDEX.md` entry is therefore **hand-written**, not derived from front matter. The hand-written line should describe its role as the on-demand screen-reading policy. All other entries derive their TL;DR text from the source file's front-matter `tldr` field verbatim.

### 4. Voice and pedagogy notes

- **Top-down framing** (master spec §11 #7): genre cheat sheets explain what the genre is doing first; theory primitives are referenced (`See also`) only when load-bearing. Do not pre-justify a genre by walking through theory. Theory primitives stand on their own as references, not as a curriculum gate.
- **Hardware/software together** (master spec §11 #8): MPK content cross-links to Ableton content where the operations touch. `mapping-pads-to-drum-rack.md` lives in `mpk-mini-4/` (Destin's mental anchor is "I'm at my MPK"), with a `See also` pointer to `ableton/drum-rack-basics.md`.
- **Lite floor honesty** (master spec §3 #2): when a cheat sheet covers an Ableton feature whose limits matter (track counts, send counts), call out the Lite floor explicitly. No "Intro+ note" callouts here — those belong in teardown recipes (Subsystem #8).
- **No theory-exam tone.** Destin is learning to make music he likes, not pass an exam. Cheat blocks are reference; "Read this yourself" sections are encouraging, second-person, low-jargon.

## What this subsystem must NOT do

- Do not modify `knowledge/ableton/companion-mode.md` (Session A's, byte-identical preservation required).
- Do not author any `knowledge/artists/*` content. That is Session D / Subsystem #7's responsibility once the taste profile reveals which artists matter.
- Do not download, redistribute, or re-index any external manuals. The Reference Vault (Subsystem #2) owns `reference/` — cheat sheets cite into it by topic name, never duplicate its content.
- Do not author `taste/profile.md`, any `taste/` data files, or any `teardowns/` artifacts.
- Do not author lessons or modify `curriculum.md`. Curriculum is Session D / Subsystem #4.
- Do not write Python or shell scripts. `knowledge/INDEX.md` regeneration is by-hand.
- Do not embed URLs or page numbers directly inside cheat sheets. All citations route through `reference/INDEX.md` by topic name.

## Verification gates

All of these must pass before Session B is marked complete:

1. **All 19 cheat sheets present** at the paths listed in §2.
2. **Every cheat sheet's front matter is valid** — has all six fields (`slug`, `category`, `tldr`, `prerequisites`, `references`, `next`); `slug` matches the filename; `category` is one of the five enum values; `tldr` is ≤25 words.
3. **Every `references` entry resolves** — semantically corresponds to a bullet under the matching `## ...` section of `reference/INDEX.md` (`Ableton Manual: <topic>` -> the Ableton manual section; `MPK Manual: <topic>` -> the MPK section). Spot-check by following each reference to its INDEX entry; verbatim string match is not required.
4. **Every `prerequisites` slug resolves** — points to a cheat sheet that exists in this commit.
5. **Every `next` slug resolves** — points to a cheat sheet that exists in this commit, OR is `null`.
6. **Every cheat sheet's body has all four sections** — `## TL;DR`, `## Cheat block`, `## Read this yourself`, `## See also` — and none is empty/trivial (≥3 bullets or a non-trivial paragraph in each).
7. **`knowledge/INDEX.md` exists** with one entry per cheat sheet (including `companion-mode.md`), grouped by subdirectory; each entry's TL;DR matches the source file's front-matter `tldr` field verbatim **except** for `companion-mode.md`, whose entry is hand-written (no front matter to derive from).
8. **`knowledge/ableton/companion-mode.md` is byte-identical** to Session A's committed version (`git diff` against Session A's commit shows no changes to this file).
9. **`knowledge/artists/` is empty** (no `.md` files inside).
10. **Spot check** — pick 3 random cheat sheets across different subdirectories; confirm Cheat block and Read-this-yourself sections both substantive (not placeholder).
