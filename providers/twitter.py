from __future__ import annotations

from urllib.request import Request, urlopen

from ..models import MediaItem, Preview
from .base import PreviewFetchError
from .meta import parse_meta


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


async def fetch_twitter_preview(url: str, timeout_seconds: int) -> Preview:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 AstrBotLinkPreview/0.1"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        raise PreviewFetchError(f"Twitter/X 页面请求失败：{exc}") from exc
    return parse_twitter_html(url, html)
