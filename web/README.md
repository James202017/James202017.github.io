# Веб-интерфейс для мониторинга Telegram ботов

Этот каталог содержит веб-интерфейс для мониторинга работы Telegram ботов недвижимости.

## 📁 Структура проекта

```
web/
├── Dockerfile                 # Docker образ для веб-сайта
├── docker-compose.web.yml    # Docker Compose для запуска веб-сайта
├── nginx-web.conf            # Конфигурация nginx
├── index.html                # Главная страница
├── assets/                   # Статические ресурсы
│   └── qr/                  # QR коды
└── README.md                # Эта документация
```

## 🚀 Быстрый запуск

### Вариант 1: Только веб-сайт

```bash
# Переходим в папку web
cd web

# Запускаем веб-сайт
docker-compose -f docker-compose.web.yml up -d

# Проверяем статус
docker-compose -f docker-compose.web.yml ps

# Открываем в браузере
# http://localhost:8080
```

### Вариант 2: Сборка и запуск вручную

```bash
# Переходим в папку web
cd web

# Собираем образ
docker build -t real-estate-web .

# Запускаем контейнер
docker run -d \
  --name real-estate-web \
  -p 8080:80 \
  --restart unless-stopped \
  real-estate-web

# Проверяем работу
curl http://localhost:8080/health
```

## 🔧 Конфигурация

### Порты
- **8080** - веб-интерфейс (HTTP)

### Ресурсы
- **RAM**: 32MB лимит, 16MB резерв
- **CPU**: 0.1 ядра
- **Диск**: ~50MB (образ + логи)

### Nginx настройки
- Сжатие gzip включено
- Кэширование статических файлов
- Безопасные заголовки
- Оптимизация производительности

## 📊 Мониторинг

### Проверка здоровья
```bash
# Проверка через Docker
docker exec real-estate-web wget -qO- http://localhost/health

# Проверка через curl
curl http://localhost:8080/health
```

### Логи
```bash
# Просмотр логов
docker-compose -f docker-compose.web.yml logs -f web

# Логи nginx
docker exec real-estate-web tail -f /var/log/nginx/access.log
docker exec real-estate-web tail -f /var/log/nginx/error.log
```

### Статистика ресурсов
```bash
# Использование ресурсов
docker stats real-estate-web

# Информация о контейнере
docker inspect real-estate-web
```

## 🛠 Разработка

### Локальная разработка
```bash
# Для разработки можно запустить простой HTTP сервер
python -m http.server 8080

# Или использовать nginx локально
nginx -c $(pwd)/nginx-web.conf -p $(pwd)
```

### Обновление контейнера
```bash
# Остановка
docker-compose -f docker-compose.web.yml down

# Пересборка и запуск
docker-compose -f docker-compose.web.yml up -d --build

# Или принудительная пересборка
docker-compose -f docker-compose.web.yml build --no-cache
docker-compose -f docker-compose.web.yml up -d
```

## 🔒 Безопасность

### Настройки безопасности
- Запуск от непривилегированного пользователя
- Отключение server tokens nginx
- Безопасные HTTP заголовки
- Ограничение доступа к служебным файлам

### Рекомендации для продакшена
```bash
# Использование HTTPS (требует SSL сертификаты)
# Настройка firewall
# Регулярные обновления образа
# Мониторинг безопасности
```

## 📈 Производительность

### Оптимизации
- Предварительное сжатие статических файлов
- Кэширование с правильными заголовками
- Оптимизированная конфигурация nginx
- Минимальный размер образа (Alpine Linux)

### Масштабирование
```bash
# Запуск нескольких экземпляров
docker-compose -f docker-compose.web.yml up -d --scale web=3

# Использование load balancer (например, traefik)
# Настройка CDN для статических файлов
```

## 🐛 Устранение неполадок

### Частые проблемы

1. **Порт 8080 занят**
   ```bash
   # Изменить порт в docker-compose.web.yml
   ports:
     - "8081:80"  # Вместо 8080
   ```

2. **Контейнер не запускается**
   ```bash
   # Проверить логи
   docker-compose -f docker-compose.web.yml logs web
   
   # Проверить конфигурацию nginx
   docker run --rm -v $(pwd)/nginx-web.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t
   ```

3. **Файлы не обновляются**
   ```bash
   # Пересобрать образ
   docker-compose -f docker-compose.web.yml build --no-cache
   ```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи контейнера
2. Убедитесь в корректности конфигурации
3. Проверьте доступность портов
4. Обратитесь к документации Docker и nginx