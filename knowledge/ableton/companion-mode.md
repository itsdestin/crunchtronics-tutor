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
