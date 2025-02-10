## Сервис постов и комментариев

### Зона ответственности:

* Создание, редактирование и удаление постов
* Создание, редактирование и удаление комментариев

## Таблицы:

### Posts Table
---

Таблица со списком и информацией о всех постах

Primary key: **(id)**

Поля:
* **UUID** - **id**
* **UUID** - **user_id**
* **string** - **title**
* **string** - **text**
* **datetime** - **created_at**

### Comment Table
---

Таблица со списком и информацией о всех комментариях

Primary key: **(id)**

Поля:
* **UUID** - **id**
* **UUID** - **user_id**
* **UUID** - **parent_id**
* **string** - **text**
* **datetime** - **created_at**

### User Content Table
---

Таблица со списком id постов и комментариев созданных пользователем

Primary key: **(user_id)**

Поля:
* **UUID** - **user_id**
* **list\<UUID\>** - **content_ids**
