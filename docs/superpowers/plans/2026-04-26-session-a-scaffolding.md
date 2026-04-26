# Session A Scaffolding — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Session A of the Crunchtronics Tutor project: bootstrap the repo, acquire and index the reference vault, define the reactive-companion policy. Three subsystems in build order — #1 Project Shell → #2 Reference Vault → #9 Reactive Companion.

**Architecture:** Three sequential phases, each producing a self-contained verifiable subsystem. Phase 1 creates the folder skeleton, CLAUDE.md, .gitignore, git repo, and the external secrets directory. Phase 2 acquires vendor manuals (curl-then-fallback) and authors INDEX.md + ONLINE.md. Phase 3 writes the companion-mode policy; live MCP testing is explicitly deferred until windows-control is installed. One git commit per phase.

**Tech Stack:** Bash (Git Bash on Windows), curl for HTTP downloads, PowerShell `Invoke-WebRequest` as fallback if curl misbehaves on a specific URL, git for version control. No code runtime.

**Read first (mandatory):**
- `docs/superpowers/specs/2026-04-26-master-architecture.md`
- `docs/superpowers/specs/subsystems/01-project-shell.md`
- `docs/superpowers/specs/subsystems/02-reference-vault.md`
- `docs/superpowers/specs/subsystems/09-reactive-companion.md`
- `docs/superpowers/plans/2026-04-26-master-orchestration.md` (Session A section)

---

## File structure (everything Session A creates or modifies)

**Project root** (`C:\Users\desti\crunchtronics-tutor\`):

- Create: `CLAUDE.md`, `README.md`, `curriculum.md`, `.gitignore`
- Create: `reference/.gitkeep`, `knowledge/theory/.gitkeep`, `knowledge/ableton/.gitkeep`, `knowledge/mpk-mini-4/.gitkeep`, `knowledge/genres/.gitkeep`, `knowledge/artists/.gitkeep`, `taste/.gitkeep`, `teardowns/.gitkeep`, `sessions/.gitkeep`, `scripts/.gitkeep`
- Create: `reference/INDEX.md`, `reference/ONLINE.md`
- Create (conditional): `reference/HOW-TO-FETCH.md` (only if any manual download fails)
- Create (gitignored, downloaded): `reference/mpk-mini-4-user-guide.pdf` (best-effort; if URL changes, falls back to HOW-TO-FETCH)
- Create: `knowledge/ableton/companion-mode.md`
- Modify (Phase 3, only if Phase 1's wording needs polish): `CLAUDE.md`

**Outside the repo** (`C:\Users\desti\.crunchtronics-tutor-secrets\`):

- Create: `spotify.json`, `audio-enrichment.json`, `README.txt`

---

## Phase 1: Subsystem #1 — Project Shell

Spec: `docs/superpowers/specs/subsystems/01-project-shell.md`

### Task 1.1: Verify git author identity is configured

**Files:** none

- [ ] **Step 1: Check global git config**

Run:

```bash
git config --global user.name
git config --global user.email
```

Expected: both return non-empty values.

- [ ] **Step 2: If either is empty, STOP and ask the user**

Surface the issue to Destin with this ask:

> "Git's global `user.name` and/or `user.email` aren't set. What name and email should I use for commits in this project? (I can set them as repo-local config, or you can set them globally yourself.)"

Wait for user response before moving to Task 1.2. If the user provides a name/email and asks for repo-local config, defer that to Task 1.8 — at this step you only confirm what to use.

### Task 1.2: Create the folder skeleton + .gitkeep files

**Files:**
- Create: `reference/.gitkeep`, `knowledge/theory/.gitkeep`, `knowledge/ableton/.gitkeep`, `knowledge/mpk-mini-4/.gitkeep`, `knowledge/genres/.gitkeep`, `knowledge/artists/.gitkeep`, `taste/.gitkeep`, `teardowns/.gitkeep`, `sessions/.gitkeep`, `scripts/.gitkeep`

- [ ] **Step 1: Create all directories and .gitkeep files**

Run from `/c/Users/desti/crunchtronics-tutor`:

```bash
mkdir -p reference knowledge/theory knowledge/ableton knowledge/mpk-mini-4 knowledge/genres knowledge/artists taste teardowns sessions scripts
touch reference/.gitkeep knowledge/theory/.gitkeep knowledge/ableton/.gitkeep knowledge/mpk-mini-4/.gitkeep knowledge/genres/.gitkeep knowledge/artists/.gitkeep taste/.gitkeep teardowns/.gitkeep sessions/.gitkeep scripts/.gitkeep
```

- [ ] **Step 2: Verify all .gitkeep files exist**

Run:

```bash
ls reference/.gitkeep knowledge/theory/.gitkeep knowledge/ableton/.gitkeep knowledge/mpk-mini-4/.gitkeep knowledge/genres/.gitkeep knowledge/artists/.gitkeep taste/.gitkeep teardowns/.gitkeep sessions/.gitkeep scripts/.gitkeep
```

Expected: all 10 paths listed (no errors).

### Task 1.3: Write .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Write .gitignore**

Write to `/c/Users/desti/crunchtronics-tutor/.gitignore`:

```
.secrets/
sessions/*.draft.md
scripts/__pycache__/
scripts/.venv/
*.log
.DS_Store
reference/*.pdf
```

- [ ] **Step 2: Verify exact content**

```bash
cat .gitignore
```

Expected: 7 lines, matching exactly the content above (no trailing blank line required, no leading whitespace).

### Task 1.4: Write CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md content**

Write to `/c/Users/desti/crunchtronics-tutor/CLAUDE.md`:

```markdown
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
- `docs/superpowers/plans/` — implementation plans

Secrets live **outside** this repo at `C:\Users\desti\.crunchtronics-tutor-secrets\`.

## Pointers

- Master architecture: `docs/superpowers/specs/2026-04-26-master-architecture.md`
- Orchestration plan: `docs/superpowers/plans/2026-04-26-master-orchestration.md`
```

- [ ] **Step 2: Verify file exists and has the expected sections**

Run:

```bash
test -f CLAUDE.md && grep -c "^## " CLAUDE.md
```

Expected: prints `4` (four `##` sections: What this project is, How Claude operates here, Folder map, Pointers).

### Task 1.5: Write README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md content**

Write to `/c/Users/desti/crunchtronics-tutor/README.md`:

```markdown
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

Secrets live outside this repo at `C:\Users\desti\.crunchtronics-tutor-secrets\` (Spotify OAuth, GetSongBPM API key, etc.).

## How to run a session

1. Open Claude Code in this directory: `C:\Users\desti\crunchtronics-tutor\`.
2. Claude reads `CLAUDE.md` and the master spec automatically when needed.
3. Ask away — about theory, Ableton navigation, the MPK, a track you want to deconstruct, or what to learn next.

This is a local-only project. No remote, no cloud, no telemetry. Everything stays on your machine.
```

- [ ] **Step 2: Verify**

```bash
test -f README.md && wc -l README.md
```

Expected: file exists with at least 20 lines.

### Task 1.6: Write curriculum.md

**Files:**
- Create: `curriculum.md`

- [ ] **Step 1: Write curriculum.md content**

Write to `/c/Users/desti/crunchtronics-tutor/curriculum.md`:

```markdown
---
last_updated: 2026-04-26T00:00:00Z
next: lesson-001
---

# Curriculum

> Schema reference: `docs/superpowers/specs/2026-04-26-master-architecture.md` §7.3.

## lesson-001: <to be authored by Subsystem #4 — Curriculum & Nudges> [blocked]
- Why blocked: depends on Subsystem #7 (Taste Profile) and Subsystem #3 (Knowledge Base)
- This is a schema placeholder; real lessons land in Session D.
```

- [ ] **Step 2: Verify front matter and placeholder lesson**

```bash
head -4 curriculum.md
grep -c "^## lesson-" curriculum.md
```

Expected: head shows the YAML front matter starting with `---`; grep returns `1`.

### Task 1.7: Create the secrets directory + placeholder files

**Files:**
- Create: `C:\Users\desti\.crunchtronics-tutor-secrets\spotify.json`
- Create: `C:\Users\desti\.crunchtronics-tutor-secrets\audio-enrichment.json`
- Create: `C:\Users\desti\.crunchtronics-tutor-secrets\README.txt`

- [ ] **Step 1: Create the directory if missing**

```bash
mkdir -p /c/Users/desti/.crunchtronics-tutor-secrets
```

- [ ] **Step 2: Idempotent placeholder writes for the two JSON files**

For each of `spotify.json` and `audio-enrichment.json`: if the file does NOT exist OR exists with content `{}` (or empty), write `{}`. If it exists with non-empty non-`{}` content, leave it untouched.

```bash
for f in spotify.json audio-enrichment.json; do
  path="/c/Users/desti/.crunchtronics-tutor-secrets/$f"
  if [ ! -s "$path" ] || [ "$(cat "$path" | tr -d '[:space:]')" = "{}" ]; then
    echo '{}' > "$path"
    echo "wrote placeholder: $path"
  else
    echo "preserved existing: $path"
  fi
done
```

- [ ] **Step 3: Always (re)write README.txt**

Write to `/c/Users/desti/.crunchtronics-tutor-secrets/README.txt`:

```
Crunchtronics Tutor — secrets
=============================

This directory holds credentials for the Crunchtronics Tutor project, kept
OUTSIDE the repo so they never end up in git.

Project: C:\Users\desti\crunchtronics-tutor\
Master spec: docs/superpowers/specs/2026-04-26-master-architecture.md  (§4 + §11 #1, #2)

Files
-----

spotify.json
  Holds the Spotify Developer app's OAuth credentials and refresh token.
  Populated by Subsystem #5 (Spotify Integration). Expected shape (subject
  to that subsystem's spec):
    {
      "client_id":     "...",
      "client_secret": "...",
      "refresh_token": "...",
      "redirect_uri":  "..."
    }

audio-enrichment.json
  Holds the GetSongBPM API key (and any future enrichment-service keys).
  Populated by Subsystem #6 (Audio Feature Enrichment). Expected shape
  (subject to that subsystem's spec):
    {
      "getsongbpm_api_key": "..."
    }

Do not commit these files anywhere. The .gitignore inside the project
repo also excludes a defensive ".secrets/" folder, but that's belt-and-
suspenders — the real protection is keeping the files at this path.
```

- [ ] **Step 4: Verify**

```bash
ls -la /c/Users/desti/.crunchtronics-tutor-secrets/
```

Expected: shows `spotify.json`, `audio-enrichment.json`, `README.txt`.

### Task 1.8: Initialize git and make the first commit

**Files:** none new

- [ ] **Step 1: git init**

```bash
cd /c/Users/desti/crunchtronics-tutor
git init
```

Expected: prints "Initialized empty Git repository in …/crunchtronics-tutor/.git/".

- [ ] **Step 2: Set repo-local user identity if Task 1.1 surfaced an unset global**

Only do this if Task 1.1 found global config unset and the user provided values then. Otherwise skip to Step 3.

```bash
git config user.name "<name from user>"
git config user.email "<email from user>"
```

- [ ] **Step 3: Stage everything currently in the repo**

```bash
git add -A
git status
```

Expected: `git status` shows the planning docs (`docs/superpowers/specs/2026-04-26-master-architecture.md`, the orchestration plan, the three subsystem specs, this plan), the new scaffolding files (`CLAUDE.md`, `README.md`, `curriculum.md`, `.gitignore`), and the `.gitkeep` files — all staged. No `*.pdf` files staged.

- [ ] **Step 4: Create the initial commit**

```bash
git commit -m "init: project scaffold + master spec + Session A subsystem specs"
```

Expected: commit succeeds. `git log --oneline` shows one entry with that message.

### Task 1.9: Phase 1 verification gate

**Files:** none

- [ ] **Step 1: Confirm root-level files**

```bash
test -f CLAUDE.md && test -f README.md && test -f curriculum.md && test -f .gitignore && echo "OK"
```

Expected: prints `OK`.

- [ ] **Step 2: Confirm all §4 directories exist**

```bash
for d in reference knowledge/theory knowledge/ableton knowledge/mpk-mini-4 knowledge/genres knowledge/artists taste teardowns sessions scripts docs/superpowers/specs/subsystems docs/superpowers/plans; do
  test -d "$d" || echo "MISSING: $d"
done
echo "done"
```

Expected: prints only `done` (no MISSING lines).

- [ ] **Step 3: Confirm initial commit**

```bash
git log --oneline
```

Expected: shows exactly one commit titled `init: project scaffold + master spec + Session A subsystem specs`.

- [ ] **Step 4: Confirm secrets directory**

```bash
test -f /c/Users/desti/.crunchtronics-tutor-secrets/spotify.json && test -f /c/Users/desti/.crunchtronics-tutor-secrets/audio-enrichment.json && test -f /c/Users/desti/.crunchtronics-tutor-secrets/README.txt && echo "OK"
```

Expected: prints `OK`.

- [ ] **Step 5: Smoke test — gitignore actually excludes PDFs in `reference/`**

```bash
echo "dummy" > reference/test.pdf
git status --short reference/
rm reference/test.pdf
```

Expected: `git status --short` for `reference/` shows nothing (the dummy PDF is ignored). After deletion, no leftover files.

**Phase 1 complete. Subsystem #1 ships. Proceed to Phase 2.**

---

## Phase 2: Subsystem #2 — Reference Vault

Spec: `docs/superpowers/specs/subsystems/02-reference-vault.md`

### Task 2.1: Attempt Akai MPK Mini 4 user guide download

**Files:**
- Create (target): `reference/mpk-mini-4-user-guide.pdf`

- [ ] **Step 1: Locate the canonical download URL**

The MPK Mini 4 product page is `https://www.akaipro.com/mpk-mini-4`. The user guide PDF is reachable from there. Use WebFetch on the product page to find the current direct PDF URL (Akai sometimes restructures their CDN paths).

If WebFetch identifies a direct `.pdf` link in the page's downloads section, use that URL. If it doesn't, defer the download to the user-handoff fallback (Task 2.4).

- [ ] **Step 2: Attempt download with curl**

If a direct PDF URL was found:

```bash
cd /c/Users/desti/crunchtronics-tutor
curl -L --fail --max-time 60 -o reference/mpk-mini-4-user-guide.pdf "<URL from Step 1>"
```

Expected: file is downloaded; curl returns exit code 0.

If curl fails or returns a non-PDF (HTML error page), delete the bad file and fall through to Task 2.4 for this manual:

```bash
rm -f reference/mpk-mini-4-user-guide.pdf
```

- [ ] **Step 3: Validate it's a real PDF**

```bash
head -c 4 reference/mpk-mini-4-user-guide.pdf | od -c | head -1
```

Expected: shows `%   P   D   F` (the four magic bytes `%PDF`). If not, delete the file and fall through to Task 2.4 for this manual.

### Task 2.2: Attempt MPK Mini 4 MIDI implementation chart download (optional)

**Files:**
- Create (target, optional): `reference/mpk-mini-4-midi-chart.pdf`

- [ ] **Step 1: Determine whether a separate MIDI chart exists**

The MIDI implementation chart is often integrated into the user guide as an appendix rather than a standalone PDF. Use WebFetch on the Akai MPK Mini 4 product page to look for a separately-linked MIDI chart PDF.

If a separate file is linked, attempt download with curl as in Task 2.1. If not (chart is in the user guide), skip this task — note it in INDEX.md as part of the user guide.

- [ ] **Step 2: Validate (only if downloaded)**

If a separate file was downloaded, validate the PDF magic bytes as in Task 2.1 Step 3. Delete and skip if invalid.

### Task 2.3: Attempt Ableton Live 12 reference manual download (expected fail)

**Files:** none expected

- [ ] **Step 1: Try the manual landing page**

The Ableton Live 12 manual is at `https://www.ableton.com/en/live-manual/12/`. It is HTML, not a downloadable PDF. Attempt anyway as a sanity check:

```bash
curl -L --fail --max-time 30 -o /tmp/ableton-test.pdf "https://www.ableton.com/en/live-manual/12/"
head -c 4 /tmp/ableton-test.pdf | od -c | head -1
```

Expected: either curl fails OR magic bytes are not `%PDF` (the response is HTML). Delete `/tmp/ableton-test.pdf`.

- [ ] **Step 2: Treat as expected fallback**

The Ableton manual is the canonical "online-only" source. INDEX.md will reference URL anchors instead of page numbers; ONLINE.md will list the live HTML manual as the authoritative source. No HOW-TO-FETCH entry is needed for this manual — its acquisition path *is* the live URL.

### Task 2.4: Write reference/HOW-TO-FETCH.md (only if any acquisition failed)

**Files:**
- Create (conditional): `reference/HOW-TO-FETCH.md`

- [ ] **Step 1: Decide whether the file is needed**

Only create this file if Task 2.1 (and/or Task 2.2 when applicable) failed. If both Akai downloads succeeded, skip the entire task.

- [ ] **Step 2: Write the file**

Write to `/c/Users/desti/crunchtronics-tutor/reference/HOW-TO-FETCH.md`. Include only the manuals that failed. Template:

```markdown
# Manuals to fetch manually

> Auto-acquisition by curl failed for the items below. Please grab them via your browser and save into `reference/`.

## Akai MPK Mini 4 user guide

- **URL:** <last attempted URL>
- **Save as:** `reference/mpk-mini-4-user-guide.pdf`
- **How:** open the product page at https://www.akaipro.com/mpk-mini-4, scroll to the "Downloads" section, click the user guide link, save the PDF here.

(Repeat the block for any other failed manual. Omit blocks for manuals that downloaded successfully.)
```

- [ ] **Step 3: Verify (if created)**

```bash
test -f reference/HOW-TO-FETCH.md && head -1 reference/HOW-TO-FETCH.md
```

Expected: prints `# Manuals to fetch manually`.

### Task 2.5: Write reference/INDEX.md

**Files:**
- Create: `reference/INDEX.md`

- [ ] **Step 1: Author entries by reading the actual sources**

For each acquired source, read the material and produce at least 10 topic→location entries at chapter / major-topic granularity. Sources to index:

1. **Akai MPK Mini 4 user guide** (PDF — read it via the Read tool; identify chapter/major-topic boundaries; record page numbers from the PDF's own page numbering, not absolute file pages, since manuals often have front-matter).
2. **Ableton Live 12 reference manual** (HTML — fetch the table of contents at `https://www.ableton.com/en/live-manual/12/` via WebFetch; pick the chapter URLs; for a beginner-relevant subset prioritize: Session view, Arrangement view, MIDI tracks, Audio tracks, Mixer, Browser, Simpler, Drum Rack, Warping, Recording, Effects overview, Setup & I/O).

If the MPK MIDI implementation chart was downloaded as a separate PDF (Task 2.2), index it as its own section in INDEX.md.

- [ ] **Step 2: Write INDEX.md**

Write to `/c/Users/desti/crunchtronics-tutor/reference/INDEX.md`. Format:

```markdown
# Reference Index

> Topic → page (PDF) or URL anchor (online).

## Akai MPK Mini 4 user guide  (reference/mpk-mini-4-user-guide.pdf)

- <topic 1> → p. <N>
- <topic 2> → p. <N>
- ... (at least 10 entries)

## Ableton Live 12 reference manual  (online: https://www.ableton.com/en/live-manual/12/)

- <topic 1> → <full URL anchor>
- <topic 2> → <full URL anchor>
- ... (at least 10 entries)
```

Replace the angle-bracket placeholders with real entries from Step 1. Keep entries terse (3–8 words for the topic name).

- [ ] **Step 3: Verify minimum-entry counts**

```bash
awk '/^## /{section=$0; count=0; next} /^- /{count++} END{print count}' reference/INDEX.md
```

Easier: count entries per section by hand or with:

```bash
grep -c "^- " reference/INDEX.md
```

Expected: ≥ 20 total entries (10 per section × 2 sections, minimum). If a separate MIDI chart was indexed, expect ≥ 30.

### Task 2.6: Write reference/ONLINE.md

**Files:**
- Create: `reference/ONLINE.md`

- [ ] **Step 1: Verify each URL returns 200 + matches its title**

For each of the 5 seed URLs below, run WebFetch and confirm the page loads and the title roughly matches:

| Title | URL |
|---|---|
| Ableton Live 12 reference manual | https://www.ableton.com/en/live-manual/12/ |
| Ableton Learn Live | https://www.ableton.com/en/live/learn-live/ |
| Akai MPK Mini 4 product page | https://www.akaipro.com/mpk-mini-4 |
| Camelot Wheel reference | https://mixedinkey.com/camelot-wheel/ |
| Ableton Live 12 release notes | https://www.ableton.com/en/release-notes/live-12/ |

If a URL has changed (404 or significantly different content), find a current equivalent before adding it. Don't ship a stale URL.

- [ ] **Step 2: Write ONLINE.md**

Write to `/c/Users/desti/crunchtronics-tutor/reference/ONLINE.md`:

```markdown
# Online reference resources

> Curated authoritative resources for Ableton Live 12 and the Akai MPK Mini 4. Each URL was verified at last-verified date below.

| Title | URL | What it's good for | Last verified |
|---|---|---|---|
| Ableton Live 12 reference manual | https://www.ableton.com/en/live-manual/12/ | Authoritative live manual (HTML, current) | 2026-04-26 |
| Ableton Learn Live | https://www.ableton.com/en/live/learn-live/ | Official video tutorials for beginners | 2026-04-26 |
| Akai MPK Mini 4 product page | https://www.akaipro.com/mpk-mini-4 | Product specs, downloads, support | 2026-04-26 |
| Camelot Wheel reference | https://mixedinkey.com/camelot-wheel/ | Standard Camelot notation reference | 2026-04-26 |
| Ableton Live 12 release notes | https://www.ableton.com/en/release-notes/live-12/ | What's in 12 vs prior versions | 2026-04-26 |
```

If any URL needed substitution in Step 1, swap it in here. Optionally add up to 2 more authoritative resources if Step 1 surfaced obvious gaps (e.g., Splice docs landing page).

- [ ] **Step 3: Verify**

```bash
grep -c "^| " reference/ONLINE.md
```

Expected: ≥ 6 (one header row + ≥ 5 data rows). The separator row `|---|---|---|---|` does not start with `| ` (no space after `|`), so it doesn't count.

### Task 2.7: Phase 2 verification gate + commit

**Files:** none new

- [ ] **Step 1: Confirm INDEX.md and ONLINE.md present and meet minimums**

```bash
test -f reference/INDEX.md && test -f reference/ONLINE.md && echo "OK"
```

Expected: prints `OK`.

- [ ] **Step 2: Confirm acquired manuals are present (or HOW-TO-FETCH.md exists)**

```bash
ls reference/*.pdf 2>/dev/null
test -f reference/HOW-TO-FETCH.md && echo "HOW-TO-FETCH present" || echo "no HOW-TO-FETCH (all downloads succeeded)"
```

Expected: at least one of (`reference/*.pdf` exists, `reference/HOW-TO-FETCH.md` exists).

- [ ] **Step 3: Confirm no `*.pdf` files staged**

```bash
git status --short
```

Expected: no lines for `reference/*.pdf` (gitignore working). The PDFs are present on disk but not in `git status`.

- [ ] **Step 4: Spot-check 3 INDEX.md entries**

Pick 3 entries from INDEX.md. For each:
- If PDF entry: open the PDF to the listed page (use the Read tool with the `pages:` parameter), confirm the page covers the listed topic.
- If URL entry: WebFetch the URL, confirm the page covers the listed topic.

If any spot-check fails, fix the entry in INDEX.md before committing.

- [ ] **Step 5: Stage + commit Phase 2 deliverables**

```bash
git add reference/INDEX.md reference/ONLINE.md
[ -f reference/HOW-TO-FETCH.md ] && git add reference/HOW-TO-FETCH.md
git commit -m "feat(reference): subsystem #2 — INDEX, ONLINE, manual acquisition"
git log --oneline | head -3
```

Expected: 2 commits in log.

**Phase 2 complete. Subsystem #2 ships. Proceed to Phase 3.**

---

## Phase 3: Subsystem #9 — Reactive Companion

Spec: `docs/superpowers/specs/subsystems/09-reactive-companion.md`

### Task 3.1: Verify CLAUDE.md already contains the companion-mode paragraph

**Files:** none modified yet

- [ ] **Step 1: Check for the paragraph**

```bash
grep -i "Companion-mode preference" CLAUDE.md
```

Expected: returns a non-empty line (the bullet that #1 wrote in Task 1.4 starting with `- **Companion-mode preference.**`).

- [ ] **Step 2: If missing, fix it**

If grep returns nothing, the paragraph was dropped during Phase 1. Open CLAUDE.md and re-add it under "How Claude operates here" before proceeding (use the wording from Task 1.4 Step 1).

### Task 3.2: Author knowledge/ableton/companion-mode.md

**Files:**
- Create: `knowledge/ableton/companion-mode.md`

- [ ] **Step 1: Write the policy doc**

Write to `/c/Users/desti/crunchtronics-tutor/knowledge/ableton/companion-mode.md`:

```markdown
# Companion mode — policy

Companion mode is how Claude reads Destin's Ableton screen during a session and gives directions oriented to what's actually on screen. It is on-demand, intent-inferred, and never autonomous.

## 1. What companion mode is

On-demand only, intent-inferred, never autonomous, never predictive. Claude does not watch Ableton in the background. Claude does not capture without an explicit invitation from Destin.

## 2. When it triggers

Claude reads intent from Destin's natural signals — there is no canned trigger-phrase catalog. Examples of signals (illustrative, not exhaustive):

- "I can't find…" / "where is the…" / "what's this thing on my screen"
- Visible frustration with menus or device chains
- Questions about Ableton state that Claude can't answer from memory alone (e.g., "is my clip quantized?" or "what device do I have open?")

If Claude is unsure whether a question warrants companion mode, Claude asks rather than capturing.

## 3. The policy (load-bearing)

When companion mode is warranted, Claude:

1. **Offers first.** "Want me to take a look?" — never captures unprompted.
2. **On assent, captures the Ableton window** via the windows-control MCP.
3. **Cross-references the Reference Vault.** Looks up the relevant entry in `reference/INDEX.md` and cites the page number or URL anchor when applicable. This is a hard expectation, not optional polish.
4. **Responds in terms of what's actually on Destin's screen.** "You're in Session view; the Simpler is on track 2; click the magnifying glass at the top-right of the device."
5. **Closes the loop.** "Did that work, or should I look again?" — invites a follow-up capture if directions don't land.

## 4. What Claude will not do

- No unprompted captures.
- No autonomous mouse/keyboard actions that produce work on Destin's behalf.
- No continuous monitoring loops or background watchers.
- No companion mode for non-Ableton windows unless Destin explicitly requests it.

## 5. Reference-vault tie-in

Every companion-mode answer that maps to a documented concept SHOULD cite `reference/INDEX.md` (page number for PDFs, URL anchor for the live HTML manual). This is the integration glue between this subsystem (#9) and the Reference Vault (#2).

## 6. Tool-surface assumption

This policy is written against an abstract windows-control MCP that exposes at minimum:

- **List windows** — return a list of open application windows so Claude can find the Ableton one.
- **Capture window** — given a window identifier (or "active"), return an image Claude can see.

When the actual MCP is installed, this section gets updated with the concrete tool names. That update is a search-and-replace, not a redesign.

## Status

- **Doc gate:** ready (this file exists, CLAUDE.md companion-mode paragraph in place, reference-vault citation requirement explicit above).
- **Live gate:** **deferred** — runs the moment a windows-control MCP is installed. Test: with Ableton open, Destin says something like "I'm stuck — I can't find where to add a Simpler." Confirm Claude (a) offers to look, (b) captures after assent, (c) cites the Reference Vault, (d) gives directions oriented to the actual screen state. When the gate passes, append a "live gate passed: <date>" line to this Status section.
```

- [ ] **Step 2: Verify file structure**

```bash
test -f knowledge/ableton/companion-mode.md && grep -c "^## " knowledge/ableton/companion-mode.md
```

Expected: file exists; grep returns `7` (six numbered sections + Status).

- [ ] **Step 3: Verify reference-vault citation requirement is explicit**

```bash
grep -i "cite.*reference.*vault\|reference/INDEX.md" knowledge/ableton/companion-mode.md | wc -l
```

Expected: ≥ 2 matches (the requirement appears in section 3 and section 5 at minimum).

### Task 3.3: Polish CLAUDE.md companion-mode paragraph (only if needed)

**Files:**
- Modify (conditional): `CLAUDE.md`

- [ ] **Step 1: Decide whether polish is needed**

Read the companion-mode paragraph from CLAUDE.md (the bullet starting with `**Companion-mode preference.**`). Compare to the policy doc just written. If the CLAUDE.md paragraph is already accurate and points to `knowledge/ableton/companion-mode.md`, skip this task — no edit needed.

- [ ] **Step 2: Edit only if needed**

If the wording is stale (e.g., implies pattern-matching triggers, omits the reference-vault citation, or omits the pointer), use Edit to refine. Keep the paragraph short (single bullet under "How Claude operates here").

### Task 3.4: Phase 3 verification gate + commit

**Files:** none new

- [ ] **Step 1: Confirm doc gate**

```bash
test -f knowledge/ableton/companion-mode.md && grep -q "Companion-mode preference" CLAUDE.md && echo "OK"
```

Expected: prints `OK`.

- [ ] **Step 2: Confirm live gate is recorded as deferred**

```bash
grep -i "live gate.*deferred" knowledge/ableton/companion-mode.md
```

Expected: returns a non-empty line (the Status section's live-gate entry).

- [ ] **Step 3: Stage + commit Phase 3 deliverables**

```bash
git add knowledge/ableton/companion-mode.md
git diff --cached --name-only | grep -q CLAUDE.md && git add CLAUDE.md
git commit -m "feat(companion): subsystem #9 — companion-mode policy + CLAUDE.md tie-in"
git log --oneline | head -5
```

Expected: 3 commits in log (init + reference + companion).

**Phase 3 complete. Subsystem #9 ships (with live gate explicitly deferred until windows-control MCP is installed).**

---

## Session A done criteria

- [ ] Phase 1 verification gate passed.
- [ ] Phase 2 verification gate passed.
- [ ] Phase 3 doc gate passed; live gate recorded as deferred.
- [ ] `git log --oneline` shows 3 commits.
- [ ] Update orchestration plan: mark Session A `[x]` and check off all 3 step boxes.
- [ ] Note for next session: Sessions B and C are now unblocked and may run in parallel.

---

## Self-review (run by plan author after writing)

1. **Spec coverage:** Phase 1 maps to all artifacts in `01-project-shell.md` (CLAUDE.md, README.md, curriculum.md, .gitignore, folder skeleton, secrets dir, git init). Phase 2 maps to all artifacts in `02-reference-vault.md` (manual acquisition with hybrid fallback, INDEX.md, ONLINE.md, HOW-TO-FETCH.md). Phase 3 maps to all artifacts in `09-reactive-companion.md` (companion-mode.md with all 6 sections + Status, CLAUDE.md companion-mode paragraph). ✓

2. **Placeholder scan:** No "TBD" / "TODO" / "implement later" / "fill in details" / "add error handling" patterns. The angle-bracket placeholders in Task 2.5's INDEX.md template are intentional fill-in-the-blanks for an artifact whose content depends on what was actually downloaded — that's not a plan placeholder, it's a template the implementer fills in by reading the manuals. Same for Task 2.4's HOW-TO-FETCH.md template (only created if a download fails). The curriculum.md placeholder lesson node in Task 1.6 is a deliberate user-visible schema marker, also not a plan TBD. ✓

3. **Type/identifier consistency:** Commit messages used: `init: project scaffold + master spec + Session A subsystem specs` (Phase 1), `feat(reference): subsystem #2 — INDEX, ONLINE, manual acquisition` (Phase 2), `feat(companion): subsystem #9 — companion-mode policy + CLAUDE.md tie-in` (Phase 3). File paths consistent throughout (forward slashes, project root assumed at `/c/Users/desti/crunchtronics-tutor`). The "companion-mode paragraph" in CLAUDE.md is referred to by the same anchor (`Companion-mode preference`) in Tasks 1.4, 3.1, and 3.4. ✓

4. **Cross-phase ordering:** Each phase ends with a verification gate before commit. Phase 2 depends on Phase 1's `.gitignore` (PDF exclusion) and folder skeleton. Phase 3 depends on Phase 1's CLAUDE.md (companion-mode paragraph) and Phase 2's INDEX.md (citation target). Order is enforced by the gates. ✓
