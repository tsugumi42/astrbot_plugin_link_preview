from __future__ import annotations

import time
from typing import Any

import astrbot.api.message_components as Comp
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .access_control import access_allowed
from .extractors import SupportedLink, extract_supported_links
from .message_parts import compose_preview_parts
from .providers.base import PreviewFetchError
from .providers.twitter import fetch_twitter_preview
from .providers.youtube import fetch_youtube_preview
from .status import send_processing_status


@register("astrbot_plugin_link_preview", "local", "自动预览 YouTube 和 Twitter/X 链接", "0.1.0")
class LinkPreviewPlugin(Star):
    def __init__(self, context: Context, config: dict[str, Any] | None = None):
        super().__init__(context)
        self.config = config or {}
        self._last_preview_at: dict[str, float] = {}

    def _cfg(self, key: str, default: Any) -> Any:
        if key in self.config:
            return self.config.get(key, default)
        for group in self.config.values():
            if isinstance(group, dict) and key in group:
                return group.get(key, default)
        return default

    def _cooldown_key(self, event: AstrMessageEvent) -> str:
        message_obj = event.message_obj
        return getattr(message_obj, "session_id", "") or event.unified_msg_origin

    def _cooldown_ready(self, key: str) -> bool:
        now = time.monotonic()
        cooldown = max(0, int(self._cfg("cooldown_seconds", 10)))
        last = self._last_preview_at.get(key, 0)
        if now - last < cooldown:
            return False
        self._last_preview_at[key] = now
        return True

    def _enabled(self, link: SupportedLink) -> bool:
        if link.platform == "youtube":
            return bool(self._cfg("enable_youtube", True))
        if link.platform == "twitter":
            return bool(self._cfg("enable_twitter", True))
        return False

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        if not access_allowed(
            event,
            group_mode=str(self._cfg("group_mode", "all")),
            group_ids=self._cfg("group_ids", ""),
            private_mode=str(self._cfg("private_mode", "all")),
            private_whitelist=self._cfg("private_whitelist", ""),
            private_blacklist=self._cfg("private_blacklist", ""),
        ):
            return
        links = [item for item in extract_supported_links(event.message_str or "") if self._enabled(item)]
        if not links:
            return
        if not self._cooldown_ready(self._cooldown_key(event)):
            return

        max_links = max(1, int(self._cfg("max_links_per_message", 1)))
        timeout = max(3, int(self._cfg("request_timeout_seconds", 10)))
        if bool(self._cfg("send_processing_status", True)):
            await send_processing_status(event, "已收到链接，正在读取预览信息。")
        for link in links[:max_links]:
            try:
                if link.platform == "youtube":
                    preview = await fetch_youtube_preview(
                        link.url,
                        timeout,
                        fetch_page_details=bool(self._cfg("youtube_fetch_page_details", True)),
                        detail_timeout_seconds=max(1, int(self._cfg("youtube_detail_timeout_seconds", 4))),
                    )
                elif link.platform == "twitter":
                    preview = await fetch_twitter_preview(link.url, timeout)
                else:
                    continue

                send_images = (
                    link.platform == "youtube"
                    and bool(self._cfg("send_thumbnail_image", False))
                    or link.platform == "twitter"
                    and bool(self._cfg("send_twitter_images", True))
                )
                chain = []
                for kind, value in compose_preview_parts(
                    preview,
                    send_images=send_images,
                    image_position=str(self._cfg("image_position", "after_text")),
                    fields=self._cfg(
                        "youtube_fields" if link.platform == "youtube" else "twitter_fields",
                        None,
                    ),
                ):
                    if kind == "image":
                        chain.append(Comp.Image.fromURL(value))
                    else:
                        chain.append(Comp.Plain(value))
                yield event.chain_result(chain)
            except PreviewFetchError as exc:
                logger.warning("link preview failed: %s", exc)
                yield event.plain_result(str(exc))
