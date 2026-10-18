# 💕 Dating API — Django REST Framework

API для платформы знакомств с возможностью поиска партнёров, лайков, дизлайков и приглашений на свидание.

## 📋 Требования

- **Docker Desktop** (с WSL 2)
- **Git**
- **PowerShell** или терминал

## 🚀 Запуск через Docker (рекомендуется)

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Anton180391/dating_api.git
cd dating_api
```

### 2. Запустить контейнеры

```bash
docker-compose up --build
```

⏱ **Первый запуск:** 3–7 минут (скачивание образов + сборка).

### 3. Создать суперпользователя

**В новом терминале:**

```bash
docker-compose exec web python manage.py createsuperuser
```

Введи:
- Email: `admin@example.com`
- Username: `admin`
- Password: `test12345`

### 4. Открыть в браузере

| Ссылка | Описание |
|--------|----------|
| http://127.0.0.1:8000/api/docs/ | **Swagger** (документация API) |
| http://127.0.0.1:8000/api/redoc/ | **ReDoc** |
| http://127.0.0.1:8000/admin/ | **Админка Django** |
| http://127.0.0.1:8000/api/ | **API** |

### 5. Остановить

```bash
docker-compose down
```

**С удалением БД:**

```bash
docker-compose down -v
```

---

## 🛠️ Локальный запуск (без Docker)

### 1. Виртуальное окружение

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Миграции

```bash
python manage.py migrate
```

### 4. Суперпользователь

```bash
python manage.py createsuperuser
```

### 5. Запуск

```bash
python manage.py runserver
```

---

## 📚 API Эндпоинты

### Пользователи

| Метод | URL | Описание | Права |
|-------|-----|----------|-------|
| **POST** | `/api/users/` | Регистрация (по email) | Все |
| **GET** | `/api/users/` | Список пользователей | Все |
| **GET** | `/api/users/{id}/` | Профиль пользователя | Все |
| **PATCH** | `/api/users/{id}/` | Обновить профиль | Только свой |
| **DELETE** | `/api/users/{id}/` | Удалить | Только свой |
| **GET** | `/api/users/me/` | Текущий пользователь | Авторизованные |
| **GET** | `/api/users/random/` | Случайный профиль с фильтром | Авторизованные |

### Лайки/Дизлайки

| Метод | URL | Описание |
|-------|-----|----------|
| **POST** | `/api/interactions/` | Лайк/дизлайк |
| **GET** | `/api/interactions/my-likes/` | Кого я лайкнул |
| **GET** | `/api/interactions/my-dislikes/` | Кого я дизлайкнул |
| **GET** | `/api/interactions/liked-me/` | Кто лайкнул меня |
| **GET** | `/api/interactions/mutual/` | Взаимные лайки |

### Приглашения

| Метод | URL | Описание |
|-------|-----|----------|
| **POST** | `/api/invitations/` | Создать приглашение |
| **POST** | `/api/invitations/{id}/accept/` | Принять |
| **POST** | `/api/invitations/{id}/reject/` | Отклонить |

### Просмотры

| Метод | URL | Описание |
|-------|-----|----------|
| **POST** | `/api/views/` | Записать просмотр |
| **GET** | `/api/views/who-viewed-me/` | Кто смотрел меня |

### JWT

| Метод | URL | Описание |
|-------|-----|----------|
| **POST** | `/api/token/` | Получить access + refresh (по email) |
| **POST** | `/api/token/refresh/` | Обновить access |

### Фильтрация

```
/api/users/?gender=M&min_age=20&max_age=30&city=Москва&status=searching
/api/users/?search=Антон
/api/users/?ordering=-age
```

---

## 🔐 Авторизация

**Через email + JWT:**

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "test12345"}'
```

**Ответ:**

```json
{
    "refresh": "eyJhbGciOi...",
    "access": "eyJhbGciOi..."
}
```

**Использование:**

```bash
curl http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

---

## 🔧 Технологии

- **Python 3.13**
- **Django 6.1**
- **Django REST Framework**
- **Simple JWT** — авторизация через email
- **PostgreSQL 16** — БД
- **Docker + Docker Compose**
- **Gunicorn** — production-сервер
- **drf-spectacular** — Swagger
- **django-cors-headers** — CORS
- **Pillow** — изображения

---

## 📁 Структура проекта

```
dating_api/
├── config/               # настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                # приложение пользователей
│   ├── models.py         # User, Hobby, UserPhoto
│   ├── serializers.py
│   ├── views.py
│   ├── tokens.py         # JWT через email
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── interactions/         # приложение взаимодействий
│   ├── models.py         # Interaction, ProfileView, DateInvitation
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── manage.py
```

---

## 🐳 Полезные Docker-команды

```bash
docker-compose up -d            # Запустить в фоне
docker-compose logs -f web      # Логи
docker-compose exec web bash    # Войти в контейнер
docker-compose restart web      # Перезапустить
docker-compose down -v          # Удалить всё (включая БД)
```

---

## 👤 Автор

**Anton180391** — [GitHub](https://github.com/Anton180391)
---
**Проект завершен и направлен на проверку 18.10.2026**