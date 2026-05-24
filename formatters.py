from __future__ import annotations

from .models import Preview


def format_preview_text(preview: Preview) -> str:
    if preview.platform == "youtube":
        return _format_youtube(preview)
    if preview.platform == "twitter":
        return _format_twitter(preview)
    return f"链接预览\n链接：{preview.url}"


def _metrics_text(metrics: dict[str, str]) -> str:
    return " / ".join(f"{key} {value}" for key, value in metrics.items() if value)


def _format_youtube(preview: Preview) -> str:
    lines = ["YouTube 预览"]
    if preview.title:
        lines.append(f"标题：{preview.title}")
    if preview.author:
        lines.append(f"频道：{preview.author}")
    if preview.published_at:
        lines.append(f"发布时间：{preview.published_at}")
    metrics = _metrics_text(preview.metrics)
    if metrics:
        lines.append(f"数据：{metrics}")
    if preview.description:
        lines.append(f"简介：{preview.description}")
    lines.append(f"链接：{preview.url}")
    return "\n".join(lines)


def _format_twitter(preview: Preview) -> str:
    lines = ["Twitter/X 预览"]
    if preview.author:
        lines.append(f"作者：{preview.author}")
    if preview.published_at:
        lines.append(f"发布时间：{preview.published_at}")
    if preview.description:
        lines.append(f"正文：{preview.description}")
    metrics = _metrics_text(preview.metrics)
    if metrics:
        lines.append(f"数据：{metrics}")
    image_count = sum(1 for item in preview.media if item.kind == "image")
    video_count = sum(1 for item in preview.media if item.kind in {"video", "gif"})
    if image_count:
        lines.append(f"媒体：检测到 {image_count} 张图片")
    if video_count:
        lines.append(f"媒体：检测到 {video_count} 个视频/GIF，第一版暂不下载")
    lines.append(f"链接：{preview.url}")
    return "\n".join(lines)
