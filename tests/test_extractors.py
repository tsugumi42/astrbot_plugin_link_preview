from astrbot_plugin_link_preview.extractors import extract_supported_links


def test_extract_youtube_and_x_links_in_order():
    text = "看这个 https://youtu.be/abc123 和 https://x.com/u/status/123"
    links = extract_supported_links(text)
    assert [(item.platform, item.url) for item in links] == [
        ("youtube", "https://youtu.be/abc123"),
        ("twitter", "https://x.com/u/status/123"),
    ]


def test_ignores_unsupported_links():
    assert extract_supported_links("https://example.com/a") == []


def test_normalizes_twitter_domain():
    [item] = extract_supported_links("https://twitter.com/u/status/123?s=20")
    assert item.platform == "twitter"
    assert item.url == "https://twitter.com/u/status/123?s=20"
