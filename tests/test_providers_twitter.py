from astrbot_plugin_link_preview.providers.twitter import parse_twitter_html
from astrbot_plugin_link_preview.providers.twitter import parse_vxtwitter_payload
from astrbot_plugin_link_preview.providers.twitter import vxtwitter_api_url


def test_parse_twitter_opengraph_html():
    html = """
    <html><head>
      <meta property="og:title" content="Name on X: tweet body">
      <meta property="og:description" content="tweet body">
      <meta property="og:image" content="https://pbs.twimg.com/media/a.jpg">
    </head></html>
    """
    preview = parse_twitter_html("https://x.com/u/status/1", html)
    assert preview.platform == "twitter"
    assert preview.author == "Name on X"
    assert preview.description == "tweet body"
    assert preview.media[0].kind == "image"


def test_parse_vxtwitter_payload_with_media_and_metrics():
    payload = {
        "user_name": "ほし",
        "user_screen_name": "HOSHIBACKYARD",
        "text": "画集「遺失物統轄機構」本日発売です。",
        "date": "Mon Feb 03 15:00:48 +0000 2025",
        "likes": 17516,
        "retweets": 3821,
        "replies": 24,
        "mediaURLs": ["https://pbs.twimg.com/media/Gi3xE7YbAAAyIe6.jpg"],
    }
    preview = parse_vxtwitter_payload("https://x.com/HOSHIBACKYARD/status/1886429636135174546?s=20", payload)
    assert preview.author == "ほし (@HOSHIBACKYARD)"
    assert preview.description == "画集「遺失物統轄機構」本日発売です。"
    assert preview.metrics["喜欢"] == "17516"
    assert preview.media[0].url.endswith(".jpg")


def test_parse_vxtwitter_payload_does_not_send_video_as_image():
    payload = {
        "user_name": "Name",
        "user_screen_name": "name",
        "text": "video tweet",
        "mediaURLs": ["https://video.twimg.com/ext_tw_video/1/pu/vid/avc1/720x720/a.mp4"],
    }
    preview = parse_vxtwitter_payload("https://x.com/name/status/1", payload)
    assert preview.media[0].kind == "video"


def test_parse_vxtwitter_payload_sends_video_thumbnail_as_image():
    payload = {
        "user_name": "Name",
        "user_screen_name": "name",
        "text": "video tweet",
        "media_extended": [
            {
                "type": "video",
                "url": "https://video.twimg.com/ext_tw_video/a.mp4",
                "thumbnail_url": "https://pbs.twimg.com/ext_tw_video_thumb/a.jpg",
            }
        ],
    }
    preview = parse_vxtwitter_payload("https://x.com/name/status/1", payload)
    assert preview.media[0].kind == "image"
    assert preview.media[0].url.endswith(".jpg")
    assert preview.media[1].kind == "video"


def test_parse_vxtwitter_payload_reads_extended_media_type():
    payload = {
        "user_name": "Name",
        "user_screen_name": "name",
        "text": "gif tweet",
        "media_extended": [
            {
                "type": "gif",
                "url": "https://video.twimg.com/tweet_video/a.mp4",
                "thumbnail_url": "https://pbs.twimg.com/tweet_video_thumb/a.jpg",
            }
        ],
    }
    preview = parse_vxtwitter_payload("https://x.com/name/status/1", payload)
    assert preview.media[0].kind == "image"
    assert preview.media[0].url.endswith(".jpg")
    assert preview.media[1].kind == "gif"
    assert preview.media[1].url.endswith(".mp4")


def test_vxtwitter_api_url_for_x_status():
    assert (
        vxtwitter_api_url("https://x.com/HOSHIBACKYARD/status/1886429636135174546?s=20")
        == "https://api.vxtwitter.com/HOSHIBACKYARD/status/1886429636135174546"
    )
