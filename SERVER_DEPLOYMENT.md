# Инструкция развертывания ботов и сайта на удаленном сервере

## 🚨 Диагностика проблем с Docker Compose

### Проблема: Зависание на 8/11 при `docker-compose up -d`

**Основные причины:**
1. **Недостаток ресурсов** - одновременная сборка 5 контейнеров
2. **Проблемы с сетью** - медленная загрузка зависимостей
3. **Конфликты портов** - отсутствие явного указания портов
4. **Проблемы с .env файлом** - неправильные переменные окружения

## 📋 Предварительные требования

### Системные требования:
- **RAM**: минимум 2GB, рекомендуется 4GB+
- **CPU**: 2+ ядра
- **Диск**: 10GB+ свободного места
- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+

### Установка Docker и Docker Compose:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений
sudo reboot
```

## 🔧 Подготовка к развертыванию

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### 2. Настройка переменных окружения
```bash
# Создание .env файла
cp .env.example .env
nano .env
```

**Обязательные переменные:**
```env
# Токены ботов (получить у @BotFather)
BOT_TOKEN_P=your_purchase_bot_token
BOT_TOKEN_PR=your_sales_bot_token
BOT_TOKEN_INV=your_investment_bot_token
BOT_TOKEN_STR=your_insurance_bot_token
BOT_TOKEN_OCENKA=your_evaluation_bot_token

# ID администратора (получить у @userinfobot)
ADMIN_CHAT_ID=your_admin_chat_id

# Настройки логирования
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

### 3. Создание директорий
```bash
mkdir -p logs
mkdir -p data
sudo chown -R $USER:$USER logs data
```

## 🚀 Методы развертывания

### Метод 1: Поэтапный запуск (Рекомендуется при проблемах)

```bash
# 1. Сборка образов по одному
docker-compose build bot_p
docker-compose build bot_pr
docker-compose build bot_inv
docker-compose build bot_str
docker-compose build bot_ocenka

# 2. Запуск по одному с интервалом
docker-compose up -d bot_p
sleep 30
docker-compose up -d bot_pr
sleep 30
docker-compose up -d bot_inv
sleep 30
docker-compose up -d bot_str
sleep 30
docker-compose up -d bot_ocenka
```

### Метод 2: Оптимизированный docker-compose

Создайте файл `docker-compose.optimized.yml`:
```yaml
version: '3.9'

services:
  bot_p:
    build: 
      context: .
      dockerfile: Dockerfile
    command: python BOT_P.py
    env_file: .env
    restart: unless-stopped
    mem_limit: 256m
    cpus: 0.5
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  bot_pr:
    build: 
      context: .
      dockerfile: Dockerfile
    command: python BOT_PR.py
    env_file: .env
    restart: unless-stopped
    mem_limit: 256m
    cpus: 0.5
    volumes:
      - ./logs:/app/logs
    depends_on:
      bot_p:
        condition: service_healthy

  bot_inv:
    build: 
      context: .
      dockerfile: Dockerfile
    command: python BOT_Inv.py
    env_file: .env
    restart: unless-stopped
    mem_limit: 256m
    cpus: 0.5
    volumes:
      - ./logs:/app/logs
    depends_on:
      bot_pr:
        condition: service_healthy

  bot_str:
    build: 
      context: .
      dockerfile: Dockerfile
    command: python BOT_Str.py
    env_file: .env
    restart: unless-stopped
    mem_limit: 256m
    cpus: 0.5
    volumes:
      - ./logs:/app/logs
    depends_on:
      bot_inv:
        condition: service_healthy

  bot_ocenka:
    build: 
      context: .
      dockerfile: Dockerfile
    command: python BOT_Ocenka.py
    env_file: .env
    restart: unless-stopped
    mem_limit: 256m
    cpus: 0.5
    volumes:
      - ./logs:/app/logs
    depends_on:
      bot_str:
        condition: service_healthy

networks:
  default:
    name: bots-network
```

Запуск:
```bash
docker-compose -f docker-compose.optimized.yml up -d
```

### Метод 3: Использование готовых образов (Production)

```bash
# Использование production конфигурации
export DOCKER_USERNAME=your_dockerhub_username
export BOT_P_TOKEN=$BOT_TOKEN_P
export BOT_PR_TOKEN=$BOT_TOKEN_PR
export BOT_INV_TOKEN=$BOT_TOKEN_INV
export BOT_STR_TOKEN=$BOT_TOKEN_STR
export BOT_OCENKA_TOKEN=$BOT_TOKEN_OCENKA

docker-compose -f docker-compose.production.yml up -d
```

## 🔍 Диагностика и мониторинг

### Проверка статуса контейнеров
```bash
# Статус всех контейнеров
docker-compose ps

# Логи конкретного бота
docker-compose logs -f bot_p

# Логи всех ботов
docker-compose logs -f

# Использование ресурсов
docker stats
```

### Проверка работоспособности ботов
```bash
# Проверка через Telegram API
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"

# Проверка логов на ошибки
docker-compose logs | grep -i error
```

## 🛠️ Устранение проблем

### Проблема: Контейнер не запускается
```bash
# Проверка логов
docker-compose logs bot_p

# Запуск в интерактивном режиме
docker-compose run --rm bot_p bash

# Проверка переменных окружения
docker-compose exec bot_p env | grep BOT
```

### Проблема: Недостаток памяти
```bash
# Проверка использования памяти
free -h
docker system df

# Очистка неиспользуемых образов
docker system prune -a
```

### Проблема: Медленная сборка
```bash
# Использование кэша Docker
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Сборка с кэшем
docker-compose build --parallel
```

## 📊 Мониторинг и логирование

### Настройка ротации логов
```bash
# Создание конфигурации logrotate
sudo nano /etc/logrotate.d/docker-bots
```

Содержимое файла:
```
/path/to/your/project/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### Мониторинг с Prometheus (опционально)
```bash
# Запуск с мониторингом
docker-compose -f docker-compose.production.yml --profile monitoring up -d

# Доступ к Grafana: http://your-server:3000
# Доступ к Prometheus: http://your-server:9090
```

## 🔄 Автоматизация

### Скрипт автоматического развертывания
```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Начало развертывания ботов..."

# Проверка .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    exit 1
fi

# Остановка старых контейнеров
echo "🛑 Остановка старых контейнеров..."
docker-compose down

# Очистка
echo "🧹 Очистка старых образов..."
docker system prune -f

# Сборка новых образов
echo "🔨 Сборка образов..."
export DOCKER_BUILDKIT=1
docker-compose build --parallel

# Запуск контейнеров
echo "▶️ Запуск контейнеров..."
docker-compose up -d

# Проверка статуса
echo "✅ Проверка статуса..."
sleep 30
docker-compose ps

echo "🎉 Развертывание завершено!"
```

Сделайте скрипт исполняемым:
```bash
chmod +x deploy.sh
./deploy.sh
```

## 🔐 Безопасность

### Настройка файрвола
```bash
# Ubuntu/Debian
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Закрытие портов мониторинга (если не нужны извне)
sudo ufw deny 3000
sudo ufw deny 9090
```

### Регулярное обновление
```bash
# Создание cron задачи для обновления
crontab -e

# Добавить строку (обновление каждую неделю в 2:00)
0 2 * * 0 cd /path/to/your/project && git pull && ./deploy.sh
```

## 📞 Поддержка

### Полезные команды
```bash
# Перезапуск всех ботов
docker-compose restart

# Перезапуск конкретного бота
docker-compose restart bot_p

# Просмотр логов в реальном времени
docker-compose logs -f --tail=100

# Подключение к контейнеру
docker-compose exec bot_p bash

# Проверка конфигурации
docker-compose config
```

### Контакты для поддержки
- Telegram API статус: https://status.telegram.org
- Docker документация: https://docs.docker.com
- Логи проекта: `./logs/`

---

**⚠️ Важно**: Всегда делайте резервные копии данных перед обновлением!