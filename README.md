# AstrBot 链接预览

自动解析 YouTube 和 Twitter/X 链接并生成清晰的文字预览，优先面向中文 AstrBot 社区和 QQ 小号 + NapCat/OneBot v11 使用环境。

仓库描述建议：

```text
AstrBot 链接预览插件：自动解析 YouTube 和 Twitter/X 链接并生成文字预览，优先适配 QQ 小号 + NapCat/OneBot v11。
```

## 功能

- 自动监听普通消息中的 YouTube 与 Twitter/X 链接。
- 以清晰文本返回标题、作者、正文/简介和原链接。
- YouTube 优先使用公开 oEmbed 信息，减少直接抓取页面导致的超时。
- Twitter/X 图片会在配置开启时尽量随消息发送。
- 可配置图片在文字前或文字后发送。
- 官方 API 字段已预留，默认不使用。
- 不生成图片卡片，保留可复制、可点击的文本链接。

## 安装

将本目录放入 AstrBot 的插件目录后，在 WebUI 启用插件。

推荐 QQ 接入方式：

```text
QQ 小号 -> NapCat -> OneBot v11 反向 WebSocket -> AstrBot aiocqhttp 适配器
```

## 配置

- `enable_youtube`: 是否启用 YouTube 预览。
- `enable_twitter`: 是否启用 Twitter/X 预览。
- `max_links_per_message`: 单条消息最多解析几个链接。
- `cooldown_seconds`: 同一会话自动预览冷却时间。
- `send_thumbnail_image`: 是否尝试发送 YouTube 缩略图。
- `send_twitter_images`: 是否尝试发送 Twitter/X 图片。
- `image_position`: 图片位置，`after_text` 为文字后，`before_text` 为文字前。
- `youtube_api_key` / `twitter_bearer_token`: 预留字段，第一版为空即可。

## 已知限制

- 第一版主要依赖公开页面 metadata，遇到反爬、删除、私密内容时可能解析失败。
- Twitter/X 视频和 GIF 第一版不下载。
- 官方 QQ 机器人不是第一验证目标。
