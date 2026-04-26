# Subsystem #1 — Project Shell

- **Date:** 2026-04-26
- **Status:** Approved (via Session A brainstorm)
- **Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md`
- **Master-spec sections referenced:** §1 (purpose), §4 (folder layout), §5.1 #1 (one-liner contract), §11 (default decisions, especially #5 git-local-only and #9 CLAUDE.md scope)
- **Session:** A (Scaffolding)
- **Build order:** First in Session A (precedes #2 and #9)
- **Depends on:** nothing
- **Blocks:** all other subsystems and sessions

## One-liner contract

Bootstraps the project folder, writes `CLAUDE.md` (project description + Claude pedagogy conventions), `README.md`, an initial empty `curriculum.md`, `.gitignore`; runs `git init`; creates the secrets directory at `C:\Users\desti\.crunchtronics-tutor-secrets\` with placeholder files.

## What this subsystem does

### 1. Folder skeleton

Creates every directory listed in master spec §4. Each directory gets a `.gitkeep` so it survives the initial commit. The `docs/superpowers/specs/` directory already contains the master spec, the orchestration plan, and the three Session A subsystem specs (this file plus 02 and 09); they are preserved.

```
crunchtronics-tutor/
├── reference/.gitkeep
├── knowledge/{theory,ableton,mpk-mini-4,genres,artists}/.gitkeep
├── taste/.gitkeep
├── teardowns/.gitkeep
├── sessions/.gitkeep
├── docs/superpowers/{plans,specs,specs/subsystems}/  (already populated)
└── scripts/.gitkeep
```

### 2. CLAUDE.md (project root)

Voice: addresses Destin by name; plain prose, no emoji. Sections:

1. **What this project is** — one paragraph from master spec §1.
2. **How Claude operates here** — pedagogy conventions from master spec §11:
   - Read the master spec first when entering a fresh session: `docs/superpowers/specs/2026-04-26-master-architecture.md`
   - Top-down framing (master spec §11 #7): genre patterns first, theory invoked as needed.
   - Hardware/software learned together (master spec §11 #8): MPK ↔ Ableton mappings appear from day 1.
   - Check `curriculum.md` before suggesting next concepts.
   - **Companion-mode preference** (one paragraph): when Destin is in Ableton and signals navigation confusion, prefer offering to look at his screen over verbal-only directions; never capture unprompted; ground every companion answer in the Reference Vault when applicable. Pointer to `knowledge/ableton/companion-mode.md`. *Drafted here; Subsystem #9 may refine the wording during its phase, but the paragraph and pointer ship in #1.*
3. **Folder map** — compressed §4.
4. **Pointers** — master spec, orchestration plan.

### 3. README.md (project root)

Human-facing one-pager. Sections: what this is, how it's organized (folder map), how to run a session ("open Claude Code in this directory; read CLAUDE.md and the master spec; ask away"). Pointer to master spec.

### 4. curriculum.md (project root)

Front matter:

```yaml
---
last_updated: 2026-04-26T00:00:00Z
next: lesson-001
---
```

Body:

```markdown
# Curriculum

## lesson-001: <to be authored by Subsystem #4 — Curriculum & Nudges> [blocked]
- Why blocked: depends on Subsystem #7 (Taste Profile)
```

NO real lesson content. The placeholder exists only so the master spec §7.3 schema is visible to anyone reading the file before #4 ships.

### 5. .gitignore

```
.secrets/
sessions/*.draft.md
scripts/__pycache__/
scripts/.venv/
*.log
.DS_Store
reference/*.pdf
```

PDF exclusion is per Session A brainstorm default: PDF manuals stay out of git (large binaries; repo is local-only per master spec §11 #5 anyway).

### 6. Git init + initial commit

- Run `git init` in project root.
- Use global `git config user.name / user.email`. **If unset, stop and ask before continuing.**
- Stage all files in the repo at this point (scaffolding + the pre-existing planning docs: master spec, orchestration plan, the three Session A subsystem specs).
- Single initial commit with message: `init: project scaffold + master spec + Session A subsystem specs`.

### 7. Secrets directory

Path: `C:\Users\desti\.crunchtronics-tutor-secrets\`

Contents:

- `spotify.json` containing `{}`.
- `audio-enrichment.json` containing `{}`.
- `README.txt` explaining what each file will hold once Sessions C/D run, with pointers to master spec §4 and §11 #1/#2.

**Idempotency:** if the directory already exists, do not overwrite existing files. If `spotify.json` or `audio-enrichment.json` exists with non-empty content, leave it untouched and skip the placeholder write for that file. Always (re-)write README.txt — it's documentation, not data.

## What this subsystem must NOT do

- Do not author any `knowledge/` content (that's Session B / Subsystem #3 — except `knowledge/ableton/companion-mode.md` which #9 owns later in this same session).
- Do not write any Python scripts.
- Do not author `taste/` or `teardowns/` content.
- Do not author curriculum lesson nodes beyond the §7.3 schema placeholder.
- Do not push to a remote (per master spec §11 #5).
- Do not commit secrets — secrets live outside the repo at `C:\Users\desti\.crunchtronics-tutor-secrets\`.

## Verification gates (must all pass before #2 starts)

- `CLAUDE.md`, `README.md`, `curriculum.md`, `.gitignore` all present at project root.
- All §4 directories exist with `.gitkeep` files (or non-empty contents in the case of `docs/`).
- `git log --oneline` shows the initial commit `init: project scaffold + master spec + Session A subsystem specs`.
- `C:\Users\desti\.crunchtronics-tutor-secrets\` exists with `spotify.json`, `audio-enrichment.json`, `README.txt`.
- Smoke test: drop a 1KB dummy `reference/test.pdf`, run `git status`, confirm it is ignored. Delete the dummy.
