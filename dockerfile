# Використовуємо базовий образ Python
FROM python:3.10

# Копіюємо файли вашого застосунку в контейнер
COPY main.py /app/main.py
COPY error.html /app/error.html
COPY index.html /app/index.html
COPY message.html /app/message.html
COPY style.css /app/style.css
COPY logo.png /app/logo.png
COPY storage/data.json /app/storage/data.json

# Встановлюємо робочий каталог
WORKDIR /app

# Налаштовуємо зберігання даних за допомогою механізму volumes
VOLUME /app/storage

# Вказуємо команду, яка буде виконуватись при запуску контейнера
CMD ["python", "main.py"]
