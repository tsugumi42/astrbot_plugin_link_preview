from __future__ import annotations

import json
import re
from urllib.request import Request, urlopen

from ..models import MediaItem, Preview
from .base import PreviewFetchError
from .meta import parse_meta

STATUS_RE = re.compile(r"https?://(?:www\.)?(?:x|twitter)\.com/([^/\s]+)/status/(\d+)")
IMAGE_RE = re.compile(r"\.(?:jpg|jpeg|png|webp)(?:\?|$)", re.IGNORECASE)
VIDEO_RE = re.compile(r"\.(?:mp4|m3u8|mov)(?:\?|$)", re.IGNORECASE)


def _media_kind_from_url(url: str) -> str:
    if IMAGE_RE.search(url) or "pbs.twimg.com/media/" in url:
        return "image"
    if VIDEO_RE.search(url) or "video.twimg.com/" in url:
        return "video"
    if ".gif" in url.lower():
        return "gif"
    return "link"


def _media_kind_from_type(value: object, fallback_url: str) -> str:
    media_type = str(value or "").lower()
    if media_type in {"photo", "image"}:
        return "image"
    if media_type in {"gif", "animated_gif"}:
        return "gif"
    if media_type == "video":
        return "video"
    return _media_kind_from_url(fallback_url)


def parse_twitter_html(url: str, html: str) -> Preview:
    meta = parse_meta(html)
    title = meta.get(("property", "og:title"), "")
    description = meta.get(("property", "og:description"), "")
    author = title.split(":", 1)[0].strip() if ":" in title else ""
    image = meta.get(("property", "og:image"), "")
    media = [MediaItem("image", image)] if image and "pbs.twimg.com" in image else []
    return Preview(
        platform="twitter",
        url=url,
        title=title,
        author=author,
        description=description,
        media=media,
    )


def parse_vxtwitter_payload(url: str, payload: dict) -> Preview:
    display_name = str(payload.get("user_name") or "").strip()
    screen_name = str(payload.get("user_screen_name") or "").strip()
    if screen_name and display_name and screen_name != display_name:
        author = f"{display_name} (@{screen_name})"
    else:
        author = f"@{screen_name}" if screen_name else display_name
    media = []
    for item in payload.get("media_extended", []) or []:
        if not isinstance(item, dict):
            continue
        media_url = str(item.get("url") or item.get("thumbnail_url") or "")
        if media_url:
            media.append(MediaItem(_media_kind_from_type(item.get("type"), media_url), media_url))
    if not media:
        media = [
            MediaItem(_media_kind_from_url(item), item)
            for item in payload.get("mediaURLs", [])
            if isinstance(item, str)
        ]
    metrics = {}
    for source_key, label in (("likes", "喜欢"), ("retweets", "转发"), ("replies", "回复")):
        value = payload.get(source_key)
        if value is not None:
            metrics[label] = str(value)
    return Preview(
        platform="twitter",
        url=url,
        author=author,
        author_url=f"https://x.com/{screen_name}" if screen_name else "",
        published_at=str(payload.get("date", "") or ""),
        description=str(payload.get("text", "") or ""),
        metrics=metrics,
        media=media,
    )


def vxtwitter_api_url(url: str) -> str | None:
    match = STATUS_RE.search(url)
    if not match:
        return None
    user, status_id = match.groups()
    return f"https://api.vxtwitter.com/{user}/status/{status_id}"


async def fetch_vxtwitter_preview(url: str, timeout_seconds: int) -> Preview:
    api_url = vxtwitter_api_url(url)
    if not api_url:
        raise PreviewFetchError("Twitter/X 链接格式无法识别。")
    request = Request(api_url, headers={"User-Agent": "Mozilla/5.0 AstrBotLinkPreview/0.1"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except Exception as exc:
        raise PreviewFetchError(f"Twitter/X 兜底解析失败：{exc}") from exc
    return parse_vxtwitter_payload(url, payload)


async def fetch_twitter_preview(url: str, timeout_seconds: int) -> Preview:
    if vxtwitter_api_url(url):
        try:
            return await fetch_vxtwitter_preview(url, timeout_seconds)
        except PreviewFetchError:
            pass
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 AstrBotLinkPreview/0.1"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return await fetch_vxtwitter_preview(url, timeout_seconds)
    preview = parse_twitter_html(url, html)
    if preview.description or preview.author or preview.media:
        return preview
    return await fetch_vxtwitter_preview(url, timeout_seconds)
