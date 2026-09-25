# Changelog

## [0.1.15] - 2026-09-25

Capture keeps corrections. A same-shape update ("we use npm" -> "we use bun") or a reverted decision is no longer dropped as a duplicate of the earlier note, and duplicate checks look only at live memories in the same project. Same-shape updates dropped on the synthetic bench fell from 29 of 106 to 2 of 106 and reverts from 26 of 26 to 0. The client cache gains plain nullable scope columns it fills itself, with no triggers and no SQLite JSON functions, so older plugin versions keep reading and writing the same file. Built from emergence-lab main 0f173e98c (lab gate cleared: LabDirector ruling 9b38478c, CodeRedTeam ec375bd7, DXCritic 6f7c6cf8). Known limit: a correction that only reassigns a value already named in the same note may still be treated as a duplicate; state the change in its own sentence.

## [0.1.14] - 2026-09-24

Intel Macs now get memory: the plugin runtime asks for cryptography 48.x on Intel (x86_64) Macs only, so it installs there instead of failing silently; every other platform keeps cryptography 50.x. With ATLASO_DEBUG=1 the session-start and per-turn hooks now write one counts-only line when they fire, so you can tell a hook that ran from one that was skipped. No memory text is logged.

## [0.1.13] — 2026-09-23

New Atlaso logo: the plugin listing and composer icon now show the ten-dot mark on a black square. No behavior changes.

## [0.1.12] — 2026-09-21

Project-bound SessionStart context with fresh policy checks and a bounded hook deadline. Preserve reconnect notices until output is flushed. Prepared as an unpublished candidate; actual-host delivery remains a separate qualification gate.

All notable changes to the Atlaso Memory plugin.

## [0.1.11] — 2026-08-03

### Fixed
- **The memory tools work again on a fresh install.** The plugin asked for "the
  MCP library, version 1.27 or newer". A version 2 of that library was published
  on 28 July which moved things around, so any *new* install picked it up and the
  memory tools (`remember`, `recall`, `forget`, `recent`, `status`) failed to
  start. Automatic recall and capture were unaffected — they don't use that
  library — so memory kept working; only the tools you call on purpose were
  broken. The version is now pinned so this cannot happen again.

## [0.1.10] — 2026-08-02

### Fixed
- **Memory recall no longer gives up too early on a busy machine.** Recall runs
  before your prompt is sent, and it was allowed only 15 seconds. That is plenty
  once it is warm (it normally takes about a second), but on a cold start — the
  first prompt after opening your editor, especially while your machine is busy —
  it could run out of time. When that happened the recall was discarded silently:
  no memory for that turn, and nothing to tell you why. The limit is now 30
  seconds, which clears a cold start with room to spare.

  The limit is deliberately kept, not removed: recall blocks your prompt while it
  runs, so an unbounded wait would turn a slow lookup into a frozen session.
