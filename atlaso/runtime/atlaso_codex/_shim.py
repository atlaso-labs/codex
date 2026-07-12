"""Shared plumbing for the Atlaso Codex hooks.

Mirrors the Claude Code connector's shim: read the event payload from stdin, build
the tool-agnostic ``atlaso_client.Client`` tagged with THIS tool's id, do one small
thing, and NEVER break the session (all failures swallow → exit 0).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_payload() -> dict:
    """Parse the hook's stdin JSON; {} on anything malformed/empty.

    Codex delivers the hook event as a JSON object on stdin with common fields:
    session_id, transcript_path (may be null), cwd, hook_event_name, model,
    turn_id, permission_mode. UserPromptSubmit adds `prompt`; Stop adds
    `last_assistant_message` + `stop_hook_active`.
    """
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def is_recursive() -> bool:
    """True inside our own nested model calls (future server/L2 enrichment), so
    memory never recalls/captures itself into a loop."""
    return bool(os.environ.get("ATLASO_EXTRACTING"))


# This connector's tool id — must match the agent id the web app / brain use for
# per-plan tool entitlement (free = only the active tool is cloud-linked; the rest
# run local-only). Overridable via ATLASO_TOOL for testing/forward-compat.
TOOL = os.environ.get("ATLASO_TOOL") or "codex"


def make_client():
    """Build the memory client (reads ~/.atlaso/auth.json; offline-safe).
    Imported lazily so the hook modules stay importable without the client dep
    (tests inject a fake client). Tagged with this tool id so the client's plan
    entitlement knows which tool is asking."""
    from atlaso_client import Client

    return Client(tool=TOOL)


def maybe_autoconnect() -> bool:
    """If this machine isn't connected yet, spawn the (detached) browser-authorize
    flow. Fast + best-effort — never blocks the hook, never raises. Passes THIS
    tool's id so /v1/device/start carries it → the authorize page shows "Codex CLI
    wants to connect" (name + logo) and the server wires the tool onto the device
    (token tool scope + active_tool + device_tools) at approve time."""
    try:
        from atlaso_client.connect import maybe_autoconnect as _mc

        return _mc(TOOL)
    except Exception:
        return False


def log(name: str, msg: str) -> None:
    """Opt-in debug log (set ATLASO_DEBUG=1). Off by default — hooks stay quiet."""
    if not os.environ.get("ATLASO_DEBUG"):
        return
    try:
        base = (
            os.environ.get("ATLASO_GLOBAL_PATH")
            or os.environ.get("ATLASO_PATH")
            or str(Path.home() / ".atlaso")
        )
        d = Path(base)
        d.mkdir(parents=True, exist_ok=True)
        with open(d / f"atlaso-codex-{name}.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} {msg}\n")
    except Exception:
        pass
