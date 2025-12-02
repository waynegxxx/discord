# 如何将代码上传到GitHub

## 方法一：使用命令行（推荐）

### 1. 在GitHub上创建新仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角的 `+` 号，选择 `New repository`
3. 填写仓库名称（例如：`rss-monitor`）
4. 选择 `Public` 或 `Private`
5. **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
6. 点击 `Create repository`

### 2. 在本地初始化Git仓库

打开终端（PowerShell或命令提示符），进入项目目录：

```bash
cd C:\Users\Administrator\Desktop\code
```

初始化Git仓库：

```bash
git init
```

### 3. 添加文件到Git

```bash
# 添加所有文件
git add .

# 或者逐个添加
git add rss_monitor.py
git add config.example.json
git add .github/workflows/rss-monitor.yml
git add requirements.txt
git add README.md
git add .gitignore
```

### 4. 提交代码

```bash
git commit -m "初始提交：RSS监控推送工具"
```

### 5. 连接到GitHub仓库并推送

GitHub创建仓库后会显示命令，类似这样：

```bash
# 添加远程仓库（将 YOUR_USERNAME 和 YOUR_REPO_NAME 替换为你的实际信息）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 推送代码到GitHub
git branch -M main
git push -u origin main
```

**注意**：首次推送可能需要登录GitHub，可以使用：
- Personal Access Token（推荐）
- GitHub Desktop
- SSH密钥

## 方法二：使用GitHub Desktop（图形界面，更简单）

### 1. 下载安装GitHub Desktop

访问：https://desktop.github.com/

### 2. 登录GitHub账号

在GitHub Desktop中登录你的GitHub账号

### 3. 创建新仓库

1. 点击 `File` → `New Repository`
2. 填写仓库名称
3. 选择本地路径：`C:\Users\Administrator\Desktop\code`
4. 点击 `Create Repository`

### 4. 提交并推送

1. 在GitHub Desktop中，所有文件会显示在左侧
2. 在底部填写提交信息（例如："初始提交：RSS监控推送工具"）
3. 点击 `Commit to main`
4. 点击 `Publish repository` 将代码推送到GitHub

## 方法三：使用VS Code内置Git功能

如果你使用VS Code：

1. 点击左侧的源代码管理图标（或按 `Ctrl+Shift+G`）
2. 点击"初始化仓库"（如果还没初始化）
3. 点击"+"号添加所有文件
4. 填写提交信息并提交
5. 点击"..."菜单 → "推送" → 选择"发布到GitHub"

## 重要提示

### 不要上传敏感信息

`config.json` 文件已经在 `.gitignore` 中，不会被上传。但请确认：

- ✅ `config.json` 不会被上传（已在.gitignore中）
- ✅ 不要上传包含真实Webhook地址的配置文件
- ✅ 只上传 `config.example.json` 作为模板

### 设置GitHub Secrets（用于GitHub Actions）

代码上传后，需要设置Secrets才能让GitHub Actions正常工作：

1. 进入你的GitHub仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加以下两个Secret：

   **Secret 1:**
   - Name: `FEISHU_WEBHOOK`
   - Value: 你的飞书机器人Webhook地址

   **Secret 2:**
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

## 验证上传成功

上传后，访问你的GitHub仓库页面，应该能看到所有文件：
- ✅ rss_monitor.py
- ✅ config.example.json
- ✅ .github/workflows/rss-monitor.yml
- ✅ requirements.txt
- ✅ README.md
- ✅ .gitignore

## 后续更新代码

如果以后修改了代码，使用以下命令更新：

```bash
git add .
git commit -m "更新说明"
git push
```

## 常见问题

### Q: 提示需要用户名和密码？
A: GitHub已不再支持密码登录，需要使用Personal Access Token：
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 生成新token，勾选 `repo` 权限
3. 使用token作为密码

### Q: 如何查看远程仓库地址？
```bash
git remote -v
```

### Q: 如何修改远程仓库地址？
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

