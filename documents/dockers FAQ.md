## Возможные проблемы и их решения в запуске контейнеров
### Ошибка при обращении к порту БД 5433
"Погасить" все контейнеры и убедиться, что всё выполнилось Ok
```bash
docker-compose down
```
Одна из ошибок м.б.:  
[+] Running 0/0
 - Network web_net  Error                                                                                                                                                          0.0s 
failed to remove network web_net: Error response from daemon: error while removing network: network web_net id af9b6d66f70751130608d5142da28a0297323139f83515d73c6766fa1b65a4e0 has active endpoints
  
В этом случае смотрим с какими сервисами связана "неудаляемая" сеть
```
docker network inspect af9b6d66f70751130608d5142da28a0297323139f83515d73c6766fa1b65a4e0
```
Ответ будет в виде json'а. И удаляем привязку сети к сервису (пример):
```
docker network disconnect -f af9b6d66f70751130608d5142da28a0297323139f83515d73c6766fa1b65a4e0 python_django_team14-postgres_db
```
После чего "гасим" все контейнеры повторно.

### ERROR: The Compose file './docker-compose.yml' is invalid because: services.web.depends_on contains an invalid type, it should be an array
Проблема в изменении формата данных в файле, который не понимает старый docker-compose. Вариант решения - если апгрейд для docker-compose сделать почему-то не получилось, то с последним docker'ом устанавливается свой compose-plugin, запускается почти так же.
```
$ docker-compose --version
docker-compose version 1.26.0, build d4451659

$ docker compose version
Docker Compose version v2.10.2

$ docker-compose up -d
ERROR: The Compose file './docker-compose.yml' is invalid because:
services.web.depends_on contains an invalid type, it should be an array

$ docker compose up -d
... всё поднимается и работает
```

