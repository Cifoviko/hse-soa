## Сервис статистики

### Зона ответственности:

* Подсчет количества просмотров постов
* Управление лайками постов и комментариев
* Хранение и анализ статистики пользовательской активности
* Генерация отчетов о статистике по пользователю

## Таблицы:

### Like Info Table
---

Таблица со списком и информацией о всех лайках

Primary key: **(user_id, content_id)**

Поля:
* **UUID** - **user_id**
* **enum** - **content_type**
* **UUID** - **content_id**
* **bool** - **is_liked**
* **datetime** - **timestamp**

### User Liked Table
---

Таблица со списком и информацией о всех постах и лайках которые пользователь лайкал

Primary key: **(user_id)**

Поля:
* **UUID** - **user_id**
* **list\<UUID\>** - **content_ids**


### Content Read Table
---

Таблица со списком и информацией о всех прочтениях постов и комментариев

Primary key: **(user_id, content_id)**

Поля:
* **UUID** - **user_id**
* **enum** - **content_type**
* **UUID** - **content_id**
* **datetime** - **timestamp**
* **enum** - **device_type**
