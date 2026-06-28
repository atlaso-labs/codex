"""Atlaso × Codex connector (OpenAI Codex CLI + IDE/Desktop).

Thin lifecycle hooks that wire Codex's hook events to the tool-agnostic memory
core (``atlaso_client.Client``). Nothing tool-specific lives in the core; nothing
smart lives here — each hook just reads the event and calls the client.

Codex's hook events differ from Claude Code's (verified against
developers.openai.com/codex/hooks + /codex/config-reference):

  recall  (UserPromptSubmit) → inject recalled memory before the model sees input
  capture (Stop)             → save the just-finished exchange (instant, local)
                               + flush/sync (Codex has NO SessionEnd event, so the
                               end-of-turn flush rides on Stop here)
  start   (SessionStart)     → notice banner + sync the local cache (background)

There is NO SessionEnd event in Codex — end/flush logic is folded into Stop and
the next SessionStart (see capture.py + start.py). Do not add an end.py here.
"""
__version__ = "0.1.0"
