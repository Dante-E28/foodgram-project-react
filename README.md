`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL` `Yandex Cloud`

# **_Foodgram_**
Добро пожаловать в проект "Фудграм" - ваш личный помощник в мире кулинарии! Этот проект представляет собой веб-приложение, где пользователи могут делиться своими рецептами, добавлять чужие рецепты в избранное, подписываться на других авторов, а также использовать удобный сервис "Список Покупок" для планирования покупок продуктов.

**_Ссылка на [проект](https://tabemono.zapto.org "Гиперссылка к проекту.")_**
Вход: admin@admin.com - tabemono1 (для ревьюера)

### _Развернуть проект на удаленном сервере:_

**_Клонировать репозиторий:_**
```
git@github.com:Dante-E28/foodgram-project-react.git
```
**_Установить на сервере Docker, Docker Compose:_**
```
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки
sh get-docker.sh                                        - запуск скрипта
sudo apt-get install docker-compose-plugin              - последняя версия docker compose
```
**_Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):_**
```
scp docker-compose.production.yml nginx.conf username@IP:/home/username/

# username - имя пользователя на сервере
# IP - публичный IP сервера
```

**_Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:_**
```
SECRET_KEY              - секретный ключ Django проекта
DOCKER_PASSWORD         - пароль от Docker Hub
DOCKER_USERNAME         - логин Docker Hub
HOST                    - публичный IP сервера
USER                    - имя пользователя на сервере
PASSPHRASE              - *если ssh-ключ защищен паролем
SSH_KEY                 - приватный ssh-ключ
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, посылающего сообщение

DB_ENGINE               - django.db.backends.postgresql
DB_NAME                 - postgres
POSTGRES_USER           - postgres
POSTGRES_PASSWORD       - postgres
DB_HOST                 - db
DB_PORT                 - 5432 (порт по умолчанию)
```

**_Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):**_
```
sudo docker compose -f docker-compose.production.yml up -d
```
**_Выполнить миграции:_**
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
**_Собрать статику:_**
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
```
**_Наполнить базу данных содержимым по-умолчанию**
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata dump.json
```
**_Создать суперпользователя:_**
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker compose down -v      - удаление контейнеров и volumes
sudo docker compose stop         - остановка
```
### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

### Локальный запуск проекта:

**_Создать и запустить контейнеры Docker, как указано выше._**

**_После запуска проект будут доступен по адресу: http://localhost/_**

**_Документация будет доступна по адресу: http://localhost/api/docs/_**


### Автор
Сазонов Егор