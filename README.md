# Atlaso Memory for Codex

Automatic long-term memory for OpenAI Codex. Atlaso recalls relevant context
before each prompt, captures durable facts and decisions as you work, and syncs
across your sessions and devices — for the **CLI, the IDE extension, and the
Desktop app** (they share one config, so a single install covers all three).

- 🧠 **Recall** — relevant past context is injected before Codex answers.
- 📝 **Capture** — durable decisions, preferences, and gotchas are saved as you work.
- 🔒 **Local-first** — memory works offline on your machine; sign in to sync to the cloud.
- 🗂️ **Personal + project memory** — preferences follow you everywhere; repo facts stay in the repo.

## Install

### Codex Desktop / IDE (GUI)

1. Open **Codex → Plugins**.
2. Click **+** (top right) → **Add marketplace**.
3. Fill in:
   - **Source:** `atlaso-labs/codex`
   - **Git ref:** `main`
   - **Sparse paths:** *(leave blank)*
4. Click **Add marketplace**, then open **Atlaso** and **Add to Codex** on the *Atlaso Memory* plugin.
5. Your first prompt opens a browser to connect your account (optional — memory works locally without it).

### Codex CLI

```bash
codex plugin marketplace add atlaso-labs/codex
codex plugin add atlaso@atlaso
```

Requires [`uv`](https://docs.astral.sh/uv/) — the plugin runs on a uv-managed Python, so there's nothing else to install.

## What gets installed

| Piece | Mechanism | What it does |
|---|---|---|
| recall | `UserPromptSubmit` hook | injects recalled memory before Codex sees your prompt |
| capture | `Stop` hook | saves the finished exchange (instant local write, synced later) |
| start | `SessionStart` hook | background cache sync; never delays session open |
| memory tools | MCP server — `recall`, `remember`, `forget`, `recent`, `status` | deliberate, model-invoked memory |
| skill + rules | `SKILL.md` + `AGENTS.md` | when to remember, personal vs project, fixing memory |

Recalled memory is injected as a plain branded block — no instructions, the model decides how to use it:

```
=== Atlaso Memory ===
- recalled note
- recalled note
=== Atlaso Memory ===
```

Hooks **fail open**: any error → silent no-op, your turn proceeds. Free plan = local-only; paid = cloud sync across devices.

## Privacy

Memory is stored locally on your machine by default. Cloud sync is opt-in (sign in). Learn more at [atlaso.ai](https://atlaso.ai).

## Note for Codex Desktop

A past Desktop update temporarily stopped hooks from firing ([openai/codex#21639](https://github.com/openai/codex/issues/21639)). If automatic recall/capture seems quiet on Desktop, the model-invoked memory tools (MCP) still work. Set `ATLASO_DEBUG=1` and check `~/.atlaso/atlaso-codex-*.log` to confirm hooks fire.

---

Built by [Atlaso Labs Inc.](https://atlaso.ai) · source: [github.com/atlaso-labs/codex](https://github.com/atlaso-labs/codex)
