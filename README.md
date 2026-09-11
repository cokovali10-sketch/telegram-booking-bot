<div align="center">

# Telegram Booking Bot

**A production-ready Telegram bot for service businesses — salons, clinics, workshops, and more.**

Built with **aiogram 3**, **SQLAlchemy 2 (async)**, and **Pydantic v2**.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![aiogram 3](https://img.shields.io/badge/aiogram-3.x-26A5E4.svg?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-CC0000.svg?logo=sqlalchemy&logoColor=white)](https://docs.sqlalchemy.org/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-FF6434.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## Features

### Client-Facing
- **5-step booking flow** — Category → Service → Master → Date → Time → Confirm
- **Interactive calendar** — month navigation, past-date blocking, visual slot availability
- **Promo codes** — apply discount codes during checkout
- **Reviews & ratings** — 1–5 star ratings with comments on completed bookings
- **Profile management** — edit name and phone number
- **My Bookings** — view, reschedule, or cancel existing appointments
- **FAQ & Contacts** — built-in info pages

### Admin Panel
- **Booking management** — confirm, complete, or cancel any booking
- **Analytics dashboard** — total clients, bookings by status, revenue estimate
- **Service & Master CRUD** — add, activate, or deactivate items
- **Promo code creation** — set discount percentage and usage limits
- **CSV export** — download full booking history as a spreadsheet
- **Broadcast messaging** — send announcements to all registered users
- **Admin notifications** — instant alerts on new bookings

### Technical
- **Async architecture** — fully async/await with aiosqlite
- **FSM-based flows** — aiogram state machines for multi-step interactions
- **Session management** — scoped SQLAlchemy sessions with context managers
- **Seed data** — auto-populates services, masters, and promo codes on first run
- **Structured logging** — timestamped, level-based log output

---

## Architecture

```
telegram-booking-bot/
├── bot.py                          # Entry point — bot initialization & polling
├── app/
│   ├── config/
│   │   └── settings.py             # Pydantic BaseSettings (env-based config)
│   ├── database/
│   │   ├── models.py               # SQLAlchemy ORM models (User, Service, Master, Booking, etc.)
│   │   ├── db.py                   # Engine, session factory, init_db()
│   │   ├── session.py              # Async session context manager
│   │   └── requests.py             # All database queries & mutations
│   ├── handlers/
│   │   ├── start.py                # /start, profile, bookings, reviews, FAQ
│   │   ├── booking.py              # 5-step booking flow with FSM
│   │   └── admin.py                # Admin panel — CRUD, stats, broadcast, export
│   ├── keyboards/
│   │   ├── inline.py               # All inline keyboards (categories, services, etc.)
│   │   ├── reply.py                # Reply keyboards (main menu)
│   │   ├── main_menu.py            # Menu helpers
│   │   └── services.py             # Service-related keyboards
│   ├── services/
│   │   └── calendar_service.py     # Calendar generation & time slot logic
│   ├── states/
│   │   ├── booking_states.py       # Booking FSM states
│   │   ├── booking.py              # Additional booking states
│   │   └── admin_states.py         # Admin FSM states
│   ├── middlewares/
│   │   └── errors.py               # Error handling middleware
│   └── utils/
│       ├── validators.py           # Input validation (date, phone, etc.)
│       ├── formatters.py           # Display formatting helpers
│       └── exceptions.py           # Custom exception classes
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Database Schema

| Model | Description |
|---|---|
| `User` | Telegram user profile (tg_id, name, phone, role) |
| `Category` | Service category with title and description |
| `Service` | Individual service with price and duration |
| `Master` | Employee with name, specialization, and bio |
| `PromoCode` | Discount codes with usage limits |
| `Booking` | Appointment linking user, service, master, and time slot |
| `Review` | 1–5 star rating with optional comment |

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/yourname/telegram-booking-bot.git
cd telegram-booking-bot
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_IDS=123456789,987654321
DB_PATH=data/booking.db
LOG_LEVEL=INFO
```

### 3. Run

```bash
python bot.py
```

The bot starts polling. Database and seed data are created automatically on first run.

---

## Usage

### Client Flow

```
/user starts bot
  → Welcome message with reply keyboard
  → "📅 Записаться" triggers 5-step booking:
      Step 1: Choose category
      Step 2: Choose service
      Step 3: Choose master
      Step 4: Pick date (interactive calendar)
      Step 5: Pick time (visual slot grid)
  → Apply promo code (optional)
  → Add comment (optional)
  → Confirm → booking saved, admin notified
```

### Admin Flow

```
Click "👑 Админ-панель" (admin-only)
  → View active bookings with status management
  → Analytics dashboard (clients, bookings, revenue)
  → Add/manage services and masters
  → Create promo codes
  → Broadcast messages
  → Export bookings to CSV
```

### Bot Commands

| Command | Description |
|---|---|
| `/start` | Register and show main menu |
| `/book` | Start the booking flow |
| `/my_bookings` | View your bookings |
| `/admin` | Open admin panel (admins only) |

---

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | Yes | — | Telegram Bot API token |
| `ADMIN_IDS` | No | `[]` | Comma-separated Telegram user IDs for admin access |
| `DB_PATH` | No | `data/booking.db` | SQLite database file path |
| `LOG_LEVEL` | No | `INFO` | Python logging level |

---

## Tech Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram bot framework
- **SQLAlchemy 2.0** — async ORM with aiosqlite backend
- **Pydantic v2** — settings management via pydantic-settings
- **SQLite** — lightweight file-based database

---

## License

MIT — use freely for personal and commercial projects.
