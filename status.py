from __future__ import annotations

from typing import Any


def event_group_id(event: Any) -> str:
    message_obj = getattr(event, "message_obj", None)
    group_id = getattr(message_obj, "group_id", "") if message_obj else ""
    if group_id:
        return str(group_id)
    getter = getattr(event, "get_group_id", None)
    if callable(getter):
        try:
            value = getter()
        except Exception:
            value = ""
        if value:
            return str(value)
    return ""


def event_message_id(event: Any) -> str:
    message_obj = getattr(event, "message_obj", None)
    for source in (message_obj, event):
        if not source:
            continue
        for attr in ("message_id", "id"):
            value = getattr(source, attr, "")
            if value:
                return str(value)
    raw = getattr(message_obj, "raw_message", None) if message_obj else None
    if isinstance(raw, dict):
        value = raw.get("message_id") or raw.get("id")
        if value:
            return str(value)
    return ""


async def send_processing_status(event: Any, text: str, *, emoji_id: str = "289") -> None:
    import astrbot.api.message_components as Comp
    from astrbot.api import logger

    group_id = event_group_id(event)
    message_id = event_message_id(event)
    bot = getattr(event, "bot", None)
    if group_id and message_id and bot:
        try:
            await bot.call_action(
                "set_msg_emoji_like",
                message_id=int(message_id),
                emoji_id=str(emoji_id),
                emoji_type="1",
                set=True,
            )
            return
        except Exception as exc:
            logger.debug("link preview status reaction failed: %s", exc)
    try:
        await event.send(event.chain_result([Comp.Plain(text)]))
    except Exception as exc:
        logger.debug("link preview status text failed: %s", exc)
