import httpx
import logging
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.models import WeatherInfo
from app.config import get_settings

logger = logging.getLogger(__name__)

_CACHE: dict[str, WeatherInfo] = {}
_FAILED: set[str] = set()
_LAST_REFRESH: datetime | None = None
_REFRESH_TASK: asyncio.Task | None = None


def _fetch_openweather(city: str, api_key: str) -> WeatherInfo | None:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "imperial"}
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get(url, params=params)
            if resp.status_code != 200:
                # log non-200 responses for debugging (include body when available)
                text = resp.text if resp is not None else ''
                logger.warning("OpenWeather current weather fetch failed for %s: %s %s", city, resp.status_code, text)
                return None
            data = resp.json()
    except Exception as exc:
        logger.exception("Exception fetching OpenWeather current weather for %s: %s", city, exc)
        return None

    try:
        description = data["weather"][0]["description"].title()
        temperature = float(data["main"]["temp"])
        temp_min = float(data["main"]["temp_min"])
        temp_max = float(data["main"]["temp_max"])
        # Map a simple icon name (Bootstrap Icons) based on conditions
        cond = data["weather"][0]["main"].lower()
        icon = "bi-cloud"
        if "rain" in cond:
            icon = "bi-cloud-rain"
        elif "clear" in cond:
            icon = "bi-sun"
        elif "snow" in cond:
            icon = "bi-cloud-snow"
        elif "storm" in cond or "thunder" in cond:
            icon = "bi-cloud-lightning"
        elif "fog" in cond or "mist" in cond:
            icon = "bi-cloud-fog"
        return WeatherInfo(
            city=city,
            description=description,
            temperature_f=temperature,
            high_f=temp_max,
            low_f=temp_min,
            icon=icon,
            hourly=None,
        )
    except Exception as exc:
        logger.exception("Exception parsing OpenWeather current weather data for %s: %s", city, exc)
        return None


def get_weather_stub(city: str) -> WeatherInfo:
    # build a simple hourly stub for the next 12 hours
    now = datetime.now()
    hourly = []
    for i in range(12):
        t = (now.replace(minute=0, second=0, microsecond=0) + 
             __import__('datetime').timedelta(hours=i))
        hourly.append({
            "time": t.strftime('%I %p').lstrip('0'),
            "temp": 72 + (i % 3),
            "pop": 0.0,
            "icon": "bi-cloud-sun",
        })
    return WeatherInfo(
        city=city,
        description="Partly Cloudy",
        temperature_f=72.0,
        high_f=75.0,
        low_f=58.0,
        icon="bi-cloud-sun",
        hourly=hourly,
    )


def get_weather(city: str | None = None) -> WeatherInfo:
    settings = get_settings()
    c = city or settings.location_city or "Your City"
    api_key = settings.weather_api_key

    # Return cached successful value quickly
    if c in _CACHE:
        return _CACHE[c]

    # Avoid hammering API if it failed previously in this run
    if c in _FAILED or not api_key:
        if not api_key:
            logger.info("No WEATHER_API_KEY set; using stub weather for %s", c)
        else:
            logger.info("Using stub weather for %s (previous failure recorded)", c)
        info = get_weather_stub(c)
        _CACHE.setdefault(c, info)  # Cache stub for consistency
        return info

    live = _fetch_openweather(c, api_key)
    if live is None:
        logger.warning("Current weather fetch failed for %s; falling back to stub", c)
        _FAILED.add(c)
        stub = get_weather_stub(c)
        _CACHE[c] = stub
        return stub

    # Attempt to fetch hourly forecast using One Call 3.0 (requires lat/lon)
    settings = get_settings()
    lat = settings.weather_lat
    lon = settings.weather_lon
    if lat is not None and lon is not None:
        try:
            url = "https://api.openweathermap.org/data/3.0/onecall"
            params = {
                "lat": lat,
                "lon": lon,
                "exclude": "minutely,daily,alerts",
                "units": "imperial",
                "appid": api_key,
            }
            with httpx.Client(timeout=5) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 200:
                    odata = resp.json()
                    hourly = []
                    for h in odata.get("hourly", [])[:12]:
                        ts = int(h.get("dt", 0))
                        temp = float(h.get("temp", 0.0))
                        pop = float(h.get("pop", 0.0))
                        w = h.get("weather", [{}])[0].get("main", "").lower()
                        icon = "bi-cloud"
                        if "rain" in w:
                            icon = "bi-cloud-rain"
                        elif "clear" in w:
                            icon = "bi-sun"
                        elif "snow" in w:
                            icon = "bi-cloud-snow"
                        elif "storm" in w or "thunder" in w:
                            icon = "bi-cloud-lightning"
                        elif "fog" in w or "mist" in w:
                            icon = "bi-cloud-fog"
                        # Convert UTC timestamp to local timezone
                        settings = get_settings()
                        local_tz = ZoneInfo(settings.timezone)
                        local_time = datetime.fromtimestamp(ts, tz=local_tz)
                        time_str = local_time.strftime('%I %p').lstrip('0')
                        hourly.append({
                            "time": time_str,
                            "temp": temp,
                            "pop": pop,
                            "icon": icon,
                        })
                    live.hourly = hourly
                    logger.info("OpenWeather One Call fetched %d hourly entries for %s", len(hourly), c)
                else:
                    logger.warning("OpenWeather One Call fetch failed for %s (%s,%s): %s %s", c, lat, lon, resp.status_code, resp.text)
                    live.hourly = None
        except Exception as exc:
            logger.exception("Exception fetching OpenWeather One Call for %s (%s,%s): %s", c, lat, lon, exc)
            # if hourly fetch fails, just leave hourly as None
            live.hourly = None

    _CACHE[c] = live
    global _LAST_REFRESH
    _LAST_REFRESH = datetime.now()
    return live


def _should_refresh_weather() -> bool:
    """Check if weather cache should be refreshed based on time interval."""
    settings = get_settings()
    if _LAST_REFRESH is None:
        return True
    elapsed = datetime.now() - _LAST_REFRESH
    return elapsed >= timedelta(minutes=settings.weather_refresh_minutes)


def clear_weather_cache():
    """Clear weather cache to force a refresh on next request."""
    global _CACHE, _LAST_REFRESH
    _CACHE.clear()
    _LAST_REFRESH = None
    logger.info("Weather cache cleared")


async def _background_refresh_weather():
    """Background task to periodically refresh weather data."""
    while True:
        try:
            settings = get_settings()
            interval = max(5, settings.weather_refresh_minutes)
            await asyncio.sleep(interval * 60)
            logger.info("Background weather refresh triggered")
            clear_weather_cache()
        except Exception as exc:
            logger.exception("Exception in background weather refresh: %s", exc)


def start_background_refresh():
    """Start the background weather refresh task."""
    global _REFRESH_TASK
    if _REFRESH_TASK is None:
        _REFRESH_TASK = asyncio.create_task(_background_refresh_weather())
        logger.info("Weather background refresh task started")

