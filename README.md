# Жидков Артем сергеевич (БПМИ226)
# Вариант 1 (Социальная сеть)

## Запуск

Для запуска всех сервисов надо поднять докер:

```
sudo docker compose build
sudo docker compose up
```

Для простоты можно просто запустить

```
sudo bash ./launch.sh
```

После запуска поднимется два микросервиса:

* service-users (по адресу http://127.0.0.1:8000/) - Реализует регистрацию и вход для пользователей

* service-api (по адресу http://127.0.0.1:8080/) - Сейчас просто прокси для передачи запросов в сервис пользователей

## Пользование

Дли использования тыкаемся в прокси. Примеры запросов:

### Регистрация:

```
curl -X POST "http://127.0.0.1:8080/register" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"password\": \"Password#1\", \"username\": \"username\"}"
```

```
Code: 201

Response body:
{
  "msg": "User registered successfully!"
}
```

### Логин:

```
curl -X POST "http://127.0.0.1:8080/login" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"password\": \"Password#1\", \"username\": \"username\"}"
```

```
Code: 200

Response body:
{
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MDgxOTk3OSwianRpIjoiMjhiMmU2MGMtYWUxZi00NDI2LWE4MGQtODUwMTViMGFiYzY1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXJuYW1lIiwibmJmIjoxNzQwODE5OTc5LCJjc3JmIjoiZDI3MzNkZGItNDFiNi00YTAyLTg3YTMtN2YwNDU2ZDkyNmJmIiwiZXhwIjoxNzQwODIwODc5fQ.rSj4oj5GzeJpcsuouu-gdBt3l0zIKlgyhabPtDG60R4"
}
```

### Обновление данных:

```
curl -X POST "http://127.0.0.1:8080/update_info" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"jwt_token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MDgxOTk3OSwianRpIjoiMjhiMmU2MGMtYWUxZi00NDI2LWE4MGQtODUwMTViMGFiYzY1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXJuYW1lIiwibmJmIjoxNzQwODE5OTc5LCJjc3JmIjoiZDI3MzNkZGItNDFiNi00YTAyLTg3YTMtN2YwNDU2ZDkyNmJmIiwiZXhwIjoxNzQwODIwODc5fQ.rSj4oj5GzeJpcsuouu-gdBt3l0zIKlgyhabPtDG60R4\", \"user_data\": { \"birth_date\": \"2025-03-01\", \"email\": \"test@test.com\", \"first_name\": \"Artem\", \"phone_number\": \"+88005553535\", \"second_name\": \"Zhidkov\" }}"
```

```
Code: 200

Response body:
{
  "birth_date": "2025-03-01",
  "created_at": "2025-03-01 09:04:57",
  "email": "test@test.com",
  "first_name": "Artem",
  "id": 1,
  "phone_number": "+88005553535",
  "second_name": "Zhidkov",
  "updated_at": "2025-03-01 09:09:09",
  "username": "username"
}
```

### Получение данных:

```
curl -X POST "http://127.0.0.1:8080/me" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"jwt_token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MDgxOTk3OSwianRpIjoiMjhiMmU2MGMtYWUxZi00NDI2LWE4MGQtODUwMTViMGFiYzY1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXJuYW1lIiwibmJmIjoxNzQwODE5OTc5LCJjc3JmIjoiZDI3MzNkZGItNDFiNi00YTAyLTg3YTMtN2YwNDU2ZDkyNmJmIiwiZXhwIjoxNzQwODIwODc5fQ.rSj4oj5GzeJpcsuouu-gdBt3l0zIKlgyhabPtDG60R4\"}"
```

```
Code: 201

Response body:
{
  "msg": "Successfuly updated user information"
}
```

## Тестирование

Для тестирования к сервису пользователей прикручен swagger (по адресу http://127.0.0.1:8000/apidocs). С помощью него можно удобнее посылать запросы для проверки

Также сервис пользователей полностью покрыт юнит тестами с использованием pytest (```service-users/test```). Для запуска тестов необходимо выполнить из папки ```service-users/```:

```
pytest test/
```

Тесты проверяю все возможные поведения:

* Отстутствие нужных для запроса данных

* Некоректные данные (Слишком длинные имена, слабый пароль, некоректный номер телефона, некоректный email, неправильный формат даты)

* Невалидный jwt токен

* Логин и регистрация для существующих\несуществующих пользователей

* Обновление и получение данных

## Open API спецификация

Сейчас спецификация лежит по пути ```service-users/api-spec.yaml```

Спецификация генерируется swagger по анотациям из кода. Для простоты обновления спецификации написан скрипт ```update-openapi.sh```
