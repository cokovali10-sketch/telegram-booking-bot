<div align="center">

# 📅 Telegram Booking Bot

**Async appointment & booking management bot** built with Python 3.10+ and aiogram 3.x

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python)
![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?style=flat-square)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

## ✨ Features

- **📅 Smart booking calendar** — clients pick a date/time through an interactive calendar UI
- **👑 Admin panel** — manage services, view and confirm bookings
- **💾 SQLite + SQLAlchemy** — reliable async persistence with `aiosqlite`
- **📊 Excel export** — dump bookings to `.xlsx` for reporting
- **🔔 Scheduling** — automated reminders with `apscheduler`
- **🛡️ Error middleware** — graceful failure handling, no silent crashes
- **🌍 Multi-language ready** — clean separation of texts for localization

## 🚀 Quick Start

```bash
# 1. Clone and install
git clone https://github.com/cokovali10-sketch/telegram-booking-bot
cd telegram-booking-bot
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
copy .env.example .env   # fill in BOT_TOKEN and admin settings

# 3. Run
python bot.py
```

## 🗂️ Project Structure

```
app/
├── config/     # pydantic-settings configuration
├── database/   # models, session, queries
├── handlers/   # start, booking, admin flows
├── keyboards/  # inline, reply, calendar, services
├── middlewares/# error handling
├── services/   # calendar logic, business rules
├── states/     # FSM states (booking, admin)
└── utils/      # validators, formatters, exceptions
```

## 🛠️ Tech Stack

- **Python 3.10+** · **aiogram 3.x** (async)
- **SQLAlchemy 2.0** + **aiosqlite**
- **pydantic-settings** · **python-dotenv**
- **openpyxl** (Excel export) · **APScheduler**

---

<div align="center"><i>Built for fast, reliable, and easy-to-extend booking automation.</i></div>