from __future__ import annotations

import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

from ..models import MediaItem, Preview
from .base import PreviewFetchError
from .meta import parse_meta


def _first_regex(patterns: list[str], text: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""


def _clean_metric(value: str) -> str:
    return value.replace(",", "").strip()


def parse_youtube_html(url: str, html: str) -> Preview:
    meta = parse_meta(html)
    image = meta.get(("property", "og:image"), "")
    media = [MediaItem("image", image)] if image else []
    published_at = (
        meta.get(("itemprop", "datePublished"), "")
        or _first_regex([r'"publishDate"\s*:\s*"([^"]+)"', r'"datePublished"\s*:\s*"([^"]+)"'], html)
    )
    view_count = _clean_metric(
        _first_regex([r'"viewCount"\s*:\s*"([0-9,]+)"', r'"interactionCount"\s*content="([0-9,]+)"'], html)
    )
    like_count = _clean_metric(
        _first_regex(
            [
                r'"label"\s*:\s*"([0-9,.]+)\s+likes?"',
                r'"accessibilityData"\s*:\s*\{\s*"label"\s*:\s*"([0-9,.]+)\s+likes?"',
            ],
            html,
        )
    )
    metrics = {}
    if view_count:
        metrics["观看"] = view_count
    if like_count:
        metrics["点赞"] = like_count
    return Preview(
        platform="youtube",
        url=url,
        title=meta.get(("property", "og:title"), ""),
        author=meta.get(("itemprop", "name"), ""),
        published_at=published_at,
        description=meta.get(("property", "og:description"), ""),
        metrics=metrics,
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


def _merge_preview(primary: Preview, details: Preview) -> Preview:
    return Preview(
        platform=primary.platform,
        url=primary.url,
        title=primary.title or details.title,
        author=primary.author or details.author,
        published_at=details.published_at or primary.published_at,
        description=details.description or primary.description,
        metrics=details.metrics or primary.metrics,
        media=primary.media or details.media,
    )


async def fetch_youtube_preview(
    url: str,
    timeout_seconds: int,
    *,
    fetch_page_details: bool = True,
    detail_timeout_seconds: int = 4,
) -> Preview:
    try:
        preview = _fetch_youtube_oembed(url, timeout_seconds)
    except Exception as exc:
        oembed_error = exc
    else:
        if not fetch_page_details:
            return preview
        try:
            details = _fetch_youtube_html(url, max(1, detail_timeout_seconds))
            return _merge_preview(preview, details)
        except Exception:
            return preview
    try:
        return _fetch_youtube_html(url, timeout_seconds)
    except Exception as exc:
        raise PreviewFetchError(f"YouTube 页面请求失败：{exc}；oEmbed 也失败：{oembed_error}") from exc
