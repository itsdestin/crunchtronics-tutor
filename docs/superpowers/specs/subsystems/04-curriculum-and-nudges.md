# Subsystem #4 — Curriculum & Nudges

- **Date:** 2026-04-28
- **Status:** Spec drafted (Session D, Phase 2)
- **Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md`
- **Master-spec sections referenced:** §5.1 #4 (one-liner contract), §6 (data flow — reads `knowledge/` + `taste/profile.md`; writes/updates `curriculum.md`; drives nudges), §7.3 (`curriculum.md` schema — **extended** by this spec; see §3.3), §7.6 (`sessions/YYYY-MM-DD-<topic>.md` shape — **formalized** by this spec; see §3.7), §8 (refresh cadence — **overridden** for nudges; see §2), §11 default decisions #4 (M/W/F nudge cadence — **overridden**; see §2), #7 (top-down framing), #8 (hardware/software together), #11 (sessions/ logs feed back)
- **Companion specs:**
  - `docs/superpowers/specs/subsystems/07-taste-profile.md` (this subsystem's input producer; sibling in Session D)
  - `docs/superpowers/specs/subsystems/03-knowledge-base.md` (this subsystem cross-references its cheat sheets)
- **Session:** D (combined with #7)
- **Build order:** Second subsystem in Session D; depends on #7 having produced `taste/profile.md` and the 14 artist pages.
- **Depends on:**
  - Subsystem #3 (Knowledge Base — lessons reference its cheat sheets)
  - Subsystem #7 (Taste Profile — `profile_anchors` field drives genre-ordering of seed lessons)
- **Blocks:** none directly. Subsystem #8 (Teardown Pipeline) is independent of curriculum but optionally cross-references lesson IDs in teardown recipes.

## 1. One-liner contract

Owns `curriculum.md` (the living lesson plan), `sessions/*.md` (per-session logs), and the conventions Claude follows to update both at session boundaries. Nudges are computed inline at session start from `curriculum.md` when the most recent session log is older than a configurable staleness threshold; there is no scheduled job. The seed curriculum is taste-aware via `taste/profile.md`'s `profile_anchors`.

## 2. Master-spec overrides

Two overrides, both rooted in the brainstorm decision to gate nudge delivery on session-start (option E3 of the Session D brainstorm).

### 2.1 Override of §11 #4 — Nudge cadence

- **Original default:** M/W/F mornings, configurable.
- **Overridden to:** **Session-start, when the most recent `sessions/*.md` log is ≥ 2 calendar days before today.** The threshold is configurable in `CLAUDE.md` (one line).
- **Reason:** `/schedule` runs **remote agents** that have no access to the local filesystem and therefore cannot write to a local `nudges/` file. The brainstorm rejected both Windows-Task-Scheduler-based local automation (E1, adds an OS-scheduler dependency for one feature) and remote-agent-plus-sync (E2, adds a network surface area). Since "next-session greeting" already gates delivery on Destin opening Claude Code, automating the timing gains nothing — the inline staleness check produces the same UX with zero new infrastructure. The cadence remains roughly equivalent: under regular use, "≥ 2 days since the last log" fires on the same days a M/W/F cron would have fired.

### 2.2 Override of §8 — Nudges row

- **Original:** "Nudges (#4) | M/W/F mornings via `/schedule`, configurable."
- **Overridden to:** "Nudges (#4) | Session-start when the most recent `sessions/*.md` log is ≥ 2 calendar days old; threshold configurable in `CLAUDE.md`."
- Same reason as §2.1.

The Session D verification gate in `docs/superpowers/plans/2026-04-26-master-orchestration.md` mentions "/schedule entry exists for M/W/F nudges" as a check; that gate is satisfied by the documented override and the absence of any `/schedule` entry — there is nothing to register. The implementation-plan author should mark that gate item complete-via-override rather than treating it as missing work.

## 3. What this subsystem does

### 3.1 Owns `curriculum.md`

The file's existence, location, schema (§3.3), update lifecycle (§3.4), and re-sync-to-profile behavior (§3.5) are this subsystem's responsibility. Session A wrote a placeholder; this subsystem replaces it with the real schema and the seed lessons (§3.6). Committed to git as a snapshot — every session-end update is a git diff.

### 3.2 Owns `sessions/*.md`

Per-session logs, one file per session, written at session end. Format defined in §3.7. Filename pattern `YYYY-MM-DD-<topic-slug>.md`. Per master spec §11 default #11, logs are kept forever — no rotation.

### 3.3 `curriculum.md` schema

Extends master spec §7.3's example with two additional front-matter fields and a tightened lesson-node template.

#### 3.3.1 Front matter

```yaml
---
last_updated: 2026-04-28T15:30:00Z      # ISO 8601 UTC; refreshed at every session-end update
next: lesson-001                         # ID of the active lesson to greet Destin with at session start
generated_from_profile: 2026-04-28T...Z  # Mirrors taste/profile.md's generated_at; drift signal
profile_anchors: [tech-house, melodic-dubstep, dubstep, bass-house]
---
```

- `last_updated` — set on every save by the session-end protocol (§3.4).
- `next` — the lesson ID currently in `[active]`. Schema invariant: exactly one lesson is `[active]` at any time, and `next` matches its ID. If no lesson is active (e.g., one was just `[done]`-ed and the dependent isn't yet unblocked), `next` is set to the first unblocked successor.
- `generated_from_profile` — copied from `taste/profile.md`'s `generated_at` at the time curriculum was last re-synced to the profile. Lets Claude detect "profile has been regenerated since curriculum was last updated against it" and offer a re-sync.
- `profile_anchors` — copied from `taste/profile.md`'s `profile_anchors` array, verbatim. Used by Claude to bias new lesson insertions and to detect when the anchor set has shifted (signal that genre order in the curriculum may need re-balancing).

#### 3.3.2 Lesson node template

Every lesson is one `## lesson-NNN: <title> [<status>]` block. ID format is zero-padded three-digit (`lesson-001` … `lesson-999`).

```markdown
## lesson-003: Sidechain compression in a tech-house drop [active]

- **Why next:** Profile shows a 124–128 BPM cluster + Disco Lines / John Summit
  dominance; sidechain is the single defining technique of the genre per
  knowledge/genres/tech-house.md.
- **Estimated time:** 45 min
- **Depends on:** lesson-001, lesson-002
- **Hardware:** MPK pads for kick/clap, MPK keys for bass.
- **Practice task:** In a fresh Ableton project, build the first 32-bar drop of a
  tech-house track with sidechain compression on the bass triggered by the kick.
  Aim for 3–6 dB of gain reduction. Reference: knowledge/genres/tech-house.md,
  knowledge/ableton/the-mixer.md.
- **Done criteria:**
  - [ ] Project at 126 BPM in C minor (or any 124–128 / minor key from your taste)
  - [ ] Kick on every beat, bass between kicks
  - [ ] Sidechain audibly pumping; meter shows ~3–6 dB GR
  - [ ] Saved at projects/tech-house-drop-01.als
- **Notes:** (Claude appends here at session end — what worked, what stuck, what to revisit)
```

Field-by-field:

- **Title** — short imperative or noun phrase describing the outcome, not the activity.
- **Status** — one of `[active]`, `[blocked]`, `[done]`, `[skipped]`. See §3.3.3.
- **Why next** / **Why blocked** — a one-sentence justification. For `[active]` and `[done]` lessons it explains why this lesson sits where it does in the order. For `[blocked]` lessons it identifies what unblocks it.
- **Estimated time** — round number in minutes; informs the nudge prose. Pick from the set `{15, 30, 45, 60, 90}` for v1 to keep the language stable.
- **Depends on** — comma-separated list of prior lesson IDs, or `none` for foundational lessons. A lesson is unblockable iff every ID in this list is `[done]`.
- **Hardware** — one line naming which MPK affordance(s) the practice task uses. Realizes master spec §11 #8 (hardware/software together from day 1). For lessons that don't touch the MPK, write `Hardware: not used in this lesson.`
- **Practice task** — 1–3 sentences describing what Destin actually does. Must reference at least one `knowledge/` cheat sheet by relative path.
- **Done criteria** — 3–5 markdown checkboxes. The only checkable items inside a lesson. Each criterion is an objectively verifiable artifact or state (a saved file, an audible result, a measurable parameter). Avoid subjective criteria like "feels right."
- **Notes** — initially empty. Claude appends 1–3 sentences per session about what was actually worked on. History accumulates here; never deleted.

#### 3.3.3 Status enum and invariants

Statuses: `[active]`, `[blocked]`, `[done]`, `[skipped]`.

Invariants enforced at every session-end update:

- Exactly one `[active]` lesson at any time, OR zero `[active]` lessons if all currently-unblocked lessons are `[done]` or `[skipped]` (hand-off state — `next` points to the next unblocked candidate, status `[blocked]` if none yet).
- Every `[blocked]` lesson has at least one ID in `Depends on` whose lesson is not `[done]`.
- Every `[done]` lesson has all `Done criteria` checkboxes marked `[x]`.
- `[done]` and `[skipped]` lessons are never re-opened. Re-doing material spawns a new lesson with a fresh ID.

### 3.4 End-of-session update protocol

Encoded in `CLAUDE.md` (§3.8). At every session end, before declaring done, Claude:

1. **Tick done-criteria.** For the active lesson, flip any `[ ]` boxes Destin completed during the session to `[x]`.
2. **Append to Notes.** 1–3 sentences on what was actually worked on, what stuck, what to revisit. Never overwrite previous notes — append.
3. **Advance status.** If all done-criteria for the active lesson are `[x]`, mark the lesson `[done]` and find the next unblocked successor (smallest-numbered `[blocked]` lesson whose `Depends on` list is now fully `[done]`). Set that lesson `[active]`, update `next:` in front matter.
4. **Spawn follow-up lessons.** If a question or topic came up that warrants its own lesson, draft a `[blocked]` lesson node at the bottom of the file with a clear `Depends on` and a stub `Practice task`. Don't write done-criteria yet — they get fleshed out when the lesson becomes active.
5. **Refresh `last_updated`.** Set to current UTC timestamp.
6. **Save.** No commit by Claude — the diff sits in working tree until Destin commits at his discretion (matching the pattern for `taste/tracks.csv` updates by Subsystem #6).

### 3.5 Re-sync to profile

When `taste/profile.md` is regenerated (Subsystem #7), `profile_anchors` may shift — e.g., `[tech-house, melodic-dubstep, dubstep, bass-house]` becomes `[melodic-dubstep, tech-house, dubstep, bass-house]`. On the next session start where Claude reads `curriculum.md`, if the file's `generated_from_profile` predates `taste/profile.md`'s `generated_at`, Claude:

1. Loads the new `profile_anchors`.
2. Walks `[blocked]` lessons (only) and considers reordering to match the new anchor order. `[active]` and `[done]` lessons are not touched.
3. May insert a new `[blocked]` lesson if the new anchors include a genre with no representation in the current `[blocked]` queue.
4. Updates `generated_from_profile` to match `taste/profile.md`'s `generated_at`.
5. Updates `profile_anchors` to match.
6. Surfaces the changes to Destin in chat: "I re-synced curriculum to the new taste profile — moved lesson-009 ahead of lesson-007 because melodic dubstep is now your top anchor. Want me to revert?"

Re-sync is automatic but reversible (Destin can say "revert" and Claude undoes within the same session).

### 3.6 Initial 12-lesson seed (8 fleshed + 4 stubs)

Implementation writes all 12 nodes into `curriculum.md` in the order below. Lessons 001–008 are fully fleshed per §3.3.2 (full done-criteria, practice task, references). Lessons 009–012 are stubs: title + status + `Depends on` + a one-sentence "Why blocked" only. They get fully fleshed when their dependency chain unblocks them, by which time the taste profile may have shifted.

#### Fleshed lessons

| ID | Title | Status (initial) | Genre angle | Hardware-software glue |
|---|---|---|---|---|
| lesson-001 | MPK ↔ Ableton first connection (transport + pads) | `[active]` | none — setup foundation | MPK USB → Ableton MIDI input → pads sound a Drum Rack |
| lesson-002 | Map MPK pads to Drum Rack, play kick + clap | `[blocked]` on 001 | groove primitives | knowledge/mpk-mini-4/mapping-pads-to-drum-rack.md |
| lesson-003 | Four-on-the-floor at 126 BPM | `[blocked]` on 002 | tech-house groove | MPK pads for kick/clap |
| lesson-004 | First sidechained bass — the tech-house signature | `[blocked]` on 003 | tech-house | MPK keys for bass; Compressor on bass track |
| lesson-005 | Pick a key from your taste, write a 4-bar hook | `[blocked]` on 004 | uses Camelot bias from profile | MPK keys; knowledge/theory/the-camelot-wheel.md |
| lesson-006 | Stack the groove — open hat + percussion loop | `[blocked]` on 005 | tech-house texture | tactile MPK pad work |
| lesson-007 | Session view → Arrangement view: intro / drop A / break / drop B | `[blocked]` on 006 | tech-house structure | knowledge/ableton/session-vs-arrangement-view.md |
| lesson-008 | Save and bounce your first complete short track (~2 min) | `[blocked]` on 007 | end of foundation arc | save to projects/, bounce to wav |

#### Stub lessons

| ID | Title | Status (initial) | Why stubbed |
|---|---|---|---|
| lesson-009 | Half-time dubstep pattern at 140 BPM | `[blocked]` on 008 | first tempo / groove switch — Subtronics / Zeds Dead territory |
| lesson-010 | Wobble bass in Operator | `[blocked]` on 009 | first synthesis-design lesson |
| lesson-011 | Melodic dubstep build — piano intro into a soft drop | `[blocked]` on 010 | Wooli / ILLENIUM territory |
| lesson-012 | Cross-genre tempo / key planning with the Camelot wheel | `[blocked]` on 011 | bridges back to taste profile, sets up DJ-adjacent thinking |

Schema invariant at write time: `[active]` count = 1 (lesson-001); `next: lesson-001`; all others `[blocked]`.

The order tech-house-first is justified by `taste/profile.md`'s data: the 124–128 BPM cluster combined with Disco Lines (12 tracks) and John Summit (5) is the strongest signal in the v1 data. If a future profile regen shifts `profile_anchors`, the §3.5 re-sync rule reorders the `[blocked]` queue — `[done]` lessons are sticky.

### 3.7 `sessions/YYYY-MM-DD-<topic-slug>.md` template

Formalizes master spec §7.6 into a small required template. Each session log starts with YAML front matter and four required sections.

```markdown
---
date: 2026-04-28
duration_min: 45
lessons_touched: [lesson-002, lesson-003]
---

# 2026-04-28 — First tech-house drop

## What we covered
- Quick recap of four-on-the-floor (lesson-002 done-criteria all ticked)
- Started lesson-003: walked through sidechain routing in Ableton's mixer

## Blockers hit
- Couldn't find the sidechain dropdown on the Compressor — used companion mode
  (knowledge/ableton/companion-mode.md), found it under the unfold arrow

## Curriculum updates
- lesson-002 → [done]
- lesson-003 → [active], 2 of 4 done-criteria ticked
- Notes appended to lesson-003

## Next session
- Finish lesson-003 done-criteria (3 and 4 — meter check, project save)
- If time: preview lesson-004 (kick + clap layering)
```

Field semantics:

- `date` — calendar date in `YYYY-MM-DD`. Must match the date in the filename.
- `duration_min` — integer minutes. Best-effort estimate.
- `lessons_touched` — array of lesson IDs that were active or referenced during the session. The one structured field — anything that reads `sessions/` for analytics later (e.g., a future "what did we cover this month" query) relies on this.

Topic slug rules: short, lowercase, hyphenated, ASCII (`first-tech-house-drop`, `wobble-bass-experiments`). Pick from what was actually worked on.

The four body sections are required; their headings are fixed. Body content is free-form prose / bullets at Claude's discretion.

### 3.8 Nudge mechanics

Implemented as Claude-side rules in `CLAUDE.md` (§3.10). No script, no scheduler.

#### 3.8.1 Staleness check

Before Claude's first response in any session:

1. List `sessions/*.md` (excluding `.gitkeep`).
2. Find the most recent by filename (lexicographic sort works because the format is `YYYY-MM-DD-<topic-slug>.md`).
3. Parse the date from the filename.
4. Compute calendar-day delta to today's date.
5. If no log exists yet **or** delta ≥ `nudge_staleness_threshold` (default 2 days, configurable in CLAUDE.md), generate a nudge per §3.8.2. Otherwise proceed normally without any nudge prefix.

The staleness threshold is the configurability knob from master spec §11 #4. Destin tweaks it by editing one line in CLAUDE.md.

#### 3.8.2 Nudge content rule

Exactly three sentences, in this order:

1. **Greeting + lesson identity.** "Welcome back — it's been [N] days. You're on `lesson-NNN: <title>`."
2. **Practice task + estimated time.** "Today's practice (~[E] min): [practice task summary in one clause]."
3. **Offer to redirect.** "Want to dive in, switch lessons, or just chat?"

No padding, no streak counters, no motivational copy. The three-sentence rule is the spec's nudge content contract; longer nudges drift toward pestering.

#### 3.8.3 What if no lesson is `[active]`?

If `next` points to a `[blocked]` lesson (the hand-off state from §3.3.3), the nudge says: "Welcome back — you finished lesson-NNN last session. The next lesson is `lesson-NNN: <title>` but it's blocked on [reason]. Want to unblock it, pick a different lesson, or just chat?"

### 3.9 Session-end ritual

When Destin signals end-of-session ("done for tonight", "wrap up", "see you tomorrow", "let's stop here", or similar), Claude:

1. Writes `sessions/YYYY-MM-DD-<topic-slug>.md` per §3.7.
2. Updates `curriculum.md` per §3.4.
3. Confirms in chat: "Logged today's session and updated curriculum. lesson-NNN is `[active]` with X done-criteria left." or similar.

The session log is the artifact that drives the next session's staleness check (§3.8.1) — skipping the log breaks the nudge mechanism.

### 3.10 `CLAUDE.md` edits

Append a new section after the existing "## Audio enrichment" / "## Taste profile" sections:

```markdown
## Curriculum & nudges

The living lesson plan is `curriculum.md`. Schema reference:
`docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md`. Per-session
logs live in `sessions/YYYY-MM-DD-<topic-slug>.md` (template in §3.7 of that
spec).

**Session-start nudge.** Before your first response in any session, list
`sessions/*.md` (excluding `.gitkeep`) and find the most recent by filename.
Parse the date from the filename. If no log exists or the delta to today is
≥ the nudge staleness threshold below, lead your first reply with a
3-sentence nudge per §3.8.2 of the spec: lesson identity, practice task +
time, offer to redirect. Skip the nudge if the most recent log is within
the threshold.

**Nudge staleness threshold:** 2 calendar days. (Adjust here to retune.)

**Session-end ritual.** When Destin signals end-of-session, write
`sessions/YYYY-MM-DD-<topic-slug>.md` per §3.7 of the spec and update
`curriculum.md` per the §3.4 end-of-session protocol. Confirm both in
chat. Do not commit — leave the diff in the working tree.

**Profile drift.** When you read `curriculum.md`, compare its
`generated_from_profile` front-matter to `taste/profile.md`'s `generated_at`.
If the profile is newer, run the §3.5 re-sync rule (reorder `[blocked]`
lessons to the new anchor order; insert lessons for newly-anchored genres
if missing). Surface the changes to Destin and offer to revert.

This subsystem overrides master spec §11 #4 and §8's nudge row — see
`docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md` §2.
```

## 4. What this subsystem must NOT do

- **No `/schedule` entry.** Per §2.1, nudges are inline at session start. Do not register a remote agent.
- **No Windows Task Scheduler / cron / file-watcher** that automates curriculum or nudge updates. The brainstorm rejected E1 explicitly.
- **No modification of `taste/profile.md`** or `knowledge/artists/*.md`. Owned by Subsystem #7. This subsystem reads `taste/profile.md`'s front matter only.
- **No modification of `taste/tracks.csv`** or `taste/playlists.json`. Owned by #6 / #5.
- **No modification of `knowledge/genres/*.md`, `knowledge/theory/*.md`, `knowledge/ableton/*.md`, `knowledge/mpk-mini-4/*.md`** during curriculum updates. Lessons reference these via path; do not edit them.
- **No re-opening of `[done]` or `[skipped]` lessons.** Re-doing material spawns a new lesson ID per §3.3.3.
- **No deletion of session logs.** Logs are append-only, kept forever per master spec §11 default #11.
- **No automatic git commits** by Claude. Updates land in the working tree; Destin commits at his discretion.
- **No nudges longer than 3 sentences** (§3.8.2). Padding violates the contract.
- **No fabrication.** If `taste/profile.md` is missing or stale, surface it and ask — do not invent `profile_anchors`.

## 5. Verification gate

Before declaring this subsystem complete:

- [ ] `curriculum.md` exists with the §3.3 schema (front matter populated; `next: lesson-001`; `profile_anchors` copied from `taste/profile.md`).
- [ ] All 12 seed lessons present in the order from §3.6. Lessons 001–008 fully fleshed per §3.3.2 with done-criteria checkboxes; 009–012 are stubs (title + status + Depends on + one-sentence Why blocked only).
- [ ] Schema invariants from §3.3.3 hold at the seed: exactly one `[active]` lesson (lesson-001); every `[blocked]` lesson has a satisfiable `Depends on`; no `[done]` or `[skipped]` lessons in the seed.
- [ ] Each fleshed lesson references at least one `knowledge/*.md` cheat sheet by relative path.
- [ ] `CLAUDE.md` has the §3.10 section appended.
- [ ] Sessions/ template (§3.7) is referenced from `CLAUDE.md` and the spec; no template file is needed (spec is the reference).
- [ ] No `/schedule` entry exists for nudges (verification gate item satisfied via the §2.1 override).
- [ ] No new files in a `nudges/` directory; the directory does not exist.
- [ ] Manual rehearsal: Claude can articulate, given today's date and the current `sessions/` listing, whether a nudge would fire and what it would say.

## 6. Implementation notes

- **Seed authoring scope.** Lessons 001–008 are written as full nodes in `curriculum.md`. The `Practice task` text needs to be concrete enough that Destin can act on it without further design help — but does not need to be a step-by-step recipe. Reference cheat sheets handle the recipe layer.
- **Spec-driven content for seeds.** When implementing the seed, derive each lesson's `Why next:` line from the actual contents of `taste/profile.md` (not from spec §3.6's table justifications, which are summaries). E.g., quote the actual top BPM cluster's track count when it's most relevant.
- **Ableton companion mode in lessons.** Whenever a lesson's practice task involves locating an Ableton UI element, the `Practice task` line should mention `knowledge/ableton/companion-mode.md` as a fallback path — matches the §11 #9 / Subsystem #9 preference for companion mode over verbal directions when the user is in Ableton.
- **Session-log file naming when multiple sessions in one day.** If two sessions happen in one calendar day, the second log's filename is `YYYY-MM-DD-<topic>-2.md`. The lexicographic-sort staleness check in §3.8.1 still finds the most recent correctly.
- **Filename-vs-front-matter date.** The filename's date is authoritative for staleness; the front-matter `date` is a redundancy check. If they disagree, prefer the filename and fix the front matter.
- **Profile drift detection.** §3.10's CLAUDE.md instruction tells Claude to run §3.5 re-sync on profile drift. The check is cheap (compare two ISO timestamps) and is performed once per session, at the same moment as the staleness check.
- **The "configurability" knob.** Per master spec §11 #4 the nudge cadence is "configurable." In v1 the only configurable axis is the staleness threshold (one line in CLAUDE.md). Other axes (different thresholds for weekdays vs weekends, e.g.) are out of scope.
- **First-session bootstrap.** The very first session has no prior log. The staleness check (§3.8.1) treats "no log" as "stale" → nudge fires. The nudge will surface lesson-001. Verify this case in the rehearsal step of §5.

## 7. Self-review checklist

- [x] **Placeholders / TBDs:** none. All 12 seed lessons have IDs, titles, dependencies, and initial statuses; nudge content rule is exactly three sentences with prescribed structure; staleness threshold has a numeric default.
- [x] **Internal consistency:** §2 overrides ↔ §3.8 mechanics ↔ §3.10 CLAUDE.md ↔ §4 prohibitions all agree on "no scheduler." §3.3.3 invariants ↔ §3.4 end-of-session protocol ↔ §3.6 seed all agree on "exactly one `[active]` at any time." §3.7 sessions/ template ↔ §3.8.1 staleness check both rely on the same filename-date format.
- [x] **Scope:** narrowly bounded to `curriculum.md` + `sessions/*.md` + nudge mechanics. Does not author cheat sheets, taste profiles, or audio analysis. Does not modify any file owned by another subsystem.
- [x] **Ambiguity:** seed-lesson definitions are concrete (titles + dependencies + status); end-of-session triggers are an explicit phrase set; staleness check has unambiguous "≥ threshold calendar days from today" semantics; resync rule defines exactly which lesson statuses are touched (only `[blocked]`).
- [x] **Master-spec relationship:** §2 enumerates two overrides explicitly with reasons; §3.3 documents extensions to §7.3; §3.7 documents formalization of §7.6.
- [x] **Subsystem boundaries:** §4 prohibits modifying any file owned by Subsystems #3, #5, #6, #7. The only inputs are read-only references to `knowledge/*.md` (#3), `taste/profile.md` (#7).
- [x] **Subsystem #7 boundary:** clean — this spec consumes `taste/profile.md`'s front-matter (`generated_at`, `profile_anchors`) only; never modifies it.
