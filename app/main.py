from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers.dashboard import router as dashboard_router
from app.routers.api import router as api_router
from app.services import calendar_service, weather_service
import logging


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="HomeBrain Dashboard", version="0.1.0")

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.include_router(dashboard_router)
    app.include_router(api_router, prefix="/api", tags=["api"])

    @app.on_event("startup")
    async def _startup_refresh():
        # Kick off background refresh of calendar events (Google ICS if configured)
        try:
            calendar_service.start_background_refresh()
        except Exception:
            pass
        # Kick off background refresh of weather (single-city local dashboard)
        try:
            weather_service.start_background_refresh()
        except Exception:
            pass
        # Log that background refreshers have been requested to start
        try:
            settings = get_settings()
            logging.getLogger(__name__).info("Background refreshers started: calendar every %s minutes, weather every %s minutes", settings.calendar_refresh_minutes, settings.weather_refresh_minutes)
        except Exception:
            pass

    @app.on_event("shutdown")
    async def _shutdown_cleanup():
        # Attempt to gracefully stop background tasks
        try:
            await weather_service.stop_background_refresh_async()
        except Exception:
            pass

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
