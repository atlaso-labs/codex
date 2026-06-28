#!/usr/bin/env bash
# Atlaso Memory — capture hook (Codex Stop).
# Saves the just-finished exchange (instant local; synced later) and, because
# Codex has NO SessionEnd event, kicks off the end-of-turn flush in the background.
# Best-effort, always exit 0.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
atlaso_run atlaso_codex.capture
exit 0
