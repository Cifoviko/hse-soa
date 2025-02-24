# Сервис API (gateway)

## Зона ответственности:

* Принимает все запросы от UI и перенаправляет их в соответствующие сервисы
* Логирует запросы
* Кеширует часто запрашиваемые данные для снижения нагрузки на микросервисы
* Управляет API-ключами для внутренних и внешних сервисов

## Таблицы:

### Logs Table
---

Таблица со всеми логами

Primary key: **(id, user_id)**

Поля:
* **UUID** - **id**
* **UUID** - **user_id**
* **enum** - **action_type**
* **json** - **data**
* **datetime** - **timestamp**

### Cache Table
---

Таблица с кешом запросов для ускорения ответа

Primary key: **(id)**

Поля:
* **UUID** - **id**
* **json** - **request**
* **json** - **responce**
* **datetime** - **created_at**
* **datetime** - **expires_at**

### API Table
---

Таблица со списком всех API ключей других сервисов

Primary key: **(service name, key_version)**

Поля:
* **string** - **service_name**
* **int** - **key_version**
* **string** - **key**
* **datetime** - **created_at**
* **datetime** - **expires_at**