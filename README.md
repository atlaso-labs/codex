# Atlaso — memory for Codex

**Every Codex session starts from zero. Atlaso gives it continuity** — automatic
recall before each turn and capture after, in Codex CLI, the IDE extension, and
Codex Desktop (they share `~/.codex`, so one install covers all three).

## Install

1. Create a free account at [app.atlaso.ai](https://app.atlaso.ai/sign-in) and
   follow the connect flow for Codex, then:

```
codex plugin marketplace add atlaso-labs/codex && codex plugin add atlaso@atlaso
```

(Codex Desktop: Plugins → **+ Add marketplace** → Source `atlaso-labs/codex`.)

**What you get**

- One memory across every AI tool you use — what Codex learns, Cursor, Codex, and the rest already know
- Personal memory that follows you, plus per-project memory keyed to each repo
- Secrets scrubbed client-side before anything is stored; your memory is never trained on or sold
- Free for one device and one tool — no credit card ([pricing](https://www.atlaso.ai/pricing))

**Links:** [Why Atlaso for Codex](https://www.atlaso.ai/for/codex) ·
[Setup guide](https://docs.atlaso.ai/tools/codex) ·
[What is an AI memory layer?](https://www.atlaso.ai/what-is-an-ai-memory-layer) ·
[Dashboard](https://app.atlaso.ai/sign-in)

---

## How it's built (for the curious)

The Codex connector for Atlaso memory (OpenAI Codex **CLI + IDE extension +
Desktop** — they all share `~/.codex/config.toml`, so one install covers all three
surfaces). Lives under `platform/tools/<tool>/` — one folder per tool we support.

Like every Atlaso connector it's deliberately thin: every hook + MCP tool just
calls the tool-agnostic core (`platform/client` → `atlaso_client.Client`) and the
shared MCP server (`platform/mcp` → `atlaso_mcp`). Nothing smart lives here; the
engine stays on the server. No memory logic is reimplemented for Codex.

## What you get

Codex supports a **full plugin bundle** (verified against
developers.openai.com/codex), so this is the complete automatic-memory loop —
the same shape as the Claude Code connector:

| Atlaso piece | Codex mechanism | What it does |
|---|---|---|
| **recall** (`hooks/recall.sh`) | `UserPromptSubmit` hook | Injects recalled memory as `additionalContext` before the model sees the prompt. Synchronous, fast. |
| **capture** (`hooks/capture.sh`) | `Stop` hook | Saves the just-finished exchange. Instant **local** write (no network), synced later. Also fires the end-of-turn flush (see caveat 1). |
| **start** (`hooks/start.sh`) | `SessionStart` hook | Local-only banner (once) + background cache sync. Detached — never delays session open. |
| **Atlaso MCP server** (`.mcp.json` → `bin/atlaso-memory-mcp`) | `[mcp_servers.Atlaso]` | Model-invoked deliberate tools: `recall`, `remember`, `forget`, `recent`, `status`. |
| **skill** (`skills/memory/SKILL.md`) | Codex skill | Curation judgment — when to remember, personal vs project, fixing memory. |
| **rules** (`AGENTS.md`) | Auto-loaded `AGENTS.md` | Tells the model to recall before answering + deposit durable facts (works even MCP-only, no plugin). |

Injected block (no instructions — the model decides how to use it):

```
=== Atlaso Memory ===
- recalled note
- recalled note
=== Atlaso Memory ===
```

Hooks **fail open**: a missing interpreter or any error → silent no-op (exit 0),
the turn proceeds. A light commodity filter skips trivial acks ("ok", "thanks") on
capture; the real "worth keeping" gate runs server-side. Free plan = local-only;
paid = cloud sync across devices. A revoked/non-entitled tool keeps working
**locally** and never deletes memories (handled by the shared client's state
machine).

## ⚠️ Two honest caveats (verified, not assumptions)

1. **Codex has NO `SessionEnd` event.** Both
   `developers.openai.com/codex/hooks` and `/codex/config-reference` enumerate the
   10 hook events (SessionStart, SubagentStart, PreToolUse, PermissionRequest,
   PostToolUse, PreCompact, PostCompact, UserPromptSubmit, SubagentStop, Stop) and
   neither lists SessionEnd. So the end-of-turn **flush** that the Claude Code
   connector puts on SessionEnd rides on **Stop** here (`capture.py` kicks off a
   detached background `sync` after each local write), plus the next
   **SessionStart** sync. There is intentionally **no `end.sh`** in this connector.

2. **Desktop hook reliability regressed once.** GitHub `openai/codex#21639`
   ("Hooks no longer run after Codex Desktop update", Desktop 26.506.21252, macOS)
   is a genuine report of `SessionStart` + `PreToolUse` not firing on Desktop.
   The MCP server (model-invoked memory) is unaffected. **If you use Codex
   Desktop, smoke-test that hooks fire** (set `ATLASO_DEBUG=1` and check
   `~/.atlaso/atlaso-codex-*.log` after a turn — see Debug below). If they don't,
   you still have full model-invoked memory via the MCP server + AGENTS.md rules.

## Install

### A. Full plugin (automatic loop — recommended)

Build the self-contained plugin, then add it as a marketplace and install:

```bash
cd platform/tools/codex
python package.py                                   # → dist/atlaso + dist/.agents/plugins/marketplace.json

# Dev / local install from the built dir:
codex plugin marketplace add ./dist
codex plugin add atlaso@atlaso
```

For real users, publish `dist/` to a marketplace repo and install with:

```bash
codex plugin marketplace add atlaso-labs/codex      # the published marketplace repo
codex plugin add atlaso@atlaso
```

The built plugin is self-contained: launchers run the vendored packages on a
uv-managed Python (`uv run`), so nothing is needed but `uv`. One install via
`~/.codex/config.toml` covers the CLI, the IDE extension, and Desktop.

### B. MCP-only (model-invoked memory, no automatic loop)

If you only want the deliberate memory tools (no auto recall/capture), register
just the MCP server — see `config.toml.example`, or:

```bash
codex mcp add memory -- /ABSOLUTE/PATH/TO/bin/atlaso-memory-mcp
```

Then copy the `## Atlaso memory` section of `AGENTS.md` into `~/.codex/AGENTS.md`
so the model knows to use the tools. **No automatic capture in this mode — the
model deposits via the MCP `remember` tool.**

## Layout

```
tools/codex/
  .codex-plugin/plugin.json   plugin manifest (bundles mcp + hooks + skills)
  .mcp.json                   registers the `Atlaso` MCP server (mcp_servers map)
  config.toml.example         manual MCP-only TOML snippet
  AGENTS.md                   auto-loaded rules snippet (recall + remember)
  hooks/      recall.sh · capture.sh · start.sh · _resolve.sh · hooks.json
  atlaso_codex/  recall.py · capture.py · sync.py · notice.py · transcript.py · _shim.py
  bin/atlaso-memory-mcp       MCP launcher (dual-mode: built runtime / dev venv)
  skills/memory/SKILL.md      curation-judgment skill
  package.py                  builds the self-contained dist/ plugin + marketplace
  tests/      test_recall · test_capture · test_transcript · test_notice
```

## Dev / test

Hooks resolve the SDK venv (it has `httpx`) and `atlaso_client` by relative path.

```bash
cd platform/tools/codex
PYTHONPATH=".:../../client" ../../sdk/.venv/bin/python -m pytest tests -q
```

Manual end-to-end (offline, throwaway dir):

```bash
export ATLASO_GLOBAL_PATH=/tmp/atlaso-codextest   # redirects auth + cache here
printf '{"type":"user","message":{"content":"always use pnpm not npm"}}\n' > /tmp/t.jsonl
echo '{"transcript_path":"/tmp/t.jsonl"}' | ./hooks/capture.sh
echo '{"prompt":"which package manager"}' | ./hooks/recall.sh   # → injects the block
```

### Debug

`ATLASO_DEBUG=1` writes per-hook logs to `<atlaso dir>/atlaso-codex-*.log`. Use it
to smoke-test that Desktop hooks fire (caveat 2).
