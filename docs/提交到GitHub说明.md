# 提交到 GitHub 说明

> 若想系统学习「本地创建项目 → 在 GitHub 建仓 → 初始提交 → 日常提交代码」的完整流程，请查看 **[Git与GitHub从零到提交完整流程.md](./Git与GitHub从零到提交完整流程.md)**。

## 当前状态

- 远程仓库已配置：**https://github.com/haiyiguoHarry/AI-.git**
- 分支：**main**
- 已添加 `.gitignore`（排除 `.env`、`venv/`、`__pycache__/`、`data/*.pdf` 等）
- 所有文档与项目骨架已**暂存**（`git add` 已完成），只差执行 **commit** 和 **push**

若在 Cursor 内置终端执行 `git commit` 出现 `unknown option 'trailer'`，多半是环境或 IDE 对 Git 的包装导致，请在本机**单独打开** 命令提示符 或 **Git Bash** 执行下面步骤。

---

## 方式一：在本机终端手动执行（推荐）

1. **打开 命令提示符(CMD)** 或 **Git Bash**（不要用 Cursor 里的终端）。

2. 进入项目目录并提交、推送：

```bash
cd /d e:\workspace\AI-
git status
git commit -m "Add learning plan, docs and 4 RAG/Agent project skeletons"
git push -u origin main
```

3. 若需要登录 GitHub，按提示输入用户名和**个人访问令牌（Token）**（密码已不再支持）。

---

## 方式二：用脚本

双击运行：

**e:\\workspace\\AI-\\scripts\\commit-and-push.bat**

若脚本里 `git commit` 仍报错，请改用方式一，在**本机新开的 CMD** 里执行上述命令。

---

## 首次推送如遇认证

- GitHub 已不再支持账号密码，需使用 **Personal Access Token (PAT)**：
  1. 打开 https://github.com/settings/tokens
  2. Generate new token (classic)，勾选 `repo` 权限
  3. 复制生成的 token，在 `git push` 时「密码」处粘贴该 token

- 或使用 **Git Credential Manager**：首次 push 会弹出浏览器完成登录，之后会记住。

---

## 提交后

仓库地址：**https://github.com/haiyiguoHarry/AI-**

可在该页面查看 README、`docs/` 与 `projects/` 是否已完整显示。
