from __future__ import annotations

import time
from typing import Any

import astrbot.api.message_components as Comp
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .extractors import SupportedLink, extract_supported_links
from .formatters import format_preview_text
from .providers.base import PreviewFetchError
from .providers.twitter import fetch_twitter_preview
from .providers.youtube import fetch_youtube_preview


@register("astrbot_plugin_link_preview", "local", "自动预览 YouTube 和 Twitter/X 链接", "0.1.0")
class LinkPreviewPlugin(Star):
    def __init__(self, context: Context, config: dict[str, Any] | None = None):
        super().__init__(context)
        self.config = config or {}
        self._last_preview_at: dict[str, float] = {}

    def _cfg(self, key: str, default: Any) -> Any:
        return self.config.get(key, default)

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
        links = [item for item in extract_supported_links(event.message_str or "") if self._enabled(item)]
        if not links:
            return
        if not self._cooldown_ready(self._cooldown_key(event)):
            return

        max_links = max(1, int(self._cfg("max_links_per_message", 1)))
        timeout = max(3, int(self._cfg("request_timeout_seconds", 10)))
        for link in links[:max_links]:
            try:
                if link.platform == "youtube":
                    preview = await fetch_youtube_preview(link.url, timeout)
                elif link.platform == "twitter":
                    preview = await fetch_twitter_preview(link.url, timeout)
                else:
                    continue

                chain = [Comp.Plain(format_preview_text(preview))]
                send_images = (
                    link.platform == "youtube"
                    and bool(self._cfg("send_thumbnail_image", False))
                    or link.platform == "twitter"
                    and bool(self._cfg("send_twitter_images", True))
                )
                if send_images:
                    for media in preview.media:
                        if media.kind == "image":
                            chain.append(Comp.Image.fromURL(media.url))
                yield event.chain_result(chain)
            except PreviewFetchError as exc:
                logger.warning("link preview failed: %s", exc)
                yield event.plain_result(str(exc))
