"""sync (SessionStart background + Stop end-of-turn flush): sync the local cache.

Pushes any queued local memories up and pulls new ones down (other devices, this
session's captures). Launched DETACHED — by start.sh on SessionStart, and by
capture.py after each Stop (Codex has no SessionEnd, so the flush rides on Stop).
Same entrypoint everywhere — the work is identical.
"""
from __future__ import annotations

import sys

from . import _shim


def run(client) -> dict:
    return client.sync_once()


def main() -> int:
    # Also kick off connect if this machine isn't linked yet.
    _shim.maybe_autoconnect()
    # Sync lease: Codex + Claude Code share one cache/outbox on a machine; a fresh
    # lease means another sync is already in flight — skip instead of stampeding.
    from atlaso_client import _flush
    with _flush.lease() as acquired:
        if not acquired:
            return 0
        try:
            client = _shim.make_client()
        except Exception:
            return 0
        try:
            out = run(client)
            _shim.log("sync", f"{out}")
        except Exception as e:
            _shim.log("sync", f"error {e!r}")
        finally:
            try:
                client.close()
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
