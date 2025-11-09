# Настройка Ubuntu сервера для сайта тда.store

## Подготовка сервера (выполнить на сервере)

### 1. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установка Nginx
```bash
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 3. Установка Node.js (опционально, для будущих проектов)
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 4. Настройка файрвола
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## Настройка DNS (в панели reg.ru)

1. Войдите в панель управления reg.ru
2. Перейдите в управление доменом `тда.store`
3. Установите DNS-серверы:
   - ns1.hosting.reg.ru
   - ns2.hosting.reg.ru
4. Создайте A-записи:
   - `@` (корень домена) → IP_ВАШЕГО_СЕРВЕРА
   - `www` → IP_ВАШЕГО_СЕРВЕРА

## Деплой сайта

### 1. Локально отредактируйте файл `deploy.sh`:
- Замените `USER@YOUR_SERVER_IP` на ваши данные (например, `root@123.456.789.000`)
- Убедитесь, что у вас есть SSH-доступ к серверу

### 2. Сделайте скрипт исполняемым:
```bash
chmod +x deploy.sh
```

### 3. Запустите деплой:
```bash
./deploy.sh
```

## Проверка после деплоя

1. Проверьте сайт: https://тда.store
2. Убедитесь, что музыкальный визуализатор работает
3. Проверьте SSL-сертификат (должен быть зеленый замок в браузере)

## Дополнительные настройки

### Автоматическое обновление SSL
```bash
sudo crontab -e
# Добавьте строку:
0 2 * * * /usr/bin/certbot renew --quiet
```

### Мониторинг (опционально)
```bash
# Установка htop для мониторинга
sudo apt install htop

# Проверка логов Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Проблемы и решения

### Если сайт не открывается:
1. Проверьте DNS-записи: `dig тда.store`
2. Проверьте фаервол: `sudo ufw status`
3. Проверьте Nginx: `sudo systemctl status nginx`

### Если музыка не играет:
1. Проверьте путь к файлу в браузере
2. Убедитесь, что файл доступен по URL
3. Проверьте консоль браузера (F12 → Console)

## Контакт для помощи
Если возникнут проблемы, проверьте логи и свяжитесь с поддержкой хостинга.