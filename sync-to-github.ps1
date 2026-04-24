# WorkBuddy GitHub 同步脚本
# 使用方法：
#   1. 在私人电脑上，确保已安装 Git
#   2. 打开 PowerShell，进入你的WorkBuddy目录
#   3. 直接运行此脚本，或复制下面的命令执行

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   WorkBuddy GitHub 同步向导" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: 配置Git用户信息
Write-Host "[1/5] 配置Git用户信息..." -ForegroundColor Yellow
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的邮箱@example.com"

# Step 2: 创建GitHub仓库
Write-Host ""
Write-Host "[2/5] 创建GitHub仓库..." -ForegroundColor Yellow
Write-Host "请在浏览器中打开: https://github.com/new" -ForegroundColor Green
Write-Host "  - Repository name: workbuddy-projects" -ForegroundColor White
Write-Host "  - 选择 Private (私有仓库)" -ForegroundColor White
Write-Host "  - 不要勾选 Initialize this repository with a README" -ForegroundColor White
Write-Host "  - 点击 Create repository" -ForegroundColor White
Write-Host ""
$repo_url = Read-Host "创建完成后，粘贴仓库地址 (例如: https://github.com/你的用户名/workbuddy-projects.git)"

# Step 3: 添加远程仓库
Write-Host ""
Write-Host "[3/5] 添加远程仓库..." -ForegroundColor Yellow
git remote add origin $repo_url

# Step 4: 推送代码
Write-Host ""
Write-Host "[4/5] 推送到GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

# Step 5: 验证
Write-Host ""
Write-Host "[5/5] 验证推送结果..." -ForegroundColor Yellow
git remote -v

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "   同步完成！✅" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "日常使用命令:" -ForegroundColor Cyan
Write-Host "  git status     - 查看修改状态"
Write-Host "  git add .      - 添加所有修改"
Write-Host "  git commit -m '描述' - 提交"
Write-Host "  git push       - 推送到GitHub"
Write-Host "  git pull       - 从GitHub拉取更新"
Write-Host ""
Write-Host "在新设备上同步:" -ForegroundColor Cyan
Write-Host "  git clone $repo_url" -ForegroundColor White
Write-Host ""
