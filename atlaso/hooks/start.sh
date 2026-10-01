#!/usr/bin/env bash
# Atlaso Memory — start hook (Codex SessionStart).
# Fires on session start/resume. Foreground + bounded (fresh ambient policy validation): if the
# device is local-only, show a one-time banner (its stdout IS a SessionStart
# systemMessage). Then sync in the BACKGROUND (detached) without waiting for the full sync. In built mode a runtime that is not ready yet is warmed in the background (never inside this hook).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
atlaso_fg codex start "$ATLASO_START_BUDGET" atlaso_codex.start
atlaso_bg codex start atlaso_codex.sync
exit 0
