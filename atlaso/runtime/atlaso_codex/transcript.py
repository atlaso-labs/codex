"""Read a Codex transcript JSONL and pull message text.

Codex exposes ``transcript_path`` on the hook stdin payload (verified on
developers.openai.com/codex/hooks; may be null). The exact per-line JSON shape is
NOT pinned by the docs, so this reader is deliberately tolerant of the common
message-object shapes:

  {"type": "user"|"assistant"|..., "message": {"content": ...}}   (Claude-Code-like)
  {"role": "user"|"assistant"|..., "content": ...}                (chat-style)

``content`` may be a plain string or a list of blocks; only text blocks
(``{"type":"text","text":...}`` or ``{"type":"input_text"/"output_text"}``) carry
prose — tool calls / results / reasoning blocks are skipped.

For the Stop hook, Codex ALSO hands us ``last_assistant_message`` directly on
stdin, so capture never depends on parsing the transcript correctly — the
transcript only enriches the saved exchange with the matching user prompt.
"""
from __future__ import annotations

import json

_TEXT_BLOCK_TYPES = {"text", "input_text", "output_text"}


def _is_text_block(el: dict) -> bool:
    """True for a prose block. Accepts the known text types, or a block with a
    ``text`` key and NO explicit type. Blocks with a non-text type (thinking,
    tool_use, tool_result, reasoning, …) are skipped even if they carry ``text``."""
    typ = el.get("type")
    if typ in _TEXT_BLOCK_TYPES:
        return True
    if typ is None and "text" in el:
        return True
    return False


def _flatten(content: object) -> str:
    if isinstance(content, list):
        parts = []
        for el in content:
            if isinstance(el, dict):
                if _is_text_block(el):
                    t = el.get("text", "")
                    if isinstance(t, str) and t:
                        parts.append(t)
            elif isinstance(el, str):
                parts.append(el)
        return " ".join(p for p in parts if p).strip()
    if isinstance(content, str):
        return content.strip()
    return ""


def _role(obj: dict) -> str:
    """Normalise role across the two shapes: prefer 'role', fall back to 'type'."""
    r = obj.get("role") or obj.get("type") or ""
    return r if isinstance(r, str) else ""


def _content(obj: dict) -> object:
    """The message body, across both shapes."""
    msg = obj.get("message")
    if isinstance(msg, dict) and "content" in msg:
        return msg.get("content")
    return obj.get("content")


def last_exchange(path: str) -> tuple[str, str]:
    """Return (last_user_text, assistant_reply_to_it); either may be ''.

    The assistant text is ONLY a reply AFTER the last user message — never an
    earlier turn's — so a Stop hook firing before the reply is flushed pairs the
    new question with '' rather than a stale answer.
    """
    msgs: list[tuple[str, str]] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if not isinstance(obj, dict):
                    continue
                role = _role(obj)
                if role not in ("user", "assistant"):
                    continue
                text = _flatten(_content(obj))
                if text:
                    msgs.append((role, text))
    except (FileNotFoundError, OSError):
        return "", ""

    last_user_idx = None
    for i, (role, _) in enumerate(msgs):
        if role == "user":
            last_user_idx = i
    if last_user_idx is None:
        return "", ""

    last_user = msgs[last_user_idx][1]
    asst = ""
    for role, text in msgs[last_user_idx + 1:]:
        if role == "assistant":
            asst = text
    return last_user, asst
