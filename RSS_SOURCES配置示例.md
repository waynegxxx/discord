# RSS_SOURCES 配置示例

## ⚠️ 重要提示

在GitHub Secrets中设置 `RSS_SOURCES` 时，必须使用**纯JSON数组格式**，不要包含任何注释或多余的内容。

## ✅ 正确格式

### 单个RSS源
```json
[{"name": "网站名称", "url": "https://example.com/rss"}]
```

### 多个RSS源
```json
[
  {
    "name": "网站名称1",
    "url": "https://example.com/rss"
  },
  {
    "name": "网站名称2",
    "url": "https://another-example.com/feed"
  }
]
```

### 紧凑格式（单行，适合复制）
```json
[{"name": "网站名称1", "url": "https://example.com/rss"}, {"name": "网站名称2", "url": "https://another-example.com/feed"}]
```

## ❌ 常见错误

### 错误1：包含外层大括号
```json
{
  "rss_sources": [
    {"name": "网站名称", "url": "https://example.com/rss"}
  ]
}
```
❌ **错误**：不要包含外层的 `{"rss_sources": ...}`，直接使用数组

### 错误2：使用单引号
```json
[{'name': '网站名称', 'url': 'https://example.com/rss'}]
```
❌ **错误**：JSON必须使用双引号

### 错误3：包含注释
```json
[
  {
    "name": "网站名称",
    "url": "https://example.com/rss"
    // 这是注释，JSON不支持
  }
]
```
❌ **错误**：JSON不支持注释

### 错误4：缺少逗号
```json
[
  {"name": "网站1", "url": "https://example.com/rss"}
  {"name": "网站2", "url": "https://another.com/feed"}
]
```
❌ **错误**：多个对象之间需要逗号分隔

### 错误5：多余的逗号
```json
[
  {"name": "网站1", "url": "https://example.com/rss"},
  {"name": "网站2", "url": "https://another.com/feed"},  // ← 多余的逗号
]
```
❌ **错误**：最后一个元素后不能有逗号（虽然有些JSON解析器允许，但最好避免）

## 📝 实际配置示例

### 示例1：技术博客
```json
[
  {
    "name": "阮一峰的网络日志",
    "url": "https://www.ruanyifeng.com/blog/atom.xml"
  },
  {
    "name": "InfoQ",
    "url": "https://www.infoq.cn/feed"
  }
]
```

### 示例2：新闻网站
```json
[
  {
    "name": "BBC中文",
    "url": "https://www.bbc.com/zhongwen/simp/rss.xml"
  },
  {
    "name": "Reuters",
    "url": "https://www.reuters.com/rssFeed/worldNews"
  }
]
```

### 示例3：使用RSSHub
```json
[
  {
    "name": "GitHub仓库",
    "url": "https://rsshub.app/github/repos/用户名/仓库名"
  },
  {
    "name": "B站UP主",
    "url": "https://rsshub.app/bilibili/user/video/用户ID"
  }
]
```

## 🔍 如何验证JSON格式

### 方法1：在线验证工具
1. 访问：https://jsonlint.com/
2. 粘贴你的JSON内容
3. 点击 "Validate JSON"
4. 如果有错误，会显示具体位置

### 方法2：使用Python
```python
import json

# 你的RSS_SOURCES内容
rss_sources = '[{"name": "测试", "url": "https://example.com/rss"}]'

try:
    data = json.loads(rss_sources)
    print("✅ JSON格式正确")
    print(f"包含 {len(data)} 个RSS源")
    for i, source in enumerate(data, 1):
        print(f"  {i}. {source.get('name')}: {source.get('url')}")
except json.JSONDecodeError as e:
    print(f"❌ JSON格式错误: {e}")
    print(f"   位置: 第{e.lineno}行，第{e.colno}列")
```

## 📋 配置步骤

1. **准备JSON内容**
   - 使用上面的示例格式
   - 替换为你的实际RSS链接
   - 使用在线工具验证格式

2. **复制到GitHub Secrets**
   - 访问：https://github.com/waynegxxx/discord/settings/secrets/actions
   - 点击 "New repository secret"
   - Name: `RSS_SOURCES`
   - Value: 粘贴你的JSON内容（**不要换行，或确保格式正确**）

3. **验证配置**
   - 运行GitHub Actions
   - 查看日志，应该显示：
     ```
     ✅ RSS_SOURCES: 已设置
     ✅ RSS源数量: X
     ```

## 💡 小贴士

1. **推荐使用紧凑格式**（单行），避免换行导致的格式问题
2. **先验证再配置**：使用在线工具验证JSON格式
3. **逐个添加**：如果多个源有问题，先配置一个测试，成功后再添加其他
4. **检查特殊字符**：URL中的特殊字符会自动处理，不需要手动转义

## 🆘 如果仍然出错

如果配置后仍然出现JSON格式错误：

1. **查看错误信息**：GitHub Actions日志会显示具体错误位置
2. **复制错误内容**：从日志中复制RSS_SOURCES的内容
3. **在线验证**：粘贴到 https://jsonlint.com/ 查看具体问题
4. **重新配置**：修复后重新设置Secret

