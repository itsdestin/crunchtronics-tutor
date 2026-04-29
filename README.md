# Crunchtronics Tutor

A personal music-production learning system for Destin — a long-running, taste-aware tutor that teaches Ableton Live 12 Lite and the Akai MPK Mini 4 in a top-down, genre-first way.

## What's in here

- **`CLAUDE.md`** — how Claude operates inside this project (read this first when opening a session).
- **`docs/superpowers/specs/2026-04-26-master-architecture.md`** — the canonical architecture spec. The "why" behind every folder and decision.
- **`docs/superpowers/plans/`** — implementation plans, one per session/cycle.
- **`reference/`** — vendor manuals (PDFs, gitignored) and a topic-to-page index.
- **`knowledge/`** — Claude-authored cheat sheets organized by theory / Ableton / MPK / genres / artists.
- **`taste/`** — Spotify pull artifacts + Claude-authored taste profile.
- **`teardowns/`** — per-track teardowns (analysis + narrative + Lite-floor build recipe).
- **`sessions/`** — logs of every learning session.
- **`scripts/`** — local CLI tools (Spotify pull, audio enrichment, librosa analysis, etc.).
- **`curriculum.md`** — living lesson plan; Claude updates it at the end of every session.

Secrets live outside this repo at `C:\Users\desti\.crunchtronics-tutor-secrets\` (Spotify OAuth, etc.).

## How to run a session

1. Open Claude Code in this directory: `C:\Users\desti\crunchtronics-tutor\`.
2. Claude reads `CLAUDE.md` and the master spec automatically when needed.
3. Ask away — about theory, Ableton navigation, the MPK, a track you want to deconstruct, or what to learn next.

This is a local-only project. No remote, no cloud, no telemetry. Everything stays on your machine.
