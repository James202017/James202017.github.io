FROM python:3.11-alpine

# Устанавливаем зависимости для компиляции
RUN apk add --no-cache --virtual .build-deps gcc musl-dev

WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt ./

# Устанавливаем зависимости с оптимизацией памяти
RUN pip install --no-cache-dir --no-deps -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /root/.cache/pip/* && \
    mkdir logs

# Копируем код приложения
COPY bots/ ./bots/
COPY .env* ./

CMD ["python", "bots/BOT_P.py"]