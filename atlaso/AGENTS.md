<!--
  Atlaso Memory — Codex rules snippet.

  Codex auto-loads AGENTS.md files (verified: developers.openai.com/codex/guides/
  agents-md) from the global ~/.codex/AGENTS.md, the project root, and nested
  per-directory files, concatenated root-down. Copy the "## Atlaso memory" section
  below into your ~/.codex/AGENTS.md (applies everywhere) or a project AGENTS.md.

  This is what gives the MEMORY discipline even when only the MCP server is
  installed (no plugin/hooks): it tells the model to recall before answering and to
  deposit durable facts via the `memory` MCP tools. With the full plugin installed,
  recall + capture also happen automatically each turn via lifecycle hooks — but
  these rules still sharpen WHAT the model chooses to remember.

  Keep this well under the default project_doc_max_bytes (32 KiB) limit.
-->

## Atlaso memory

You have a long-term memory via the Atlaso `memory` MCP server (tools: `recall`,
`remember`, `forget`, `recent`, `status`). Treat it as the user's own second brain.

- **Recall before answering** anything that could depend on prior decisions,
  preferences, or project conventions — call `recall` with a short query. If the
  Atlaso plugin is installed, relevant memories are already injected each turn as an
  "Atlaso Memory" block; in that case only `recall` for more when the auto-injected
  context is insufficient. Don't over-search.
- **Remember durable things** with `remember`: decisions *and their reason*, stable
  user preferences and working style, hard-won gotchas, and stable facts/commands
  (ports, endpoints, conventions). Do NOT save transient state, secrets/tokens, or
  restatements of files already in the repo.
- **Personal vs project:** ask "would this still be true in a different project?"
  Yes → it's personal (follows the user everywhere). No → it's project-specific.
- **Changed vs wrong:** when a decision changes, save the change naming both
  values and the reason ("moved from A to B because ...") and keep the old note.
  Only a memory that was never true gets `forget` (after `recall` finds its id).
  Never re-save something you only read from memory.

Memory is the user's data — you decide how to use it, and you keep it small and
high-signal.
