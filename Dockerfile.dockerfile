FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 django \
    && chown -R django:django /app

USER django

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]