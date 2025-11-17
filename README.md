# HomeBrain Dashboard

A self-hosted **family dashboard** built with **FastAPI + Jinja2 + Bootstrap** that displays:
- 📅 **Today & Tomorrow** – events, weather, school lunch menu
- 📆 **This Week** – upcoming important dates and activities  
- 🍽️ **Weekly Lunch Menu** – automatically updated school cafeteria menu
- ☁️ **Weather** – current conditions and hourly forecast

Designed to run on a home server via **Docker** or **bare Python**, with:
- No user accounts or authentication
- Simple `.env` configuration
- Automated nightly data updates
- Clean, modern UI optimized for kitchen displays

---

## Features

### 1. Dashboard View
Single-page dashboard (`/`) with responsive grid layout:
- **Weather Card**: Current temperature, conditions, and 12-hour forecast
- **Today Card**: Events scheduled for today + today's lunch menu
- **Tomorrow Card**: Tomorrow's events + tomorrow's lunch menu  
- **This Week Card**: All upcoming events for the next 7 days
- **Weekly Menu Card**: Full week school lunch menu with daily entrees

### 2. Data Sources

#### Calendar Events
- **Google Calendar ICS feeds** (recommended):
  - Supports single or multiple calendars
  - Auto-refreshes in background (configurable interval)
  - Cached to disk for offline resilience
- **Local JSON** fallback: `app/data/sample_events.json`

#### School Lunch Menu
- **Automated scraper**: 
  - Runs nightly at 10 PM via cron in Docker container
  - Scrapes SchoolCafe website for weekly menu
  - Saves to `cache/weekly_menu_data.json`
  - Includes entrees, calories, and allergen info
- See [`SCRAPER_README.md`](SCRAPER_README.md) for management commands

#### Weather
- **OpenWeatherMap API** integration:
  - Current conditions, daily high/low
  - Hourly forecast with temperature and precipitation
  - Results cached per city per process
- **RainViewer radar** (optional):
  - Live precipitation overlay map
  - No API key required

### 3. Configuration
All settings via `.env` file (see `.env.example`):
- `APP_ENV`: dev or prod
- `TIMEZONE`: Local timezone (e.g., `America/Chicago`)
- `LOCATION_CITY`: City for weather
- `WEATHER_API_KEY`: OpenWeatherMap API key (optional)
- `WEATHER_LAT`, `WEATHER_LON`: Coordinates for radar map
- `CALENDAR_SOURCE`: `google_ics` or `local_json`
- `GOOGLE_CALENDAR_ICAL_URL`: Single calendar ICS URL
- `CALENDAR_ICAL_SOURCES`: Multiple calendar URLs (JSON array or object)
- `CALENDAR_REFRESH_MINUTES`: Background refresh interval (default 30)
- `CALENDAR_CACHE_DIR`: Cache directory path

### 4. Services Layer
- **`calendar_service.py`**: 
  - Loads events from Google ICS feeds or local JSON
  - Filters: today, tomorrow, this week
  - Background refresh task
- **`menu_service.py`**:
  - Loads weekly menu from cached JSON
  - Provides today/tomorrow menu helpers
- **`weather_service.py`**:
  - OpenWeatherMap API integration
  - Hourly forecast parsing
  - In-memory caching

### 5. Automated Scraper
Dedicated Docker service (`scraper`) that:
- Runs `scripts/scrape_weekly_menu.py` nightly at 10 PM
- Uses Selenium + headless Chrome via separate container
- Saves menu to `cache/weekly_menu_data.json`
- Configured with cron job and auto-restart policy
- See [`SCRAPER_README.md`](SCRAPER_README.md) for details

---

## Tech Stack

- **Backend**: Python 3.14, FastAPI, Uvicorn
- **Frontend**: Jinja2 templates, Bootstrap 5 (Bootswatch Flatly theme)
- **Styling**: Custom CSS with gradient backgrounds and card layouts
- **Scraping**: Selenium WebDriver, BeautifulSoup4, ChromeDriver
- **Deployment**: Docker Compose (3 services: dashboard, selenium, scraper)
- **Data Storage**: 
  - JSON files in `cache/` directory
  - Docker volume for persistence (`dashboard_data`)

---

## Setup Instructions

### Option 1: Docker Compose (Recommended)

The easiest way to run the dashboard with all features including the automated scraper.

#### Prerequisites
- Docker and Docker Compose installed
- (Optional) OpenWeatherMap API key for live weather

#### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/PorkChopExpress86/Dashboard.git
   cd Dashboard
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure:
   ```env
   APP_ENV=prod
   TIMEZONE=America/Chicago
   LOCATION_CITY=Houston
   WEATHER_API_KEY=your_openweathermap_api_key
   WEATHER_LAT=29.7604
   WEATHER_LON=-95.3698
   
   # Google Calendar (see Google Calendar section below)
   CALENDAR_SOURCE=google_ics
   GOOGLE_CALENDAR_ICAL_URL=https://calendar.google.com/calendar/ical/.../basic.ics
   CALENDAR_REFRESH_MINUTES=30
   ```

3. **Build and start services**:
   ```bash
   docker compose up -d --build
   ```
   
   This starts three services:
   - `dashboard`: Web application (http://localhost:8000)
   - `selenium`: Headless Chrome for scraping
   - `scraper`: Automated menu scraper (runs at 10 PM nightly)

4. **Access the dashboard**:
   - Open http://localhost:8000 in your browser
   - Initial menu data is scraped immediately on startup

#### Docker Management Commands

```bash
# View logs
docker compose logs -f dashboard
docker compose logs -f scraper

# Restart services
docker compose restart

# Stop all services
docker compose down

# Rebuild after code changes
docker compose up -d --build

# Manually trigger menu scraper
docker exec schoolcafe-scraper python /work/scripts/scrape_weekly_menu.py
```

---

### Option 2: Local Development (Python)

Run without Docker for development and testing.

#### Prerequisites
- Python 3.11 or higher
- Chrome/Chromium installed (for menu scraper)
- ChromeDriver (auto-downloaded by webdriver-manager)

#### Steps

1. **Clone and set up environment**:
   ```bash
   git clone https://github.com/PorkChopExpress86/Dashboard.git
   cd Dashboard
   
   # Create virtual environment (Windows PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   
   # Or on Linux/macOS
   # python -m venv .venv
   # source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your settings (see Docker example above)

3. **Run the dashboard**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Access at http://localhost:8000

4. **Run menu scraper manually** (optional):
   ```bash
   python scripts/scrape_weekly_menu.py
   ```
   
   This creates/updates `cache/weekly_menu_data.json`

---

## Configuration Details

---

## Configuration Details

### Weather API (OpenWeatherMap)

To enable live weather:

1. Create a free account at <https://openweathermap.org/> and obtain an API key
2. Add to `.env`:

   ```env
   WEATHER_API_KEY=your_api_key_here
   LOCATION_CITY=Houston
   WEATHER_LAT=29.7604
   WEATHER_LON=-95.3698
   ```

3. Restart the app

Behavior:

- Weather API results are cached per city for the process lifetime
- Falls back to stub data if API key missing or API call fails
- Radar map requires `WEATHER_LAT` and `WEATHER_LON` coordinates

### Google Calendar Integration

The dashboard supports Google Calendar via public or private ICS feeds.

#### Getting Your ICS URL

1. In Google Calendar web UI: Settings → Select calendar → "Integrate calendar"
2. Copy either:
   - **Public address in iCal format** (if calendar is public)
   - **Secret address in iCal format** (private - recommended)

⚠️ **Security Note**: The secret ICS URL acts as a password. Do not commit it to version control. Keep it in `.env` only.

#### Single Calendar Setup

Add to `.env`:

```env
CALENDAR_SOURCE=google_ics
GOOGLE_CALENDAR_ICAL_URL=https://calendar.google.com/calendar/ical/.../basic.ics
CALENDAR_REFRESH_MINUTES=30
```

#### Multiple Calendars Setup

**With labels** (shows calendar name with events):

```env
CALENDAR_SOURCE=google_ics
CALENDAR_ICAL_SOURCES={"Family":"https://calendar.google.com/calendar/ical/.../basic.ics","Work":"https://calendar.google.com/calendar/ical/.../basic.ics"}
CALENDAR_REFRESH_MINUTES=30
```

**Without labels** (array format):

```env
CALENDAR_SOURCE=google_ics
CALENDAR_ICAL_SOURCES=["https://calendar.google.com/calendar/ical/.../basic.ics","https://calendar.google.com/calendar/ical/.../basic.ics"]
CALENDAR_REFRESH_MINUTES=30
```

#### Calendar Behavior

- Events cached to disk in `CALENDAR_CACHE_DIR` (default `./cache`, Docker: `/data/cache`)
- Cache persists across restarts
- Initial load from disk if available, then refreshes from ICS
- Background task refreshes every `CALENDAR_REFRESH_MINUTES` (minimum 5)
- If Google ICS fetch fails, uses cached events or falls back to `app/data/sample_events.json`
- Local timezone (`TIMEZONE`) applied to ICS events lacking explicit timezone info
- Docker: Events persist in `dashboard_data` volume

### School Lunch Menu Scraper

The menu scraper automatically fetches weekly lunch menus from SchoolCafe.

#### Configuration

The scraper is pre-configured for:

- **School**: Post Elementary (CFISD)
- **Grade**: 1st grade
- **Meal**: Lunch
- **Schedule**: Every night at 10:00 PM

To modify the school, grade, or schedule:

1. Edit `scripts/scrape_weekly_menu.py` - change the `view_id` parameter
2. Edit `scraper.cron` - change the cron schedule
3. Rebuild: `docker compose build scraper && docker compose up -d scraper`

#### Finding Your School's ViewID

1. Visit <https://www.schoolcafe.com/> and navigate to your school's menu
2. Select your grade and meal type
3. Copy the `viewID` parameter from the URL (e.g., `?viewID=4322524b-1f7e-476a-9139-814c671143ef`)
4. Update the script with your viewID

#### Scraper Management

See [`SCRAPER_README.md`](SCRAPER_README.md) for detailed commands:

- View logs: `docker compose logs scraper`
- Manual trigger: `docker exec schoolcafe-scraper python /work/scripts/scrape_weekly_menu.py`
- Check schedule: `docker exec schoolcafe-scraper crontab -l`
- View execution logs: `docker exec schoolcafe-scraper cat /var/log/cron.log`

---

## Project Structure

```text
Dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (from .env)
│   ├── models.py            # Pydantic models
│   ├── routers/
│   │   ├── dashboard.py     # Main dashboard route
│   │   └── api.py           # JSON API endpoints (if needed)
│   ├── services/
│   │   ├── calendar_service.py   # ICS/JSON event loading & filtering
│   │   ├── menu_service.py       # School lunch menu service
│   │   └── weather_service.py    # OpenWeatherMap integration
│   ├── templates/
│   │   ├── base.html        # Base layout
│   │   └── dashboard.html   # Main dashboard view
│   ├── static/
│   │   ├── css/main.css     # Custom styles
│   │   └── js/main.js       # Client-side JavaScript
│   └── data/
│       ├── sample_events.json    # Fallback calendar data
│       └── sample_tasks.json     # Sample tasks (unused currently)
├── scripts/
│   ├── scrape_weekly_menu.py     # Weekly menu scraper
│   ├── scrape_schoolcafe.py      # Alternative scraper
│   └── test_scraper.py           # Scraper testing utilities
├── cache/
│   └── weekly_menu_data.json     # Cached menu data (generated)
├── tests/
│   ├── test_dashboard.py
│   └── test_services.py
├── docker-compose.yml       # Docker services definition
├── Dockerfile               # Dashboard container
├── Dockerfile.scraper       # Scraper container
├── entrypoint.sh            # Scraper startup script
├── scraper.cron             # Cron schedule for scraper
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── README.md                # This file
└── SCRAPER_README.md        # Scraper documentation
```

---

## Development

### Running Tests

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/macOS

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Code Style

The project uses:

- **Formatter**: autopep8 or black (optional)
- **Linter**: pylint or ruff (optional)
- **Type hints**: Throughout codebase

### Adding New Features

1. **New data source**: Add service in `app/services/`
2. **New UI section**: Update `app/templates/dashboard.html` and `app/static/css/main.css`
3. **New API endpoint**: Add route in `app/routers/api.py`
4. **New scraper**: Add script in `scripts/` and update `scraper.cron`

---

## Troubleshooting

### Dashboard not loading

- Check if service is running: `docker compose ps`
- View logs: `docker compose logs dashboard`
- Verify `.env` file exists and is configured
- Check port 8000 is not in use: `netstat -ano | findstr :8000`

### Weather not showing

- Verify `WEATHER_API_KEY` is set in `.env`
- Check API key is valid at <https://openweathermap.org/api>
- View logs for API errors: `docker compose logs dashboard`

### Calendar events not appearing

- Verify ICS URL is accessible (test in browser)
- Check `CALENDAR_SOURCE=google_ics` is set
- View logs: `docker compose logs dashboard`
- Check cache file exists: `ls cache/` or `dir cache\`
- Manually refresh: Restart the dashboard service

### Menu scraper not running

- Check scraper container status: `docker compose ps scraper`
- View scraper logs: `docker compose logs scraper`
- Verify cron job: `docker exec schoolcafe-scraper crontab -l`
- Check execution logs: `docker exec schoolcafe-scraper cat /var/log/cron.log`
- Manually trigger: `docker exec schoolcafe-scraper python /work/scripts/scrape_weekly_menu.py`

### Selenium/Chrome issues

- Ensure selenium service is running: `docker compose ps selenium`
- Check selenium logs: `docker compose logs selenium`
- Verify scraper can reach selenium: `docker exec schoolcafe-scraper ping selenium`

---

## License

MIT License - see LICENSE file for details

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## Roadmap

Potential future enhancements:

- [ ] Multiple school menu support (siblings in different schools)
- [ ] Chores/tasks tracking integration
- [ ] Shopping list widget
- [ ] Family photo slideshow
- [ ] Package delivery tracking
- [ ] Sports scores widget
- [ ] Gas prices nearby
- [ ] Home automation integration (lights, thermostat)
- [ ] Mobile app companion
- [ ] Voice assistant integration

---

## Credits

Built with:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Bootstrap](https://getbootstrap.com/) - CSS framework
- [Bootswatch](https://bootswatch.com/) - Bootstrap themes
- [Selenium](https://www.selenium.dev/) - Web automation
- [OpenWeatherMap](https://openweathermap.org/) - Weather API
- [RainViewer](https://www.rainviewer.com/) - Radar tiles
