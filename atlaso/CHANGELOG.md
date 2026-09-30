# Changelog

## [0.1.18] - 2026-09-30

Security fixes (batch B1). A saved note can no longer add lines to the injected memory block or fake its start or end, and invisible control, zero-width and bidirectional-override characters are removed from recalled notes. Ordinary notes print exactly as before, tabs and emoji included. A note written on several lines now prints on one line, as it already did in Claude Code, Grok Build, Cursor and OpenCode. The plugin's Python runtime now installs only the exact dependency versions in its lock file.

## [0.1.17] - 2026-09-26

Dated recall lines. Each note in the injected memory block now starts with the latest UTC day you stated it, for example `- [Aug 14] use bun`. A note rewritten later by server-side enrichment keeps the day of the statement it restates, not the rewrite day. A note whose day is unknown shows no date and is listed first. Repeating a note in your own words can update its statement date even if Atlaso skips the repeated text as a duplicate; the assistant repeating a note back never re-dates it. Notes queued offline are sent with the time they were captured. Against a brain that does not return dates, lines stay undated.

Measured once on the lab's synthetic multi-session bench, on the 150 questions where a newer decision replaced an older one: with dates, gpt-4.1-mini picked the newest decision in 126 of 150 (117 without dates) and DeepSeek V4.1 Flash in 132 of 150 (131 without). On the other 244 recall questions the net change was +2 and +1. The same notes were injected with and without dates; only the dates differed. This is one run per reader, not a statistical certification.

Dated MCP results. The `recall` and `recent` memory tools now return `stated_on`, the day the user stated each note (YYYY-MM-DD), or null when that is unknown. It is the same day the injected block shows, never the day a note was stored, imported, synced or rewritten, and `recent` no longer returns the storage time. Covered by unit tests, not by the bench.

One memory skill. The judgment part of the memory skill is now one shared text, byte-identical in all seven Atlaso tools and checked by a parity test. It says to save a changed decision as a change that names both values and the reason and keep the old note, to forget only a memory that was never true, to name a return to an earlier choice as a change, and never to re-save something that was only read from memory. It adds a rule for reading notes that disagree: in the same scope the most recently stated note is current, an undated note is not newer, and when neither is clearly newer the model asks you. The forget wording from the previous release is kept. Not measured by the bench.

## [0.1.16] - 2026-09-26

Forget now excludes a forgotten memory from Atlaso’s recall and export tools, cleans this device’s cache when possible, and deletes Ambient snapshots already on disk. The MCP result reports `local_cache_cleanup: "done"` or `"pending"`; pending cache cleanup retries when the cache opens or syncs. Memory skills now say that you can’t undo forget, and OpenCode installs the memory skill. A context load already in flight can still contain the forgotten text and make it available to new sessions for up to 15 minutes after that load finishes. The in-flight Ambient fence and the hosted MCP description are not part of this release. Product bytes equal the lab-gated emergence-lab commit 0578e74ac (CodeRedTeam bfe4497e, carried by byte identity 972f474e; DXCritic c27cb73e).

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
