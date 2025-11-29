from fastapi import APIRouter

from app.services import calendar_service, tasks_service, weather_service


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/events/today")
def api_events_today():
    return [e.model_dump() for e in calendar_service.events_today()]


@router.get("/tasks/today")
def api_tasks_today():
    return [t.model_dump() for t in tasks_service.tasks_due_today()]


@router.get("/weather")
def api_weather():
    info = weather_service.get_weather()
    return info.model_dump()


@router.get("/location")
def api_get_location():
    """Return the current configured location for the dashboard."""
    from app.config import get_settings
    settings = get_settings()
    return {
        "lat": settings.weather_lat or 41.8781,
        "lon": settings.weather_lon or -87.6298,
        "city": settings.location_city or "Your City"
    }
