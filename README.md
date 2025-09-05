
# СhatSpace — чат на FastAPI + WebSockets

Проєкт: легка альтернатива Discord — веб-чат із серверами (гільдіями), каналами та особистими повідомленнями. Реалізовано на **FastAPI** з **WebSocket**, збереження у **SQLite** через `aiosqlite`. Автентифікація — JWT, сесії — `fastapi-sessions`.


---

## Можливості
- Створення/вступ до **серверів** (guilds), базові ролі власника/учасника.
- Текстові **канали** всередині сервера.
- **Чат у реальному часі** через WebSocket: надсилання, редагування й видалення повідомлень.
- **Особисті повідомлення** (DM) по WebSocket.
- **Онлайн-статуси**, індикатори набору тексту, список учасників.
- **Автентифікація** за email/паролем → JWT; refresh/rotate (за потреби). Сесії для веб-клієнта.
- **Валідація** email (`email_validator`), хешування паролів (`bcrypt`/`passlib`).
- **Завантаження аватарів** (опційно, `pillow`).
- **Тести** на `pytest`.

---

## Технічний стек
- **FastAPI** `0.116.1`, **Starlette** `0.47.2`
- **WebSocket**: `websockets==15.0.1` (сервер під управлінням Uvicorn)
- **Бекенд**: Python 3.11+ (рекомендовано 3.12)
- **Сховище**: `aiosqlite==0.21.0` (SQLite)
- **Автентифікація**: `python-jose`, `passlib`, `bcrypt`, `fastapi-sessions`
- **HTTP**: `httpx` для інтеграційних викликів/тестів
- **Сервер**: `uvicorn==0.35.0` (dev), `gevent`/`greenlet` опційно для прод

Повний список залежностей див. у `requirements.txt`.

---

## Швидкий старт

### 1) Підготовка оточення
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
````

### 2) Змінні оточення (.env)

Створіть файл `.env` у корені:

```env
# Безпека
    APP_NAME: str = "name"
    DEBUG: bool = True

    DB_NAME: str = "data.db"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data.db'}"

    SECRET_KEY: str = "your_secret_key"
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = number

```

### 3) Ініціалізація БД

```bash
python scripts/init_db.py  # створить таблиці (прикладовий скрипт)
```

### 4) Запуск dev-сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Відкрийте `http://localhost:8000/docs` для Swagger UI.

---

## Структура проєкту (рекомендація)

```
app/
  core/
    config.py            # конфиг
main.py              # створення FastAPIу корені проекту
```
