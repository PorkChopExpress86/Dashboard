from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[str] = None
    is_all_day: bool = False


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
