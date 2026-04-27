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

### 3.2 Owns `taste/playlists.json` and `taste/.playlist-selection.json`

The files' existence, locations, and schemas are this subsystem's responsibility.

`taste/playlists.json` schema follows master spec §7.1 verbatim — raw Spotify Web API shape, top-level `{ user_id, fetched_at, playlists: [...] }`. The pull workflow (§3.3) assembles this file from the plugin's per-playlist tools rather than the bulk `export_all_playlists` tool, because pulls are **selective**: Destin chooses which playlists to include rather than dumping his entire library.

`taste/.playlist-selection.json` records which playlists Destin chose to pull. Schema:

```json
{
  "selected_at": "2026-04-26T18:30:00Z",
  "playlists": [
    {"id": "37i9dQZF1DXcBWIGoYBM5M", "name": "Today's Top Hits"},
    {"id": "...", "name": "..."}
  ]
}
```

Both files are committed to git (small, useful as snapshots, and committing the selection means the saved choice survives across machines / fresh clones).

This subsystem does not transform the playlist data — it stores the raw plugin responses and treats them as opaque to everything except the schema-level contract.

### 3.3 Documents the on-demand selective pull mechanism

Adds a section to `CLAUDE.md` describing how Destin (and Claude) trigger a pull. The workflow is **selective with persisted choice**: Destin picks playlists once, the choice is saved, subsequent pulls re-use it silently. Re-picking is explicit (he says "fresh" / "reselect" / "pick again", or invokes a `--reselect`-style flag in a future CLI wrapper).

When Destin says "pull my Spotify data" (or similar):

1. Read `taste/.playlist-selection.json` if it exists.
2. **If the file exists AND Destin did not request a fresh pick:**
   - Use the saved playlist IDs.
   - Briefly tell Destin: *"Pulling your saved selection: <names>. Say 'pull my Spotify data fresh' to re-pick."*
3. **Otherwise** (no saved selection, or fresh/reselect requested):
   1. Call the plugin's `playlists_list_mine` tool (with `--all` to paginate) to get every playlist Destin owns or follows.
   2. Show Destin a numbered list with playlist names and track counts.
   3. Ask which playlists to include (he can pick by number, name, comma-separated list, or "all").
   4. Save the chosen playlist IDs + names to `taste/.playlist-selection.json` (per §3.2).
4. For each selected playlist ID, call the plugin's `playlists_get_items` tool (with `--all`) to get its tracks.
5. Assemble the per-playlist responses into `taste/playlists.json` matching master spec §7.1:
   ```json
   {
     "user_id": "<from playlists_list_mine response or user_profile call>",
     "fetched_at": "<UTC ISO timestamp>",
     "playlists": [{"id": "...", "name": "...", "tracks": [...]}]
   }
   ```
6. Report the playlist count, total track count, and any errors.

The plugin is invokable from any MCP client (Claude Code, Claude Desktop, Cursor); the workflow above is the same regardless.

### 3.4 Verification of first run

After a pull completes, Claude verifies:
- `taste/playlists.json` exists at the expected path.
- File size > 0 and valid JSON.
- Top-level keys match `{user_id, fetched_at, playlists}`.
- `playlists` is a non-empty list — at least one of the selected playlists has tracks.
- `taste/.playlist-selection.json` exists with the same playlist IDs that appear in `playlists.json` (consistency check).

If any of these fail, Claude does not declare the subsystem working; instead, it surfaces the diagnostic and points at `/spotify-services-reauth` if the failure suggests an auth problem.

## 4. What this subsystem must NOT do

- **No OAuth code.** No PKCE flow, no token persistence, no refresh handling — the plugin owns all of this.
- **No `spotipy` import in this repo.** No Python script under `scripts/` for Spotify pulls.
- **No `/schedule` entry.** Pulls are manual only (per §2 above).
- **No transformation of `playlists.json`.** That's #6's job (read raw, dedupe, enrich, write `tracks.csv`).
- **No `taste/profile.md` writing.** That's Session D / Subsystem #7.
- **No bulk `export_all_playlists` invocation.** Pulls are selective per §3.3; the bulk export tool would dump the entire library and bypass the selection mechanism. The plugin's per-playlist tools (`playlists_list_mine`, `playlists_get_items`) are the contract surface.
- **No other plugin tools as part of this subsystem's contract.** Tools like `now_playing` and `search` are available to Claude opportunistically inside sessions, but they're not what this subsystem owns.
- **No automatic fresh re-pick.** Once the saved selection exists, every subsequent pull re-uses it unless Destin explicitly asks to re-pick. The selection persists.

## 5. Verification gate

Before declaring this subsystem complete:

- [ ] `CLAUDE.md` updated with the selective-pull workflow from §3.3.
- [ ] `spotify-services` plugin installed on the development machine; `/spotify-services-setup` has been run successfully.
- [ ] `taste/.playlist-selection.json` exists with at least one playlist chosen.
- [ ] `taste/playlists.json` populated from the saved selection via `playlists_get_items` calls.
- [ ] File contents satisfy §3.4 verification checks (valid JSON, schema match, non-empty playlists, selection consistency).
- [ ] No Spotify-specific code in this repo (`scripts/` and root contain nothing referencing `spotipy`, OAuth, or the Spotify Web API directly).
- [ ] No `export_all_playlists` invocation in the workflow (per §4 — selection bypasses the bulk export).

## 6. Implementation notes

This subsystem ships in <45 minutes once the plugin exists. The work is:

1. CLAUDE.md prose for the selective-pull workflow (§3.3) — ~30 lines.
2. Run the plugin's setup once on Destin's machine.
3. Walk Destin through the playlist picker once; save `taste/.playlist-selection.json`.
4. Pull the selected playlists into `taste/playlists.json`.
5. Verify per §3.4.
6. Commit CLAUDE.md, `taste/playlists.json`, and `taste/.playlist-selection.json`.

The brevity is the point. The original Session C plan budgeted a full session for this subsystem because OAuth + script authoring + scheduling were all in scope. After the plugin extraction, the subsystem is a configuration + workflow-design step.

## 7. Self-review checklist

- [x] **Placeholders / TBDs:** none.
- [x] **Internal consistency:** §3, §4, §5 describe the same shrunken footprint; the §11 #12 override is called out explicitly in §2.
- [x] **Scope:** narrowly bounded — one CLAUDE.md edit and one verified data file. Out-of-scope items listed in §4.
- [x] **Ambiguity:** the verification checks in §3.4 and §5 are explicit; the boundary against #6 (no transformation) is explicit.
- [x] **Plugin-side boundary:** this spec does not duplicate any of the plugin design spec's content — it references it.
