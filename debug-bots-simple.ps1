# Диагностика ботов - упрощенная версия
param(
    [switch]$Verbose
)

Write-Host "=== ДИАГНОСТИКА БОТОВ ===" -ForegroundColor Green

# 1. Проверка .env файла
Write-Host "`n1. Проверка переменных окружения..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "✓ Файл .env найден" -ForegroundColor Green
    $envContent = Get-Content ".env" | Where-Object { $_ -match "BOT_TOKEN" }
    if ($envContent) {
        Write-Host "✓ Найдены токены ботов:" -ForegroundColor Green
        $envContent | ForEach-Object { 
            $tokenName = ($_ -split "=")[0]
            Write-Host "  - $tokenName" -ForegroundColor White
        }
    } else {
        Write-Host "✗ Токены ботов не найдены в .env" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Файл .env не найден" -ForegroundColor Red
    Write-Host "Создайте файл .env на основе .env.example" -ForegroundColor Yellow
}

# 2. Проверка Docker
Write-Host "`n2. Проверка Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✓ Docker установлен: $dockerVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Docker не найден" -ForegroundColor Red
}

# 3. Проверка контейнеров
Write-Host "`n3. Проверка контейнеров..." -ForegroundColor Cyan
try {
    $containers = docker ps -a --format "table {{.Names}}\t{{.Status}}" 2>$null
    if ($containers) {
        Write-Host "Статус контейнеров:" -ForegroundColor White
        Write-Host $containers -ForegroundColor Gray
    } else {
        Write-Host "Контейнеры не найдены" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Ошибка при проверке контейнеров" -ForegroundColor Red
}

# 4. Проверка файлов ботов
Write-Host "`n4. Проверка файлов ботов..." -ForegroundColor Cyan
$botFiles = @("BOT_P.py", "BOT_PR.py", "BOT_Inv.py", "BOT_Str.py", "BOT_Ocenka.py")
foreach ($bot in $botFiles) {
    $path = "bots\$bot"
    if (Test-Path $path) {
        Write-Host "✓ $bot найден" -ForegroundColor Green
    } else {
        Write-Host "✗ $bot не найден" -ForegroundColor Red
    }
}

# 5. Проверка requirements.txt
Write-Host "`n5. Проверка зависимостей..." -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    Write-Host "✓ requirements.txt найден" -ForegroundColor Green
} else {
    Write-Host "✗ requirements.txt не найден" -ForegroundColor Red
}

# 6. Рекомендации
Write-Host "`n=== РЕКОМЕНДАЦИИ ===" -ForegroundColor Yellow
Write-Host "1. Убедитесь что .env файл содержит все токены" -ForegroundColor White
Write-Host "2. Запустите: docker compose up -d" -ForegroundColor White
Write-Host "3. Проверьте логи: docker compose logs -f" -ForegroundColor White
Write-Host "4. Для отладки одного бота: python bots\BOT_P.py" -ForegroundColor White

Write-Host "`nДля запуска ботов используйте:" -ForegroundColor Cyan
Write-Host "docker compose up -d" -ForegroundColor Gray