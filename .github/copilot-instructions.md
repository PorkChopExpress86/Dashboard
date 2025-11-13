# Home Dashboard
## What it is
A small web dashboard that pulls together the stuff your family actually cares about: schedules, reminders, and maybe some “house stats.”

## Core features

- Pull in:
  - Upcoming events (iCal/Google Calendar export)
  - Important school / sports dates from a CSV/Google Sheet
  - Weather + “today’s reminders”
- Have a “Tonight” section
  - Homework due?
  - Who has practice?
  - Dinner plan?
  - Any must-do tasks?

- Stack ideas:
  - Backend: Python (FastAPI or Django)
  - Frontend: basic HTML + Bootstrap (no heavy JS needed)
  - Run in Docker on your home server, expose via reverse proxy

- Stretch ideas:
  - Integrate with a chores schedule or “who’s on dishes / trash” rotator
  - Add a “What broke this week?” log that you can export when you go to Home Depot

# File Structure
homebrain-dashboard/
├─ app/
│  ├─ __init__.py
│  ├─ main.py               # FastAPI app factory / entrypoint
│  ├─ config.py             # Settings (API keys, location, feature flags)
│  ├─ models.py             # Pydantic models for Events, Tasks, Reminders
│  ├─ routers/
│  │  ├─ dashboard.py       # Web routes (HTML pages)
│  │  └─ api.py             # JSON endpoints if needed
│  ├─ services/
│  │  ├─ calendar_service.py   # Pull events from iCal/Google or local CSV
│  │  ├─ tasks_service.py      # Simple local tasks/reminders logic
│  │  └─ weather_service.py    # Weather API integration (can stub at first)
│  ├─ templates/
│  │  ├─ base.html          # Layout: navbar, base styling
│  │  └─ dashboard.html     # Main “Tonight / Today / This Week” view
│  ├─ static/
│  │  ├─ css/
│  │  │  └─ main.css        # Custom styles on top of Bootstrap
│  │  └─ js/
│  │     └─ main.js         # Small JS enhancements (if any)
│  └─ data/
│     ├─ sample_events.json # Example event data
│     └─ sample_tasks.json  # Example tasks/reminders
├─ tests/
│  ├─ test_dashboard.py
│  └─ test_services.py
├─ .env.example             # Example env vars (no secrets)
├─ requirements.txt         # Python dependencies
├─ Dockerfile               # Optional: containerize the app
├─ docker-compose.yml       # Optional: run app + reverse proxy, etc.
├─ .gitignore
├─ .vscode/
│  ├─ settings.json         # Python path, formatting, etc.
│  └─ launch.json           # Debug configuration (FastAPI/Uvicorn)
└─ README.md                # Copilot “spec” and setup instructions
