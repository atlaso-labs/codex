"""Codex SessionStart entrypoint: emit the local-only notice (systemMessage, USER-
facing) AND the Ambient Memory orientation block (additionalContext, MODEL-facing)
in ONE hook result. Either may be absent. Fast + fail-open; background sync stays
in start.sh.
"""
from __future__ import annotations

import json
import sys

from . import _shim, ambient, notice


def run(client) -> dict | None:
    """Merge notice + ambient into a single SessionStart hook output dict."""
    out: dict = {}
    try:
        n = notice.run(client)
        if n and n.get("systemMessage"):
            out["systemMessage"] = n["systemMessage"]
    except Exception:
        pass
    try:
        a = ambient.run(client)
        if a and a.get("hookSpecificOutput"):
            out["hookSpecificOutput"] = a["hookSpecificOutput"]
    except Exception:
        pass
    return out or None


def main() -> int:
    try:
        client = _shim.make_client()
    except Exception:
        return 0
    out = None
    try:
        out = run(client)
    except Exception as e:
        _shim.log("start", f"error {e!r}")
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
