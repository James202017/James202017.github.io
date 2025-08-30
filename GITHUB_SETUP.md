# 📚 Пошаговая настройка GitHub Pages и Actions

## 🎯 Цель
Настроить автоматическое развертывание веб-сайта на GitHub Pages и Docker образов на Docker Hub.

## 📋 Что вы получите
- ✅ Автоматическое развертывание сайта на GitHub Pages
- ✅ Автоматическая сборка Docker образов
- ✅ Рабочий сайт-визитка доступный по ссылке
- ✅ Готовые Docker образы для ботов

---

## 🚀 Шаг 1: Создание репозитория на GitHub

### 1.1 Создайте новый репозиторий
1. Перейдите на [GitHub.com](https://github.com)
2. Нажмите кнопку **"New"** (зеленая кнопка)
3. Заполните данные:
   - **Repository name**: `dmitry-realtor` (или любое другое имя)
   - **Description**: `Сайт-визитка риэлтора Дмитрия с Telegram ботами`
   - ✅ **Public** (обязательно для бесплатного GitHub Pages)
   - ❌ НЕ добавляйте README, .gitignore, license (у нас уже есть файлы)
4. Нажмите **"Create repository"**

### 1.2 Скопируйте ссылку на репозиторий
После создания скопируйте ссылку вида:
```
https://github.com/ВАШ_USERNAME/dmitry-realtor.git
```

---

## 💻 Шаг 2: Загрузка файлов в репозиторий

### 2.1 Инициализация Git (если еще не сделано)
Откройте терминал в папке с проектом и выполните:

```bash
# Инициализация Git репозитория
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Dmitry realtor website with Telegram bots"

# Переименование ветки в main
git branch -M main

# Добавление удаленного репозитория (замените на вашу ссылку)
git remote add origin https://github.com/ВАШ_USERNAME/dmitry-realtor.git

# Загрузка файлов на GitHub
git push -u origin main
```

### 2.2 Проверка загрузки
Обновите страницу репозитория на GitHub. Вы должны увидеть все файлы проекта, включая:
- ✅ `index.html`
- ✅ `style.css` 
- ✅ `script.js`
- ✅ `.github/workflows/deploy.yml`
- ✅ `.github/workflows/docker.yml`
- ✅ Все файлы ботов (`BOT_*.py`)

---

## ⚙️ Шаг 3: Настройка GitHub Pages

### 3.1 Включение GitHub Pages
1. В репозитории перейдите в **Settings** (вкладка справа)
2. Прокрутите вниз до раздела **"Pages"** (в левом меню)
3. В разделе **"Source"** выберите:
   - **Source**: `GitHub Actions`
4. Нажмите **"Save"**

### 3.2 Настройка разрешений для Actions
1. В том же разделе **Settings** найдите **"Actions"** → **"General"**
2. В разделе **"Workflow permissions"** выберите:
   - ✅ **"Read and write permissions"**
   - ✅ **"Allow GitHub Actions to create and approve pull requests"**
3. Нажмите **"Save"**

---

## 🐳 Шаг 4: Настройка Docker Hub (опционально)

### 4.1 Создание аккаунта Docker Hub
1. Перейдите на [hub.docker.com](https://hub.docker.com)
2. Создайте бесплатный аккаунт
3. Запомните ваш **username**

### 4.2 Создание Access Token
1. В Docker Hub перейдите в **Account Settings** → **Security**
2. Нажмите **"New Access Token"**
3. Введите название: `GitHub Actions`
4. Скопируйте созданный токен (он больше не будет показан!)

### 4.3 Добавление секретов в GitHub
1. В репозитории перейдите в **Settings** → **Secrets and variables** → **Actions**
2. Нажмите **"New repository secret"**
3. Добавьте два секрета:

**Секрет 1:**
- **Name**: `DOCKERHUB_USERNAME`
- **Secret**: ваш username на Docker Hub

**Секрет 2:**
- **Name**: `DOCKERHUB_TOKEN`
- **Secret**: созданный access token

---

## 🎉 Шаг 5: Запуск и проверка

### 5.1 Автоматический запуск
После загрузки файлов GitHub Actions автоматически:
1. Запустит workflow для GitHub Pages
2. Запустит workflow для Docker (если настроены секреты)

### 5.2 Проверка статуса
1. Перейдите во вкладку **"Actions"** в репозитории
2. Вы увидите запущенные workflows:
   - ✅ **"Deploy to GitHub Pages and Docker Hub"**
   - ✅ **"Build and Push Docker Images"** (если настроен Docker Hub)

### 5.3 Получение ссылки на сайт
1. После успешного выполнения workflow для Pages
2. Перейдите в **Settings** → **Pages**
3. Вы увидите ссылку вида:
   ```
   https://ВАШ_USERNAME.github.io/dmitry-realtor/
   ```
4. Сайт будет доступен через несколько минут

---

## 🔧 Устранение проблем

### ❌ Проблема: "Pages build and deployment failed"
**Решение:**
1. Проверьте, что в Settings → Pages выбран источник "GitHub Actions"
2. Убедитесь, что файл `.github/workflows/deploy.yml` загружен
3. Проверьте логи в разделе Actions

### ❌ Проблема: "Docker build failed"
**Решение:**
1. Проверьте, что секреты `DOCKERHUB_USERNAME` и `DOCKERHUB_TOKEN` добавлены
2. Убедитесь, что токен Docker Hub действителен
3. Проверьте логи в разделе Actions

### ❌ Проблема: "Сайт не открывается"
**Решение:**
1. Подождите 5-10 минут после деплоя
2. Проверьте, что репозиторий публичный (Public)
3. Очистите кэш браузера (Ctrl+F5)
4. Проверьте статус в Settings → Pages

---

## 📁 Структура .github папки

Ваша папка `.github` должна выглядеть так:
```
.github/
└── workflows/
    ├── deploy.yml    # GitHub Pages развертывание
    └── docker.yml    # Docker образы (опционально)
```

### Важно:
- ✅ Папка `.github` должна быть в корне проекта
- ✅ Файлы `.yml` должны быть в папке `workflows`
- ✅ Соблюдайте точные названия файлов
- ✅ Проверьте, что файлы загружены на GitHub

---

## 🎯 Финальная проверка

### Чек-лист готовности:
- ✅ Репозиторий создан и публичный
- ✅ Все файлы загружены на GitHub
- ✅ GitHub Pages включен (Source: GitHub Actions)
- ✅ Workflow permissions настроены
- ✅ Actions запустились без ошибок
- ✅ Сайт доступен по ссылке
- ✅ Docker секреты добавлены (если нужен Docker)

### Ваш сайт готов! 🎉
После выполнения всех шагов ваш сайт будет доступен по адресу:
```
https://ВАШ_USERNAME.github.io/НАЗВАНИЕ_РЕПОЗИТОРИЯ/
```

---

## 📞 Нужна помощь?

Если что-то не работает:
1. Проверьте логи в разделе **Actions**
2. Убедитесь, что все файлы загружены
3. Проверьте настройки репозитория
4. Обратитесь к документации GitHub Pages

**Удачи с развертыванием! 🚀**