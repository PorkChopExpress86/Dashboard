# HomeBrain Dashboard

A small self-hosted **home dashboard** built with **FastAPI + Jinja2 + Bootstrap**.

Goal: pull together **family-relevant info** into one page:
- "Tonight" – who has practice, meetings, or events?
- "Today" – weather, must-do reminders.
- "This Week" – upcoming important dates.

This app is designed to run on a home server (Docker or bare Python) and be simple:
- No user accounts
- Local config via `.env` and small JSON/CSV files
- Easy to extend with new widgets (finance, chores, projects, etc.)

---

## Features (MVP)

1. **Dashboard Page**
   - Single-page HTML dashboard (`/`) showing:
     - "Tonight" section: events after 5 PM local time
     - "Today" section: next few events and reminders
     - "This Week" section: important events (games, practices, meetings)
   - Layout:
     - Bootstrap cards for each section
     - Responsive design (looks OK on phone & desktop)

2. **Data Sources**
   - Calendar:
     - Initially: read from `app/data/sample_events.json`
     - Later: allow pointing to:
       - An iCal file
       - A CSV export
       - Or a simple local JSON config
   - Tasks/Reminders:
     - Initially: read from `app/data/sample_tasks.json`
     - Simple model:
       - title
       - due_date
       - category (home, kids, work, etc.)
       - importance (low/med/high)
   - Weather:
     - Start with a stub (hard-coded example data)
     - Later: integrate with a real weather API using `WEATHER_API_KEY` from `.env`.

3. **Configuration**
   - `.env` file to specify:
     - `APP_ENV` (dev/prod)
     - `TIMEZONE`
     - `LOCATION_CITY`
     - `WEATHER_API_KEY` (optional at first)
     - `CALENDAR_SOURCE` (e.g. `local_json`, `ics_file`)
   - `app/config.py` loads these values into a `Settings` Pydantic class.

4. **Services Layer**
   - `calendar_service.py`:
     - Function(s) to load events from JSON/CSV/ICS
     - Normalize to a common `Event` model
     - Helpers to filter:
       - events for today
       - events for tonight (after 17:00)
       - events for the next 7 days
   - `tasks_service.py`:
     - Function(s) to load tasks from JSON
     - Helpers to filter tasks by:
       - due today
       - overdue
       - this week
   - `weather_service.py`:
     - Stub function returning fake weather data for now.
     - Later: real API call.

5. **Testing**
   - Basic tests in `tests/`:
     - Loading sample events
     - Filtering logic (today, tonight, this week)
     - Rendering the dashboard route returns HTTP 200

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI
- **Templates**: Jinja2 via FastAPI `Jinja2Templates`
- **Styles**: Bootstrap 5 (CDN is fine to start) + `static/css/main.css`
- **Server**: Uvicorn (dev), can be run behind Nginx/Caddy in prod
- **Data Storage**: 
  - Initially: JSON files in `app/data/`
  - Optionally: upgrade to SQLite if needed later

---

## Setup Instructions (Local Dev)

### 1. Clone and Set Up Environment

```bash
git clone <your-repo-url> homebrain-dashboard
cd homebrain-dashboard

# Create and activate virtualenv (Windows PowerShell example)
python -m venv .venv
. .venv/Scripts/Activate.ps1

# Or on Linux/macOS:
# python -m venv .venv
# source .venv/bin/activate

pip install -r requirements.txt

### 2. Weather API (Optional Live Data)

To enable live weather instead of the stub:
1. Create a free account at https://openweathermap.org/ and obtain an API key.
2. Add `WEATHER_API_KEY=<your_key>` to `.env`.
3. (Optional) Adjust `LOCATION_CITY` for your preferred city (e.g. `LOCATION_CITY=Boston`).

The app will fall back to the stub automatically if the key is missing or the API call fails; results are cached per city for the process lifetime.

### 3. Weather Radar (Optional)

Add a live precipitation radar tile layer (RainViewer) displayed in a card:
1. Provide approximate coordinates in `.env` for centering:

  ```env
  WEATHER_LAT=42.3601
  WEATHER_LON=-71.0589
  ```

1. The dashboard will render an interactive radar map (Leaflet + RainViewer). If lat/lon not set it defaults to `(0,0)` zoomed out.

1. No extra API key required; tiles are public.

Notes:

- Radar loads client-side; if offline it silently shows a fallback message.
- You can adjust zoom level by editing `RADAR_DEFAULT_ZOOM` in `static/js/main.js` if desired.

### 4. Google Calendar Sync (ICS Feed)

Simplest integration uses a public or private ICS feed URL from Google Calendar:
1. In Google Calendar web UI: Settings &rarr; Select calendar &rarr; "Integrate calendar".

2. Copy either the "Public address in iCal format" (if calendar made public) or the private "Secret address in iCal format".

3. Add to `.env`:

   **For a single calendar:**
   ```env
   CALENDAR_SOURCE=google_ics
   GOOGLE_CALENDAR_ICAL_URL=https://calendar.google.com/calendar/ical/.../basic.ics
   CALENDAR_REFRESH_MINUTES=30
   ```

   **For multiple calendars with labels:**
   ```env
   CALENDAR_SOURCE=google_ics
   CALENDAR_ICAL_SOURCES={"Family":"https://calendar.google.com/calendar/ical/.../basic.ics","Work":"https://calendar.google.com/calendar/ical/.../basic.ics"}
   CALENDAR_REFRESH_MINUTES=30
   ```

   **Or as an array (no labels):**
   ```env
   CALENDAR_SOURCE=google_ics
   CALENDAR_ICAL_SOURCES=["https://calendar.google.com/calendar/ical/.../basic.ics","https://calendar.google.com/calendar/ical/.../basic.ics"]
   ```

1. Restart the app. Events will populate automatically and refresh in the background at the specified interval.

Behavior:

- Events are cached to disk in `CALENDAR_CACHE_DIR` (default `./cache`, in Docker `/data/cache`).
- Cache persists across restarts; initial load is from disk if available, then refreshes from ICS.
- If Google ICS fetch fails, uses cached events or falls back to local JSON sample data.
- Background task refreshes every `CALENDAR_REFRESH_MINUTES` (minimum 5).
- Local timezone (`TIMEZONE`) is applied to ICS events lacking explicit tz info.
- Docker: Events persist in the `dashboard_data` volume.

Security Note: Treat the secret ICS URL as a credential; do not commit it. Use `.env` only.
