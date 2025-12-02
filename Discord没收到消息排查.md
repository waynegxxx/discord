# Discord没收到消息 - 完整排查指南

## 🔍 快速诊断

运行诊断脚本：
```bash
python diagnose_discord.py
```

这个脚本会：
1. ✅ 检查配置文件是否存在
2. ✅ 检查Discord Webhook是否配置
3. ✅ 检查RSS源是否配置
4. ✅ 测试Discord Webhook是否正常工作
5. ✅ 检查推送状态文件

## 📋 可能的原因

### 1. Discord Webhook未配置或配置错误

**检查方法**：
1. 访问：https://github.com/waynegxxx/discord/settings/secrets/actions
2. 确认 `DISCORD_WEBHOOK` 已设置
3. 确认Webhook地址格式正确：`https://discord.com/api/webhooks/xxxxx/xxxxx`

**测试方法**：
```bash
python test_discord.py "你的Discord Webhook地址"
```

如果测试失败，说明Webhook有问题。

### 2. 所有文章都已经推送过了

**情况说明**：
- 首次运行会推送RSS源中的最新文章（最多10条）
- 之后只会推送**新发布的文章**
- 如果RSS源没有新文章，就不会发送消息

**解决方法**：
1. **删除状态文件重新推送**（如果使用GitHub Actions）：
   - 访问：https://github.com/waynegxxx/discord
   - 找到 `rss_state.json` 文件
   - 删除该文件并提交
   - 下次运行会重新推送所有文章

2. **本地运行**：
   ```bash
   # 删除状态文件
   rm rss_state.json
   # 重新运行
   python rss_monitor.py
   ```

### 3. RSS源没有新文章

**检查方法**：
1. 查看GitHub Actions日志
2. 查看是否有 "📬 发现新文章" 的提示
3. 如果显示 "✨ 暂无新消息（所有文章都已推送过）"，说明没有新文章

**解决方法**：
- 等待RSS源发布新文章
- 或者删除状态文件重新推送

### 4. RSS源获取失败

**检查方法**：
1. 查看GitHub Actions日志
2. 查看是否有错误信息
3. 如果RSS源失败，应该会发送**错误通知**到Discord

**如果没有收到错误通知**：
- 可能是Discord Webhook配置错误
- 或者错误通知发送也失败了

### 5. GitHub Actions没有运行

**检查方法**：
1. 访问：https://github.com/waynegxxx/discord/actions
2. 查看是否有工作流运行记录
3. 查看最新的运行是否成功

**解决方法**：
- 手动触发工作流：点击 "Run workflow"
- 检查工作流是否启用

### 6. 代码执行出错但未显示

**检查方法**：
1. 查看GitHub Actions的完整日志
2. 展开 "运行RSS监控" 步骤
3. 查看是否有异常或错误

## 🔧 详细排查步骤

### 步骤1：验证Discord Webhook

```bash
# 运行测试脚本
python test_discord.py "你的Discord Webhook地址"
```

**预期结果**：
- ✅ 应该收到两条测试消息（文本消息和Embed消息）
- ❌ 如果失败，检查Webhook地址是否正确

### 步骤2：检查GitHub Secrets

访问：https://github.com/waynegxxx/discord/settings/secrets/actions

确认：
- ✅ `DISCORD_WEBHOOK` 已设置
- ✅ `RSS_SOURCES` 已设置（JSON格式）

### 步骤3：查看GitHub Actions日志

1. 访问：https://github.com/waynegxxx/discord/actions
2. 点击最新的工作流运行
3. 展开 "运行RSS监控" 步骤
4. 查看日志输出

**关键信息**：
- `📋 配置检查:` - 检查Webhook是否配置
- `🔍 检查RSS源:` - 检查RSS源是否正常
- `📬 发现新文章:` - 是否有新文章
- `📤 正在发送到Discord:` - 是否尝试发送
- `✅ 推送成功:` 或 `❌ 推送失败:` - 发送结果

### 步骤4：检查推送状态

**如果使用GitHub Actions**：
1. 访问：https://github.com/waynegxxx/discord
2. 查看 `rss_state.json` 文件
3. 如果文件存在且有内容，说明已经推送过文章

**如果使用本地运行**：
```bash
# 查看状态文件
cat rss_state.json
```

### 步骤5：手动测试推送

**方法1：删除状态文件**
```bash
# 本地
rm rss_state.json
python rss_monitor.py

# GitHub Actions
# 删除 rss_state.json 文件并提交
```

**方法2：添加测试RSS源**
在 `RSS_SOURCES` 中添加一个测试源：
```json
[
  {
    "name": "测试源",
    "url": "https://www.ruanyifeng.com/blog/atom.xml"
  }
]
```

### 步骤6：检查Discord服务器

1. 进入Discord服务器
2. 服务器设置 → 集成 → Webhooks
3. 确认Webhook仍然存在
4. 检查Webhook是否有发送记录

## 🎯 常见场景

### 场景1：首次运行，没有收到任何消息

**可能原因**：
1. Discord Webhook配置错误
2. RSS源获取失败
3. GitHub Actions没有运行

**解决方法**：
1. 运行 `python diagnose_discord.py` 诊断
2. 运行 `python test_discord.py` 测试Webhook
3. 查看GitHub Actions日志

### 场景2：之前收到过消息，现在收不到了

**可能原因**：
1. 所有文章都已经推送过了
2. RSS源没有新文章
3. RSS源失效

**解决方法**：
1. 查看GitHub Actions日志，确认是否有新文章
2. 如果显示"暂无新消息"，说明没有新文章
3. 等待RSS源发布新文章

### 场景3：收到错误通知，但没有收到文章推送

**可能原因**：
1. RSS源有问题（会发送错误通知）
2. 文章推送失败（400错误等）

**解决方法**：
1. 查看错误通知的详细信息
2. 根据错误信息修复RSS源
3. 检查文章推送是否失败（查看日志）

## 📝 检查清单

- [ ] Discord Webhook已配置
- [ ] Webhook地址格式正确
- [ ] 运行 `test_discord.py` 测试成功
- [ ] GitHub Secrets已设置
- [ ] RSS_SOURCES格式正确
- [ ] GitHub Actions正在运行
- [ ] 查看GitHub Actions日志
- [ ] 检查是否有新文章
- [ ] 检查推送状态文件
- [ ] Discord服务器中Webhook仍然有效

## 🆘 如果仍然无法解决

1. **运行完整诊断**：
   ```bash
   python diagnose_discord.py
   ```

2. **查看GitHub Actions完整日志**：
   - 复制完整的日志输出
   - 检查每个步骤的执行情况

3. **手动测试**：
   ```bash
   # 测试Webhook
   python test_discord.py "你的Webhook地址"
   
   # 运行监控脚本
   python rss_monitor.py
   ```

4. **提供以下信息**：
   - GitHub Actions日志
   - 诊断脚本输出
   - Discord Webhook测试结果

