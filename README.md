# Ветеринарная клиника

Пример проекта на FastAPI для курса по программированию на Django

## Команда разработки
- @VitDub - backend

# Переменные среды
Перед запуском необходимо указать переменные среды\
Шаблон файла переменных среды - ```.env.example```\
Переменные среды должны быть указаны в ```.env```

| Название | Описание | Тип | Значение по умолчанию |
| --- | --- | --- | --- |
| DB_SCHEMA | Протокол подключения к БД | Строка, драйвер | postgresql+asyncpg |
| DB_HOST | Хост БД | Строка | localhost |
| DB_PORT | Порт БД | Число | 5432 |
| DB_USER | Имя пользователя в БД | Строка | postgres |
| DB_PASSWORD | Пароль БД | Строка | pass |
| DB_NAME | Название БД | Строка | db |
| AUTH_SECRET | Секрет для создания JWT-токенов | Строка | secret |
| AUTH_ACCESS_TOKEN_LIFETIME_SECONDS | Время жизни access-токенов в секундах | Число | 300 |
| AUTH_REFRESH_TOKEN_LIFETIME_SECONDS | Время жизни refresh-токенов в секундах | Число | 600 |
| AUTH_TOKEN_ALGORITHM | Алгоритм шифрования JWT-токенов | Строка | HS256 |

Для генерации AUTH_SECRET можно использовать openssl
```bash
openssh rand -hex 32
```

# Инструкции по запуску
## Пререквизиты
- Установлен python
- Установлен uv

## Подготовка к запуску
### Установка зависимостей
```bash
uv sync
```

### Запуск миграций
```bash
uv run alembic upgrade head
```

## Запуск проекта
```bash
uv run fastapi dev
```

## Команды для разработки
### Генерация миграций
```bash
uv run alembic revision --autogenerate -m "<коментарий>"
```

### Установка pre-commit
```bash
uv run pre-commit install
```

```bash
gunicorn app.main:app -c gunicorn_config.py --reload
```

