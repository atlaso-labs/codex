---
name: memory
description: >-
  Atlaso memory curation judgment. Use ONLY when deciding whether/what to save to
  memory, whether something is personal vs project-specific, or when deliberately
  recalling, forgetting, or correcting a memory. Do NOT use for ordinary recall —
  relevant memories are already injected automatically every turn.
when_to_use: >-
  deciding if something is worth remembering; choosing personal vs project memory;
  superseding or forgetting a wrong/outdated memory; deliberately searching past
  sessions for a prior decision.
---

# Using Atlaso memory well

Relevant memories are **auto-injected every turn** (the "Atlaso Memory" block) — so
most of the time you do nothing. Reach for the memory tools (`recall`, `remember`,
`forget`, `recent`, `status`) only for the judgment calls below. When in doubt, do
less: a smaller, higher-signal memory is worth more than volume.

## What's worth remembering (default: don't)

Save **durable** things:
- decisions **and the reason** behind them
- the user's stable preferences and working style
- hard-won gotchas ("X silently fails unless Y")
- stable facts/commands (ports, endpoints, conventions)

Don't save: transient state ("ran the tests just now"), secrets/tokens, restatements
of files already in the repo, or anything that's just in this turn's context.

## Personal vs project — Atlaso's dual memory

Atlaso keeps two memories. Route deliberately:
- **Personal** (follows the user across every project/tool): cross-project preferences,
  identity, working style. → "true in every repo."
- **Project** (this repo only): architecture, repo-specific decisions and gotchas.
  → "true only here."

Rule of thumb: *would this still be true in a different project?* Yes → personal. No → project.

## When to deliberately `recall` (vs trusting the auto-injection)

The automatic block usually has what you need. Search explicitly only when:
- the user references a past decision ("what did we decide about X?"),
- you're about to do something that might contradict an earlier choice, or
- you're starting unfamiliar work where prior context would clearly help.

Otherwise, trust the injected memories and **don't over-search**.

## Fixing memory

A memory is wrong or outdated → `recall` to find its id, then `forget` it (or save the
correction). Supersede rather than piling up contradictions.

## Good vs skip

- ✅ "Use pnpm, never npm — the user's standard across all projects." *(personal)*
- ✅ "Brain server runs on port 8800; recall is `GET /v1/recall`." *(project)*
- ✅ "Tauri signing key must be single-line in CI or it errors." *(hard-won gotcha)*
- ⏭️ "Compiled the app and the tests passed." *(ephemeral — skip)*
