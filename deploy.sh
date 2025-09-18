#!/bin/bash

# Скрипт развертывания Telegram Bots на Ubuntu 22.04
# Оптимизирован для слабых серверов

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🚀 Начинаем развертывание Telegram Bots..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    log "📦 Устанавливаем Docker..."
    sudo apt update
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
    log_success "Docker установлен"
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    log_warning "Файл .env не найден. Копируем из примера..."
    cp .env.example .env
    log_error "Настройте файл .env с вашими токенами: nano .env"
    log_error "Остановка. Настройте .env и запустите скрипт снова."
    exit 1
fi

# Проверка токенов в .env
if grep -q "your_bot_token_here" .env; then
    log_error "Обнаружены незаполненные токены в .env файле"
    log_error "Настройте файл .env с реальными токенами: nano .env"
    exit 1
fi

log_success "Конфигурация проверена"

# Выбор режима запуска
echo "🔧 Выберите режим запуска:"
echo "1) Минимальные ресурсы (32MB на бот) - для слабых серверов"
echo "2) Стандартные ресурсы (128MB на бот) - для обычных серверов"
read -p "Введите номер (1 или 2): " mode

case $mode in
    1)
        log "🐧 Запускаем в режиме минимальных ресурсов..."
        COMPOSE_FILE="docker-compose.yml"
        ;;
    2)
        log "🚀 Запускаем в стандартном режиме..."
        COMPOSE_FILE="docker-compose.fast.yml"
        ;;
    *)
        log_warning "Неверный выбор. Запускаем в минимальном режиме..."
        COMPOSE_FILE="docker-compose.yml"
        ;;
esac

# Проверка наличия файлов
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Файл $COMPOSE_FILE не найден!"
    exit 1
fi

# Остановка существующих контейнеров
log "Остановка существующих контейнеров..."
docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true

# Сборка и запуск
log "Сборка и запуск сервисов..."
docker compose -f "$COMPOSE_FILE" up -d --build

log "⏳ Ждем запуска контейнеров..."
sleep 15

# Проверка статуса
log "📊 Статус контейнеров:"
docker compose -f "$COMPOSE_FILE" ps

# Показать логи
log "📋 Последние логи:"
docker compose -f "$COMPOSE_FILE" logs --tail=5

echo ""
log_success "✅ Развертывание завершено!"
echo "📋 Полезные команды:"
echo "   Просмотр логов: docker compose logs -f"
echo "   Остановка: docker compose down"
echo "   Перезапуск: docker compose restart"
echo "   Статус: docker compose ps"