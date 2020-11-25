# test_assignment

Тестовое задание: реализация CRUD для юзеров с токен аутентификацией.

**Permissions**

| Action            | Permission          |
|-------------------|:-------------------:|
|List, Retrieve     |AllowAny             |
|Post               |Admin                |
|Put, Patch, Delete |Own account or Admin |

**Technologies**

Обеспечение различных наборов полей сериализатора для запросов (request) 
и ответов (response) осуществляется пакетом 'drf-rw-serializers'
Ссылка на пакет: (https://github.com/vintasoftware/drf-rw-serializers)

**Requirements**

Необходимые для работы приложения пакеты перечислены в 'requirements.txt'
