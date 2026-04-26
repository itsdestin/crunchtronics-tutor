# Subsystem #5 — Spotify Integration

- **Date:** 2026-04-26
- **Status:** Drafted (via brainstorm; awaiting user review)
- **Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md`
- **Master-spec sections referenced:** §3.1 (Spotify deprecation context), §5.1 #5 (one-liner contract), §6 (data flow), §7.1 (`taste/playlists.json` shape), §11 default decision #1 (user registers app), §11 default decision #12 (pull frequency — **overridden**, see §2)
- **Companion spec:** `docs/superpowers/specs/2026-04-26-spotify-services-plugin-design.md` (the plugin this subsystem consumes)
- **Session:** C-tutor (split from original Session C in master orchestration; precedes #6)
- **Build order:** First subsystem in Session C-tutor; depends on plugin shipping
- **Depends on:**
  - Subsystem #1 (Project Shell — folder skeleton + secrets dir + .gitignore)
  - The `spotify-services` plugin published and installed on Destin's machine (separate session, see plugin design spec)
- **Blocks:** Subsystem #6 (Audio Feature Enrichment) — #6 reads `taste/playlists.json` produced by this subsystem.

## One-liner contract

Configures the Crunchtronics Tutor to consume the `spotify-services` marketplace plugin for all Spotify Web API access. Owns the `taste/playlists.json` file (master spec §7.1) but does not own the code that produces it; the plugin does. No Spotify-specific code lives in this repo.

## 2. Master-spec overrides

This subsystem overrides one default decision from the master spec:

- **Master spec §11 #12 — Pull frequency.** Original default: "Weekly scheduled + on-demand." **Overridden to: on-demand only.** No `/schedule` entry. Destin pulls his Spotify data manually, either by asking Claude inside a tutor session or by invoking the plugin tool directly. Reason: simpler, fewer moving parts, taste evolves slowly enough that automated weekly pulls aren't load-bearing.

When the master spec is next revised, §11 #12 should be updated to reflect this override (or kept as the default with this subsystem documenting its deviation).

## 3. What this subsystem does

### 3.1 Declares the plugin dependency in `CLAUDE.md`

Adds a section to project `CLAUDE.md` that says, in plain prose: this project depends on the `spotify-services` marketplace plugin. If it isn't installed, run `/spotify-services-setup`. The taste data lives at `taste/playlists.json`, written by the plugin.

### 3.2 Owns `taste/playlists.json`

The file's existence, location, and schema are this subsystem's responsibility. The schema follows master spec §7.1 verbatim — raw Spotify Web API shape, top-level `{ user_id, fetched_at, playlists: [...] }`. The plugin's `export_all_playlists` tool writes exactly this shape.

This subsystem does not transform the data. It does not validate field-by-field. It treats the file as opaque to everything except the schema-level contract.

### 3.3 Documents the on-demand pull mechanism

Adds a short section to `CLAUDE.md` describing how Destin (and Claude) trigger a pull:

- **Inside a tutor session:** Destin says "pull my Spotify data" or similar. Claude invokes the plugin's `export_all_playlists` tool with the path `C:\Users\desti\crunchtronics-tutor\taste\playlists.json`. After it completes, Claude reports row count and any errors.
- **Outside a session:** Destin can invoke the plugin tool directly (e.g., from Claude Desktop, Cursor, or a one-shot Claude Code invocation), passing the same target path.

### 3.4 Verification of first run

The first time the plugin is invoked, Claude verifies:
- `taste/playlists.json` exists at the expected path.
- File size > 0 and valid JSON.
- Top-level keys match `{user_id, fetched_at, playlists}`.
- `playlists` is a non-empty list (Destin has at least one playlist on Spotify).

If any of these fail, Claude does not declare the subsystem working; instead, it surfaces the diagnostic and points at `/spotify-services-reauth` if the failure suggests an auth problem.

## 4. What this subsystem must NOT do

- **No OAuth code.** No PKCE flow, no token persistence, no refresh handling — the plugin owns all of this.
- **No `spotipy` import in this repo.** No Python script under `scripts/` for Spotify pulls.
- **No `/schedule` entry.** Pulls are manual only (per §2 above).
- **No transformation of `playlists.json`.** That's #6's job (read raw, dedupe, enrich, write `tracks.csv`).
- **No `taste/profile.md` writing.** That's Session D / Subsystem #7.
- **No use of plugin tools beyond `export_all_playlists` for the v1 contract.** Other plugin tools (`now_playing`, `search`, etc.) are available to Claude opportunistically inside sessions, but they're not part of this subsystem's contract.

## 5. Verification gate

Before declaring this subsystem complete:

- [ ] `CLAUDE.md` updated with the plugin dependency declaration and pull-mechanism documentation.
- [ ] `spotify-services` plugin installed on the development machine; `/spotify-services-setup` has been run successfully.
- [ ] `taste/playlists.json` populated by a real run of `export_all_playlists` against Destin's account.
- [ ] File contents satisfy §3.4 verification checks (valid JSON, schema match, non-empty playlists).
- [ ] No Spotify-specific code in this repo (`scripts/` and root contain nothing referencing `spotipy`, OAuth, or the Spotify Web API directly).

## 6. Implementation notes

This subsystem ships in <30 minutes once the plugin exists. The work is:

1. ~10 lines of new prose in `CLAUDE.md`.
2. Run the plugin's setup once on Destin's machine.
3. Run the plugin's `export_all_playlists` tool once to populate `taste/playlists.json`.
4. Verify per §3.4.
5. Commit `CLAUDE.md` changes and `taste/playlists.json` (the JSON file is committed because it's small enough and useful as a snapshot; if it grows large later, switch to gitignored).

The brevity is the point. The original Session C plan budgeted a full session for this subsystem because OAuth + script authoring + scheduling were all in scope. After the plugin extraction, the subsystem is essentially a configuration step.

## 7. Self-review checklist

- [x] **Placeholders / TBDs:** none.
- [x] **Internal consistency:** §3, §4, §5 describe the same shrunken footprint; the §11 #12 override is called out explicitly in §2.
- [x] **Scope:** narrowly bounded — one CLAUDE.md edit and one verified data file. Out-of-scope items listed in §4.
- [x] **Ambiguity:** the verification checks in §3.4 and §5 are explicit; the boundary against #6 (no transformation) is explicit.
- [x] **Plugin-side boundary:** this spec does not duplicate any of the plugin design spec's content — it references it.
