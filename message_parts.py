from __future__ import annotations

from .formatters import format_preview_text
from .models import Preview


def compose_preview_parts(
    preview: Preview,
    *,
    send_images: bool,
    image_position: str,
    fields: list[str] | tuple[str, ...] | None = None,
) -> list[tuple[str, str]]:
    text_part = ("text", format_preview_text(preview, fields=fields))
    image_parts = [
        ("image", media.url)
        for media in preview.media
        if media.kind == "image" and media.url
    ]
    if not send_images or not image_parts:
        return [text_part]
    if image_position == "before_text":
        return image_parts + [text_part]
    return [text_part] + image_parts
