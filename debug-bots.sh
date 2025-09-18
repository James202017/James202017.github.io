#!/bin/bash

# Скрипт диагностики ботов для GitHub Codespaces
# Использование: ./debug-bots.sh

echo "🔍 Диагностика ботов в GitHub Codespaces"
echo "=================================================="

# 1. Проверка переменных окружения
echo -e "\n📋 1. Проверка переменных окружения:"
if [ -f ".env" ]; then
    echo "✅ Файл .env найден"
    while IFS= read -r line; do
        if [[ $line =~ BOT_TOKEN_([A-Z_]+)=(.+) ]]; then
            bot_name="${BASH_REMATCH[1]}"
            token="${BASH_REMATCH[2]}"
            token_length=${#token}
            if [ $token_length -gt 10 ]; then
                echo "✅ $bot_name токен установлен (длина: $token_length)"
            else
                echo "❌ $bot_name токен не установлен или некорректный"
            fi
        fi
    done < .env
else
    echo "❌ Файл .env не найден!"
    echo "💡 Создайте .env файл на основе .env.example"
fi

# 2. Проверка Docker контейнеров
echo -e "\n🐳 2. Проверка Docker контейнеров:"
if command -v docker &> /dev/null; then
    containers=$(docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")
    if [ -n "$containers" ]; then
        echo "$containers"
    else
        echo "❌ Нет запущенных контейнеров"
    fi
else
    echo "❌ Docker недоступен"
fi

# 3. Проверка логов контейнеров
echo -e "\n📝 3. Проверка логов ботов:"
bot_names=("bot_p" "bot_pr" "bot_inv" "bot_str" "bot_ocenka")
for bot in "${bot_names[@]}"; do
    echo -e "\n--- Логи $bot ---"
    if docker ps -a --format "{{.Names}}" | grep -q "^${bot}$"; then
        docker logs "$bot" --tail 10 2>&1 || echo "❌ Ошибка получения логов $bot"
    else
        echo "❌ Контейнер $bot не найден или не запущен"
    fi
done

# 4. Проверка сетевого подключения
echo -e "\n🌐 4. Проверка подключения к Telegram API:"
if curl -s --connect-timeout 10 https://api.telegram.org > /dev/null; then
    echo "✅ Подключение к Telegram API работает"
else
    echo "❌ Проблемы с подключением к Telegram API"
fi

# 5. Проверка процессов Python
echo -e "\n🐍 5. Проверка процессов Python:"
python_processes=$(ps aux | grep -E "python.*BOT_" | grep -v grep)
if [ -n "$python_processes" ]; then
    echo "✅ Найдены процессы ботов:"
    echo "$python_processes"
else
    echo "❌ Процессы ботов не найдены"
fi

# 6. Рекомендации по исправлению
echo -e "\n💡 Рекомендации по исправлению:"
echo "1. Убедитесь, что все BOT_TOKEN_* переменные установлены в .env"
echo "2. Проверьте, что токены ботов действительны в @BotFather"
echo "3. Убедитесь, что ADMIN_CHAT_ID корректный"
echo "4. Перезапустите контейнеры: docker compose restart"
echo "5. Проверьте логи: docker compose logs -f"

echo -e "\n🔧 Быстрые команды для исправления:"
echo "docker compose down && docker compose up -d"
echo "docker compose logs -f bot_p"

# Делаем скрипт исполняемым
chmod +x "$0" 2>/dev/null || true