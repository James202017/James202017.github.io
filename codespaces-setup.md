# 🚀 Настройка ботов в GitHub Codespaces

## 📋 Пошаговая инструкция

### 1. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл и добавьте ваши токены:

```env
# Telegram Bot Tokens - получите в @BotFather
BOT_TOKEN_P=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
BOT_TOKEN_PR=1234567890:BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
BOT_TOKEN_INV=1234567890:CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
BOT_TOKEN_STR=1234567890:DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
BOT_TOKEN_OCENKA=1234567890:EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE

# Admin Chat ID - ваш Telegram ID
ADMIN_CHAT_ID=123456789
```

### 2. Запуск ботов

#### Вариант A: Docker Compose (рекомендуется)

```bash
# Запуск всех ботов
docker compose up -d

# Проверка статуса
docker compose ps

# Просмотр логов
docker compose logs -f
```

#### Вариант B: Ультра-легкий режим (при проблемах с памятью)

```bash
# Только один бот
docker compose -f docker-compose.ultra-light.yml up -d
```

#### Вариант C: Прямой запуск Python (для отладки)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск конкретного бота
python bots/BOT_P.py
```

### 3. Диагностика проблем

Запустите скрипт диагностики:

```bash
# Linux/Mac
chmod +x debug-bots.sh
./debug-bots.sh

# Windows (если используете PowerShell)
.\debug-bots.ps1
```

### 4. Проверка работы ботов

1. **Откройте Telegram**
2. **Найдите ваших ботов** по username
3. **Отправьте команду** `/start`
4. **Проверьте ответ** бота

### 5. Частые проблемы и решения

#### ❌ Бот не отвечает на /start

**Причины:**
- Неправильный токен бота
- Бот не запущен
- Проблемы с сетью

**Решение:**
```bash
# Проверьте логи
docker compose logs bot_p

# Перезапустите бота
docker compose restart bot_p

# Проверьте токен в .env файле
```

#### ❌ Ошибка "BOT_TOKEN_P не найден"

**Решение:**
```bash
# Убедитесь, что .env файл существует
ls -la .env

# Проверьте содержимое
cat .env | grep BOT_TOKEN_P
```

#### ❌ Контейнер не запускается

**Решение:**
```bash
# Очистите Docker кэш
docker system prune -f

# Пересоберите образы
docker compose build --no-cache

# Запустите заново
docker compose up -d
```

### 6. Мониторинг

#### Просмотр логов в реальном времени:
```bash
docker compose logs -f bot_p
```

#### Проверка использования ресурсов:
```bash
docker stats
```

#### Проверка статуса всех контейнеров:
```bash
docker compose ps
```

### 7. Остановка ботов

```bash
# Остановить все боты
docker compose down

# Остановить с удалением данных
docker compose down -v
```

## 🔧 Полезные команды

```bash
# Быстрый перезапуск
docker compose restart

# Обновление образов
docker compose pull && docker compose up -d

# Просмотр конфигурации
docker compose config

# Выполнение команды в контейнере
docker compose exec bot_p bash
```

## 📞 Поддержка

Если проблемы не решаются:

1. Запустите `./debug-bots.sh`
2. Сохраните вывод команды
3. Проверьте логи: `docker compose logs`
4. Убедитесь, что токены ботов действительны в @BotFather