# Руководство по установке и запуску ботов

## 🐳 Установка Docker на Windows

### Метод 1: Docker Desktop (Рекомендуется)

1. **Скачайте Docker Desktop:**
   - Перейдите на https://www.docker.com/products/docker-desktop/
   - Скачайте Docker Desktop для Windows

2. **Установите Docker Desktop:**
   - Запустите установщик
   - Следуйте инструкциям мастера установки
   - Перезагрузите компьютер при необходимости

3. **Проверьте установку:**
   ```powershell
   docker --version
   docker-compose --version
   ```

### Метод 2: Docker через WSL2

1. **Включите WSL2:**
   ```powershell
   # Запустите PowerShell от имени администратора
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

2. **Установите Ubuntu из Microsoft Store**

3. **Установите Docker в WSL2:**
   ```bash
   # В терминале Ubuntu
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

## 🚀 Альтернативные методы запуска (без Docker)

### Метод 1: Прямой запуск Python

1. **Установите Python 3.11+:**
   - Скачайте с https://www.python.org/downloads/
   - Убедитесь, что Python добавлен в PATH

2. **Установите зависимости:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**
   ```powershell
   # Скопируйте .env.example в .env
   copy .env.example .env
   # Отредактируйте .env файл с вашими токенами
   ```

4. **Запустите боты:**
   ```powershell
   # Запуск всех ботов в отдельных окнах
   start powershell -ArgumentList "-NoExit", "-Command", "python BOT_P.py"
   start powershell -ArgumentList "-NoExit", "-Command", "python BOT_PR.py"
   start powershell -ArgumentList "-NoExit", "-Command", "python BOT_Inv.py"
   start powershell -ArgumentList "-NoExit", "-Command", "python BOT_Str.py"
   start powershell -ArgumentList "-NoExit", "-Command", "python BOT_Ocenka.py"
   ```

### Метод 2: Использование виртуального окружения

1. **Создайте виртуальное окружение:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Установите зависимости:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Запустите боты:**
   ```powershell
   # В активированном виртуальном окружении
   python BOT_P.py
   ```

### Метод 3: Использование PM2 (Node.js Process Manager)

1. **Установите Node.js и PM2:**
   ```powershell
   # Установите Node.js с https://nodejs.org/
   npm install -g pm2
   ```

2. **Создайте ecosystem.config.js:**
   ```javascript
   module.exports = {
     apps: [
       {
         name: 'bot-p',
         script: 'python',
         args: 'BOT_P.py',
         interpreter: 'none',
         env: {
           NODE_ENV: 'production'
         }
       },
       {
         name: 'bot-pr',
         script: 'python',
         args: 'BOT_PR.py',
         interpreter: 'none'
       },
       {
         name: 'bot-inv',
         script: 'python',
         args: 'BOT_Inv.py',
         interpreter: 'none'
       },
       {
         name: 'bot-str',
         script: 'python',
         args: 'BOT_Str.py',
         interpreter: 'none'
       },
       {
         name: 'bot-ocenka',
         script: 'python',
         args: 'BOT_Ocenka.py',
         interpreter: 'none'
       }
     ]
   };
   ```

3. **Запустите через PM2:**
   ```powershell
   pm2 start ecosystem.config.js
   pm2 status
   pm2 logs
   ```

## 🌐 Запуск веб-интерфейса

### С помощью Python HTTP сервера:
```powershell
cd web
python -m http.server 8080
```

### С помощью Node.js (http-server):
```powershell
npm install -g http-server
cd web
http-server -p 8080
```

## 📊 Мониторинг и логирование

### Создание папки для логов:
```powershell
mkdir logs
```

### Просмотр логов:
```powershell
# Для прямого запуска Python
Get-Content logs\bot_p.log -Wait

# Для PM2
pm2 logs bot-p

# Для Docker
docker-compose logs -f bot_p
```

## 🔧 Устранение неполадок

### Проблема: "Модуль не найден"
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Проблема: "Токен бота недействителен"
1. Проверьте файл .env
2. Убедитесь, что токены корректны
3. Проверьте, что боты не заблокированы в Telegram

### Проблема: "Порт уже используется"
```powershell
# Найти процесс, использующий порт
netstat -ano | findstr :8080
# Завершить процесс
taskkill /PID <PID> /F
```

## 🚀 Быстрый старт

### Для разработки (без Docker):
```powershell
# 1. Клонируйте репозиторий
# 2. Установите зависимости
pip install -r requirements.txt

# 3. Настройте .env файл
copy .env.example .env
# Отредактируйте .env

# 4. Запустите боты
.\start_bots.ps1

# 5. Запустите веб-интерфейс
cd web
python -m http.server 8080
```

### Для продакшена (с Docker):
```powershell
# 1. Установите Docker Desktop
# 2. Настройте .env файл
# 3. Запустите
docker-compose -f docker-compose.optimized.yml up -d
```

## 📝 Полезные команды

```powershell
# Проверка статуса Python
python --version
pip --version

# Проверка установленных пакетов
pip list

# Обновление всех пакетов
pip install --upgrade -r requirements.txt

# Проверка портов
netstat -an | findstr :8080

# Мониторинг процессов
Get-Process python
```