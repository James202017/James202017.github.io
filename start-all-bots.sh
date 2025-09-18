#!/bin/bash

# Скрипт для запуска всех ботов в GitHub Codespaces

BOTS=("BOT_P" "BOT_PR" "BOT_Inv" "BOT_Str" "BOT_Ocenka")

# Функция для остановки ботов
stop_bots() {
    echo "🛑 Остановка всех ботов..."
    
    if command -v powershell.exe >/dev/null 2>&1; then
        # Windows окружение - используем WMI для остановки процессов
        powershell.exe -Command "Get-WmiObject Win32_Process | Where-Object { \\\$_.Name -eq 'python.exe' -and \\\$_.CommandLine -like '*bots/*' } | ForEach-Object { Stop-Process -Id \\\$_.ProcessId -Force }" 2>/dev/null
    else
        # Linux окружение - используем pkill
        pkill -f "python.*bots/"
    fi
    
    echo "✅ Все боты остановлены"
}

# Функция для проверки статуса
check_status() {
    echo "📊 Статус ботов:"
    
    # Проверяем процессы через PowerShell (для Windows)
    if command -v powershell.exe >/dev/null 2>&1; then
        # Используем Get-Process для проверки процессов Windows
        for bot in "${BOTS[@]}"; do
            result=$(powershell.exe -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { (Get-WmiObject Win32_Process -Filter \"ProcessId = \\\$(\\\$_.Id)\").CommandLine -like '*bots/$bot.py*' } | Select-Object -First 1 -ExpandProperty Id" 2>/dev/null | tr -d '\r\n' | sed 's/[[:space:]]*$//')
            if [ ! -z "$result" ] && [ "$result" != "" ]; then
                echo "✅ $bot запущен (PID: $result)"
            else
                echo "❌ $bot не запущен"
            fi
        done
    else
        # Стандартная проверка для Linux
        for bot in "${BOTS[@]}"; do
            if pgrep -f "python.*bots/$bot.py" > /dev/null; then
                pid=$(pgrep -f "python.*bots/$bot.py")
                echo "✅ $bot запущен (PID: $pid)"
            else
                echo "❌ $bot не запущен"
            fi
        done
    fi
}

# Обработка параметров
case "$1" in
    "stop")
        stop_bots
        exit 0
        ;;
    "status")
        check_status
        exit 0
        ;;
    "restart")
        stop_bots
        sleep 2
        ;;
esac

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "💡 Создайте файл .env на основе .env.example:"
    echo "   cp .env.example .env"
    echo "   nano .env  # Добавьте ваши токены"
    exit 1
fi

# Проверка токенов
echo "🔍 Проверка токенов..."
missing_tokens=()

for bot in "${BOTS[@]}"; do
    token_var="BOT_TOKEN_${bot#BOT_}"
    if ! grep -q "^$token_var=" .env; then
        missing_tokens+=("$token_var")
    fi
done

if [ ${#missing_tokens[@]} -gt 0 ]; then
    echo "❌ Отсутствуют токены:"
    for token in "${missing_tokens[@]}"; do
        echo "   - $token"
    done
    echo "💡 Добавьте недостающие токены в файл .env"
    exit 1
fi

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
if ! python3 -c "import aiogram" 2>/dev/null; then
    echo "⚠️  Установка зависимостей..."
    pip install -r requirements.txt
fi

# Создание директории для логов
mkdir -p logs

echo "🚀 Запуск всех ботов..."

# Остановка существующих процессов
stop_bots
sleep 1

# Запуск каждого бота в фоновом режиме
for bot in "${BOTS[@]}"; do
    echo "🔄 Запуск $bot..."
    nohup python3 "bots/$bot.py" > "logs/$bot.log" 2>&1 &
    sleep 0.5
done

echo ""
echo "✅ Все боты запущены!"
echo ""
echo "📋 Полезные команды:"
echo "   ./start-all-bots.sh status    # Проверить статус"
echo "   ./start-all-bots.sh stop      # Остановить все боты"
echo "   ./start-all-bots.sh restart   # Перезапустить все боты"
echo "   tail -f logs/BOT_P.log        # Просмотр логов"
echo ""
echo "🔗 Проверьте работу ботов в Telegram!"
echo ""

# Показать статус через 3 секунды
sleep 3
check_status