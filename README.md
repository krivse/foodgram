# Foodgram
### Описание
Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи публикуют свои рецепты, подписываются на публикации других пользователей, добавляют понравившиеся рецепты в список «Избранное», а перед походом в магазин могут скачать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии
Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Yandex Cloud, Continuous Integration, Continuous Deployment

### Запуск проекта в dev-режиме
Установите виртуальное окружение:
```
python -m venv venv
```
Активируйте виртуальное окружение:
```
windows: source venv/Scripts/activate

unix: source venv/bin/activate
```
Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
В папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```

### Автор
Иван Красников