# RSS链接获取指南

## 📚 什么是RSS？

RSS（Really Simple Syndication）是一种信息聚合格式，网站通过RSS源发布最新内容，你可以订阅这些源来获取更新。

## 🔍 方法一：使用RSSHub Radar浏览器扩展（推荐）

### 安装步骤

1. **Chrome/Edge浏览器**：
   - 访问：https://chrome.google.com/webstore/detail/rsshub-radar/kefjpfngnndepjbopdmoebkipbgkggaa
   - 点击"添加至Chrome"

2. **Firefox浏览器**：
   - 访问：https://addons.mozilla.org/firefox/addon/rsshub-radar/
   - 点击"添加到Firefox"

### 使用方法

1. 安装扩展后，访问你想监控的网站
2. 点击浏览器工具栏中的RSSHub Radar图标
3. 扩展会自动检测页面上的RSS链接
4. 如果有RSS源，会显示一个列表，点击即可复制链接

### 优点
- ✅ 自动检测RSS链接
- ✅ 支持RSSHub生成的RSS源
- ✅ 一键复制，非常方便

---

## 🔍 方法二：手动查找RSS链接

### 1. 查看网页源代码

1. 在网页上右键 → **查看网页源代码**（或按 `Ctrl+U`）
2. 按 `Ctrl+F` 搜索以下关键词：
   - `rss`
   - `feed`
   - `atom`
   - `application/rss+xml`
   - `application/atom+xml`
3. 找到类似这样的代码：
   ```html
   <link rel="alternate" type="application/rss+xml" href="https://example.com/feed">
   ```
4. 复制 `href` 中的链接

### 2. 尝试常见RSS地址格式

很多网站使用标准的RSS地址格式，可以直接尝试：

```
https://网站域名/feed
https://网站域名/rss
https://网站域名/feed.xml
https://网站域名/rss.xml
https://网站域名/index.xml
https://网站域名/atom.xml
```

**示例**：
- `https://example.com/feed`
- `https://example.com/rss`
- `https://blog.example.com/feed`

### 3. 查看网站底部或侧边栏

很多网站会在页面底部或侧边栏显示RSS图标（通常是橙色图标），点击即可获取RSS链接。

---

## 🔍 方法三：使用RSSHub（适用于不支持RSS的网站）

RSSHub是一个开源、易用、可扩展的RSS生成器，可以为很多不支持RSS的网站生成RSS源。

### 官方实例
- 访问：https://rsshub.app/
- 搜索你想监控的网站或平台
- 按照说明构建RSS链接

### 常见RSSHub路由示例

**GitHub仓库**：
```
https://rsshub.app/github/repos/用户名/仓库名
```

**Twitter用户**：
```
https://rsshub.app/twitter/user/用户名
```

**YouTube频道**：
```
https://rsshub.app/youtube/channel/频道ID
```

**B站UP主**：
```
https://rsshub.app/bilibili/user/video/用户ID
```

**微博用户**：
```
https://rsshub.app/weibo/user/用户ID
```

---

## 🔍 方法四：使用在线RSS检测工具

### FeedBurner
- 访问：https://feedburner.google.com/
- 输入网站URL，检测是否有RSS源

### Feed Validator
- 访问：https://validator.w3.org/feed/
- 输入RSS链接，验证是否有效

---

## ✅ 如何验证RSS链接是否有效

### 方法1：在浏览器中打开
直接在浏览器地址栏输入RSS链接，如果看到XML格式的内容（通常以 `<rss>` 或 `<feed>` 开头），说明链接有效。

### 方法2：使用测试脚本
运行我们的监控脚本，如果RSS链接无效，会显示错误信息：

```bash
python rss_monitor.py
```

### 方法3：在线验证工具
- https://validator.w3.org/feed/ - W3C Feed验证器
- https://www.feedvalidator.org/ - Feed验证器

---

## 📝 常见网站RSS获取示例

### 技术博客

**阮一峰的网络日志**：
```
https://www.ruanyifeng.com/blog/atom.xml
```

**掘金**：
```
https://rsshub.app/juejin/posts/用户名
```

**InfoQ**：
```
https://www.infoq.cn/feed
```

### 新闻网站

**BBC中文**：
```
https://www.bbc.com/zhongwen/simp/rss.xml
```

**Reuters（路透社）**：
```
https://www.reuters.com/rssFeed/worldNews
```

### 社交媒体

**Twitter**（使用RSSHub）：
```
https://rsshub.app/twitter/user/用户名
```

**微博**（使用RSSHub）：
```
https://rsshub.app/weibo/user/用户ID
```

### GitHub

**仓库Issues**：
```
https://github.com/用户名/仓库名/issues.atom
```

**仓库Releases**：
```
https://github.com/用户名/仓库名/releases.atom
```

**使用RSSHub**：
```
https://rsshub.app/github/repos/用户名/仓库名
```

---

## 🎯 配置到监控脚本

获取RSS链接后，添加到配置文件中：

### 本地配置文件（config.json）

```json
{
  "discord_webhook": "你的Discord Webhook地址",
  "rss_sources": [
    {
      "name": "网站名称1",
      "url": "https://example.com/feed"
    },
    {
      "name": "网站名称2",
      "url": "https://another-example.com/rss"
    }
  ]
}
```

### GitHub Secrets（RSS_SOURCES）

```json
[
  {
    "name": "网站名称1",
    "url": "https://example.com/feed"
  },
  {
    "name": "网站名称2",
    "url": "https://another-example.com/rss"
  }
]
```

---

## 💡 小贴士

1. **RSS链接格式**：
   - RSS 2.0：通常以 `.rss` 或 `/feed` 结尾
   - Atom：通常以 `.atom` 或 `/atom.xml` 结尾
   - 两者都可以使用

2. **如果网站没有RSS**：
   - 尝试使用RSSHub生成
   - 或者联系网站管理员询问是否有RSS源

3. **RSS链接失效**：
   - 定期检查RSS链接是否仍然有效
   - 如果失效，尝试更新链接或使用RSSHub

4. **多个RSS源**：
   - 可以添加多个RSS源到配置中
   - 脚本会依次检查所有源

---

## 🔗 相关资源

- **RSSHub官方文档**：https://docs.rsshub.app/
- **RSSHub Radar扩展**：https://github.com/DIYgod/RSSHub-Radar
- **Feed验证器**：https://validator.w3.org/feed/
- **RSS阅读器推荐**：
  - Feedly
  - Inoreader
  - NetNewsWire

---

## ❓ 常见问题

**Q: 网站没有RSS怎么办？**
A: 尝试使用RSSHub为网站生成RSS源，或者使用RSSHub Radar扩展自动检测。

**Q: RSS链接打不开？**
A: 检查链接是否正确，尝试在浏览器中直接打开验证。如果确实无效，可能需要使用RSSHub。

**Q: 如何知道RSS源是否有新内容？**
A: 运行监控脚本，它会自动检查并推送新内容。或者使用RSS阅读器订阅。

**Q: 可以监控多少个RSS源？**
A: 理论上没有限制，但建议不要添加太多，以免影响性能。建议控制在10-20个以内。

