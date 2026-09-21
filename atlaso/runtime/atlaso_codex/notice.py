"""SessionStart notice: if this device is LOCAL-ONLY, tell the user — once.

Prints a Codex SessionStart hook result with a ``systemMessage`` (a banner the
USER sees — NOT injected into the model's context; `systemMessage` is a documented
common hook output field on developers.openai.com/codex/hooks) when the device is
running local-only. Shown at most once per distinct local-only episode (keyed by
the state's ``since`` timestamp), so we never nag every session. A cloud-linked
device prints nothing. Fast + file-only (no network). Never breaks the session —
any error → silent exit 0.
"""
from __future__ import annotations

import json
import sys

from . import _shim

_APP = "https://app.atlaso.ai"


def _grace_message(grace: dict) -> str:
    """The escalating upgrade banner shown DURING the post-downgrade grace window
    (the tool is still syncing; the expensive features are already off)."""
    days = grace.get("days_left")
    tools = grace.get("tools_connected") or 0
    head = (
        f"Atlaso · your Pro plan ended. Free keeps 1 tool — you have {tools} "
        "connected. "
    )
    if days is not None and days <= 1:
        return (
            head + "Last day: upgrade at " + _APP + " to keep them all, or we'll "
            "keep your most-recently-used tool and unlink the rest. Your memory "
            "stays safe either way."
        )
    if days is not None and days <= 2:
        return (
            head + f"{days} days left — upgrade at {_APP} to keep them all, or "
            "pick one to keep. Your memory stays safe."
        )
    n = f"{days} days" if days is not None else "A few days"
    return (
        head + f"{n} left to upgrade at {_APP} and keep them all, or choose one "
        "to keep. Your memory stays safe."
    )


def build_message(mode: dict) -> str | None:
    """The user-facing banner: a downgrade-grace warning (shown while still
    linked), else a local-only notice, else nothing."""
    grace = mode.get("grace")
    if grace and grace.get("in_grace"):
        return _grace_message(grace)
    if mode.get("mode") != "local_only":
        return None
    reason = mode.get("reason")
    # "revoked" is the legacy spelling; the client now writes the precise
    # auth_rejected / reconnect_required — all three deserve the banner.
    if reason in ("revoked", "auth_rejected", "reconnect_required"):
        return (
            "Atlaso · this device was disconnected — running in local-only mode. "
            "Your memory still works locally; reconnect at " + _APP + " to resume "
            "cloud sync."
        )
    if reason == "not_entitled":
        return (
            "Atlaso · Codex isn't your active tool on the free plan — running in "
            "local-only mode. Switch tools or upgrade at " + _APP + "."
        )
    # not_connected → the autoconnect flow handles first-time linking; stay quiet.
    return None


def _marker_path():
    from atlaso_client import config

    return config.atlaso_dir() / "notice_seen_codex"


def _already_shown(since) -> bool:
    try:
        return _marker_path().read_text().strip() == str(since)
    except OSError:
        return False


def _mark_shown(since) -> None:
    try:
        p = _marker_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(since))
    except OSError:
        pass


def _dedupe_key(mode: dict) -> str:
    """What makes this banner 'the same' for once-per-episode de-dupe. For grace
    we key on the day count so the COUNTDOWN re-shows as it ticks down (5→4→…),
    but not twice on the same day. For local-only we key on the episode `since`."""
    grace = mode.get("grace")
    if grace and grace.get("in_grace"):
        return f"grace:{grace.get('days_left')}"
    return str(mode.get("since") or 0)


def _degraded_banner(mode: dict) -> tuple[str, str] | None:
    """(message, dedupe_key) when the device is LINKED but server recall keeps failing — the fail-open path that
    otherwise degrades recall to the local keyword floor with nobody told (production audit E6 / C15; the
    interventional falsifier of LabDirector 160ff6e9: keyed on the EXISTING fallback episode, no emitter changed).
    Byte-identical to the Claude Code connector's banner so the two surfaces stay in parity. Keyed on the episode's
    nonce (_fallback.episode_key; first_ts alone collided on same-second reform, cc61a3cf) so it shows once per episode, and clears itself on the next successful server recall."""
    if mode.get("mode") != "linked":
        return None
    try:
        from atlaso_client import _fallback
        ep = _fallback.episode()
    except Exception:
        return None
    if not ep:
        return None
    return (
        "Atlaso · cloud recall isn't responding — memory is running from this "
        "device's local cache (results may be shallower). Capture and sync are "
        "unaffected; this clears on its own once the service responds.",
        _fallback.episode_key(ep),
    )


class NoticeOutput(dict):
    """Serializable hook output with an un-serialized pending acknowledgement."""

    def __init__(self, output=None, *, key: str | None = None):
        super().__init__(output or {})
        self.notice_key = key

    def acknowledge(self) -> None:
        # Call only after the complete hook JSON has been written and flushed.
        # A timeout, broken pipe or aborted construction leaves the notice due.
        if self.notice_key is not None:
            _mark_shown(self.notice_key)


def run(client) -> NoticeOutput | None:
    """Prepare a notice without consuming its once-per-episode marker."""
    mode = client.cloud_mode()
    msg = build_message(mode)
    key = _dedupe_key(mode) if msg else None
    if not msg:
        degraded = _degraded_banner(mode)
        if not degraded:
            return None
        msg, key = degraded
    if _already_shown(key):
        return None
    return NoticeOutput({"systemMessage": msg}, key=key)


def main() -> int:
    try:
        client = _shim.make_client()
    except Exception:
        return 0
    out = None
    try:
        out = run(client)
    except Exception as e:
        _shim.log("notice", f"error {e!r}")
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


if __name__ == "__main__":
    sys.exit(main())
