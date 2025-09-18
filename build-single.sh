#!/bin/bash

# Скрипт для поэтапной сборки контейнеров с экономией памяти
# Использование: ./build-single.sh [bot_name]

set -e

BOT_NAME=${1:-"bot_p"}
echo "Сборка контейнера для $BOT_NAME..."

# Очищаем неиспользуемые образы и контейнеры
echo "Очистка Docker кэша..."
docker system prune -f --volumes

# Ограничиваем память для Docker daemon
echo "Сборка с ограничением памяти..."
docker build --memory=256m --memory-swap=512m -t "bots_${BOT_NAME}" .

echo "Сборка завершена для $BOT_NAME"
echo "Запуск: docker run -d --name $BOT_NAME --env-file .env --memory=24m bots_${BOT_NAME} python bots/BOT_${BOT_NAME^^}.py"