from __future__ import annotations

from html.parser import HTMLParser


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: dict[tuple[str, str], str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta":
            return
        attr = {key.lower(): value or "" for key, value in attrs}
        content = attr.get("content", "").strip()
        if not content:
            return
        if attr.get("property"):
            self.values[("property", attr["property"])] = content
        if attr.get("name"):
            self.values[("name", attr["name"])] = content
        if attr.get("itemprop"):
            self.values[("itemprop", attr["itemprop"])] = content


def parse_meta(html: str) -> dict[tuple[str, str], str]:
    parser = MetaParser()
    parser.feed(html)
    return parser.values
