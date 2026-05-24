from __future__ import annotations

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


async def fetch_youtube_preview(url: str, timeout_seconds: int) -> Preview:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 AstrBotLinkPreview/0.1"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        raise PreviewFetchError(f"YouTube 页面请求失败：{exc}") from exc
    return parse_youtube_html(url, html)
