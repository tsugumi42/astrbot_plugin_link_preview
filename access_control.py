from __future__ import annotations

import re
from typing import Any


def parse_id_list(value: object) -> set[str]:
    if isinstance(value, (list, tuple, set)):
        candidates = [str(item) for item in value]
    else:
        candidates = re.split(r"[\s,，]+", str(value or ""))
    return {item.strip() for item in candidates if item and item.strip()}


def _message_obj(event: Any) -> Any:
    return getattr(event, "message_obj", None)


def group_id_from_event(event: Any) -> str:
    message_obj = _message_obj(event)
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


def user_id_from_event(event: Any) -> str:
    message_obj = _message_obj(event)
    for source in (message_obj, event):
        if not source:
            continue
        for attr in ("user_id", "sender_id"):
            value = getattr(source, attr, "")
            if value:
                return str(value)
    raw = getattr(message_obj, "raw_message", None) if message_obj else None
    if isinstance(raw, dict):
        value = raw.get("user_id") or raw.get("sender_id")
        if value:
            return str(value)
    getter = getattr(event, "get_sender_id", None)
    if callable(getter):
        try:
            value = getter()
        except Exception:
            value = ""
        if value:
            return str(value)
    return ""


def private_subtype_from_event(event: Any) -> str:
    message_obj = _message_obj(event)
    raw = getattr(message_obj, "raw_message", None) if message_obj else None
    if isinstance(raw, dict):
        return str(raw.get("sub_type") or raw.get("detail_type") or "").lower()
    return ""


def access_allowed(
    event: Any,
    *,
    group_mode: str = "all",
    group_ids: object = "",
    private_mode: str = "all",
    private_whitelist: object = "",
    private_blacklist: object = "",
) -> bool:
    group_id = group_id_from_event(event)
    if group_id:
        ids = parse_id_list(group_ids)
        if group_mode == "private_only":
            return False
        if group_mode == "whitelist":
            return group_id in ids
        if group_mode == "blacklist":
            return group_id not in ids
        return True

    user_id = user_id_from_event(event)
    if user_id and user_id in parse_id_list(private_whitelist):
        return True
    if user_id and user_id in parse_id_list(private_blacklist):
        return False
    if private_mode == "none":
        return False
    if private_mode == "whitelist":
        return False
    if private_mode == "blacklist":
        return True
    if private_mode == "friends":
        return private_subtype_from_event(event) == "friend"
    return True
