# Lelya Creator Studio — FastAPI contract

Mini app общается с FastAPI напрямую. Все запросы идут на `${VITE_API_BASE_URL}`
(переменная окружения mini app, задаётся в Vercel → Project → Settings → Environment Variables).

## 1. Авторизация

Каждый запрос содержит заголовок:

```
Authorization: tma <window.Telegram.WebApp.initData>
```

На стороне FastAPI:

1. Распарсить query-string из initData.
2. Извлечь `hash`, отсортировать остальные поля, собрать `data_check_string`.
3. `secret_key = HMAC_SHA256(key="WebAppData", msg=BOT_TOKEN)`.
4. `calc = HMAC_SHA256(key=secret_key, msg=data_check_string).hexdigest()`.
5. Если `calc != hash` → `401`.
6. Проверить `auth_date` (не старше, скажем, 24ч).
7. Из поля `user` (JSON) достать `id` — это `telegram_id`.

Пример зависимости (FastAPI):

```python
from fastapi import Header, HTTPException, Depends
import hmac, hashlib, json, time
from urllib.parse import parse_qsl

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

def verify_init_data(init_data: str) -> dict:
    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(401, "no hash")
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received_hash):
        raise HTTPException(401, "bad hash")
    if time.time() - int(parsed["auth_date"]) > 86400:
        raise HTTPException(401, "expired")
    return json.loads(parsed["user"])

async def current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("tma "):
        raise HTTPException(401, "bad scheme")
    return verify_init_data(authorization[4:])
```

## 2. CORS

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://<your-app>.vercel.app",
        "https://web.telegram.org",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Debug-User"],
)
```

## 3. Эндпоинты

### `GET /api/me`
Создаёт юзера, если не существует (первый вход = регистрация).
`is_new=true` для свежесозданного — фронт показывает onboarding-экран.

```json
{
  "telegram_id": 12345,
  "first_name": "Алекс",
  "username": "creator_alex",
  "photo_url": "https://...",
  "is_new": true,
  "streak_days": 0,
  "total_reels": 0,
  "timezone": "UTC",
  "manager_username": null,
  "notifications_enabled": true
}
```

### `POST /api/me/onboarding`
Завершает регистрацию. Body:
```json
{ "first_name": "Алекс", "timezone": "Europe/Moscow" }
```
Ответ — тот же `Me`, но `is_new=false`.

### `GET /api/studio`
```json
{
  "goals": [
    { "key": "shoot",   "label": "Съемка",     "value": 3, "total": 3 },
    { "key": "publish", "label": "Публикация", "value": 1, "total": 3 }
  ],
  "activity": [0,1,2,3, ...],  // ровно 30 значений (0..3), последний = сегодня
  "ideas": [
    { "id":"abc","title":"Сценарий для Reels","platform":"Reels","status":"planned","created_at":"2025-05-20T10:00:00Z" }
  ]
}
```
`platform`: `"Reels" | "YT" | "TikTok" | "VK"`. `status`: `"draft" | "planned" | "published"`.

### `POST /api/ideas`
Body: `{ "title": "...", "platform": "Reels" }`. Ответ — созданная `Idea`.

### `GET /api/stats`
Объединяет данные из TikTok, YouTube, Instagram, VK. Бэкенд сам ходит в API соцсетей
(по сохранённым токенам пользователя) и кэширует. Формат:

```json
{
  "total_reach": 1200000,
  "total_reach_label": "1.2M",
  "reach_by_day": [30,55,40,70,90,60,110,130,95,75,60,45],
  "reach_by_platform": [
    { "platform":"tiktok",   "label":"TikTok",   "reach":45200, "reach_label":"45.2K" },
    { "platform":"youtube",  "label":"YouTube",  "reach":28900, "reach_label":"28.9K" },
    { "platform":"instagram","label":"Instagram","reach":62100, "reach_label":"62.1K" },
    { "platform":"vk",       "label":"VK",       "reach":14700, "reach_label":"14.7K" }
  ],
  "metrics": [
    { "key":"watch_time_hours","label":"Время просмотра (ч)","value":"8,420","delta_pct":12 },
    { "key":"avg_retention",   "label":"Среднее удержание",  "value":"64.2%","delta_pct":-1.4 },
    { "key":"shares",          "label":"Репосты",            "value":"12.5K","delta_pct":34 }
  ],
  "top_videos": [
    { "id":"v1","platform":"instagram","title":"...","views":452000,"views_label":"452K","thumbnail_url":"https://...","published_at":"2025-05-18T12:00:00Z" }
  ]
}
```

- `reach_by_day` — массив одинаковой длины (рекомендую 12 или 28).
- `*_label` форматируется на сервере, чтобы фронт не парсил числа.
- `top_videos` агрегируется по всем платформам, сортируется по `views`, ограничь 5.

### `GET /api/profile`
```json
{
  "me": { /* см. /api/me */ },
  "achievements": [
    { "key":"hot_streak","label":"Hot Streak","earned_at":"2023-10-12","earned_at_label":"Oct 12, 2023","icon":"flame" }
  ]
}
```
`icon`: `"flame" | "star" | "trophy" | "gem"`.

## 4. Интеграция с ботом (общая БД)

Mini app и бот разделяют одну таблицу пользователей. Минимальная схема:

```sql
CREATE TABLE users (
  telegram_id      BIGINT PRIMARY KEY,
  first_name       TEXT NOT NULL,
  username         TEXT,
  photo_url        TEXT,
  timezone         TEXT NOT NULL DEFAULT 'UTC',
  notifications    BOOLEAN NOT NULL DEFAULT TRUE,
  onboarded_at     TIMESTAMPTZ,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE social_accounts (
  id               BIGSERIAL PRIMARY KEY,
  telegram_id      BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
  platform         TEXT NOT NULL CHECK (platform IN ('tiktok','youtube','instagram','vk')),
  external_user_id TEXT NOT NULL,
  access_token     TEXT NOT NULL,
  refresh_token    TEXT,
  expires_at       TIMESTAMPTZ,
  UNIQUE (telegram_id, platform)
);

CREATE TABLE ideas (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  telegram_id  BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
  title        TEXT NOT NULL,
  platform     TEXT NOT NULL,
  status       TEXT NOT NULL DEFAULT 'draft',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Бот пишет в `users` при `/start`. Mini app дополняет тот же ряд при первом
`GET /api/me`. Если телеграм-юзер уже есть, поле `is_new` = `onboarded_at IS NULL`.

## 5. Подключение соцсетей

OAuth выполняется на стороне бэка (FastAPI), mini app только показывает
кнопки и редиректит на `https://api.example.com/oauth/{platform}/start?tg=<id>`.
Callback'и сохраняют токены в `social_accounts`. Для агрегации `/api/stats`:

- TikTok: `display/user/info/`, `research/video/query/` или `video/list/`.
- YouTube: `youtube.channels.list`, `youtube.videos.list(stats)`.
- Instagram (Graph API): `me/media`, `media/{id}/insights`.
- VK: `stats.get`, `wall.get` + `video.get`.

Кэшируй ответы хотя бы на 5 минут — лимиты у всех жёсткие.

## 6. Деплой

- Mini app: Vercel. Переменная: `VITE_API_BASE_URL=https://api.example.com`.
- FastAPI: любой PaaS (Fly.io / Railway / Render / VPS). Главное — HTTPS и CORS из п.2.
- Не забудь добавить URL mini app в BotFather → Edit Mini App.