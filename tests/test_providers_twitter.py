from astrbot_plugin_link_preview.providers.twitter import parse_twitter_html


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
