# ЮАнна - студия массажа

Сайт для студии массажа и коррекции фигуры "ЮАнна", разработанный на Python, Django и Poetry.

## Функциональность сайта

- Просмотр услуг студии массажа по категориям
- Информация о трёх филиалах в г. Пенза с интерактивными картами
- Система онлайн-записи на процедуры
- Личный кабинет пользователя
- Просмотр и управление записями

## Технологии

- Python 3.9+
- django==5.2.4
- django-environ==0.11.2
- django-crispy-forms==2.1
- crispy-bootstrap5==2023.10
- django-allauth==0.61.1
- Pillow==10.2.0
- Poetry для управления зависимостями
- Bootstrap 5 для frontend
- Leaflet.js для отображения карт
- django-allauth для аутентификации
- django-crispy-forms для стилизации форм

## Установка и запуск

### Предварительные требования

- Python 3.9 или выше
- Poetry

### Шаги по установке

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd lpg_massage_salon
Установить зависимости с помощью Poetry:
bash
Copy code
poetry install
Создать и применить миграции:
bash
Copy code
poetry run python manage.py makemigrations
poetry run python manage.py migrate
Загрузить демо-данные:
bash
Copy code
poetry run python manage.py loaddata updated_services_data.json
poetry run python manage.py loaddata updated_services.json
poetry run python manage.py loaddata updated_locations.json
Создать суперпользователя:
bash
Copy code
poetry run python manage.py createsuperuser
Запустить сервер разработки:
bash
Copy code
poetry run python manage.py runserver

Структура проекта
- lpg_salon/ - основной пакет проекта Django
- core/ - базовый функционал (модели, общие представления)
- services/ - управление услугами и категориями
- locations/ - управление филиалами
- appointments/ - система записи на процедуры и отзывы