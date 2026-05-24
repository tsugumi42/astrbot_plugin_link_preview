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
    assert "标题：A Video" in text
    assert "上传频道：A Channel" in text
    assert "播放量 1234 / 点赞量 55 / 上传日期 2026-05-24" in text
    assert "链接：https://youtu.be/abc" in text


def test_format_youtube_preview_respects_fields():
    preview = Preview(
        platform="youtube",
        url="https://youtu.be/abc",
        title="A Video",
        author="A Channel",
        description="hello world",
    )
    text = format_preview_text(preview, fields=["title", "url"])
    assert text == "标题：A Video\n链接：https://youtu.be/abc"


def test_format_twitter_preview_with_images_and_body():
    preview = Preview(
        platform="twitter",
        url="https://x.com/u/status/1",
        title="",
        author="Name (@u)",
        published_at="2026-05-24",
        description="tweet body",
        metrics={"喜欢": "9", "转发": "2", "回复": "1"},
        media=[MediaItem(kind="image", url="https://pbs.twimg.com/a.jpg")],
        author_url="https://x.com/u",
    )
    text = format_preview_text(preview)
    assert "推文链接：https://x.com/u/status/1" in text
    assert "发布时间：2026-05-24" in text
    assert "喜欢 9 / 转发 2 / 回复 1" in text
    assert "作者：Name (@u) https://x.com/u" in text
    assert "tweet body" in text


def test_format_twitter_preview_respects_fields():
    preview = Preview(
        platform="twitter",
        url="https://x.com/u/status/1",
        author="Name (@u)",
        description="tweet body",
    )
    text = format_preview_text(preview, fields=["url", "author"])
    assert text == "推文链接：https://x.com/u/status/1\n作者：Name (@u)"
