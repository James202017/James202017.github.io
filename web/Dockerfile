# Dockerfile для веб-сайта
# Используем официальный образ nginx с Alpine Linux для минимального размера
FROM nginx:alpine

# Устанавливаем метаданные
LABEL maintainer="Real Estate Bots Team"
LABEL description="Web interface for Real Estate Telegram Bots monitoring"
LABEL version="1.0"

# Создаем пользователя для безопасности
RUN addgroup -g 1001 -S webuser && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G webuser -g webuser webuser

# Копируем веб-файлы в контейнер (исключая текущую папку web/)
COPY index.html /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/

# Копируем специализированную конфигурацию nginx для веб-сайта
COPY nginx-web.conf /etc/nginx/nginx.conf

# Создаем необходимые директории и устанавливаем права
RUN mkdir -p /var/cache/nginx/client_temp && \
    mkdir -p /var/cache/nginx/proxy_temp && \
    mkdir -p /var/cache/nginx/fastcgi_temp && \
    mkdir -p /var/cache/nginx/uwsgi_temp && \
    mkdir -p /var/cache/nginx/scgi_temp && \
    chown -R webuser:webuser /var/cache/nginx && \
    chown -R webuser:webuser /usr/share/nginx/html && \
    chown -R webuser:webuser /var/log/nginx && \
    chmod -R 755 /usr/share/nginx/html

# Оптимизация для статических файлов
RUN find /usr/share/nginx/html -type f -name "*.html" -exec gzip -k {} \; && \
    find /usr/share/nginx/html -type f -name "*.css" -exec gzip -k {} \; && \
    find /usr/share/nginx/html -type f -name "*.js" -exec gzip -k {} \;

# Переключаемся на непривилегированного пользователя
USER webuser

# Открываем порт 80
EXPOSE 80

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Запускаем nginx в foreground режиме
CMD ["nginx", "-g", "daemon off;"]