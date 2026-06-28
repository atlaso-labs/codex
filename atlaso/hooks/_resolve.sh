# Shared resolver for the Atlaso Codex hooks. Sourced by each hook.
#
# Two modes, auto-detected:
#   BUILT/installed → a vendored `runtime/` dir sits next to hooks/ (built by
#     package.py). We run the bundled packages on a uv-managed Python + deps
#     (`uv run`), so the plugin is fully self-contained — no repo, no dev venv.
#   DEV/in-repo     → no runtime/; fall back to the SDK venv + the platform
#     siblings (what our tests use).
#
# `atlaso_run <module>` runs a python module in whichever mode applies, forwarding
# stdin/stdout, and NEVER returns a turn-breaking non-zero (memory is best-effort).
#
# NOTE: Codex exposes the plugin root as PLUGIN_ROOT (not CLAUDE_PLUGIN_ROOT). The
# hook shims resolve their own dir from BASH_SOURCE, so they don't depend on it.

_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_PLUGIN_DIR="$(cd "$_HERE/.." && pwd)"

atlaso_run() {
  local mod="$1"
  if [ -d "$_PLUGIN_DIR/runtime" ]; then
    # built/installed: portable uv-managed runtime (Python + httpx + mcp, cached)
    command -v uv >/dev/null 2>&1 || return 0
    ( cd "$_PLUGIN_DIR/runtime" && uv run --quiet python -m "$mod" ) || true
  else
    # dev/in-repo
    local platform py
    platform="$(cd "$_PLUGIN_DIR/../.." && pwd)"
    py="${ATLASO_PY:-$platform/sdk/.venv/bin/python}"
    [ -x "$py" ] || return 0
    PYTHONPATH="$_PLUGIN_DIR:$platform/client${PYTHONPATH:+:$PYTHONPATH}" "$py" -m "$mod" || true
  fi
}
