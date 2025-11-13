import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from app.models import Task


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_tasks.json"


def _parse_task(raw: dict) -> Task:
    return Task(
        title=raw["title"],
        due_date=date.fromisoformat(raw["due_date"]),
        category=raw.get("category"),
        importance=raw.get("importance"),
    )


def load_tasks() -> List[Task]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [_parse_task(item) for item in data]


def tasks_due_today(today: Optional[date] = None) -> List[Task]:
    d = today or date.today()
    return [t for t in load_tasks() if t.due_date == d]


def tasks_overdue(today: Optional[date] = None) -> List[Task]:
    d = today or date.today()
    return [t for t in load_tasks() if t.due_date < d]


def tasks_this_week(today: Optional[date] = None) -> List[Task]:
    d = today or date.today()
    end = d + timedelta(days=7)
    return [t for t in load_tasks() if d <= t.due_date <= end]
