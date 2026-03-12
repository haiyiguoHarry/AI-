@echo off
cd /d "e:\workspace\AI-"
git add .
git status
echo.
echo 若上面没有待提交文件，可跳过 commit。
echo 正在执行 commit（若失败请在本机打开 CMD 或 Git Bash 手动执行下面两行）：
echo   git commit -m "Add learning plan, docs and 4 RAG/Agent project skeletons"
echo   git push -u origin main
echo.
git commit -m "Add learning plan, docs and 4 RAG/Agent project skeletons"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Commit 失败。请打开 命令提示符(CMD) 或 Git Bash，进入 e:\workspace\AI- 后执行：
    echo   git commit -m "Add learning plan, docs and 4 RAG/Agent project skeletons"
    echo   git push -u origin main
    pause
    exit /b 1
)
git push -u origin main
echo.
echo 已推送到 GitHub: https://github.com/haiyiguoHarry/AI-
pause
