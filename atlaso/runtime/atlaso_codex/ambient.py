"""Ambient Memory for Codex — fetch the orientation block from the brain (the
single source every tool shares) and inject it as SessionStart additionalContext.

The working logic lives server-side (GET /v1/ambient, paid-gated); this is just
the Codex-shaped injection. Returns the hook dict or None. Never raises.
"""
from __future__ import annotations


def run(client) -> dict | None:
    """client → SessionStart hookSpecificOutput dict, or None (nothing cached /
    not paid). Reads the CACHED block (file-only, instant); the background sync
    refreshes it."""
    try:
        block = client.ambient_cached()
    except Exception:
        return None
    if not block:
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": block,
        }
    }
