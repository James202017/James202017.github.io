# 🐳 Docker Setup для Telegram Ботов

## Статус проверки Docker

✅ **Docker файлы исправлены и готовы к использованию:**
- `Dockerfile` - исправлен и оптимизирован
- `docker-compose.yml` - исправлены синтаксические ошибки
- `.env.example` - создан шаблон переменных окружения
- `.dockerignore` - создан для оптимизации сборки

❌ **Docker не установлен в системе**

## Установка Docker

### Windows:
1. Скачайте Docker Desktop с официального сайта: https://www.docker.com/products/docker-desktop
2. Запустите установщик и следуйте инструкциям
3. После установки перезагрузите компьютер
4. Запустите Docker Desktop

### Проверка установки:
```bash
docker --version
docker-compose --version
```

## Настройка проекта

### 1. Создайте файл .env
```bash
cp .env.example .env
```

### 2. Заполните токены ботов в .env:
```env
BOT_TOKEN_P=ваш_токен_бота_покупки
BOT_TOKEN_PR=ваш_токен_бота_продажи
BOT_TOKEN_INV=ваш_токен_бота_инвестиций
BOT_TOKEN_STR=ваш_токен_бота_страхования
BOT_TOKEN_OCENKA=ваш_токен_бота_оценки
```

## Запуск проекта

### Запуск всех ботов:
```bash
docker-compose up -d
```

### Запуск конкретного бота:
```bash
docker-compose up bot_inv -d  # только бот инвестиций
docker-compose up bot_p -d    # только бот покупки
```

### Просмотр логов:
```bash
docker-compose logs -f        # все боты
docker-compose logs -f bot_inv # конкретный бот
```

### Остановка:
```bash
docker-compose down
```

## Структура проекта

```
.
├── Dockerfile              # Образ для ботов
├── docker-compose.yml      # Конфигурация сервисов
├── .env.example           # Шаблон переменных
├── .dockerignore          # Исключения для Docker
├── BOT_*.py              # Файлы ботов
└── README_Docker.md      # Эта инструкция
```

## Полезные команды

```bash
# Пересборка образов
docker-compose build

# Просмотр запущенных контейнеров
docker-compose ps

# Перезапуск сервиса
docker-compose restart bot_inv

# Удаление всех контейнеров и образов
docker-compose down --rmi all
```

## Troubleshooting

### Если бот не запускается:
1. Проверьте токены в .env файле
2. Посмотрите логи: `docker-compose logs bot_name`
3. Убедитесь, что порты не заняты

### Если ошибки сборки:
1. Очистите кэш: `docker system prune -a`
2. Пересоберите: `docker-compose build --no-cache`