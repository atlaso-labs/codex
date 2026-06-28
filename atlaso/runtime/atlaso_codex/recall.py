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
import re
import sys

from atlaso_client import _project

from . import _shim

_BANNER = "Atlaso Memory"
# Stop stored content from forging our own banner line.
_FENCE_RE = re.compile(r"(?i)=+\s*Atlaso Memory\s*=+")


def _clean(text: str) -> str:
    return _FENCE_RE.sub("[atlaso]", (text or "").strip())


def render(results: list[dict]) -> str | None:
    """Build the injection block from recall results, or None if nothing usable."""
    lines = []
    for r in results or []:
        content = _clean(r.get("content", ""))
        if content:
            lines.append("- " + content)
    if not lines:
        return None
    return f"=== {_BANNER} ===\n" + "\n".join(lines) + f"\n=== {_BANNER} ==="


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
    res = client.recall(prompt, limit=limit, project=_project.project_key(), session=session)
    block = render(res.get("results", []))
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
