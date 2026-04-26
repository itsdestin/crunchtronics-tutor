# Crunchtronics Tutor — Master Orchestration Plan

> **Revised 2026-04-26 to a 5-session structure.** Originally specified 9 sequential cycles (one per subsystem); this revision groups cohesive subsystems into 5 sessions to compress wall-clock time without diluting focus on the work that needs it. See "Why 5 sessions" below.

> **For agentic workers:** This is an **orchestration plan**, not a code-implementation plan. Each session below launches a fresh Claude Code session that runs ONE combined brainstorm → spec → plan → execute cycle covering all subsystems in its scope. Specs are still per-subsystem (one file under `docs/superpowers/specs/subsystems/` per master-spec subsystem number), but the brainstorm, the implementation plan, and the execution are unified within the session. Do NOT split a session across multiple Claude Code invocations and do NOT add subsystems beyond the session's listed scope.

**Goal:** Schedule and hand off the 9 subsystems of the Crunchtronics Tutor system, in the build order from the master architecture spec, as 5 grouped brainstorm → spec → plan → execute cycles.

**Tech stack (orchestration):** Claude Code CLI; superpowers skills (`brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`).

**Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md` — every session must read this first.

---

## Why 5 sessions instead of 9

The original plan ran one session per subsystem (9 total). Safe but slow. This revision collapses to 5 sessions by grouping subsystems that share their kind of work, while keeping the heaviest subsystems solo:

- **Session A** folds three lightweight scaffolding subsystems (Project Shell, Reference Vault, Reactive Companion) into one session — none authors substantial code or content; they're docs, downloads, and CLAUDE.md edits.
- **Session B** is the Knowledge Base alone — content authoring quality matters too much to dilute.
- **Session C** combines two sibling Python-script subsystems (Spotify, Audio Enrichment) that share a venv, a secrets dir, and a data flow.
- **Session D** combines Taste Profile and Curriculum & Nudges, both of which are largely Claude reasoning over user data → prose, and where one feeds directly into the other.
- **Session E** is the Teardown Pipeline alone — most ambitious subsystem, deserves full focus.

After Session A, sessions B and C are independent and can run in parallel (different days, different sessions). Session D requires both. Session E requires C at minimum.

---

## How to use this plan

For each session below:

1. Open a fresh Claude Code session in `C:\Users\desti\crunchtronics-tutor\`.
2. Copy the **Hand-off prompt** from the session and paste it as the first message.
3. Claude runs ONE `superpowers:brainstorming` for the session (designing all included subsystems together but preserving their boundaries), writes ONE spec file PER subsystem under `docs/superpowers/specs/subsystems/`, runs ONE `superpowers:writing-plans` to produce ONE combined implementation plan with phases per subsystem, then implements in the listed build order.
4. **Verification gates within a session:** fully verify each subsystem (run the listed verification checks) before starting the next. Do not interleave subsystems.
5. When all subsystems in the session are shipping (working, tested, committed), mark the session `[x]` and move on.

**Build order at a glance:**

```
Session A (Foundation)            Session B (Learning surface)
[Subsystems #1, #2, #9]   ───►    [Subsystem #3]
                                       ║
                          ───►    Session C (Data pull)
                                  [Subsystems #5, #6]
                                       ║
                                       ▼
                                  Session D (Personalization → curriculum)
                                  [Subsystems #7, #4]
                                       ║
                                       ▼
                                  Session E (Capstone)
                                  [Subsystem #8]
```

**Parallelization rules:**
- Session A must complete before any other session starts.
- Sessions B and C can run in parallel (different days OK; they share no inputs/outputs).
- Session D requires B + C complete (curriculum reads knowledge content + taste profile).
- Session E requires C complete (Subsystem #8 minimum dep is #6); ideally D is also done so teardown recipes can integrate with the curriculum.

---

## Sessions

### Session A: Scaffolding (Subsystems #1, #2, #9)

- **Phase:** Foundation
- **Depends on:** nothing
- **Blocks:** every other session
- **Estimated length:** 1 session
- **Status:** [ ] not started

**Hand-off prompt (paste verbatim into a fresh Claude Code session):**

```
I'm starting Session A of the Crunchtronics Tutor project: Scaffolding.

This session ships three subsystems in build order: #1 Project Shell → #2 Reference Vault → #9 Reactive Companion. Order matters: the shell must exist before manuals land in reference/, and the companion's CLAUDE.md edits go on top of the CLAUDE.md #1 just wrote.

READ FIRST (mandatory): docs/superpowers/specs/2026-04-26-master-architecture.md

================================================================
SUBSYSTEM #1 — Project Shell
================================================================
Master-spec sections: §4 (folder layout), §5.1 #1 (one-liner contract), §11 default decisions #5 (git remote = local-only) and #9 (CLAUDE.md scope = project + Claude pedagogy).

Does:
- Creates the folder skeleton from §4 (every directory mentioned, all initially empty except docs/superpowers/specs which already has the master spec)
- Writes CLAUDE.md encoding: project purpose, the pedagogy conventions from §11 (top-down framing, check curriculum before suggesting next concept, prefer reactive companion over verbal directions when Ableton is open), and pointers to the master spec
- Writes README.md — human-facing overview
- Writes initial curriculum.md with the §7.3 schema (header front matter + a single placeholder lesson node so the schema is visible)
- Writes .gitignore — at minimum: .secrets/, sessions/*.draft.md, scripts/__pycache__/, scripts/.venv/, *.log, .DS_Store
- Runs `git init`, makes initial commit
- Creates the secrets directory at C:\Users\desti\.crunchtronics-tutor-secrets\ with empty placeholder files (spotify.json, audio-enrichment.json) and a README.txt explaining what goes in each

================================================================
SUBSYSTEM #2 — Reference Vault
================================================================
Master-spec sections: §5.1 #2 (one-liner contract), §1 + §2 (target user — Ableton Lite, MPK Mini 4).

Does:
- Acquires authoritative reference materials and stores them under reference/:
  - Ableton Live 12 reference manual (PDF) — from ableton.com
  - Akai MPK Mini 4 user manual (PDF) — from akaipro.com
  - MPK Mini 4 MIDI implementation chart (often a separate PDF or appendix)
- Writes reference/INDEX.md — topic-to-page-number index for both manuals so Claude can cite specific pages mid-session ("see Ableton Reference p. 312 on Simpler envelopes")
- Writes reference/ONLINE.md — curated authoritative online resources (Ableton's official lessons URLs, Akai's MPK Mini 4 product page, Splice docs if relevant). Each entry: title, URL, what it's good for, last verified date. Verify URLs at indexing time.

Notes:
- INDEX.md is the load-bearing artifact. Without it, Claude scans an entire 800-page PDF to find anything. At minimum, one entry per major topic in each manual.

================================================================
SUBSYSTEM #9 — Reactive Companion
================================================================
Master-spec sections: §5.1 #9 (on-demand only, no autonomous monitoring), §3.4 (must not short-circuit user learning).

Does:
- Defines conventions and prompts for using the windows-control MCP (already installed in user's environment) to read Ableton's UI state on demand
- Writes knowledge/ableton/companion-mode.md — when to invoke companion mode, what screen-capture invocations look like, how to give click-by-click guidance
- Updates CLAUDE.md (the one #1 just wrote) to encode: "When the user is in Ableton and asks how to do X, prefer 'show me your Ableton window' (companion mode) over verbal-only directions; never invoke screen capture unprompted"
- Writes a small set of tested invocation patterns ("look at my Ableton mixer," "read what device I have open," "where am I in the arrangement view") with the exact MCP calls for each. Test end-to-end with Ableton actually open before declaring done.

Notes:
- This subsystem may ship as docs + CLAUDE.md edits + a few MCP recipes with no code at all. That's fine.

================================================================
CROSS-SUBSYSTEM BOUNDARIES — do NOT do any of these
================================================================
- Do not author knowledge/ content beyond knowledge/ableton/companion-mode.md (the rest is Session B / Subsystem #3)
- Do not write any Python scripts (Sessions C and E)
- Do not write taste/ or teardowns/ files
- Do not author curriculum lessons beyond the §7.3 schema placeholder
- Do not push the repo to a remote — local-only per §11 #5
- Do not implement an autonomous screen-capture watcher (companion is on-demand only)
- Do not host or redistribute the manuals — personal copies for local reference

================================================================
WORKFLOW
================================================================
1. Run superpowers:brainstorming ONCE for the whole session. Design all three subsystems together but preserve their boundaries — the brainstorm output should clearly delineate which decisions belong to which subsystem.
2. Write THREE per-subsystem spec files:
   - docs/superpowers/specs/subsystems/01-project-shell.md
   - docs/superpowers/specs/subsystems/02-reference-vault.md
   - docs/superpowers/specs/subsystems/09-reactive-companion.md
3. Run superpowers:writing-plans ONCE to produce one combined implementation plan with three numbered phases (one per subsystem, in build order #1 → #2 → #9).
4. Implement in build order. Verify each subsystem (per the verification gates below) before moving to the next.
```

**Verification gates (run before starting the next subsystem within this session):**
- After **#1 Project Shell:** `CLAUDE.md`, `README.md`, `curriculum.md`, `.gitignore` present; all §4 directories present; `git log` shows one initial commit; secrets directory exists at `C:\Users\desti\.crunchtronics-tutor-secrets\`.
- After **#2 Reference Vault:** both PDFs present in `reference/`; `INDEX.md` exists with topic-to-page mappings for both; `ONLINE.md` exists with at least 5 verified entries.
- After **#9 Reactive Companion:** `knowledge/ableton/companion-mode.md` exists with concrete invocation patterns; `CLAUDE.md` updated with companion-mode preference; one end-to-end test recorded showing the MCP returns useful Ableton screen content.

- [ ] **Step 1:** Open fresh session, paste hand-off prompt, complete the cycle
- [ ] **Step 2:** All three verification gates above passed
- [ ] **Step 3:** Mark session `[x]` and unblock Sessions B + C

---

### Session B: Knowledge Base (Subsystem #3)

- **Phase:** Learning surface
- **Depends on:** Session A
- **Parallel with:** Session C
- **Estimated length:** 1 session for seed content + ongoing iterative expansion during normal tutoring sessions
- **Status:** [ ] not started

**Hand-off prompt:**

```
I'm starting Session B of the Crunchtronics Tutor project: Knowledge Base (Subsystem #3).

READ FIRST (mandatory): docs/superpowers/specs/2026-04-26-master-architecture.md

Your scope is Subsystem #3 only, defined in the master spec at:
- §5.1 #3 (one-liner contract — Claude authors the cheat sheets under user direction)
- §11 default decisions #7, #8, #9 (top-down framing; hardware/software learned together; CLAUDE.md pedagogy already lives in #1)
- §1 + §2 (target user profile — beginner, EDM, MPK Mini 4, Ableton Lite/Intro)

What this subsystem does:
- Establishes the cheat sheet template (consistent format: TL;DR → details → links into Reference Vault → "next concept" pointer). Every knowledge file follows this template
- Authors seed content for each knowledge subdirectory:
  - knowledge/theory/ — start with: rhythm-basics.md, intervals.md, scales-and-keys.md, chord-construction.md, the-camelot-wheel.md
  - knowledge/ableton/ — start with: session-vs-arrangement-view.md, the-browser.md, midi-vs-audio-tracks.md, the-mixer.md, simpler-basics.md, drum-rack-basics.md (NOTE: companion-mode.md already exists from Session A — do not overwrite)
  - knowledge/mpk-mini-4/ — start with: pads-vs-keys-vs-knobs.md, mapping-pads-to-drum-rack.md, mpk-program-editor.md, transport-controls.md
  - knowledge/genres/ — start with one cheat sheet per identified subgenre from user's stated taste anchors (riddim/dubstep, melodic dubstep, tech house, bass house). Each cheat sheet covers: typical BPM, typical structure, signature sound design, key reference artists. Genre cheat sheets reference theory primitives (top-down framing per §11 #7)
  - knowledge/artists/ — leave empty initially; this directory gets populated by Session D (Subsystem #7) once taste profile reveals which specific artists matter
- Writes knowledge/INDEX.md — a flat index linking to every cheat sheet by topic

What this subsystem must NOT do:
- Do not download or index any external manuals (that was Session A / Subsystem #2)
- Do not author artist pages preemptively — wait for taste profile data
- Do not author lessons or curriculum content (that's Session D / Subsystem #4)

Run superpowers:brainstorming, save spec to docs/superpowers/specs/subsystems/03-knowledge-base.md, then writing-plans, then implement.

Notes:
- Top-down framing means: when you write knowledge/genres/tech-house.md, it explains tech house structure first and references theory primitives only when they're load-bearing. Theory primitives like knowledge/theory/intervals.md exist as references, not standalone curriculum.
- Hardware and software live in separate subdirectories but mpk content references ableton content where they touch (mapping pads to a drum rack is both an MPK and an Ableton operation).
```

**Verification:** `knowledge/INDEX.md` exists; each subdirectory has at least the seed files listed; every cheat sheet follows the established template; no `knowledge/artists/` content yet; `knowledge/ableton/companion-mode.md` from Session A is intact and unmodified.

- [ ] **Step 1:** Open fresh session, paste hand-off prompt, complete the cycle
- [ ] **Step 2:** Verification passed
- [ ] **Step 3:** Mark session `[x]`

---

### Session C: Data pull (Subsystems #5, #6)

- **Phase:** Personalization (data acquisition)
- **Depends on:** Session A
- **Parallel with:** Session B
- **Estimated length:** 1–2 sessions (OAuth can be finicky on first attempt)
- **Status:** [ ] not started

**Hand-off prompt:**

```
I'm starting Session C of the Crunchtronics Tutor project: Data pull.

This session ships two subsystems in build order: #5 Spotify Integration → #6 Audio Feature Enrichment. Order matters: #5's output schema (taste/playlists.json) is #6's input — lock the schema in the brainstorm before #6 starts implementation.

READ FIRST (mandatory): docs/superpowers/specs/2026-04-26-master-architecture.md

================================================================
SUBSYSTEM #5 — Spotify Integration
================================================================
Master-spec sections: §3.1 (CRITICAL: Spotify deprecated audio-features and audio-analysis for new apps as of Nov 27, 2024 — do NOT call those endpoints); §5.1 #5 (one-liner contract); §6 (data flow — your output is taste/playlists.json, consumed by #6); §7.1 (output format: raw Spotify shape, dumped verbatim); §11 default decisions #1 (user registers app), #12 (weekly schedule).

Does:
- Documents the Spotify Developer app registration steps the user must perform once (registration page URL, what scopes to request, what redirect URI to set)
- Implements OAuth 2.0 Authorization Code with PKCE (or refresh-token flow if simpler) for a personal-use app
- Writes the CLI script under scripts/ (you decide language during brainstorm — Python with `spotipy` is the obvious default; document why)
- The script:
  - Reads OAuth tokens from C:\Users\desti\.crunchtronics-tutor-secrets\spotify.json
  - Fetches all user playlists (own + followed) and their full track lists
  - Writes the result verbatim to taste/playlists.json
  - Is idempotent — re-runs overwrite cleanly
  - Refreshes the OAuth token automatically when expired
- Sets up a /schedule entry for weekly automated runs (configurable cadence, default weekly per §11 #12)

Notes:
- OAuth dance requires user interaction (browser redirect for first auth). Document this clearly so the user knows what to expect on first run.
- Test against the user's actual Spotify account end-to-end before declaring done — fetch a real playlist, confirm taste/playlists.json populates correctly.

================================================================
SUBSYSTEM #6 — Audio Feature Enrichment
================================================================
Master-spec sections: §3.1 (CRITICAL: this subsystem exists because Spotify's audio-features endpoint is deprecated for new apps); §5.1 #6 (one-liner contract); §6 (data flow — input: taste/playlists.json from #5; output: taste/tracks.csv consumed by #7 and #8); §7.2 (REQUIRED OUTPUT SCHEMA — exact column list, including genre column added in spec self-review); §11 default decision #2 (GetSongBPM as primary).

Does:
- Implements a CLI script under scripts/ that:
  - Reads taste/playlists.json
  - Dedupes tracks (a track in 5 playlists is one row in the csv)
  - Reads existing taste/tracks.csv if present, identifies rows missing data
  - Queries GetSongBPM (or agreed alternative) for BPM and key per missing row
  - Computes Camelot notation from standard key (small lookup table — exactly 24 entries)
  - Records the source per row (e.g., "getsongbpm")
  - Writes/updates taste/tracks.csv with the schema from §7.2
  - Respects API rate limits — does NOT batch-fire requests
- Designs the architecture so the enrichment service is swappable behind a clean interface (one function per service, all returning the same internal record shape) — the source column is the audit trail

Notes:
- You may discover GetSongBPM doesn't cover everything (genre, energy, danceability). That's OK — leave those columns empty, document the gap, note that future enrichment service swap (or addition of a second service) can fill them. The csv schema accommodates partial data per §7.2.
- The Camelot lookup is well-defined music theory: 24 keys (12 major + 12 minor) → 12 numbers + A/B suffix. Just code the table; don't compute it from theory.

================================================================
CROSS-SUBSYSTEM BOUNDARIES — do NOT do any of these
================================================================
- Do not call audio-features or audio-analysis Spotify endpoints (deprecated; will return 403). All audio characterization happens in #6 via a different API.
- Do not transform Spotify data shape inside #5 — store raw Spotify JSON. Schema-translation is #6's job.
- Do not modify taste/playlists.json from inside #6 (that's #5's owned file).
- Do not write taste/profile.md (Session D / Subsystem #7).
- Do not commit secrets — secrets land at C:\Users\desti\.crunchtronics-tutor-secrets\, already excluded by Session A's .gitignore. Verify nothing OAuth-related lands inside the repo.
- Do not embed API keys in code — read from C:\Users\desti\.crunchtronics-tutor-secrets\audio-enrichment.json.

================================================================
WORKFLOW
================================================================
1. Run superpowers:brainstorming ONCE. Design both subsystems together — lock the playlists.json schema first since #6 depends on it, then design #6.
2. Write TWO per-subsystem spec files:
   - docs/superpowers/specs/subsystems/05-spotify-integration.md
   - docs/superpowers/specs/subsystems/06-audio-enrichment.md
3. Run superpowers:writing-plans ONCE for one combined implementation plan with two numbered phases (#5 first, then #6).
4. Implement in build order. Verify each subsystem (per the gates below) before moving to the next.
```

**Verification gates (run before starting the next subsystem within this session):**
- After **#5 Spotify Integration:** `scripts/` has the pull script; `taste/playlists.json` populated with real data; `/schedule` entry exists; OAuth tokens live outside the repo and refresh works.
- After **#6 Audio Enrichment:** `scripts/` has the enrichment script; `taste/tracks.csv` populated with real data covering BPM and key for as many tracks as the service has; schema matches §7.2 exactly; the enricher runs incrementally (re-runs only fetch missing rows).

- [ ] **Step 1:** Open fresh session, paste hand-off prompt, complete the cycle
- [ ] **Step 2:** Both verification gates passed
- [ ] **Step 3:** Mark session `[x]`

---

### Session D: Personalization → curriculum (Subsystems #7, #4)

- **Phase:** Guided structure
- **Depends on:** Sessions B + C
- **Parallel with:** none
- **Estimated length:** 1 session + ongoing regeneration
- **Status:** [ ] not started

**Hand-off prompt:**

```
I'm starting Session D of the Crunchtronics Tutor project: Personalization → curriculum.

This session ships two subsystems in build order: #7 Taste Profile → #4 Curriculum & Nudges. Order matters: #7 produces taste/profile.md and knowledge/artists/* pages, both of which #4 reads to bias curriculum content.

READ FIRST (mandatory): docs/superpowers/specs/2026-04-26-master-architecture.md

================================================================
SUBSYSTEM #7 — Taste Profile
================================================================
Master-spec sections: §5.1 #7 (one-liner contract); §6 (data flow — input: taste/tracks.csv; outputs: taste/profile.md; informs #4 curriculum content + can populate knowledge/artists/ pages); §7.4 (OUTPUT FORMAT — prose, no schema; suggested sections listed).

Does:
- Defines the workflow Claude follows to read taste/tracks.csv and write taste/profile.md (mostly a prompted-Claude task, not heavy code)
- Writes any helper scripts needed to compute aggregates (BPM histograms, top-N artist counts, key distribution) — small Python likely
- Defines the trigger conditions (per §8 cadence: regenerate when tracks.csv row count changes ≥10%, or on demand)
- Writes the first taste/profile.md from real data
- Identifies the top N artists in the user's taste and authors knowledge/artists/<slug>.md pages for each (per §5.1 #3 — artist pages get added once taste profile reveals who matters). Each page covers: known Splice packs (search and verify), preset packs, signature techniques, notable interviews/breakdowns

Notes:
- This subsystem leans heavily on Claude generating prose. The "code" is small — aggregation helpers and a prompt template. Don't over-engineer.
- For artist resource verification, web search is the right tool. Don't claim a Splice pack exists without checking.

================================================================
SUBSYSTEM #4 — Curriculum & Nudges
================================================================
Master-spec sections: §5.1 #4 (one-liner contract); §6 (data flow — reads knowledge/ + taste/profile.md; writes/updates curriculum.md; drives nudges); §7.3 (OUTPUT FORMAT — curriculum.md schema with front matter and lesson nodes); §8 (cadence — Claude updates curriculum end of every session; nudges fire M/W/F mornings); §11 default decisions #4 (M/W/F nudges), #7 (top-down), #8 (hardware/software together), #11 (sessions/ logs feed back).

Does:
- Designs the lesson-node format inside curriculum.md (Session A wrote a placeholder; this subsystem writes the real schema and seed lessons)
- Writes the initial taste-aware curriculum: Lesson 1 begins with MPK + Ableton fundamentals (per §11 #8 they're learned together); subsequent lessons biased toward the user's taste profile (e.g., if profile shows tech house dominance, sidechain compression and four-on-the-floor groove construction come early)
- Defines the convention by which Claude updates curriculum.md at the end of every session — what gets marked done, what gets unblocked, what "next:" pointer gets advanced
- Writes the sessions/ log convention — what Claude writes at end of each session, where it goes (sessions/YYYY-MM-DD-<topic>.md per §7.6)
- Sets up /schedule entries for M/W/F morning nudges. The nudge agent reads curriculum.md, sees what's "next" or "blocked," and surfaces a nudge to the user (delivery channel: chosen during brainstorm — desktop notification via windows-control? markdown file in inbox? terminal printout on next session start? decide and document)

Notes:
- The curriculum is a living document. The first version is a starting point; it will be edited every session. Don't over-plan it.
- For nudge delivery: read the user's preferences before designing. They may prefer notifications, or they may prefer "next session greets you with the nudge." Ask during brainstorm.

================================================================
CROSS-SUBSYSTEM BOUNDARIES — do NOT do any of these
================================================================
- Do not modify taste/tracks.csv from inside #7 (Subsystem #6 owns it)
- Do not author knowledge/ content beyond the artist pages #7 specifically writes (that's Session B / Subsystem #3)
- Do not author teardown content (Session E / Subsystem #8)
- Do not fabricate artist information — if you can't verify a Splice pack exists for an artist, say "no known pack" or "unverified"
- Do not run a generative loop that auto-writes new lessons unprompted — curriculum updates happen at session boundaries, not in the background

================================================================
WORKFLOW
================================================================
1. Run superpowers:brainstorming ONCE. Design both subsystems together — establish the profile schema first (since #4 reads it), then the curriculum schema and nudge delivery.
2. Write TWO per-subsystem spec files:
   - docs/superpowers/specs/subsystems/07-taste-profile.md
   - docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md
3. Run superpowers:writing-plans ONCE for one combined implementation plan with two numbered phases (#7 first, then #4).
4. Implement in build order. Verify each subsystem (per the gates below) before moving to the next.
```

**Verification gates (run before starting the next subsystem within this session):**
- After **#7 Taste Profile:** `taste/profile.md` exists with all suggested sections from §7.4; aggregation helper scripts present in `scripts/`; at least 3 `knowledge/artists/<slug>.md` pages authored for top artists with verified resource info.
- After **#4 Curriculum & Nudges:** `curriculum.md` schema documented and seeded with at least 8 taste-aware lessons; `/schedule` entry exists for M/W/F nudges; sessions/ log convention documented in CLAUDE.md.

- [ ] **Step 1:** Open fresh session, paste hand-off prompt, complete the cycle
- [ ] **Step 2:** Both verification gates passed
- [ ] **Step 3:** Mark session `[x]` — unblocks Session E

---

### Session E: Teardown pipeline (Subsystem #8)

- **Phase:** Capstone
- **Depends on:** Session C minimum; ideally also Session D
- **Parallel with:** none
- **Estimated length:** 2–3 sessions (most ambitious subsystem)
- **Status:** [ ] not started

**Hand-off prompt:**

```
I'm starting Session E of the Crunchtronics Tutor project: Teardown Pipeline (Subsystem #8).

READ FIRST (mandatory): docs/superpowers/specs/2026-04-26-master-architecture.md

Your scope is Subsystem #8 only, defined in the master spec at:
- §3.2 (constraint: recipes target Lite floor, with Intro+ note callouts)
- §3.5 (constraint: master-first; stems/multitracks not obtainable for commercial EDM)
- §5.1 #8 (one-liner contract)
- §6 (data flow — inputs: tracks.csv from #6 + user-supplied audio file; outputs: teardowns/<slug>/{analysis.json, teardown.md, recipe.md})
- §7.5 (OUTPUT FORMATS for the three artifacts)
- §11 default decisions #6 (librosa), #10 (yt-dlp default for audio acquisition)

What this subsystem does:
- Implements the audio acquisition step:
  - yt-dlp wrapper (default) — user supplies a YouTube URL; script downloads audio, normalizes to a working format
  - Manual file drop fallback — user puts an audio file in teardowns/<slug>/source.<ext>
- Implements the analysis step using librosa:
  - Tempo (BPM)
  - Beat grid (beat times)
  - Section detection (using librosa's structural segmentation — agglomerative or HPSS-based)
  - Chroma summary
  - MFCC summary
  - Saves to teardowns/<slug>/analysis.json per §7.5
- Implements the teardown narrative step (Claude reads analysis.json + the artist's knowledge/artists/<slug>.md if it exists + relevant knowledge/genres/<slug>.md, then writes teardowns/<slug>/teardown.md)
- Implements the recipe step (Claude writes teardowns/<slug>/recipe.md targeting Lite floor with Intro+ note callouts where extra tracks/sends would help). Recipe links to artist resource page when applicable
- Defines the user invocation — how does the user say "teardown this track"? Decide during brainstorm. Likely: a slash command, or a documented prompt template, or a script entry point

What this subsystem must NOT do:
- Do not generate .als files (deferred per §12 — would require Suite + Max for Live)
- Do not attempt to obtain stems or multitracks (per §3.5 — not realistically obtainable)
- Do not store DRM-protected audio — yt-dlp on YouTube only; do not break Spotify DRM
- Do not run librosa in the background on a watch loop — teardowns are user-triggered per §8

Run superpowers:brainstorming, save spec to docs/superpowers/specs/subsystems/08-teardown-pipeline.md, then writing-plans, then implement.

Notes:
- librosa on Windows: install carefully. The recommended path is conda + a clean environment. Document the installation steps in scripts/README.md so future installs are reproducible.
- For yt-dlp: pin a specific version in requirements; the tool changes frequently. Document how to update it.
- Test end-to-end with one of the user's actual taste-anchor tracks (e.g., a John Summit or Subtronics release) before declaring done. Verify the recipe makes sense when read by a beginner.
- If you discover that librosa's section detection is unreliable for the user's genres, document it honestly and consider an alternative (Essentia, msaf) before committing to a fragile pipeline.
```

**Verification:** end-to-end test passes — pick one taste-anchor track, run teardown, confirm `teardowns/<slug>/{analysis.json, teardown.md, recipe.md}` all populate; recipe targets Lite floor with at least one Intro+ note; recipe is comprehensible to a beginner.

- [ ] **Step 1:** Open fresh session, paste hand-off prompt, complete the cycle
- [ ] **Step 2:** Verification passed
- [ ] **Step 3:** Mark session `[x]` — full system complete

---

## Done criteria (whole system)

- [ ] All 5 sessions above marked `[x]` (which means all 9 subsystems shipping)
- [ ] User has actually used the system for at least one full Ableton session and the curriculum has at least one `[done]` lesson
- [ ] User has run at least one teardown end-to-end and used the recipe to build something in Ableton

## Self-review (run by plan author after writing this revision)

**1. Subsystem coverage:** All 9 master-spec subsystems are present across the 5 sessions: A=#1+#2+#9, B=#3, C=#5+#6, D=#7+#4, E=#8. ✓

**2. Decision coverage:** Every decision in master spec §11 is referenced in at least one session's hand-off prompt. ✓

**3. Build-order consistency:** Session ordering preserves master spec §9 build order. Within each session, subsystems are ordered to respect their data-flow dependencies (#1→#2→#9, #5→#6, #7→#4). ✓

**4. Dependency clarity:** Each session's "Depends on" line names the prior sessions that must complete first; verification gates inside multi-subsystem sessions name the order explicitly. ✓

**5. Boundary preservation:** Every "must NOT do" boundary from the original 9-task plan is preserved, redistributed into the appropriate session's cross-subsystem boundaries section. ✓

**6. Spec file mapping:** Every session lists the exact spec filenames it produces. The 9 spec files are distributed: A→01,02,09; B→03; C→05,06; D→07,04; E→08. No subsystem produces zero or two spec files. ✓

**7. Placeholder scan:** No "TBD," no "implement later," no "similar to Session N" — every hand-off prompt is self-contained and copy-pasteable. ✓
