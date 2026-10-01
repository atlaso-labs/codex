# Shared resolver for the Atlaso Codex hooks. Sourced by each hook.
#
# Two modes, auto-detected:
#   BUILT/installed → a vendored `runtime/` dir sits next to hooks/ (built by
#     package.py). We run the bundled packages on the runtime's own venv, built
#     once from the shipped uv.lock by a detached
#     `uv sync --frozen`, so the plugin is fully self-contained — no repo, no dev venv.
#   DEV/in-repo     → no runtime/; fall back to the SDK venv + the platform
#     siblings (what our tests use).
#
# atlaso_fg / atlaso_bg / atlaso_capture (in _guard.sh) run a python module in whichever
# mode applies, under a hard deadline, and NEVER return a turn-breaking non-zero.
#
# NOTE: Codex exposes the plugin root as PLUGIN_ROOT (not CLAUDE_PLUGIN_ROOT). The
# hook shims resolve their own dir from BASH_SOURCE, so they don't depend on it.

_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_PLUGIN_DIR="$(cd "$_HERE/.." && pwd)"

# Deadlines, runtime readiness, detached capture and the content-free skip counter live in
# the shared guard (byte-identical in every Python connector; see its header).
# shellcheck disable=SC2034  # read by the sourced _guard.sh
ATLASO_GUARD_ROOT="$_PLUGIN_DIR"
# shellcheck source=/dev/null
. "$_HERE/_guard.sh"
