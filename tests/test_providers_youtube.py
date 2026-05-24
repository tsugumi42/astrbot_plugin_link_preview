from astrbot_plugin_link_preview.providers.youtube import parse_youtube_html
from astrbot_plugin_link_preview.providers.youtube import parse_youtube_oembed_payload


def test_parse_youtube_opengraph_html():
    html = """
    <html><head>
      <meta property="og:title" content="Video Title">
      <meta itemprop="name" content="Channel Name">
      <meta property="og:description" content="A long description">
      <meta property="og:image" content="https://i.ytimg.com/vi/abc/hqdefault.jpg">
    </head></html>
    """
    preview = parse_youtube_html("https://youtu.be/abc", html)
    assert preview.platform == "youtube"
    assert preview.title == "Video Title"
    assert preview.author == "Channel Name"
    assert preview.description == "A long description"
    assert preview.media[0].url.endswith("hqdefault.jpg")


def test_parse_youtube_html_details_from_json_fragments():
    html = r'''
    <html><head>
      <meta property="og:title" content="Video Title">
      <meta itemprop="name" content="Channel Name">
      <meta itemprop="datePublished" content="2026-05-24">
      <meta property="og:image" content="https://i.ytimg.com/vi/abc/hqdefault.jpg">
    </head><body>
      {"viewCount":"123456","label":"789 likes"}
    </body></html>
    '''
    preview = parse_youtube_html("https://youtu.be/abc", html)
    assert preview.published_at == "2026-05-24"
    assert preview.metrics["观看"] == "123456"
    assert preview.metrics["点赞"] == "789"


def test_parse_youtube_oembed_payload():
    payload = {
        "title": "OEmbed Title",
        "author_name": "Channel Name",
        "thumbnail_url": "https://i.ytimg.com/vi/abc/hqdefault.jpg",
    }
    preview = parse_youtube_oembed_payload("https://youtu.be/abc", payload)
    assert preview.platform == "youtube"
    assert preview.title == "OEmbed Title"
    assert preview.author == "Channel Name"
    assert preview.media[0].url.endswith("hqdefault.jpg")
