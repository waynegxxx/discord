# Discord RSS监控 - 快速上手指南

## 📋 仓库信息

- **GitHub仓库**: https://github.com/waynegxxx/discord.git
- **功能**: 自动监控RSS源，推送到Discord群

## 🚀 快速开始

### 步骤1：安装Git（如果还没安装）

**Windows用户**：
```powershell
# 使用winget安装
winget install --id Git.Git -e --source winget
```

或者访问：https://git-scm.com/download/win 下载安装

### 步骤2：上传代码到GitHub

在项目目录（`C:\Users\Administrator\Desktop\code`）打开PowerShell，执行：

```powershell
# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "初始提交：Discord RSS监控工具"

# 添加远程仓库
git remote add origin https://github.com/waynegxxx/discord.git

# 设置主分支
git branch -M main

# 推送到GitHub（需要GitHub认证）
git push -u origin main
```

**如果遇到认证问题**：
- 使用Personal Access Token（推荐）
  - 访问：https://github.com/settings/tokens
  - 生成新token，勾选 `repo` 权限
  - 推送时，用户名填GitHub用户名，密码填token

### 步骤3：设置GitHub Secrets

代码上传后，需要设置Secrets才能让GitHub Actions自动运行：

1. 访问：https://github.com/waynegxxx/discord/settings/secrets/actions
2. 点击 "New repository secret"，添加以下两个Secret：

   **Secret 1（必需）:**
   - Name: `DISCORD_WEBHOOK`
   - Value: 你的Discord机器人Webhook地址
   
   **如何获取Discord Webhook地址：**
   - 在Discord服务器中，进入 **服务器设置** → **集成** → **Webhooks**
   - 点击 **新建Webhook** 或选择现有Webhook
   - 复制Webhook URL（格式：`https://discord.com/api/webhooks/xxxxx/xxxxx`）

   **Secret 2（必需）:**
   - Name: `RSS_SOURCES`
   - Value: JSON格式的RSS源配置，例如：
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

### 步骤4：验证运行

1. 访问：https://github.com/waynegxxx/discord/actions
2. 应该能看到 "RSS监控推送" 工作流
3. 工作流会自动每30分钟运行一次
4. 也可以点击 "Run workflow" 手动触发

## 📝 本地测试（可选）

如果想在本地先测试：

1. **安装依赖**：
```powershell
pip install -r requirements.txt
```

2. **创建配置文件** `config.json`：
```json
{
  "discord_webhook": "你的Discord Webhook地址",
  "rss_sources": [
    {
      "name": "网站名称",
      "url": "RSS链接"
    }
  ]
}
```

3. **运行脚本**：
```powershell
python rss_monitor.py
```

## ✅ 验证清单

上传成功后，访问 https://github.com/waynegxxx/discord 应该能看到：

- ✅ `rss_monitor.py` - 主监控脚本
- ✅ `config.example.json` - 配置文件模板
- ✅ `.github/workflows/rss-monitor.yml` - GitHub Actions工作流
- ✅ `requirements.txt` - Python依赖
- ✅ `README.md` - 使用说明
- ✅ `.gitignore` - Git忽略文件

## 🔧 常见问题

**Q: GitHub Actions没有运行？**
- 检查是否设置了 `DISCORD_WEBHOOK` 和 `RSS_SOURCES` Secrets
- 检查工作流文件 `.github/workflows/rss-monitor.yml` 是否存在

**Q: 推送失败？**
- 检查Discord Webhook地址是否正确
- 检查RSS链接是否可访问
- 查看GitHub Actions的日志输出

**Q: 如何修改RSS源？**
- 在GitHub仓库的Settings → Secrets中更新 `RSS_SOURCES`
- 或者修改本地 `config.json` 后重新推送代码

## 📚 更多信息

- 详细使用说明：查看 `README.md`
- 上传指南：查看 `上传到GitHub.md`
- 故障排查：查看 `故障排查.md`

