import json
import asyncio
from datetime import datetime, timedelta, time
from pathlib import Path
from typing import List, Optional

import httpx
from zoneinfo import ZoneInfo
from ics import Calendar

from app.config import get_settings
from app.models import Event

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_events.json"

_CACHE: List[Event] = []
_LAST_REFRESH: datetime | None = None
_REFRESH_TASK: asyncio.Task | None = None
_CACHE_LOADED_FROM_DISK: bool = False


def get_tzinfo(tz_name: Optional[str] = None) -> ZoneInfo:
    settings = get_settings()
    return ZoneInfo(tz_name or settings.timezone)


def _parse_local_event(raw: dict) -> Event:
    start = datetime.fromisoformat(raw["start"]).replace(tzinfo=get_tzinfo())
    end_val = raw.get("end")
    end = None
    if end_val:
        end = datetime.fromisoformat(end_val).replace(tzinfo=get_tzinfo())
    return Event(
        title=raw["title"],
        start=start,
        end=end,
        location=raw.get("location"),
        category=raw.get("category"),
    )


def _load_local_events() -> List[Event]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [_parse_local_event(item) for item in data]


def _fetch_google_ics(url: str) -> List[Event]:
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
            cal = Calendar(resp.text)
    except Exception:
        return []
    tz = get_tzinfo()
    events: List[Event] = []
    for e in cal.events:
        try:
            start_dt = e.begin.datetime
            end_dt = e.end.datetime if e.end else None
            
            # Check if this is an all-day event (date-only, no time component)
            is_all_day = not hasattr(e.begin, 'hour') or (hasattr(e.begin, 'datetime') and e.begin.datetime.time() == time.min)
            
            if is_all_day:
                # For all-day events, use the date at midnight in local timezone
                start_date = e.begin.date() if hasattr(e.begin, 'date') else e.begin.datetime.date()
                start_dt = datetime.combine(start_date, time.min, tzinfo=tz)
                if end_dt:
                    end_date = e.end.date() if hasattr(e.end, 'date') else e.end.datetime.date()
                    end_dt = datetime.combine(end_date, time.min, tzinfo=tz)
            else:
                # For timed events, convert timezone properly
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=tz)
                else:
                    start_dt = start_dt.astimezone(tz)
                if end_dt:
                    if end_dt.tzinfo is None:
                        end_dt = end_dt.replace(tzinfo=tz)
                    else:
                        end_dt = end_dt.astimezone(tz)
            events.append(
                Event(
                    title=e.name or "Untitled",
                    start=start_dt,
                    end=end_dt,
                    location=e.location,
                    category="google",
                    is_all_day=is_all_day,
                )
            )
        except Exception:
            continue
    return events


def _parse_sources_json(raw: str) -> list[tuple[str | None, str]]:
    try:
        obj = json.loads(raw)
        if isinstance(obj, list):
            return [(None, u) for u in obj if isinstance(u, str)]
        if isinstance(obj, dict):
            return [(k, v) for k, v in obj.items() if isinstance(v, str)]
    except Exception:
        return []
    return []


def _fetch_multi_ics(urls: list[tuple[str | None, str]]) -> List[Event]:
    all_events: List[Event] = []
    for name, url in urls:
        evts = _fetch_google_ics(url)
        if name:
            for e in evts:
                e.category = name
        all_events.extend(evts)
    return all_events


def _cache_file() -> Path:
    settings = get_settings()
    p = Path(settings.calendar_cache_dir).expanduser()
    try:
        p.mkdir(parents=True, exist_ok=True)
    except Exception:
        # fallback to local cache folder next to data
        p = Path(__file__).resolve().parent.parent / "data" / "cache"
        p.mkdir(parents=True, exist_ok=True)
    return p / "events_cache.json"


def _serialize_events(events: List[Event]) -> list[dict]:
    out: list[dict] = []
    for e in events:
        out.append(
            {
                "title": e.title,
                "start": e.start.isoformat(),
                "end": e.end.isoformat() if e.end else None,
                "location": e.location,
                "category": e.category,
            }
        )
    return out


def _deserialize_events(items: list[dict]) -> List[Event]:
    evts: List[Event] = []
    for raw in items:
        try:
            start = datetime.fromisoformat(raw["start"])  # should include tz
            end_raw = raw.get("end")
            end = datetime.fromisoformat(end_raw) if end_raw else None
            evts.append(
                Event(
                    title=raw.get("title", "Untitled"),
                    start=start,
                    end=end,
                    location=raw.get("location"),
                    category=raw.get("category"),
                )
            )
        except Exception:
            continue
    return evts


def _should_refresh(now: datetime, interval_minutes: int) -> bool:
    if _LAST_REFRESH is None:
        return True
    return (now - _LAST_REFRESH) >= timedelta(minutes=interval_minutes)


def refresh_events(force: bool = False) -> None:
    settings = get_settings()
    now = datetime.now(get_tzinfo())
    if not force and not _should_refresh(now, settings.calendar_refresh_minutes):
        return
    source = settings.calendar_source
    print(f"[Calendar] Refreshing from source: {source}")
    events: List[Event]
    if source == "google_ics":
        urls: list[tuple[str | None, str]] = []
        if settings.calendar_ical_sources:
            print(f"[Calendar] Parsing CALENDAR_ICAL_SOURCES: {settings.calendar_ical_sources[:100]}...")
            urls.extend(_parse_sources_json(settings.calendar_ical_sources))
        if settings.google_calendar_ical_url:
            print(f"[Calendar] Adding GOOGLE_CALENDAR_ICAL_URL")
            urls.append((None, settings.google_calendar_ical_url))
        print(f"[Calendar] Fetching from {len(urls)} ICS source(s)")
        if urls:
            events = _fetch_multi_ics(urls)
            print(f"[Calendar] Fetched {len(events)} events from ICS")
        else:
            events = []
        if not events:
            # fallback to local if google empty
            print(f"[Calendar] No ICS events, falling back to local JSON")
            events = _load_local_events()
    else:
        events = _load_local_events()
    global _CACHE, _LAST_REFRESH
    _CACHE = sorted(events, key=lambda e: e.start)
    _LAST_REFRESH = now
    # persist to disk
    try:
        cache_file = _cache_file()
        cache_file.write_text(json.dumps(_serialize_events(_CACHE)), encoding="utf-8")
    except Exception:
        pass


def get_events() -> List[Event]:
    global _CACHE, _CACHE_LOADED_FROM_DISK
    if not _CACHE and not _CACHE_LOADED_FROM_DISK:
        # try load from disk cache first
        try:
            cache_file = _cache_file()
            if cache_file.exists():
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                _CACHE = sorted(_deserialize_events(data), key=lambda e: e.start)
                _CACHE_LOADED_FROM_DISK = True
        except Exception:
            _CACHE_LOADED_FROM_DISK = True
    refresh_events()
    return _CACHE


def _now(now: Optional[datetime] = None) -> datetime:
    return now or datetime.now(get_tzinfo())


def events_today(now: Optional[datetime] = None) -> List[Event]:
    cur = _now(now)
    start_day = datetime.combine(cur.date(), time.min, tzinfo=cur.tzinfo)
    end_day = datetime.combine(cur.date(), time.max, tzinfo=cur.tzinfo)
    return [e for e in get_events() if start_day <= e.start <= end_day]


def events_tomorrow(now: Optional[datetime] = None) -> List[Event]:
    cur = _now(now)
    tomorrow = cur.date() + timedelta(days=1)
    start_tomorrow = datetime.combine(tomorrow, time.min, tzinfo=cur.tzinfo)
    end_tomorrow = datetime.combine(tomorrow, time.max, tzinfo=cur.tzinfo)
    return [e for e in get_events() if start_tomorrow <= e.start <= end_tomorrow]


def events_this_week(now: Optional[datetime] = None) -> List[Event]:
    cur = _now(now)
    end = cur + timedelta(days=7)
    return [e for e in get_events() if cur <= e.start <= end]


async def _background_refresh():
    while True:
        try:
            refresh_events(force=True)
        except Exception:
            pass
        interval = max(5, get_settings().calendar_refresh_minutes)
        await asyncio.sleep(interval * 60)


def start_background_refresh():
    global _REFRESH_TASK
    if _REFRESH_TASK is None:
        _REFRESH_TASK = asyncio.create_task(_background_refresh())
