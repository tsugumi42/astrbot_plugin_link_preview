from astrbot_plugin_link_preview.message_parts import compose_preview_parts
from astrbot_plugin_link_preview.models import MediaItem, Preview


def _preview():
    return Preview(
        platform="youtube",
        url="https://youtu.be/abc",
        title="Video",
        media=[MediaItem("image", "https://example.test/thumb.jpg")],
    )


def test_compose_preview_parts_image_after_text_by_default():
    assert compose_preview_parts(_preview(), send_images=True, image_position="after_text") == [
        ("text", "标题：Video\n链接：https://youtu.be/abc"),
        ("image", "https://example.test/thumb.jpg"),
    ]


def test_compose_preview_parts_image_before_text():
    assert compose_preview_parts(_preview(), send_images=True, image_position="before_text") == [
        ("image", "https://example.test/thumb.jpg"),
        ("text", "标题：Video\n链接：https://youtu.be/abc"),
    ]
