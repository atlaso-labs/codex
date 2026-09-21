#!/usr/bin/env bash
# Atlaso Memory — start hook (Codex SessionStart).
# Fires on session start/resume. Foreground + bounded (fresh ambient policy validation): if the
# device is local-only, show a one-time banner (its stdout IS a SessionStart
# systemMessage). Then sync in the BACKGROUND (detached) without waiting for the full sync. In built mode the first uv run also warms the runtime env.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
atlaso_run atlaso_codex.start
( atlaso_run atlaso_codex.sync ) >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
