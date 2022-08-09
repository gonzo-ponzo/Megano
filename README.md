# Создать локальное окружение разработки
Основано на docker-compose
* первичный запуск проект
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
