# 将代码上传到 GitHub 仓库

你的仓库地址：`https://github.com/waynegxxx/discord.git`

## 步骤一：安装 Git（如果还没安装）

### 方法1：下载安装Git for Windows
1. 访问：https://git-scm.com/download/win
2. 下载并安装（使用默认选项即可）
3. 安装完成后，重新打开终端

### 方法2：使用winget安装（Windows 10/11）
在PowerShell中运行：
```powershell
winget install --id Git.Git -e --source winget
```

## 步骤二：初始化Git仓库并上传

安装Git后，在项目目录执行以下命令：

```powershell
# 1. 进入项目目录
cd C:\Users\Administrator\Desktop\code

# 2. 初始化Git仓库
git init

# 3. 添加所有文件
git add .

# 4. 提交代码
git commit -m "初始提交：RSS监控推送工具"

# 5. 添加远程仓库
git remote add origin https://github.com/waynegxxx/discord.git

# 6. 设置主分支名称
git branch -M main

# 7. 推送到GitHub
git push -u origin main
```

## 如果遇到认证问题

### 使用Personal Access Token（推荐）

1. **生成Token**：
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 填写名称（如：rss-monitor）
   - 勾选 `repo` 权限
   - 点击 "Generate token"
   - **复制生成的token**（只显示一次！）

2. **推送时使用Token**：
   - 用户名：输入你的GitHub用户名
   - 密码：输入刚才复制的token（不是GitHub密码）

### 或者使用GitHub Desktop（更简单）

1. 下载：https://desktop.github.com/
2. 登录GitHub账号
3. File → Add Local Repository → 选择 `C:\Users\Administrator\Desktop\code`
4. 点击 "Publish repository"
5. 仓库名称会自动识别为 `discord`

## 步骤三：设置GitHub Secrets（用于自动运行）

代码上传后，需要设置Secrets才能让GitHub Actions自动运行：

1. 访问：https://github.com/waynegxxx/discord/settings/secrets/actions
2. 点击 "New repository secret"
3. 添加以下两个Secret：

   **Secret 1（必需）:**
   - Name: `DISCORD_WEBHOOK`
   - Value: 你的Discord机器人Webhook地址

   **Secret 2（必需）:**
   - Name: `RSS_SOURCES`
   - Value: JSON格式，例如：
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

   **Secret 3（可选）:**
   - Name: `FEISHU_WEBHOOK`
   - Value: 你的飞书机器人Webhook地址（如果也想推送到飞书）

## 验证上传成功

访问 https://github.com/waynegxxx/discord 应该能看到：
- ✅ rss_monitor.py
- ✅ config.example.json
- ✅ .github/workflows/rss-monitor.yml
- ✅ requirements.txt
- ✅ README.md
- ✅ .gitignore

## 后续更新代码

修改代码后，使用以下命令更新：

```powershell
git add .
git commit -m "更新说明"
git push
```

## 常见问题

**Q: 提示 "remote origin already exists"？**
```powershell
git remote remove origin
git remote add origin https://github.com/waynegxxx/discord.git
```

**Q: 如何查看当前远程仓库？**
```powershell
git remote -v
```

**Q: 如何修改远程仓库地址？**
```powershell
git remote set-url origin https://github.com/waynegxxx/discord.git
```

