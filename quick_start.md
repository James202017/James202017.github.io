# 🚀 Быстрый запуск ботов

## Для слабых серверов Ubuntu 22.04 (рекомендуется)

### 1. Клонирование репозитория
```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Настройка переменных окружения
```bash
cp .env.example .env
nano .env
```

### 3. Запуск (выберите один вариант)

#### Вариант A: Минимальные ресурсы (32MB RAM на бот)
```bash
docker compose up -d
```

#### Вариант B: Стандартные ресурсы (128MB RAM на бот)
```bash
docker compose -f docker-compose.fast.yml up -d
```

### 4. Проверка статуса
```bash
docker compose ps
docker compose logs
```

### 5. Остановка
```bash
docker compose down
```

## 📋 Требования
- Ubuntu 22.04 LTS
- Docker и Docker Compose
- Минимум 128MB RAM
- 1GB свободного места

## ⚡ Особенности оптимизации
- Использует Alpine Linux (50MB вместо 400MB)
- Минимальные зависимости (только 3 пакета)
- Быстрая сборка (10-15 секунд)
- Низкое потребление ресурсов

### 2. Установка Docker (3 способа)

#### Способ 1: Официальный репозиторий Docker
```bash
# Добавление ключа и репозитория
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
```

#### Способ 2: Через Snap (если первый не работает)
```bash
sudo snap install docker
sudo addgroup --system docker
sudo adduser $USER docker
newgrp docker
```

#### Способ 3: Без Docker (только Python)
```bash
# Пропустите установку Docker и используйте только Python
echo "Запуск без Docker - переходите к шагу 3"
```

### 3. Клонирование и настройка проекта
```bash
# Клонирование
git clone <YOUR_GITHUB_REPO_URL>
cd "Рабочие боты"

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
nano .env  # Введите ваши токены ботов
```

### 4. Запуск проекта

#### Вариант A: С Docker (быстрая сборка)
```bash
# Проверка Docker
docker --version

# БЫСТРЫЙ запуск через Alpine Linux (рекомендуется при медленной сборке)
docker compose -f docker-compose.fast.yml up -d

# Или стандартный запуск (может быть медленным)
docker compose -f docker-compose.optimized.yml up -d

# Проверка статуса
docker compose -f docker-compose.fast.yml ps
```

**Важно:** 
- При запуске Docker контейнеров команды `apt update` и `apt upgrade` **НЕ НУЖНЫ**!
- Если сборка идет очень долго (>5 минут), используйте `docker-compose.fast.yml` - он использует Alpine Linux и собирается в 3-5 раз быстрее
- При ошибках типа "ERROR [bot_p 2/7] RUN apt-get update" используйте быструю версию

#### Вариант B: Без Docker (рекомендуется при проблемах)
```bash
# Запуск ботов
chmod +x deploy.sh
./deploy.sh

# В новом терминале - запуск веб-сервера
cd "Рабочие боты"
python3 -c "
import http.server, socketserver, os
os.chdir('web')
with socketserver.TCPServer(('', 8080), http.server.SimpleHTTPRequestHandler) as httpd:
    print('Веб-сервер запущен на http://localhost:8080')
    httpd.serve_forever()
"
```

### 5. Проверка работы

```bash
# Проверка процессов Python (боты)
ps aux | grep python

# Проверка портов
sudo netstat -tlnp | grep :8080

# Открытие веб-интерфейса
# Перейдите в браузере на: http://your-server-ip:8080
```

### 6. Управление сервисами

```bash
# Остановка всех Python процессов
pkill -f python3

# Перезапуск ботов
./deploy.sh

# Остановка Docker контейнеров (если используете)
docker compose -f docker-compose.optimized.yml down
```

## Решение частых проблем

### Docker не устанавливается
```bash
# Используйте способ 3 (без Docker)
# Или попробуйте snap:
sudo snap install docker
```

### Порт 8080 занят
```bash
# Найти процесс
sudo lsof -i :8080

# Остановить процесс
sudo kill -9 <PID>
```

### Боты не запускаются
```bash
# Проверьте .env файл
cat .env

# Проверьте логи
tail -f logs/*.log

# Переустановите зависимости
pip install --force-reinstall -r requirements.txt
```

### Нет доступа к веб-интерфейсу
```bash
# Проверьте firewall
sudo ufw allow 8080

# Или запустите на всех интерфейсах
python3 -c "
import http.server, socketserver, os
os.chdir('web')
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
with socketserver.TCPServer(('0.0.0.0', 8080), Handler) as httpd:
    print('Сервер доступен на http://0.0.0.0:8080')
    httpd.serve_forever()
"
```

## Автозапуск при загрузке системы

```bash
# Создание systemd сервиса для ботов
sudo tee /etc/systemd/system/telegram-bots.service > /dev/null <<EOF
[Unit]
Description=Telegram Bots
After=network.target

[Service]
Type=forking
User=$USER
WorkingDirectory=$HOME/"Рабочие боты"
ExecStart=$HOME/"Рабочие боты"/deploy.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Активация сервиса
sudo systemctl daemon-reload
sudo systemctl enable telegram-bots.service
sudo systemctl start telegram-bots.service
```

Теперь ваши боты и веб-интерфейс должны работать!