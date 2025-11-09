#!/bin/bash

# Скрипт деплоя сайта на Ubuntu сервер с Nginx
# Замените USER@YOUR_SERVER_IP на ваши данные

SERVER="USER@YOUR_SERVER_IP"  # Измените на ваш user@server_ip
DOMAIN="тда.store"  # Ваш домен
LOCAL_DIR="."  # Локальная директория
REMOTE_DIR="/var/www/тда.store"  # Удаленная директория

echo "🚀 Начинаем деплой сайта..."

# 1. Создаем директорию на сервере
echo "📁 Создаем директорию на сервере..."
ssh $SERVER "sudo mkdir -p $REMOTE_DIR && sudo chown -R \$USER:\$USER $REMOTE_DIR"

# 2. Копируем файлы на сервер
echo "📤 Копируем файлы на сервер..."
rsync -avz --exclude='.git' --exclude='deploy.sh' --exclude='README.txt' $LOCAL_DIR/ $SERVER:$REMOTE_DIR/

# 3. Устанавливаем права
echo "🔒 Устанавливаем права доступа..."
ssh $SERVER "sudo chown -R www-data:www-data $REMOTE_DIR && sudo chmod -R 755 $REMOTE_DIR"

# 4. Проверяем/создаем конфиг Nginx
echo "⚙️ Настраиваем Nginx..."
ssh $SERVER "
cat > /tmp/nginx-config << 'EOF'
server {
    listen 80;
    server_name тда.store www.тда.store;
    root /var/www/тда.store;
    index index.html;

    # Включаем сжатие
    gzip on;
    gzip_types text/css application/javascript image/svg+xml;

    # Кэширование статических файлов
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|mp3|wav)$ {
        expires 1M;
        add_header Cache-Control \"public, immutable\";
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Безопасность
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
}
EOF

sudo mv /tmp/nginx-config /etc/nginx/sites-available/тда.store

# Удаляем старый конфиг если есть
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/sites-enabled/тда.store

# Создаем симлинк
sudo ln -s /etc/nginx/sites-available/тда.store /etc/nginx/sites-enabled/

# Проверяем конфиг
sudo nginx -t
"

# 5. Перезапускаем Nginx
echo "🔄 Перезапускаем Nginx..."
ssh $SERVER "sudo systemctl restart nginx"

# 6. Устанавливаем SSL сертификат через Certbot
echo "🔒 Устанавливаем SSL сертификат..."
ssh $SERVER "sudo apt update && sudo apt install -y certbot python3-certbot-nginx"
ssh $SERVER "sudo certbot --nginx -d тда.store -d www.тда.store --non-interactive --agree-tos -m admin@тда.store || echo 'SSL может потребовать ручной настройки'"

echo "✅ Деплой завершен!"
echo "🌐 Проверьте сайт: https://тда.store"
echo "🎵 Не забудьте включить музыку для визуализатора!"