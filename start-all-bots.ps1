# Скрипт для запуска всех ботов
param(
    [switch]$Stop,
    [switch]$Status
)

$bots = @("BOT_P", "BOT_PR", "BOT_Inv", "BOT_Str", "BOT_Ocenka")

if ($Stop) {
    Write-Host "Остановка всех ботов..." -ForegroundColor Yellow
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*bots/BOT_*" } | Stop-Process -Force
    Write-Host "Все боты остановлены" -ForegroundColor Green
    exit
}

if ($Status) {
    Write-Host "Статус ботов:" -ForegroundColor Cyan
    $processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*bots/BOT_*" }
    if ($processes) {
        $processes | ForEach-Object {
            $botName = (($_.CommandLine -split "bots/")[1] -split "\.py")[0]
            Write-Host "✓ $botName запущен (PID: $($_.Id))" -ForegroundColor Green
        }
    } else {
        Write-Host "Боты не запущены" -ForegroundColor Red
    }
    exit
}

# Проверка .env файла
if (-not (Test-Path ".env")) {
    Write-Host "❌ Файл .env не найден!" -ForegroundColor Red
    Write-Host "Создайте файл .env на основе .env.example" -ForegroundColor Yellow
    exit 1
}

# Проверка токенов
$envContent = Get-Content ".env"
$missingTokens = @()

foreach ($bot in $bots) {
    $tokenVar = "BOT_TOKEN_" + ($bot -replace "BOT_", "")
    if (-not ($envContent | Select-String "$tokenVar=")) {
        $missingTokens += $tokenVar
    }
}

if ($missingTokens.Count -gt 0) {
    Write-Host "❌ Отсутствуют токены:" -ForegroundColor Red
    $missingTokens | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    exit 1
}

Write-Host "🚀 Запуск всех ботов..." -ForegroundColor Green

# Создание директории для логов
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Запуск каждого бота в отдельном процессе
foreach ($bot in $bots) {
    $logFile = "logs/$bot.log"
    Write-Host "Запуск $bot..." -ForegroundColor Cyan
    
    # Запуск в фоновом режиме с перенаправлением вывода
    Start-Process -FilePath "python" -ArgumentList "bots/$bot.py" -RedirectStandardOutput $logFile -RedirectStandardError "$logFile.error" -WindowStyle Hidden
    
    Start-Sleep -Seconds 1
}

Write-Host "`n✅ Все боты запущены!" -ForegroundColor Green
Write-Host "`nПолезные команды:" -ForegroundColor Yellow
Write-Host "  .\start-all-bots.ps1 -Status    # Проверить статус" -ForegroundColor Gray
Write-Host "  .\start-all-bots.ps1 -Stop      # Остановить все боты" -ForegroundColor Gray
Write-Host "  Get-Content logs\BOT_P.log -Tail 10  # Просмотр логов" -ForegroundColor Gray

Write-Host "`nПроверьте работу ботов в Telegram!" -ForegroundColor Cyan