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
