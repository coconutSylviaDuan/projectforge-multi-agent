# AI 策略系统 - 启动脚本 (Windows PowerShell)
# 使用方法：右键点击此文件，选择"使用 PowerShell 运行"

Write-Host "===== AI 策略系统 - 启动中 =====" -ForegroundColor Green
Write-Host ""

# 检查后端是否已在运行
$backendRunning = netstat -ano | Select-String ":8000.*LISTENING"
$frontendRunning = netstat -ano | Select-String ":5173.*LISTENING"

# 启动后端
if (-not $backendRunning) {
    Write-Host "[1/3] 启动后端服务 (端口 8000)..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\dxy\projectforge-multi-agent\generated_projects\jq-ai-strategy-system\backend'; .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
    Start-Sleep -Seconds 3
    Write-Host "后端已启动" -ForegroundColor Green
} else {
    Write-Host "[1/3] 后端服务已在运行" -ForegroundColor Yellow
}

# 启动前端
if (-not $frontendRunning) {
    Write-Host "[2/3] 启动前端服务 (端口 5173)..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\dxy\projectforge-multi-agent\generated_projects\jq-ai-strategy-system\frontend'; C:\Users\95853\.workbuddy\binaries\python\versions\3.13.12\python.exe -m http.server 5173"
    Start-Sleep -Seconds 2
    Write-Host "前端已启动" -ForegroundColor Green
} else {
    Write-Host "[2/3] 前端服务已在运行" -ForegroundColor Yellow
}

# 打开浏览器
Write-Host "[3/3] 打开浏览器..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "===== 启动完成 =====" -ForegroundColor Green
Write-Host "前端地址: <ADDRESS_REMOVED>
Write-Host "后端地址: <ADDRESS_REMOVED>
Write-Host "API 文档: http://localhost:8000/docs"
Write-Host ""
Write-Host "提示: 关闭打开的 PowerShell 窗口即可停止服务" -ForegroundColor Yellow

# 保持窗口打开
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
