# Telegram Support Request Bot

A production-ready, multi-language (🇺🇿 Uzbek / 🇷🇺 Russian / 🇬🇧 English) Telegram bot for
collecting user support appeals and routing all staff replies through a single Telegram
group — no employee ever needs a private chat with a user.

Built with **Python 3.12**, **aiogram 3**, **PostgreSQL**, **SQLAlchemy 2.0 (async)**,
**Alembic**, and **Docker**.

---

## Table of Contents

1. [How it works](#how-it-works)
2. [Project structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Setting up the bot in BotFather](#setting-up-the-bot-in-botfather)
5. [Configuration (.env)](#configuration-env)
6. [Running with Docker (recommended)](#running-with-docker-recommended)
7. [Running locally (without Docker)](#running-locally-without-docker)
8. [Database migrations](#database-migrations)
9. [Bot commands](#bot-commands)
10. [Admin panel](#admin-panel)
11. [Deployment notes](#deployment-notes)
12. [Troubleshooting](#troubleshooting)

---

## How it works

1. A user starts the bot, picks a language, and taps **📨 New Appeal**.
2. They send any combination of text, photos, videos, voice messages, documents,
   audio, animations, stickers, locations or contacts, then confirm.
3. The bot creates an appeal (`#000001`, `#000002`, ...) and posts a formatted card
   plus all attachments into a single staff **Telegram group**.
4. A staff member simply **replies** to that card (or to any attachment message)
   from inside the group — text, photo, video, voice, document, sticker, animation,
   whatever.
5. The bot detects the reply, matches it back to the appeal/user, and delivers it
   to the user privately, formatted as an official response.
6. The user can track all of their appeals and statuses from **📂 My Appeals**.

No employee ever needs to open a private chat with a user — everything happens
through the group.

---

## Project structure

```
Bot/
├── bot/
│   ├── config/            # pydantic-settings configuration
│   ├── database/
│   │   ├── models/        # SQLAlchemy 2.0 async ORM models
│   │   └── repositories/  # Repository pattern (one per model) + UnitOfWork
│   ├── filters/            # Custom aiogram filters (admin, group, reply-detection...)
│   ├── handlers/
│   │   ├── user/           # /start, language, new appeal, my appeals, help
│   │   ├── group/          # reply detection + group-only commands
│   │   └── admin/          # admin panel: stats, broadcast, search, ban, export, settings
│   ├── keyboards/          # Inline + reply keyboards, typed callback_data
│   ├── locales/            # uz.json / ru.json / en.json + i18n loader
│   ├── middlewares/        # DB session, i18n, throttling, ban-check, logging
│   ├── services/           # Business logic layer (appeals, users, broadcast, stats, export)
│   ├── states/             # aiogram FSM states
│   └── utils/               # formatting, validators, pagination, content helpers, logging
├── alembic/                # DB migrations (async engine aware)
├── logs/                   # Rotating log files (bot.log, errors.log)
├── main.py                 # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docker-entrypoint.sh    # Waits for Postgres, runs migrations, then starts the bot
├── .env.example
└── alembic.ini
```

---

## Prerequisites

- Docker + Docker Compose (recommended), **or**
- Python 3.12+ and a running PostgreSQL 14+ instance (for local/manual runs)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Telegram supergroup that will act as the staff inbox

---

## Setting up the bot in BotFather

1. Open a chat with [@BotFather](https://t.me/BotFather) and send `/newbot`.
2. Follow the prompts to choose a name and username; copy the token you receive —
   this is your `BOT_TOKEN`.
3. (Recommended) Send `/setprivacy` → select your bot → **Disable**. This lets the
   bot read all messages in the staff group (required to detect replies to cards
   that aren't direct replies to the bot itself, and to support commands like
   `/close`, `/reopen`).
4. Create a new Telegram **supergroup** for your staff (a normal group also works,
   but Telegram will prompt you to convert it to a supergroup once it grows).
5. Add your bot to that group **as an administrator** (it needs to read all
   messages and send messages).
6. Get the group's chat ID:
   - Add [@RawDataBot](https://t.me/RawDataBot) or [@userinfobot](https://t.me/userinfobot)
     to the group temporarily, or
   - Send any message in the group, then call
     `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` and read `chat.id`
     (it will be a negative number, e.g. `-1001234567890`).
7. Get your own Telegram user ID (for `SUPER_ADMIN_ID`) from
   [@userinfobot](https://t.me/userinfobot).

---

## Configuration (.env)

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Token from BotFather |
| `DATABASE_URL` | Async SQLAlchemy URL, e.g. `postgresql+asyncpg://user:pass@host:5432/db` |
| `GROUP_ID` | Negative chat ID of the staff supergroup |
| `SUPER_ADMIN_ID` | Your Telegram user ID (always has full admin rights) |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Used by docker-compose to bootstrap Postgres |
| `THROTTLE_RATE_LIMIT` | Minimum seconds between messages per user (flood protection) |
| `MAX_ATTACHMENTS_PER_APPEAL` | Soft cap on attachments per appeal |
| `TIMEZONE` | IANA timezone used for displayed dates and statistics |

---

## Running with Docker (recommended)

```bash
cp .env.example .env
# edit .env with your BOT_TOKEN, GROUP_ID, SUPER_ADMIN_ID, etc.

docker compose up -d --build
```

This will:

1. Start a PostgreSQL 16 container with a persistent volume.
2. Build the bot image, wait for Postgres to become healthy.
3. Run `alembic upgrade head` automatically (via `docker-entrypoint.sh`).
4. Start the bot with long-polling.

View logs:

```bash
docker compose logs -f bot
```

Stop everything:

```bash
docker compose down
```

---

## Running locally (without Docker)

1. Install PostgreSQL and create a database:

   ```sql
   CREATE USER support_bot WITH PASSWORD 'support_bot_password';
   CREATE DATABASE support_bot OWNER support_bot;
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:

   ```bash
   cp .env.example .env
   # set DATABASE_URL=postgresql+asyncpg://support_bot:support_bot_password@localhost:5432/support_bot
   ```

5. Run migrations:

   ```bash
   alembic upgrade head
   ```

6. Start the bot:

   ```bash
   python main.py
   ```

---

## Database migrations

Migrations live in `alembic/versions/`. Common commands:

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after changing models
alembic revision --autogenerate -m "describe your change"

# Roll back one migration
alembic downgrade -1
```

The included `0001_initial_schema.py` migration creates all tables: `users`,
`admins`, `settings`, `statistics`, `appeals`, `appeal_messages`, `banned_users`,
plus a `appeal_number_seq` Postgres sequence that guarantees unique, gapless-per-insert
appeal numbers (`#000001`, `#000002`, ...).

---

## Bot commands

**Private chat (all users):**

| Command | Description |
|---|---|
| `/start` | Register / choose language / show main menu |
| `/menu` | Show the main menu again |
| `/help` | Show help text |

**Private chat (admins/super admin only):**

| Command | Description |
|---|---|
| `/admin` | Open the admin panel (statistics, broadcast, search, ban/unban, export, settings) |

**Inside the staff group:**

| Command | Description |
|---|---|
| *(reply to a card)* | Any reply to an appeal card or attachment is forwarded to the user automatically |
| `/status` | (as a reply to a card) Show the appeal's current status |
| `/close` | (as a reply to a card) Mark the appeal as closed |
| `/reopen` | (as a reply to a card) Reopen a closed/answered appeal |
| `/stats` | Quick statistics summary (admins only) |

---

## Admin panel

Open a private chat with the bot and send `/admin`. From there you can:

- **📊 Statistics** — today / this week / this month, total users & appeals,
  answered / pending / closed counts, language breakdown, top-replying employees.
- **📢 Broadcast** — send a text/photo/video/document message to every registered
  user, with a confirmation step before sending.
- **🔎 Search Appeal** — search by appeal number, Telegram ID, username, name or
  phone number, with paginated results.
- **🚫 Ban User** / **✅ Unban User** — block/unblock a user by Telegram ID or
  username, with an optional reason.
- **📁 Export** — download all appeals as CSV, Excel (`.xlsx`) or PDF.
- **⚙️ Settings** — view/edit arbitrary runtime key/value settings
  (`key=value` message to upsert).

Only the configured `SUPER_ADMIN_ID` and rows in the `admins` table (`is_active =
true`) can access the panel. Staff members who reply in the group are
automatically tracked (for the "top employees" statistic) the first time they
reply — they do **not** need `/admin` access to answer appeals, only group
membership.

---

## Deployment notes

- Logs are written to `logs/bot.log` (all levels ≥ `LOG_LEVEL`) and
  `logs/errors.log` (errors only, with tracebacks), both rotated at 10 MB and
  compressed.
- The global error handler (`bot/handlers/errors.py`) ensures a single failing
  update is logged and answered with a friendly message instead of crashing the
  process.
- Flood protection drops repeated messages from the same user faster than
  `THROTTLE_RATE_LIMIT` seconds (private chats only — staff activity in the
  group is never throttled).
- FSM state (in-progress appeal composition, broadcast drafts, etc.) uses
  aiogram's in-memory storage by default. For multi-instance deployments,
  swap `MemoryStorage` in `main.py` for `RedisStorage` and adjust
  `requirements.txt` accordingly.
- Back up your Postgres volume regularly (`docker compose exec postgres
  pg_dump -U <user> <db> > backup.sql`) — appeals and users live only in the
  database.

---

## Troubleshooting

**Bot doesn't respond at all**
- Check `docker compose logs -f bot` for startup errors (usually a bad
  `BOT_TOKEN` or unreachable `DATABASE_URL`).

**Appeals aren't appearing in the group**
- Confirm `GROUP_ID` is correct (must be negative for supergroups) and that the
  bot is an **administrator** of that group.
- Make sure the bot's privacy mode is disabled (`/setprivacy` in BotFather) if
  replies via `/close`, `/reopen`, `/status` aren't being recognized.

**Replies from staff aren't reaching the user**
- The staff member must **reply** (Telegram's native reply feature) directly to
  the appeal card or one of its attachments — a plain message in the group is
  ignored.
- If the user has blocked the bot, the group will receive a "delivery failed"
  notice instead of a silent failure.

**"relation ... does not exist" errors**
- Migrations haven't run. Run `alembic upgrade head` (or restart the `bot`
  container, which runs it automatically via `docker-entrypoint.sh`).

**Admin panel says "only available to administrators"**
- Only `SUPER_ADMIN_ID` and active rows in the `admins` table can use `/admin`.
  The super admin is auto-registered on every bot startup.
