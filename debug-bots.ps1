# Скрипт диагностики ботов для GitHub Codespaces
# Использование: .\debug-bots.ps1

Write-Host "🔍 Диагностика ботов в GitHub Codespaces" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# 1. Проверка переменных окружения
Write-Host "`n📋 1. Проверка переменных окружения:" -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ Файл .env найден" -ForegroundColor Green
    $envContent = Get-Content ".env" | Where-Object { $_ -match "BOT_TOKEN" }
    foreach ($line in $envContent) {
        if ($line -match "BOT_TOKEN_(\w+)=(.+)") {
            $botName = $matches[1]
            $tokenLength = $matches[2].Length
            if ($tokenLength -gt 10) {
                Write-Host "✅ $botName токен установлен (длина: $tokenLength)" -ForegroundColor Green
            } else {
                Write-Host "❌ $botName токен не установлен или некорректный" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "❌ Файл .env не найден!" -ForegroundColor Red
    Write-Host "💡 Создайте .env файл на основе .env.example" -ForegroundColor Yellow
}

# 2. Проверка Docker контейнеров
Write-Host "`n🐳 2. Проверка Docker контейнеров:" -ForegroundColor Yellow
try {
    $containers = docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    if ($containers) {
        Write-Host $containers
    } else {
        Write-Host "❌ Нет запущенных контейнеров" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Docker недоступен: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Проверка логов контейнеров
Write-Host "`n📝 3. Проверка логов ботов:" -ForegroundColor Yellow
$botNames = @("bot_p", "bot_pr", "bot_inv", "bot_str", "bot_ocenka")
foreach ($bot in $botNames) {
    Write-Host "`n--- Логи $bot ---" -ForegroundColor Cyan
    try {
        $logs = docker logs $bot --tail 10 2>&1
        if ($logs) {
            Write-Host $logs
        } else {
            Write-Host "❌ Контейнер $bot не найден или не запущен" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Ошибка получения логов $bot" -ForegroundColor Red
    }
}

# 4. Проверка сетевого подключения
Write-Host "`n🌐 4. Проверка подключения к Telegram API:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://api.telegram.org" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Подключение к Telegram API работает" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Проблемы с подключением к Telegram API: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Рекомендации по исправлению
Write-Host "`n💡 Рекомендации по исправлению:" -ForegroundColor Yellow
Write-Host "1. Убедитесь, что все BOT_TOKEN_* переменные установлены в .env" -ForegroundColor White
Write-Host "2. Проверьте, что токены ботов действительны в @BotFather" -ForegroundColor White
Write-Host "3. Убедитесь, что ADMIN_CHAT_ID корректный" -ForegroundColor White
Write-Host "4. Перезапустите контейнеры: docker compose restart" -ForegroundColor White
Write-Host "5. Проверьте логи: docker compose logs -f" -ForegroundColor White

Write-Host "`n🔧 Быстрые команды для исправления:" -ForegroundColor Yellow
Write-Host "docker compose down && docker compose up -d" -ForegroundColor Gray
Write-Host "docker compose logs -f bot_p" -ForegroundColor Gray