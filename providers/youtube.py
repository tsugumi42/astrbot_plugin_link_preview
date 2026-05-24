from __future__ import annotations

import json
from urllib.parse import quote
from urllib.request import Request, urlopen

from ..models import MediaItem, Preview
from .base import PreviewFetchError
from .meta import parse_meta


def parse_youtube_html(url: str, html: str) -> Preview:
    meta = parse_meta(html)
    image = meta.get(("property", "og:image"), "")
    media = [MediaItem("image", image)] if image else []
    return Preview(
        platform="youtube",
        url=url,
        title=meta.get(("property", "og:title"), ""),
        author=meta.get(("itemprop", "name"), ""),
        description=meta.get(("property", "og:description"), ""),
        media=media,
    )


def parse_youtube_oembed_payload(url: str, payload: dict[str, object]) -> Preview:
    image = str(payload.get("thumbnail_url") or "")
    media = [MediaItem("image", image)] if image else []
    return Preview(
        platform="youtube",
        url=url,
        title=str(payload.get("title") or ""),
        author=str(payload.get("author_name") or ""),
        description="",
        media=media,
    )


def _fetch_youtube_oembed(url: str, timeout_seconds: int) -> Preview:
    endpoint = "https://www.youtube.com/oembed?url=" + quote(url, safe="") + "&format=json"
    request = Request(endpoint, headers={"User-Agent": "Mozilla/5.0 AstrBotLinkPreview/0.1"})
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8", errors="replace"))
    if not isinstance(payload, dict):
        raise ValueError("invalid oEmbed payload")
    return parse_youtube_oembed_payload(url, payload)


def _fetch_youtube_html(url: str, timeout_seconds: int) -> Preview:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 AstrBotLinkPreview/0.1"})
    with urlopen(request, timeout=timeout_seconds) as response:
        html = response.read().decode("utf-8", errors="replace")
    return parse_youtube_html(url, html)


async def fetch_youtube_preview(url: str, timeout_seconds: int) -> Preview:
    try:
        return _fetch_youtube_oembed(url, timeout_seconds)
    except Exception as exc:
        oembed_error = exc
    try:
        return _fetch_youtube_html(url, timeout_seconds)
    except Exception as exc:
        raise PreviewFetchError(f"YouTube 页面请求失败：{exc}；oEmbed 也失败：{oembed_error}") from exc
