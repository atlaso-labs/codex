#!/usr/bin/env bash
# Atlaso Memory — recall hook (Codex UserPromptSubmit).
# Injects recalled memory as additionalContext. Resolver picks built (uv runtime)
# or dev mode. Never breaks the turn (best-effort, always exit 0).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
atlaso_run atlaso_codex.recall
exit 0
