"""recall hook (Codex UserPromptSubmit): inject recalled memory.

Codex fires UserPromptSubmit BEFORE the model processes the input and carries the
user's text on stdin as `prompt` (verified on developers.openai.com/codex/hooks).
We query the memory client and inject the hits as a plain, branded block via the
documented hook output shape:

    {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                            "additionalContext": "=== Atlaso Memory ===\\n- …"}}

Codex adds `additionalContext` to the turn as extra developer context. No
instructions, no warnings — just the brand at top and bottom; the model decides how
to use it. Synchronous + cheap (server recall, or local cache when offline). Fails
open: any error → no injection, the turn proceeds.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from atlaso_client import _project, _render

from . import _shim

_BANNER = "Atlaso Memory"


def _clean(text: str) -> str:
    """Stored text → one safe line: the shared renderer contract
    (atlaso_client._render.sanitize_line) in this connector's pre-B1 spacing mode
    ("join_lines": a line break becomes one space, tabs are kept), so a saved note can
    never add a line, forge a fence or carry invisible/bidi characters into the
    injected block, and ordinary one-line notes keep their exact bytes."""
    return _render.sanitize_line(text, "join_lines")


def render(results: list[dict], now: datetime | None = None) -> str | None:
    """Build the injection block from recall results, or None if nothing usable.
    Each line carries its note's UTC day when the server sent created_at (rung
    85bcf262 card B1; the shared label is atlaso_client._render._date_label).
    Undated lines come first (``_render.undated_first``)."""
    now = now or datetime.now(timezone.utc)
    lines = []
    for r in results or []:
        content = _clean(r.get("content", ""))
        if content:
            date = _render._date_label(r.get("created_at"), now)
            lines.append((date is not None, "- " + (f"[{date}] " if date else "") + content))
    if not lines:
        return None
    return f"=== {_BANNER} ===\n" + "\n".join(_render.undated_first(lines)) + f"\n=== {_BANNER} ==="


def run(payload: dict, client) -> dict | None:
    """Pure logic (testable): payload + client → the hookSpecificOutput dict or None."""
    prompt = (payload.get("prompt") or payload.get("message") or "").strip()
    if not prompt:
        return None
    try:
        limit = int(os.environ.get("ATLASO_RECALL_LIMIT", "5"))
    except ValueError:
        limit = 5
    # Per-project scope (personal + THIS project, like the other connectors — no
    # cross-project leak) + thread Codex's session_id so the server logs which
    # memories were injected for the recall-usefulness feedback loop.
    session = payload.get("session_id") or payload.get("session")
    # Project scope from the event's cwd (process cwd is the vendored runtime/,
    # never the user's repo — same fix as capture).
    from pathlib import Path
    cwd = payload.get("cwd")
    project = _project.project_key(Path(cwd)) if cwd else _project.project_key()
    res = client.recall(prompt, limit=limit, project=project, session=session)
    results = res.get("results", [])
    block = render(results)
    # Debug-only proof the per-turn hook fired (counts only, never content).
    n = len(results or [])
    _shim.log("recall", f"fired source={res.get('source')} results={n} "
                        f"injected={bool(block)}")
    if not block:
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": block,
        }
    }


def main() -> int:
    if _shim.is_recursive():
        return 0
    # If not connected yet, kick off the (detached) browser-authorize flow in the
    # background — so the user's next prompt after installing the plugin triggers
    # it automatically. Recall still proceeds (local) meanwhile.
    _shim.maybe_autoconnect()
    payload = _shim.read_payload()
    try:
        client = _shim.make_client()
    except Exception:
        return 0
    out = None
    try:
        out = run(payload, client)
    except Exception as e:
        _shim.log("recall", f"error {e!r}")
    finally:
        try:
            client.close()
        except Exception:
            pass
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
