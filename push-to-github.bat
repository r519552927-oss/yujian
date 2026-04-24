@echo off
chcp 65001 >nul
echo ====================================
echo   推送到 GitHub
echo ====================================
echo.
cd /d "C:\Users\r02800540\WorkBuddy"
echo 正在推送...
git push -u origin main
echo.
echo 按任意键关闭...
pause >nul
