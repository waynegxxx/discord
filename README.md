# RSS监控推送工具

自动监控多个RSS源，当有新文章时自动推送到Discord群或飞书群。

## 功能特点

- ✅ 支持监控多个RSS源
- ✅ 自动去重，避免重复推送
- ✅ 支持本地运行和GitHub Actions自动运行
- ✅ 支持Discord和飞书两种推送方式
- ✅ 美观的消息卡片格式
- ✅ 自动保存推送状态

## 使用方法

### 方式一：本地运行

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置信息**
   
   复制 `config.example.json` 为 `config.json`，并填入你的信息：

```json
{
  "discord_webhook": "你的Discord机器人Webhook地址",
  "feishu_webhook": "你的飞书机器人Webhook地址（可选）",
  "rss_sources": [
    {
      "name": "网站名称",
      "url": "RSS链接"
    }
  ]
}
```

   **注意**：至少需要配置 `discord_webhook` 或 `feishu_webhook` 其中一个。如果两者都配置，优先使用Discord。

3. **运行脚本**
```bash
python rss_monitor.py
```

4. **定时运行（可选）**
   
   Windows可以使用任务计划程序，Linux/Mac可以使用cron：
```bash
# 每5分钟运行一次
*/5 * * * * cd /path/to/project && python rss_monitor.py

# 或者每30分钟运行一次（更节省资源）
*/30 * * * * cd /path/to/project && python rss_monitor.py
```

### 方式二：GitHub Actions自动运行

1. **设置GitHub Secrets**
   
   在GitHub仓库的 Settings → Secrets and variables → Actions 中添加：
   
   - `DISCORD_WEBHOOK`: 你的Discord机器人Webhook地址
   - `RSS_SOURCES`: RSS源配置（JSON格式），例如：
   ```json
   [
     {
       "name": "网站名称1",
       "url": "RSS链接1"
     },
     {
       "name": "网站名称2",
       "url": "RSS链接2"
     }
   ]
   ```

2. **推送代码到GitHub**
   
   将代码推送到GitHub后，GitHub Actions会自动每5分钟运行一次。

3. **手动触发（可选）**
   
   在GitHub仓库的 Actions 页面可以手动触发工作流。

## 文件说明

- `rss_monitor.py` - 主监控脚本
- `config.json` - 配置文件（需要自己创建）
- `config.example.json` - 配置文件模板
- `rss_state.json` - 推送状态记录（自动生成）
- `requirements.txt` - Python依赖
- `.github/workflows/rss-monitor.yml` - GitHub Actions工作流

## 注意事项

1. 首次运行会推送RSS源中的最新文章（最多10条）
2. 后续运行只会推送新文章
3. `rss_state.json` 文件会记录已推送的文章，请勿删除
4. 如果使用GitHub Actions，`rss_state.json` 会自动提交到仓库

## 获取RSS链接

详细指南请查看：[RSS获取指南.md](RSS获取指南.md)

**快速方法**：
1. **使用RSSHub Radar浏览器扩展**（推荐）
   - Chrome: https://chrome.google.com/webstore/detail/rsshub-radar/kefjpfngnndepjbopdmoebkipbgkggaa
   - Firefox: https://addons.mozilla.org/firefox/addon/rsshub-radar/
   - 安装后访问网站，点击扩展图标即可自动检测RSS链接

2. **手动查找**
   - 查看网页源代码，搜索 `rss` 或 `feed`
   - 尝试常见格式：`https://网站域名/feed` 或 `https://网站域名/rss`

3. **使用RSSHub**（适用于不支持RSS的网站）
   - 访问：https://rsshub.app/
   - 为各种网站和平台生成RSS源

## 获取Discord Webhook地址

1. 在Discord服务器中，进入 **服务器设置** → **集成** → **Webhooks**
2. 点击 **新建Webhook** 或选择现有Webhook
3. 复制Webhook URL（格式类似：`https://discord.com/api/webhooks/xxxxx/xxxxx`）

## 测试Discord Webhook

在配置完成后，可以使用测试脚本验证Webhook是否正常工作：

```bash
# 方法1：直接提供Webhook地址
python test_discord.py "你的Discord Webhook地址"

# 方法2：交互式输入
python test_discord.py
# 然后按提示输入Webhook地址
```

测试脚本会发送两条测试消息：
1. 普通文本消息
2. Embed格式消息（错误通知格式）

如果两条消息都成功发送，说明Webhook配置正确。

## 故障排查

- 如果推送失败，检查Discord或飞书Webhook地址是否正确
- 如果RSS解析失败，检查RSS链接是否可访问
- 查看控制台输出的错误信息
- Discord Webhook消息限制：标题最多256字符，描述最多2000字符
- **如果Discord没收到消息**：
  1. 运行 `python test_discord.py` 测试Webhook是否正常
  2. 检查GitHub Actions日志，查看是否有错误信息
  3. 确认Discord Webhook地址在GitHub Secrets中配置正确
  4. 检查Discord服务器中Webhook是否仍然有效

