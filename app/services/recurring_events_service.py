import json
from datetime import datetime, date, timedelta, time as dt_time
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo

from app.models import Event, RecurringEvent

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "recurring_events.json"


def _ensure_data_file():
    """Ensure the recurring events data file exists"""
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("[]")


def load_recurring_events() -> List[RecurringEvent]:
    """Load all recurring events from JSON file"""
    _ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [RecurringEvent(**item) for item in data]
    except Exception:
        return []


def save_recurring_events(events: List[RecurringEvent]) -> None:
    """Save recurring events to JSON file"""
    _ensure_data_file()
    data = []
    for event in events:
        item = event.model_dump()
        # Convert date/time objects to strings for JSON
        if item.get("start_time"):
            item["start_time"] = item["start_time"].isoformat()
        if item.get("end_time"):
            item["end_time"] = item["end_time"].isoformat()
        if item.get("start_date"):
            item["start_date"] = item["start_date"].isoformat() if item["start_date"] else None
        if item.get("end_date"):
            item["end_date"] = item["end_date"].isoformat() if item["end_date"] else None
        data.append(item)
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_recurring_event(event_id: int) -> Optional[RecurringEvent]:
    """Get a specific recurring event by ID"""
    events = load_recurring_events()
    for event in events:
        if event.id == event_id:
            return event
    return None


def add_recurring_event(event: RecurringEvent) -> RecurringEvent:
    """Add a new recurring event"""
    events = load_recurring_events()
    # Assign new ID
    max_id = max([e.id for e in events if e.id], default=0)
    event.id = max_id + 1
    events.append(event)
    save_recurring_events(events)
    return event


def update_recurring_event(event_id: int, updated_event: RecurringEvent) -> bool:
    """Update an existing recurring event"""
    events = load_recurring_events()
    for i, event in enumerate(events):
        if event.id == event_id:
            updated_event.id = event_id
            events[i] = updated_event
            save_recurring_events(events)
            return True
    return False


def delete_recurring_event(event_id: int) -> bool:
    """Delete a recurring event"""
    events = load_recurring_events()
    filtered = [e for e in events if e.id != event_id]
    if len(filtered) < len(events):
        save_recurring_events(filtered)
        return True
    return False


def generate_instances(recurring_event: RecurringEvent, start_date: date, end_date: date) -> List[Event]:
    """
    Generate Event instances for a recurring event within a date range
    
    Args:
        recurring_event: The recurring event definition
        start_date: Start of the date range
        end_date: End of the date range
    
    Returns:
        List of Event instances
    """
    instances = []
    tz = ZoneInfo(recurring_event.timezone)
    
    # Determine the effective start date
    effective_start = recurring_event.start_date or start_date
    if effective_start < start_date:
        effective_start = start_date
    
    # Determine the effective end date
    effective_end = recurring_event.end_date or end_date
    if effective_end > end_date:
        effective_end = end_date
    
    # Find the first occurrence on or after effective_start
    current = effective_start
    # Move to the target day of week
    while current.weekday() != recurring_event.day_of_week:
        current += timedelta(days=1)
        if current > effective_end:
            return instances
    
    # Generate instances weekly
    while current <= effective_end:
        start_dt = datetime.combine(current, recurring_event.start_time, tzinfo=tz)
        end_dt = datetime.combine(current, recurring_event.end_time, tzinfo=tz)
        
        instances.append(Event(
            title=recurring_event.title,
            start=start_dt,
            end=end_dt,
            location=recurring_event.location,
            category=recurring_event.category,
            is_all_day=False
        ))
        
        current += timedelta(days=7)
    
    return instances


def get_recurring_instances_for_range(start_date: date, end_date: date) -> List[Event]:
    """Get all instances of recurring events within a date range"""
    recurring_events = load_recurring_events()
    all_instances = []
    
    for recurring_event in recurring_events:
        instances = generate_instances(recurring_event, start_date, end_date)
        all_instances.extend(instances)
    
    return sorted(all_instances, key=lambda e: e.start)
