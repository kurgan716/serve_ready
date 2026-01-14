Быстрый старт (разработка)
# 1. Клонирование репозитория
git clone https://github.com/kurgan716/serve_ready.git
cd serve_ready

# 2. Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Настройка базы данных
python manage.py migrate

# 5. Создание суперпользователя
python manage.py createsuperuser

# 6. Запуск сервера
python manage.py runserver
