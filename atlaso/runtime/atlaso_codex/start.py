"""Codex SessionStart entrypoint: emit the local-only notice (systemMessage, USER-
facing) AND the Ambient Memory orientation block (additionalContext, MODEL-facing)
in ONE hook result. Either may be absent. Bounded + fail-open; background sync stays
in start.sh.
"""
from __future__ import annotations

import json
import sys

from . import _shim, ambient, notice


def run(client, payload: dict | None = None) -> dict | None:
    """Merge notice + ambient into a single SessionStart hook output dict."""
    out = notice.NoticeOutput()
    try:
        n = notice.run(client)
        if n and n.get("systemMessage"):
            out["systemMessage"] = n["systemMessage"]
            out.notice_key = getattr(n, "notice_key", None)
    except Exception:
        pass
    try:
        a = ambient.run(client, payload)
        if a and a.get("hookSpecificOutput"):
            out["hookSpecificOutput"] = a["hookSpecificOutput"]
    except Exception:
        pass
    return out or None


def _main() -> int:
    if _shim.is_recursive():
        return 0
    payload = _shim.read_payload()
    try:
        client = _shim.make_client()
    except Exception:
        return 0
    out = None
    try:
        out = run(client, payload)
    except Exception as e:
        _shim.log("start", f"error {e!r}")
    finally:
        try:
            client.close()
        except Exception:
            pass
    if out:
        try:
            print(json.dumps(out), flush=True)
        except OSError:
            return 0
        out.acknowledge()
    return 0


def main() -> int:
    # Bound credential bootstrap, policy validation, rendering and cleanup as one
    # operation. The host manifest adds a 5s process fuse (also on Windows).
    from atlaso_client._budget import HookTimeout, hook_budget
    try:
        with hook_budget(seconds=3.0):
            return _main()
    except HookTimeout:
        return 0


if __name__ == "__main__":
    sys.exit(main())
