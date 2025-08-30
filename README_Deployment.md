# 🚀 Руководство по развертыванию проекта

## 📋 Содержание
- [GitHub Pages](#github-pages)
- [Docker Hub](#docker-hub)
- [Локальное развертывание](#локальное-развертывание)
- [Переменные окружения](#переменные-окружения)
- [Мониторинг и логи](#мониторинг-и-логи)

## 🌐 GitHub Pages

### Автоматическое развертывание

1. **Загрузите проект на GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/ВАШ_USERNAME/ВАШ_РЕПОЗИТОРИЙ.git
   git push -u origin main
   ```

2. **Настройте GitHub Pages:**
   - Перейдите в Settings → Pages
   - Source: Deploy from a branch
   - Branch: main
   - Folder: / (root)
   - Нажмите Save

3. **Активируйте GitHub Actions:**
   - Перейдите в Settings → Actions → General
   - Workflow permissions: Read and write permissions
   - Allow GitHub Actions to create and approve pull requests: ✅

### Ручное развертывание

Если нужно развернуть только веб-сайт без автоматизации:

1. Создайте новый репозиторий на GitHub
2. Загрузите файлы: `index.html`, `style.css`, `script.js`
3. Включите GitHub Pages в настройках репозитория

## 🐳 Docker Hub

### Настройка секретов GitHub

1. **Создайте аккаунт на Docker Hub** (если нет)
2. **Создайте Access Token:**
   - Docker Hub → Account Settings → Security → New Access Token
   - Скопируйте токен

3. **Добавьте секреты в GitHub:**
   - Репозиторий → Settings → Secrets and variables → Actions
   - Добавьте секреты:
     - `DOCKERHUB_USERNAME`: ваш username на Docker Hub
     - `DOCKERHUB_TOKEN`: созданный access token

### Автоматическая сборка

После настройки секретов, при каждом push в main ветку:
- ✅ Собирается общий Docker образ со всеми ботами
- ✅ Собираются отдельные образы для каждого бота
- ✅ Образы публикуются на Docker Hub

### Ручная сборка и публикация

```bash
# Сборка общего образа
docker build -t ВАШ_USERNAME/dmitry-realtor-bots:latest .
docker push ВАШ_USERNAME/dmitry-realtor-bots:latest

# Сборка отдельных ботов
docker-compose build
docker-compose push
```

## 🏠 Локальное развертывание

### Веб-сайт

```bash
# Python HTTP сервер
python -m http.server 8000

# Или Node.js (если установлен)
npx serve .
```

Сайт будет доступен по адресу: http://localhost:8000

### Telegram боты

#### Вариант 1: Docker Compose (рекомендуется)

```bash
# Создайте .env файл на основе .env.example
cp .env.example .env
# Заполните токены ботов в .env

# Запуск всех ботов
docker-compose up -d

# Запуск конкретного бота
docker-compose up -d bot_inv

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

#### Вариант 2: Прямой запуск Python

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск конкретного бота
python BOT_Inv.py
```

## 🔐 Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Токены Telegram ботов
BOT_P_TOKEN=your_bot_token_here
BOT_PR_TOKEN=your_bot_token_here
BOT_INV_TOKEN=your_bot_token_here
BOT_STR_TOKEN=your_bot_token_here
BOT_OCENKA_TOKEN=your_bot_token_here

# Дополнительные настройки (опционально)
# DATABASE_URL=sqlite:///bots.db
# LOG_LEVEL=INFO
# WEBHOOK_URL=https://yourdomain.com/webhook
```

### Получение токенов ботов

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env` файл

## 📊 Мониторинг и логи

### Docker логи

```bash
# Все сервисы
docker-compose logs -f

# Конкретный бот
docker-compose logs -f bot_inv

# Последние 100 строк
docker-compose logs --tail=100 bot_inv
```

### Проверка статуса

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats
```

### Перезапуск ботов

```bash
# Перезапуск всех ботов
docker-compose restart

# Перезапуск конкретного бота
docker-compose restart bot_inv
```

## 🔧 Устранение неполадок

### Проблемы с GitHub Actions

- Проверьте, что секреты `DOCKERHUB_USERNAME` и `DOCKERHUB_TOKEN` настроены
- Убедитесь, что GitHub Actions включены в настройках репозитория
- Проверьте логи в разделе Actions

### Проблемы с Docker

- Убедитесь, что Docker установлен и запущен
- Проверьте, что файл `.env` создан и содержит токены
- Проверьте логи: `docker-compose logs`

### Проблемы с ботами

- Проверьте правильность токенов в `.env`
- Убедитесь, что боты не заблокированы
- Проверьте интернет-соединение

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки переменных окружения
4. Обратитесь к документации Docker и GitHub Actions

---

**Проект готов к продакшену! 🎉**