from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MediaItem:
    kind: str
    url: str


@dataclass(frozen=True)
class Preview:
    platform: str
    url: str
    title: str = ""
    author: str = ""
    author_url: str = ""
    published_at: str = ""
    description: str = ""
    metrics: dict[str, str] = field(default_factory=dict)
    media: list[MediaItem] = field(default_factory=list)
