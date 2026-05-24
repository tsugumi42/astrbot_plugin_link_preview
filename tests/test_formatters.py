from astrbot_plugin_link_preview.formatters import format_preview_text
from astrbot_plugin_link_preview.models import MediaItem, Preview


def test_format_youtube_preview_text():
    preview = Preview(
        platform="youtube",
        url="https://youtu.be/abc",
        title="A Video",
        author="A Channel",
        published_at="2026-05-24",
        description="hello world",
        metrics={"观看": "1234", "点赞": "55"},
        media=[],
    )
    text = format_preview_text(preview)
    assert "YouTube 预览" in text
    assert "标题：A Video" in text
    assert "频道：A Channel" in text
    assert "链接：https://youtu.be/abc" in text


def test_format_twitter_preview_with_images_and_body():
    preview = Preview(
        platform="twitter",
        url="https://x.com/u/status/1",
        title="",
        author="Name (@u)",
        published_at="2026-05-24",
        description="tweet body",
        metrics={"喜欢": "9"},
        media=[MediaItem(kind="image", url="https://pbs.twimg.com/a.jpg")],
    )
    text = format_preview_text(preview)
    assert "Twitter/X 预览" in text
    assert "正文：tweet body" in text
    assert "媒体：检测到 1 张图片" in text
