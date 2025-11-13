from datetime import date

from app.services import calendar_service, tasks_service, weather_service


def test_calendar_filters_do_not_crash():
    today = calendar_service.events_today()
    tonight = calendar_service.events_tonight()
    week = calendar_service.events_this_week()
    assert isinstance(today, list)
    assert isinstance(tonight, list)
    assert isinstance(week, list)


def test_task_filters_do_not_crash():
    today = tasks_service.tasks_due_today()
    overdue = tasks_service.tasks_overdue()
    week = tasks_service.tasks_this_week()
    assert isinstance(today, list)
    assert isinstance(overdue, list)
    assert isinstance(week, list)


def test_weather_stub_without_key():
    info = weather_service.get_weather()
    assert info.city
    assert isinstance(info.temperature_f, float)
