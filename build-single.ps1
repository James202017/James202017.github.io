# Скрипт для поэтапной сборки контейнеров с экономией памяти
# Использование: .\build-single.ps1 [bot_name]

param(
    [string]$BotName = "bot_p"
)

Write-Host "Сборка контейнера для $BotName..." -ForegroundColor Green

try {
    # Очищаем неиспользуемые образы и контейнеры
    Write-Host "Очистка Docker кэша..." -ForegroundColor Yellow
    docker system prune -f --volumes

    # Ограничиваем память для сборки
    Write-Host "Сборка с ограничением памяти..." -ForegroundColor Yellow
    docker build --memory=256m --memory-swap=512m -t "bots_$BotName" .

    Write-Host "Сборка завершена для $BotName" -ForegroundColor Green
    
    $upperBotName = $BotName.ToUpper()
    Write-Host "Запуск: docker run -d --name $BotName --env-file .env --memory=24m bots_$BotName python bots/BOT_$upperBotName.py" -ForegroundColor Cyan
}
catch {
    Write-Host "Ошибка при сборке: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}