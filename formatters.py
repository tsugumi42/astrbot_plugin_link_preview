from __future__ import annotations

from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

from .models import Preview

DEFAULT_YOUTUBE_FIELDS = ("title", "author", "metrics", "url")
DEFAULT_TWITTER_FIELDS = ("url", "published_at", "metrics", "author", "description")


def format_preview_text(preview: Preview, fields: list[str] | tuple[str, ...] | None = None) -> str:
    if preview.platform == "youtube":
        return _format_youtube(preview, tuple(fields or DEFAULT_YOUTUBE_FIELDS))
    if preview.platform == "twitter":
        return _format_twitter(preview, tuple(fields or DEFAULT_TWITTER_FIELDS))
    return f"链接预览\n链接：{preview.url}"


def _metrics_text(metrics: dict[str, str], labels: dict[str, str] | None = None) -> str:
    labels = labels or {}
    return " / ".join(f"{key} {value}" for key, value in metrics.items() if value)


def _format_youtube(preview: Preview, fields: tuple[str, ...]) -> str:
    lines = []
    if "title" in fields and preview.title:
        lines.append(f"标题：{preview.title}")
    if "author" in fields and preview.author:
        lines.append(f"上传频道：{preview.author}")
    if "metrics" in fields:
        bits = []
        if preview.metrics.get("观看"):
            bits.append(f"播放量 {preview.metrics['观看']}")
        if preview.metrics.get("点赞"):
            bits.append(f"点赞量 {preview.metrics['点赞']}")
        if preview.published_at:
            bits.append(f"上传日期 {preview.published_at}")
        if bits:
            lines.append(" / ".join(bits))
    if "description" in fields and preview.description:
        lines.append(f"简介：{preview.description}")
    if "url" in fields:
        lines.append(f"链接：{preview.url}")
    return "\n".join(lines)


def _format_twitter_time(value: str) -> str:
    if not value:
        return ""
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return value
    return dt.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S +08:00")


def _format_twitter(preview: Preview, fields: tuple[str, ...]) -> str:
    lines = []
    if "url" in fields:
        lines.append(f"推文链接：{preview.url}")
    if "published_at" in fields and preview.published_at:
        lines.append(f"发布时间：{_format_twitter_time(preview.published_at)}")
    if "metrics" in fields:
        metrics = _metrics_text(preview.metrics)
        if metrics:
            lines.append(metrics)
    if "author" in fields and preview.author:
        author = f"{preview.author} {preview.author_url}".strip()
        lines.append(f"作者：{author}")
    if any(item.kind in {"video", "gif"} for item in preview.media):
        lines.append("媒体：包含视频/GIF，暂不发送媒体文件。")
    if "description" in fields and preview.description:
        lines.append(f"正文：\n{preview.description}")
    return "\n".join(lines)
