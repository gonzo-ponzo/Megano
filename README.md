## Локальное окружение разработки
В качестве интерпертатора IDE используется docker-compose:
* сервис - web
* интерпретатор - python
### Консольные команды для управления разработкой
* первичный запуск проекта
```commandline
docker-compose up -d --build
```
* каждый последующий запуск проекта
```commandline
docker-compose up -d
```
* пересобрать, например для установки новой библиотеки, указанной в requirements.txt
```commandline
docker-compose up -d --no-deps --build web
```
* Посмотреть запущенные контейнеры
```commandline
docker ps
```
* Войти внутрь контейнера, например в консоль сервиса web (где код)
```commandline
docker exec -it <имя контейнера, см.предыдущую команду> bash
```
* Посмотреть логи процесса внутри контейнера, например для контейнеров celery
```commandline
docker container logs --follow <имя контейнера, см. команду выше>
```

