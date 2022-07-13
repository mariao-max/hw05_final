## Проект hw05_final

Сервис Yatube. Реализованы функции регистрации, создания постов, добавления картинки в пост, комментариев.

### Стек:
Python 3, Django 2.2, pytest

### Запуск проекта в dev-режиме:
- Клонируйте репозиторий и перейдити в него в командной строке.

$ git clone https://github.com/mariao-max/hw05_final

$ cd hw05_final

- Установите и активируйте виртуальное окружение:

$ venv/Scripts/activate

- Установите все зависимости из файла requirements.txt

$ python -m pip install --upgrade pip

$ pip install -r requirements.txt

- Выполните миграции:

$ python manage.py migrate 

- Запустите проект:

$ python manage.py runserver

- Создать суперпользователя:

$ python3 manage.py createsuperuser

### Сервис доступен по адресу:

https://127.0.0.1:8000/

### Административная панель доступна по адресу

https://127.0.0.1:8000/admin/
