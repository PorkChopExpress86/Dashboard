from datetime import datetime, date, time
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[str] = None
    is_all_day: bool = False


class RecurringEvent(BaseModel):
    id: Optional[int] = None
    title: str
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    timezone: str = "America/Chicago"
    location: Optional[str] = None
    category: Optional[str] = "recurring"
    start_date: Optional[date] = None  # When recurrence starts
    end_date: Optional[date] = None  # When recurrence ends (None = forever)


class Task(BaseModel):
    title: str
    due_date: date
    category: Optional[str] = None
    importance: Optional[str] = None  # low | med | high


class WeatherInfo(BaseModel):
    city: str
    description: str
    temperature_f: float
    high_f: float
    low_f: float
    icon: str | None = None
    hourly: list[dict] | None = None


class LunchMenuItem(BaseModel):
    name: str
    calories: str
    allergens: list[str] = []
