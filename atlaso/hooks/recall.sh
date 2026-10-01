#!/usr/bin/env bash
# Atlaso Memory — recall hook (Codex UserPromptSubmit).
# Injects recalled memory as additionalContext. The shared guard (_guard.sh) bounds it and
# picks the built runtime or dev mode. Never breaks the turn (best-effort, always exit 0).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
# Shown to the user (systemMessage, never model context) when the runtime is still setting up.
ATLASO_NOTICE_NAME="Codex" atlaso_fg codex recall "$ATLASO_RECALL_BUDGET" atlaso_codex.recall
exit 0
