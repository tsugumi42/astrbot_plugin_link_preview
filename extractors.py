from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s<>\"]+")


@dataclass(frozen=True)
class SupportedLink:
    platform: str
    url: str


def extract_supported_links(text: str) -> list[SupportedLink]:
    links: list[SupportedLink] = []
    for match in URL_RE.finditer(text):
        url = match.group(0).rstrip(".,，。!！?？)")
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        if host in {"youtu.be", "www.youtu.be"}:
            links.append(SupportedLink("youtube", url))
        elif host.endswith("youtube.com") and (path.startswith("/watch") or path.startswith("/shorts/")):
            links.append(SupportedLink("youtube", url))
        elif host in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"} and "/status/" in path:
            links.append(SupportedLink("twitter", url))
    return links
