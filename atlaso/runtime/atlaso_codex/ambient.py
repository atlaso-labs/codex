"""Project-aware Ambient Memory delivery for SessionStart.

The client validates the current setting, plan and tool/project response before
injection. A cold cache can receive a brief on this session; errors stay silent.
"""
from __future__ import annotations

import os
from pathlib import Path


def run(client, payload: dict | None = None) -> dict | None:
    # The host event describes the project actually opened. Only fall back to the
    # caller cwd preserved BEFORE the installed wrapper enters its runtime dir.
    # Do not let missing/malformed hook data inherit the plugin process cwd.
    payload = payload if isinstance(payload, dict) else {}
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd.strip() or not Path(cwd).is_absolute():
        cwd = os.environ.get("ATLASO_CALLER_PWD")
    if not isinstance(cwd, str) or not cwd.strip() or not Path(cwd).is_absolute():
        cwd = None
    try:
        block = (client.ambient_start(project_dir=cwd) if cwd else
                 client.ambient_start(project=None))
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
