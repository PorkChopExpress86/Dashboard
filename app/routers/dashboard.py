from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.services import calendar_service, weather_service, menu_service


router = APIRouter()

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/")
def home(request: Request):
    settings = get_settings()

    now = datetime.now(calendar_service.get_tzinfo(settings.timezone))
    today_events = calendar_service.events_today(now)
    tomorrow_events = calendar_service.events_tomorrow(now)
    week_events = calendar_service.events_this_week(now)

    weather = weather_service.get_weather(settings.location_city)
    weekly_menu = menu_service.get_weekly_menu()
    today_menu = menu_service.get_today_menu(now)
    tomorrow_menu = menu_service.get_tomorrow_menu(now)
    today_menu_full = menu_service.get_today_menu_full()
    tomorrow_menu_full = menu_service.get_tomorrow_menu_full()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "city": settings.location_city,
            "now": now,
            "today_events": today_events,
            "tomorrow_events": tomorrow_events,
            "week_events": week_events,
            "weather": weather,
            "weather_lat": settings.weather_lat or 29.8,
            "weather_lon": settings.weather_lon or -95.6,
            "weekly_menu": weekly_menu,
            "today_menu": today_menu,
            "tomorrow_menu": tomorrow_menu,
            "today_menu_full": today_menu_full,
            "tomorrow_menu_full": tomorrow_menu_full,
        },
    )
