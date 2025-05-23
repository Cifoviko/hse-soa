## Сервис пользователей

### Зона ответственности:

* Регистрация новых пользователей
* Аутентификация (логин, хеширование паролей, выдача токенов)
* Управление ролями и правами доступа пользователей
* Обновление данных пользователя (email, имя и т.д.)

## Таблицы:

### User Table
---

Таблица со списком и информацией о всех пользователях

Primary key: **(id)**

Поля:
* **UUID** - **id**
* **string** - **login**
* **string** - **password_hash**
* **string** - **first_name**
* **string** - **second_name**
* **date** - **birth_date**
* **string** - **email**
* **string** - **phone_number**
* **datetime** - **created_at**
* **datetime** - **updated_at**

### User Role Table
---

Таблица связывающая пользователя и его роль

Primary key: **(user_id)**

Поля:
* **UUID** - **user_id**
* **UUID** - **role_id**
* **datetime** - **assigned_at**


### Role Table
---

Таблица со списком и информацией о всех ролях

Primary key: **(id)**

Поля:
* **UUID** - **id**
* **string** - **name**
* **string** - **description**
* **bool** - **can_read_everything**
* **bool** - **can_edit_everything**
