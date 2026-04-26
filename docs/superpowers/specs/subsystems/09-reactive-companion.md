# Subsystem #9 — Reactive Companion

- **Date:** 2026-04-26
- **Status:** Approved (via Session A brainstorm)
- **Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md`
- **Master-spec sections referenced:** §3.4 (must not short-circuit user learning), §5.1 #9 (on-demand only, no autonomous monitoring), §11 #9 (CLAUDE.md scope includes companion-mode preference)
- **Session:** A (Scaffolding)
- **Build order:** Third in Session A (after #1 and #2)
- **Depends on:** #1 (folder + initial CLAUDE.md), #2 (Reference Vault — companion-mode answers cite `reference/INDEX.md`)
- **Blocks:** nothing in Session A; live verification deferred until windows-control MCP is installed

## One-liner contract

Defines the **behavioral policy** by which Claude reads Destin's Ableton screen on demand and gives click-by-click guidance, grounded in the Reference Vault. Implemented as docs + a CLAUDE.md refinement — no code.

## Design intent

Companion mode is **intent-driven, not pattern-matched**. Claude infers the moment from Destin's natural signals (stuckness, navigation uncertainty), offers to look, captures on assent, cites the Reference Vault, and answers in terms of what's actually on screen. There is no canned trigger-phrase catalog and no enumerated recipes — those would feel mechanical and wouldn't survive natural conversation.

This intent-driven framing is a deliberate revision from the initial Session A brainstorm, which proposed five named recipes. The recipes are dropped.

## What this subsystem does

### 1. `knowledge/ableton/companion-mode.md`

The policy doc. Required sections:

1. **What companion mode is.** On-demand only, intent-inferred, never autonomous, never predictive.

2. **When it triggers.** Claude reads intent from Destin's natural signals:
   - "I can't find…" / "where is the…" / "what's this thing on my screen"
   - Visible frustration with menus or device chains
   - Questions about Ableton state that Claude can't answer from memory alone (e.g., "is my clip quantized?")

   Examples are illustrative — Claude treats them as heuristics, not a checklist. If in doubt, Claude asks rather than capturing.

3. **The policy (load-bearing).** When companion mode is warranted, Claude:
   1. Offers first ("want me to take a look?") rather than capturing unprompted.
   2. On assent, captures the Ableton window via the windows-control MCP.
   3. **Cross-references the Reference Vault** — looks up the relevant entry in `reference/INDEX.md` and cites the page number or URL anchor when applicable.
   4. Responds in terms of what's actually on Destin's screen ("you're in Session view; the Simpler is on track 2; click the magnifying glass at the top-right of the device").
   5. Closes the loop: invites a follow-up capture if the directions don't land ("did that work, or should I look again?").

4. **What Claude will not do.**
   - No unprompted captures.
   - No autonomous mouse/keyboard actions that produce work on Destin's behalf.
   - No continuous monitoring loops or background watchers.
   - No companion mode for non-Ableton windows unless Destin explicitly requests it.

5. **Reference-vault tie-in (hard expectation, not optional polish).** Every companion-mode answer that maps to a documented concept SHOULD cite `reference/INDEX.md` (page or URL). This is the integration glue between #9 and #2.

6. **Tool-surface assumption.** The policy is written against an abstract windows-control surface that exposes at minimum:
   - **List windows** — return a list of open application windows.
   - **Capture window** — given a window identifier (or "active"), return an image Claude can see.

   When the actual MCP is installed, the policy doc updates with concrete tool names. This is a search-and-replace, not a redesign.

### 2. CLAUDE.md refinement

Subsystem #1 drafts the companion-mode paragraph during its CLAUDE.md write. Subsystem #9's only obligation here is to verify that paragraph is present and may polish the wording. No structural change.

The paragraph reads (approximately):

> "When you (Destin) are in Ableton and signal navigation confusion, I'll offer to look at your screen rather than give verbal-only directions; I'll never capture unprompted; and I'll ground every companion answer in the Reference Vault when applicable. See `knowledge/ableton/companion-mode.md` for the full policy."

## What this subsystem must NOT do

- Do not implement an autonomous screen-capture watcher.
- Do not author any other `knowledge/` content (that's Session B).
- Do not write Python scripts.
- Do not write `taste/`, `teardowns/`, or `curriculum.md` content.
- Do not enumerate canned trigger phrases or recipe scripts — companion mode is intent-driven.
- Do not block this subsystem on the windows-control MCP being installed. Ship the policy and CLAUDE.md refinement now; the live test runs separately when the MCP arrives.

## Verification gates

### Doc gate (runs in this session — must pass to mark #9 complete)

- `knowledge/ableton/companion-mode.md` exists with all 6 sections above.
- `CLAUDE.md` contains the companion-mode paragraph (drafted by #1, optionally polished by #9).
- The reference-vault citation requirement is **explicit** in `companion-mode.md` (not implied through prose).
- The tool-surface-assumption section names the abstract operations (list windows, capture window) so the doc is unambiguous about what an MCP must provide.

### Live gate (deferred — runs the moment windows-control MCP is installed)

With Ableton open, Destin says something organic like:

> "I'm stuck — I can't find where to add a Simpler."

Confirm Claude:

1. Offers to look at the screen (does NOT capture unprompted).
2. Captures via windows-control after Destin assents.
3. Cites the relevant Reference Vault entry (page or URL).
4. Gives directions oriented to the actual screen state.

Single end-to-end behavior test, not five canned recipes. Recorded in this spec as a **pending gate**, not a skipped one. When the MCP is installed, the gate runs; if it passes, the spec gets stamped "live gate passed" with a date.
