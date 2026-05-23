# Lelya Creator Studio — Backend

Production-ready backend for Telegram Mini App + Telegram Bot.
Built with FastAPI, aiogram 3.x, SQLAlchemy 2.0, and PostgreSQL.

## 🚀 Quick Start (Docker)

1. **Clone the repository**
2. **Copy `.env.example` to `.env`** and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
3. **Launch with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000` and the Bot will start automatically.

## 🛠 Tech Stack

- **FastAPI**: High-performance web framework for the API.
- **aiogram 3.x**: Modern asynchronous framework for the Telegram Bot.
- **SQLAlchemy 2.0 (Async)**: Advanced SQL toolkit and ORM.
- **PostgreSQL**: Robust relational database (compatible with Supabase).
- **Redis**: Caching, FSM storage, and Scheduler job store.
- **APScheduler**: Task scheduling for reminders and reports.
- **Alembic**: Database migrations management.
- **Pydantic v2**: Data validation and settings management.
- **JWT**: Secure authentication layer.

## 📁 Project Structure

```
backend/
├── alembic/          # Database migrations
├── app/
│   ├── api/          # FastAPI routes & dependencies
│   ├── bot/          # Telegram Bot handlers & keyboards
│   ├── core/         # Config, Security, Logging, Scheduler
│   ├── db/           # Session management
│   ├── models/       # SQLAlchemy models
│   ├── repositories/ # Database abstraction layer
│   ├── schemas/      # Pydantic schemas (DTo)
│   ├── services/     # Business logic & Integrations
│   └── main.py       # FastAPI Entry point
├── logs/             # Application logs
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## 🔐 Authentication

The Mini App uses **Telegram WebApp initData** for initial authentication.
1. Frontend sends `initData` to `POST /api/auth/telegram`.
2. Backend validates the signature and returns JWT (Access + Refresh).
3. Subsequent requests use `Authorization: Bearer <JWT>`.

## 🤖 Telegram Bot Features

- **Daily Goals**: Track video recording and publishing progress.
- **Smart Reminders**: Morning and evening notifications (APScheduler).
- **Studio Access**: Direct link to the Mini App.
- **Statistics**: Quick overview of social media performance.

## 📈 Social Media Integrations

Architecture is ready for:
- TikTok API
- YouTube Data API
- Instagram Graph API
- VK API

Refer to `app/services/social/` for implementation details.

## 🔄 Migrations

To create a new migration:
```bash
docker-compose exec backend-api alembic revision --autogenerate -message "Description"
```

To apply migrations:
```bash
docker-compose exec backend-api alembic upgrade head
```

## 📝 Logging

Structured logging is configured using `structlog`. Logs are output to the console and can be configured to rotate in the `logs/` directory.
