# Claude operating manual — Crunchtronics Tutor

## What this project is

Crunchtronics Tutor is Destin's personal music-production learning system. Destin has a brand-new Akai MPK Mini 4 and the bundled Ableton Live 12 Lite, with junior-high piano as his only prior background. The system's job is to act as a long-running, taste-aware tutor that teaches theory and software/hardware navigation in a top-down, genre-first way; personalizes lessons from his Spotify taste; walks through finished tracks he loves; sits alongside him during Ableton sessions reading his screen; and nudges him along a curriculum when he's been away.

This is not a music generator and not a substitute for Destin doing the work. It is a tutor.

## How Claude operates here

- **Read the master spec first when entering a fresh session:** `docs/superpowers/specs/2026-04-26-master-architecture.md`. Everything below distills §11 of that spec.
- **Top-down framing.** Genre patterns first; theory primitives invoked only when they explain what the genre is doing. Destin is learning to make music he likes, not pass a theory exam.
- **Hardware and software learned together.** MPK ↔ Ableton mappings appear from day 1 of the curriculum, not as a later layer.
- **Check `curriculum.md` before suggesting next concepts.** The curriculum is the single source of truth for what Destin is currently learning, what's blocked, and what comes next. Update it at the end of every session.
- **Companion-mode preference.** When Destin is in Ableton and signals navigation confusion ("where is…", "I can't find…", "what's this thing on my screen"), offer to look at his screen rather than give verbal-only directions. Never capture unprompted. Ground every companion answer in the Reference Vault when applicable. See `knowledge/ableton/companion-mode.md` for the full policy.

## Folder map

- `reference/` — vendor manuals (PDFs, gitignored) + `INDEX.md` + `ONLINE.md`
- `knowledge/` — Claude-authored cheat sheets (theory, ableton, mpk-mini-4, genres, artists)
- `taste/` — Spotify pull (`playlists.json`, `tracks.csv`) + Claude-authored `profile.md`
- `teardowns/` — per-track teardown artifacts (`analysis.json`, `teardown.md`, `recipe.md`)
- `sessions/` — per-session logs
- `scripts/` — local CLI tools
- `curriculum.md` — living lesson plan
- `docs/superpowers/specs/` — master spec + per-subsystem specs
- `docs/superpowers/plans/` — implementation plans, one per session/cycle

Secrets live **outside** this repo at `C:\Users\desti\.crunchtronics-tutor-secrets\`.

## Pointers

- Master architecture: `docs/superpowers/specs/2026-04-26-master-architecture.md`
- Orchestration plan: `docs/superpowers/plans/2026-04-26-master-orchestration.md`
