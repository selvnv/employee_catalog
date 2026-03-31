# Контекст задачи

Крупной компании-заказчику требуется разработать онлайн-каталог, обеспечивающий быстрый и удобный поиск информации о сотрудниках компании.
Штат компании насчитывает более 50 000 сотрудников

### Задача
- Создайте базу данных, в которой будут храниться данные о сотрудниках:
  - ФИО.
  - Должность.
  - Дата приема на работу.
  - Размер заработной платы.
- У каждого сотрудника есть 1 начальник.

- База данных должна содержать не менее 50 000 сотрудников и 5 уровней иерархий по должности (например, CEO → Manager → Team Lead → Senior Developer → Developer)

### Описание команд

| Команда CLI                                                                                                 | Назначение | Внутренняя реализация                                                                 |
|-------------------------------------------------------------------------------------------------------------|---|---------------------------------------------------------------------------------------|
| `edb gen -c 1000 -s 10000 100000 -h 2025-01-01 2026-01-01 ceo manager team_lead senior_developer developer` | Генерация и загрузка данных | Генерация наполнения каталога сотрудников (библиотека Mimesis) и вставка в PostgreSQL |
| `edb list -w id gt 1300 --limit 10 --order salary`                                                          | Табличный вывод | `SELECT` + `WHERE` (фильтры) + `ORDER BY` (whitelist) + `LIMIT`                       |
| `edb tree -t team_lead`                                                                                     | Древовидный вывод | Рекурсивный CTE + вывод с форматированием                                             |
| `edb add -l Testov -f Test -p developer -h 2026-01-05 -s 5000 -m 1000`                                                                                     | CRUD-операции | `INSERT` для одной записи                                                             |
| `edb update --salary 7000 1402`                                                                                     | CRUD-операции | `UPDATE` для одной записи                                                             |
| `edb delete 1402`                                                                                     | CRUD-операции | `DELETE` для нескольких записей                                                       |

### Чеклист
- [x] Создана база данных и таблица для хранения данных о сотрудниках (ФИО, должность, дата приема, зарплата).
- [x] Установлена иерархия: каждый сотрудник имеет одного начальника.
- [ ] Реализован интерфейс командной строки для взаимодействия с базой данных:
  - [x] Генерация данных сотрудников + Вставка в базу данных
  - [x] Выборка сотрудников из таблицы
  - [x] Фильтрация сотрудников при выборке из таблицы
  - [x] Вывод данных сотрудников в виде таблицы
  - [x] Вывод данных сотрудника в виде иерерхии (дерева)
    - [x] Для каждого сотрудника видна должность и ФИО
  - [x] Добавление нового сотрудника
  - [x] Обновление данных сотрудника
  - [x] Удаление сотрудника
- [ ] База содержит минимум 50 000 записей и 5 уровней иерархии (например, CEO → Manager → Team Lead → Senior Developer → Developer).

### Установка утилиты управления базой данных сотрудников

Утилита поставляется в виде дистрибутива - предварительно скомпилированного python-пакета `.whl`. Этот пакет находится в релизе репозитория, откуда его можно свободно скачать 

```bash
# Пример скачивания пакета из релиза по ссылке из консоли
curl -L -O https://github.com/selvnv/employee_catalog/releases/download/v0.1.0/edb_utility-0.1.0-py3-none-any.whl

# Установка скачанного пакета
pip install edb_utility-0.1.0-py3-none-any.whl

pip list | grep edb
edb-utility             0.1.0
```

После установки пакета, в командной строке будет доступна команда `edb`:
```bash
$ edb --help
Usage: edb [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add
  delete
  drop
  gen
  list
  tree
  update
```

Однако для ее использования необходимы данные для подключения к базе данных

Их утилита ищет в конфиг файле `./.env/connection.env`, либо из переменных окружения:
- PG_HOST
- PG_PORT
- PG_DB_NAME
- PG_USER
- PG_PASSWORD

```bash
# Для тестов переменные окружения можно установить для текущей сессии терминала
export PG_HOST=localhost PG_PORT=5435 PG_DB_NAME=employees PG_USER=catalog_app PG_PASSWORD=catalog_app

# Выполнение запроса
edb list -w last_name eq "Зуева"
[INFO] Reading postgres config file...
Path ./.env/connection.env does not exists
[INFO] Check database connection...
[WARN] Healthcheck failed connection to server at "localhost" (::1), port 5432 failed: fe_sendauth: no password supplied

[INFO] Reading environment variables...
╭──────┬─────────────┬──────────────┬───────────────┬────────────┬─────────────┬──────────┬──────────────╮
│   id │ last_name   │ first_name   │ middle_name   │ position   │ hire_date   │   salary │   manager_id │
├──────┼─────────────┼──────────────┼───────────────┼────────────┼─────────────┼──────────┼──────────────┤
│  303 │ Зуева       │ Мелания      │ Измаиловна    │ manager    │ 2024-05-17  │       69 │          302 │
╰──────┴─────────────┴──────────────┴───────────────┴────────────┴─────────────┴──────────┴──────────────╯

Page 1 of 1.Rows 1 of 1. 
Press enter to continue (q to skip\exit): 
```

### Запуск базы данных для тестирования

База данных и UI для удобного взаимодействия с ней поднимается в Docker

##### Запуск

Для запуска потребуется
1. Наличие файлов с переменными окружения, которые необходимы для корректной работы сервисов в контейнерах. Эти файлы должны находиться в директории `/.env/` в корне проекта
   2. `/.env/postgres.env` - содержит данные о суперпользователе, который создается при первом старте контейнера базы данных
   3. `/.env/pgadmin.env` - содержит данные пользователя для подключения к интерфейсу управления базой данных
2. Наличие файлов, инициализирующих базу данных. По сути - это набор запросов, создающих интеграционного пользователя, таблицу сотрудников и предоставляющих интеграционному пользователю необходимых прав. Эти скрипты должны располагаться в директории `/schema/` в корне проекта
   3. `/schema/01-initdb.sql` - создает базу данных и интеграционного пользователя для управления ею
   4. `/schema/02-create_schema.sql` - создает таблицу сотрудников `employees`, индексы и предоставляет интеграционному пользователю права на выполнение DML-запросов
3. Наличие инструкций для запуска группы контейнеров
   4. Файл `docker-compose.yml` - содержит инструкции по созданию группы контейнеров, включающей базу данных и сервис, предоставляющий графический интерфейс для управления ею

Когда файлы с переменными окружения подготовлены, для поднятия базы данных, достаточно выполнить
```bash
# Запуск контейнеров из образов
docker compose up -d
```


##### Описание файлов с переменными окружения
Переменные окружения, необходимые для запуска сервисов базы данных находятся в каталоге `/.env/`

`.env/pgadmin.env` - содержит переменные, необходимые для запуска сервиса pgAdmin

```
# Почта (логин) для авторизации в pgAdmin
PGADMIN_DEFAULT_EMAIL=some_valid_email
# Пароль для авторизации в pgAdmin
PGADMIN_DEFAULT_PASSWORD=some_pass
```

`.env/posgres.env` - содержит переменные, необходимые для запуска сервиса базы данных PostgreSQL

```
POSTGRES_USER=some_superuser_username
POSTGRES_PASSWORD=some_superuser_pass
```

##### Описаний файлов с запросами инициализации базы данных
При первом запуске контейнера базы данных выполняются запросы из директории `/schema/` (инициализация)

Ниже приведена структура скрипта, исполняемого первым (`/schema/01-initdb.sql`)
```sqlite-psql
-- Создание интеграционного пользователя для приложения
CREATE USER integration_user WITH PASSWORD 'some_pass';
-- Создание базы данных сотрудников
CREATE DATABASE employees OWNER integration_user;
-- Выдача прав интеграционному пользователю на управление базой данных
GRANT ALL PRIVILEGES ON DATABASE employees TO integration_user;
```

Также структура второго скрипта (`/schema/02-create_schema.sql`
```sqlite-psql
-- Подключение к созданной базе данных
\connect employees

-- Создание таблицы сотрудников
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    position TEXT NOT NULL,
    hire_date DATE NOT NULL,
    salary DOUBLE PRECISION NOT NULL CHECK (salary >= 0.0),
    manager_id BIGINT REFERENCES employees(id)
);

-- Предоставление прав интеграционному пользователю на действия с данными таблицы
GRANT SELECT, INSERT, UPDATE, DELETE ON employees TO integration_user;
GRANT USAGE, SELECT ON employees_id_seq TO integration_user;

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_employees_manager_id ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_employees_position ON employees(position);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON employees(hire_date);
CREATE INDEX IF NOT EXISTS idx_employees_salary ON employees(salary);
```

Для хранения иерархии «у каждого сотрудника есть 1 начальник» удобно использовать модель, где в таблице сотрудников есть поле `manager_id`, которое ссылается на `id` начальника (у самого верхнего уровня `manager_id` будет `NULL`)

##### Проверка


Для проверки настроек можно подключиться к контейнеру базы данных...
```bash
# Подключение к контейнеру базы данных
docker exec -it employee_catalog-db-1 sh
```

...и выполнить следующие команды
```bash
# Подключение к базе данных под суперпользователем (в моем случае это postgres)
psql -U postgres -d employees

# Если мы подключились к базе данных employees, то как минимум необходимая база данных была создана при инициализации
# Можно вывести более подробную информацию о базах данных в контейнере
# Здесь нас интересует база данных employees, и то, что ее владельцем является интеграционный пользователь (в моем случае это catalog_app)
\l
                  List of databases
   Name    |    Owner    | ... |      Access privileges
-----------+-------------+-----+-----------------------------------------
-----------+-------------+-----+-----------------------------------------
 employees | catalog_app | UTF8| =Tc/catalog_app            +
           |             |     | catalog_app=CTc/catalog_app
 postgres  | postgres    | UTF8|
```

### Настройка подключения к PostgreSQL из Python

Для подключения из Python нужны 5 параметров:
- host (обычно localhost)
- port (обычно 5432)
- dbname (например, employees)
- user (например, integration_user)
- password (например, integration_user)


### Справка

> DDL (Data Definition Language) — это набор команд SQL, отвечающих за определение, изменение и удаление объектов базы данных (таблиц, индексов, представлений, схем), по сути - управление структурой данных

Некоторые команды DDL:
- CREATE — создание новых объектов;
- ALTER — изменение существующих объектов (например, добавление столбцов, изменение типа данных, изменение ключей);
- DROP — удаление объектов из базы данных (например, таблицы или индекса);
- TRUNCATE — быстрое удаление всех данных из таблицы, при этом структура таблицы остаётся неизменной.

> DML (Data Manipulation Language) — это набор команд SQL, используемых для манипулирования данными в пределах схемы, созданной DDL. DML-операторы позволяют добавлять, изменять, удалять и получать данные из таблиц
- INSERT — добавление новых строк в таблицу;
- UPDATE — изменение существующих данных в таблице;
- DELETE — удаление строк из таблицы;
- SELECT — извлечение данных из базы данных.


> DCL (Data Control Language) — это набор команд SQL, используемых для управления доступом к объектам базы данных
- GRANT — выдача прав доступа
- REVOKE — снятие (отзыв) прав доступа

### Встреченные ошибки по ходу проекта

При подключении с хоста к адресу `localhost:5432`, по которому расположена база данных столкнулся с ошибкой

```bash
'utf-8' codec can't decode byte 0xc2 in position 61: invalid continuation byte
```

Как понятно из текста ошибки, `psycopg` ожидает данные (от клиента или сервера) в формате `UTF-8`, однако на вход получает данные в иной кодировке

Однако суть становится ясна только при более полном выводе ошибки (например, с помощью `__repr__`)

```bash
# UnicodeDecodeError(encoding, object, start, end, reason)
UnicodeDecodeError('utf-8', b'connection to server at "127.0.0.1", port 5432 failed: \xc2\xc0\xc6\xcd\xce:  \xef\xee\xeb\xfc\xe7\xee\xe2\xe0\xf2\xe5\xeb\xfc "catalog_app" \xed\xe5 \xef\xf0\xee\xf8\xb8\xeb \xef\xf0\xee\xe2\xe5\xf0\xea\xf3 \xef\xee\xe4\xeb\xe8\xed\xed\xee\xf1\xf2\xe8 (\xef\xee \xef\xe0\xf0\xee\xeb\xfe)\n', 55, 56, 'invalid continuation byte')
```

Здесь уже становится понятно, что запрос к СУБД проходит, и она даже отвечает. Вот только ответ предоставляет в кодировке `CP1251`

```python
b'\xc2\xc0\xc6\xcd\xce:  \xef\xee\xeb\xfc\xe7\xee\xe2\xe0\xf2\xe5\xeb\xfc "catalog_app" \xed\xe5 \xef\xf0\xee\xf8\xb8\xeb \xef\xf0\xee\xe2\xe5\xf0\xea\xf3 \xef\xee\xe4\xeb\xe8\xed\xed\xee\xf1\xf2\xe8 (\xef\xee \xef\xe0\xf0\xee\xeb\xfe)\n'.decode("cp1251")
# 'ВАЖНО:  пользователь "catalog_app" не прошёл проверку подлинности (по паролю)\n'
```

Как оказалось, на хосте установлен локально PostgreSQL, который, судя по всему, прослушивал подключения на `localhost:5432`. 
При этом Docker-контейнер с базой данных запускался с пробросом на тот же порт хоста `5432`

Проблему решил изменением в `docker-compose.yml` порта для доступа к базе данных с хоста: `5432` на `5435` (подойдет любой свободный порт)

### Часто используемые команды

```bash
# Сборка и запуск контейнеров из образов
docker compose up -d

# Удаление контейнеров
docker rm employee_catalog-dbui-1 employee_catalog-db-1

# Удаление именованных томов
docker volume rm employee_catalog_pgadmin employee_catalog_employeesdb

# Подключение к контейнеру базы данных
docker exec -it employee_catalog-db-1 sh

# Сборка пакета с помощью setuptools в редактируемом режиме
uv pip install -e .

# Использование cli пакета при разработке
# uv run edb <command_name>
uv run edb tree

# Вывод с ограничениями
uv run edb lst --where past_name eq Doe --where salary gt 10

# Генерация + вставка данных в базу данных
uv run edb gen --count 100 --salary 100000 500000 ceo manager team_lead senior_developer developer

# Удаление всех строк (сотрудников) из базы данных (с подтверждением)
uv run edb drop
```

### Ссылки
- [О библиотеке `tabulate`](https://pypi.org/project/tabulate/)
- [Также о `tabulate`, но на русском](https://pyneng.readthedocs.io/ru/latest/book/12_useful_modules/tabulate.html)
