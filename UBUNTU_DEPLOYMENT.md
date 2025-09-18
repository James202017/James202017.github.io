# Развертывание на Ubuntu 24.04 LTS

## Системные требования

- Ubuntu 24.04 LTS
- Python 3.11+
- Git
- Минимум 1GB RAM
- 2GB свободного места на диске

## Быстрая установка

### 1. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установка зависимостей
```bash
# Python и pip
sudo apt install python3 python3-pip python3-venv git -y

# Дополнительные пакеты
sudo apt install curl wget htop nano ca-certificates gnupg lsb-release -y
```

### 3. Установка Docker (для Ubuntu 24.04)
```bash
# Удаление старых версий Docker (если есть)
sudo apt remove docker docker-engine docker.io containerd runc

# Добавление официального GPG ключа Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Добавление репозитория Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Обновление индекса пакетов
sudo apt update

# Установка Docker Engine
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагрузка для применения изменений группы
echo "Необходимо перезайти в систему или выполнить: newgrp docker"

# Проверка установки
sudo docker run hello-world
```

### 4. Установка Docker Compose (standalone)
```bash
# Загрузка последней версии Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Установка прав на выполнение
sudo chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker-compose --version
```

### 5. Клонирование проекта
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd "Рабочие боты"
```

### 6. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
```

### 7. Установка Python зависимостей
```bash
pip install -r requirements.txt
```

### 8. Настройка переменных окружения
```bash
cp .env.example .env
nano .env
```

Добавьте ваши токены ботов:
```env
BOT_P_TOKEN=your_bot_token_here
BOT_PR_TOKEN=your_bot_token_here
BOT_INV_TOKEN=your_bot_token_here
BOT_STR_TOKEN=your_bot_token_here
BOT_OCENKA_TOKEN=your_bot_token_here
```

## Запуск

### Ручной запуск (рекомендуется для тестирования)
```bash
# Активация виртуального окружения
source venv/bin/activate

# Запуск всех ботов
chmod +x deploy.sh
./deploy.sh

# Или запуск с веб-интерфейсом
./deploy.sh --web-server
```

### Запуск веб-сайта отдельно
```bash
# В отдельном терминале
cd web
python3 -m http.server 8080

# Или с помощью Python скрипта (если есть)
python3 -c "import http.server, socketserver; httpd = socketserver.TCPServer(('', 8080), http.server.SimpleHTTPRequestHandler); print('Сервер запущен на http://localhost:8080'); httpd.serve_forever()"
```

### Запуск через Docker
```bash
# Убедитесь что Docker запущен
sudo systemctl start docker
sudo systemctl enable docker

# БЫСТРЫЙ запуск (рекомендуется при медленной сборке или ошибках apt)
docker compose -f docker-compose.fast.yml up -d

# Или стандартный запуск
docker compose -f docker-compose.optimized.yml up -d

# Просмотр логов
docker compose -f docker-compose.fast.yml logs -f

# Остановка
docker compose -f docker-compose.fast.yml down
```

**Решение проблем сборки:**
- **Ошибка "ERROR [bot_p 2/7] RUN apt-get update"** - используйте `docker-compose.fast.yml`
- **Долгая сборка (>5 минут)** - используйте `docker-compose.fast.yml` (Alpine Linux)
- **Таймауты сети** - попробуйте несколько раз или используйте быструю версию

**Важно:** При запуске Docker контейнеров команды `apt update` и `apt upgrade` **НЕ НУЖНЫ**! Все зависимости уже установлены в Docker образе. Если система просит выполнить эти команды, просто проигнорируйте или нажмите Ctrl+C.

### Запуск с веб-интерфейсом на порту 8080
```bash
# Создание простого веб-сервера для мониторинга
cat > web_server.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8080
WEB_DIR = "web"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Веб-сервер запущен на http://localhost:{PORT}")
        print(f"Обслуживает файлы из папки: {WEB_DIR}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")
EOF

# Запуск веб-сервера
python3 web_server.py
```

## Автозапуск (systemd)

### 1. Создание сервиса
```bash
sudo nano /etc/systemd/system/telegram-bots.service
```

### 2. Содержимое сервиса
```ini
[Unit]
Description=Telegram Bots Service
After=network.target

[Service]
Type=forking
User=ubuntu
WorkingDirectory=/home/ubuntu/Рабочие боты
ExecStart=/home/ubuntu/Рабочие боты/deploy.sh
ExecStop=/usr/bin/pkill -f "python.*BOT_"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Активация сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bots.service
sudo systemctl start telegram-bots.service
```

### 4. Управление сервисом
```bash
# Статус
sudo systemctl status telegram-bots.service

# Перезапуск
sudo systemctl restart telegram-bots.service

# Остановка
sudo systemctl stop telegram-bots.service

# Логи
journalctl -u telegram-bots.service -f
```

## Мониторинг

### Веб-интерфейс
- URL: `http://your-server-ip:8080`
- Показывает статус всех ботов в реальном времени

### Командная строка
```bash
# Проверка процессов
ps aux | grep python

# Проверка портов
ss -tulpn | grep :8080

# Просмотр логов
tail -f logs/*.log
```

## Безопасность

### 1. Настройка файрвола
```bash
# Включение UFW
sudo ufw enable

# Разрешение SSH
sudo ufw allow ssh

# Разрешение веб-интерфейса (опционально)
sudo ufw allow 8080

# Проверка статуса
sudo ufw status
```

### 2. Обновления
```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Резервное копирование

### Создание бэкапа
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/bots_backup_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='temp' \
    --exclude='data' \
    /home/ubuntu/Рабочие\ боты

echo "Backup created: $BACKUP_DIR/bots_backup_$DATE.tar.gz"
```

### Восстановление
```bash
tar -xzf /home/ubuntu/backups/bots_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

## Устранение неполадок

### Проблемы с Docker в Ubuntu 24.04

#### Если Docker не устанавливается из стандартных репозиториев:
```bash
# Альтернативный способ 1: Установка через snap
sudo snap install docker

# Альтернативный способ 2: Установка из .deb пакета
wget https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/docker-ce_24.0.7-1~ubuntu.22.04~jammy_amd64.deb
wget https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/docker-ce-cli_24.0.7-1~ubuntu.22.04~jammy_amd64.deb
wget https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/containerd.io_1.6.24-1_amd64.deb

sudo dpkg -i containerd.io_1.6.24-1_amd64.deb
sudo dpkg -i docker-ce-cli_24.0.7-1~ubuntu.22.04~jammy_amd64.deb
sudo dpkg -i docker-ce_24.0.7-1~ubuntu.22.04~jammy_amd64.deb

# Исправление зависимостей если нужно
sudo apt --fix-broken install
```

#### Проверка статуса Docker:
```bash
# Проверка статуса службы
sudo systemctl status docker

# Запуск Docker если не запущен
sudo systemctl start docker
sudo systemctl enable docker

# Проверка версии
docker --version
docker compose version
```

#### Если проблемы с правами Docker:
```bash
# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Применение изменений без перезагрузки
newgrp docker

# Или перезайти в систему
```

### Запуск без Docker (только Python)

Если Docker не устанавливается, можно запустить проект только на Python:

```bash
# Установка системных зависимостей
sudo apt update
sudo apt install python3 python3-pip python3-venv git nginx -y

# Клонирование и настройка проекта
git clone <YOUR_GITHUB_REPO_URL>
cd "Рабочие боты"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
nano .env

# Запуск ботов
chmod +x deploy.sh
./deploy.sh

# В отдельном терминале - запуск веб-сервера
python3 web_server.py
```

### Проблемы с правами доступа
```bash
# Если боты не могут создавать файлы
sudo chown -R $USER:$USER ~/"Рабочие боты"/
chmod -R 755 ~/"Рабочие боты"/
```

### Проблемы с портами
```bash
# Проверка занятых портов
sudo netstat -tlnp | grep :8080

# Остановка процесса на порту
sudo kill -9 $(sudo lsof -t -i:8080)
```

### Проблемы с зависимостями
```bash
# Переустановка зависимостей
pip install --force-reinstall -r requirements.txt

# Обновление pip
pip install --upgrade pip
```

### Проблемы с запуском
1. Проверьте токены в `.env`
2. Убедитесь что виртуальное окружение активно
3. Проверьте логи: `tail -f logs/*.log`

### Проблемы с производительностью
1. Мониторинг ресурсов: `htop`
2. Проверка места на диске: `df -h`
3. Очистка логов: `find logs/ -name "*.log" -mtime +7 -delete`

### Проблемы с сетью
1. Проверка подключения: `curl -I https://api.telegram.org`
2. Проверка портов: `ss -tulpn`
3. Проверка DNS: `nslookup api.telegram.org`

## Полезные команды

```bash
# Просмотр всех процессов ботов
ps aux | grep "BOT_"

# Остановка всех ботов
pkill -f "python.*BOT_"

# Проверка использования памяти
free -h

# Проверка загрузки CPU
top -p $(pgrep -d',' python)

# Очистка временных файлов
find temp/ -type f -mtime +1 -delete
```

## Контакты и поддержка

Для получения помощи:
1. Проверьте логи в папке `logs/`
2. Убедитесь что все зависимости установлены
3. Проверьте статус сервисов: `systemctl status telegram-bots.service`

---

**Примечание**: Замените `<YOUR_GITHUB_REPO_URL>` на актуальный URL вашего репозитория на GitHub.