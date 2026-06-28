"""capture hook (Codex Stop): save the just-finished exchange to memory.

Codex fires Stop on turn completion and hands us `last_assistant_message` directly
on stdin, plus `transcript_path` (which we read to recover the matching user
prompt). We hand the exchange to the client as an INSTANT LOCAL write (no network
on the hot path). A light commodity filter skips trivial acks so we don't store
"ok"/"thanks"; the real "is this worth keeping" gate runs server-side.

IMPORTANT — Codex has NO SessionEnd event (verified: neither /codex/hooks nor
/codex/config-reference lists one). So the end-of-turn FLUSH that the Claude Code
connector puts on SessionEnd rides on Stop here: after the local write we kick off
a detached background sync. Stop fires every turn, so we sync at most once per turn
in the background (cheap; never blocks the turn). Never breaks the turn.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

from . import _shim
from .transcript import last_exchange

# Trivial single-word acknowledgements — not worth a memory.
_TRIVIAL = re.compile(
    r"^(?:ok(?:ay)?|yes|no|yep|nope|thanks?|ty|sure|cool|nice|got it|k|kk|"
    r"done|continue|go on|next|stop|y|n)\W*$",
    re.IGNORECASE,
)


def is_substantive(text: str) -> bool:
    """Light client-side noise filter (commodity, not the server gate)."""
    t = (text or "").strip()
    if len(t) < 16:
        return False
    if _TRIVIAL.match(t):
        return False
    if len(t.split()) < 3:
        return False
    return True


def run(payload: dict, client) -> bool:
    """Pure logic (testable): returns True if a memory was queued.

    Prefers the transcript for both sides; falls back to Codex's
    `last_assistant_message` (Stop stdin) for the assistant text and `prompt` for
    the user text when the transcript is unavailable/unparsable.

    Routes through the shared `Client.capture()` pipeline (secret-scrub → scope →
    near-dup → tagged remember) so a transcript carrying a secret is REDACTED
    before it touches the local cache/outbox/FTS. NEVER call the low-level
    `remember()` here — it skips the scrubber (the bug this connector once had).
    """
    transcript = payload.get("transcript_path") or ""
    user_text, asst_text = last_exchange(transcript) if transcript else ("", "")
    if not user_text:
        user_text = (payload.get("prompt") or "").strip()
    if not asst_text:
        asst_text = (payload.get("last_assistant_message") or "").strip()
    if not is_substantive(user_text):
        return False
    res = client.capture(user_text, asst_text or None, source_tag="codex", push=False)
    return bool(res.get("saved"))


def _flush_detached() -> None:
    """Kick off a background sync (the end-of-turn flush, since Codex has no
    SessionEnd). Detached + best-effort — never blocks or breaks the turn."""
    try:
        subprocess.Popen(
            [sys.executable, "-m", "atlaso_codex.sync"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=dict(os.environ),
        )
    except Exception:
        pass


def main() -> int:
    if _shim.is_recursive():
        return 0
    payload = _shim.read_payload()
    try:
        client = _shim.make_client()
    except Exception:
        return 0
    try:
        saved = run(payload, client)
        _shim.log("capture", f"saved={saved}")
    except Exception as e:
        _shim.log("capture", f"error {e!r}")
    finally:
        try:
            client.close()
        except Exception:
            pass
    # End-of-turn flush (no SessionEnd in Codex) — detached, after the local write.
    _flush_detached()
    return 0


if __name__ == "__main__":
    sys.exit(main())
