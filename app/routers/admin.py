from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import time as dt_time, date as dt_date
from typing import Optional

from app.services import recurring_events_service
from app.models import RecurringEvent

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

DAYS_OF_WEEK = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin panel homepage"""
    recurring_events = recurring_events_service.load_recurring_events()
    
    # Add day_name to each event for display
    events_with_day_names = []
    for event in recurring_events:
        event_dict = event.model_dump()
        event_dict['day_name'] = DAYS_OF_WEEK[event.day_of_week][1]
        events_with_day_names.append(event_dict)
    
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "recurring_events": events_with_day_names}
    )


@router.get("/admin/recurring-events/new", response_class=HTMLResponse)
async def new_recurring_event_form(request: Request):
    """Show form to create new recurring event"""
    return templates.TemplateResponse(
        "admin_recurring_form.html",
        {
            "request": request,
            "event": None,
            "days_of_week": DAYS_OF_WEEK,
            "action": "Create"
        }
    )


@router.post("/admin/recurring-events/new")
async def create_recurring_event(
    request: Request,
    title: str = Form(...),
    day_of_week: int = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    timezone: str = Form("America/Chicago"),
    location: Optional[str] = Form(None),
    category: Optional[str] = Form("recurring"),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
):
    """Create a new recurring event"""
    # Parse times
    start_time_obj = dt_time.fromisoformat(start_time)
    end_time_obj = dt_time.fromisoformat(end_time)
    
    # Parse dates
    start_date_obj = dt_date.fromisoformat(start_date) if start_date else None
    end_date_obj = dt_date.fromisoformat(end_date) if end_date else None
    
    event = RecurringEvent(
        title=title,
        day_of_week=day_of_week,
        start_time=start_time_obj,
        end_time=end_time_obj,
        timezone=timezone,
        location=location or None,
        category=category or "recurring",
        start_date=start_date_obj,
        end_date=end_date_obj,
    )
    
    recurring_events_service.add_recurring_event(event)
    
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/admin/recurring-events/{event_id}/edit", response_class=HTMLResponse)
async def edit_recurring_event_form(request: Request, event_id: int):
    """Show form to edit recurring event"""
    event = recurring_events_service.get_recurring_event(event_id)
    if not event:
        return RedirectResponse(url="/admin", status_code=303)
    
    return templates.TemplateResponse(
        "admin_recurring_form.html",
        {
            "request": request,
            "event": event,
            "days_of_week": DAYS_OF_WEEK,
            "action": "Update"
        }
    )


@router.post("/admin/recurring-events/{event_id}/edit")
async def update_recurring_event(
    request: Request,
    event_id: int,
    title: str = Form(...),
    day_of_week: int = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    timezone: str = Form("America/Chicago"),
    location: Optional[str] = Form(None),
    category: Optional[str] = Form("recurring"),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
):
    """Update an existing recurring event"""
    # Parse times
    start_time_obj = dt_time.fromisoformat(start_time)
    end_time_obj = dt_time.fromisoformat(end_time)
    
    # Parse dates
    start_date_obj = dt_date.fromisoformat(start_date) if start_date else None
    end_date_obj = dt_date.fromisoformat(end_date) if end_date else None
    
    event = RecurringEvent(
        id=event_id,
        title=title,
        day_of_week=day_of_week,
        start_time=start_time_obj,
        end_time=end_time_obj,
        timezone=timezone,
        location=location or None,
        category=category or "recurring",
        start_date=start_date_obj,
        end_date=end_date_obj,
    )
    
    recurring_events_service.update_recurring_event(event_id, event)
    
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/recurring-events/{event_id}/delete")
async def delete_recurring_event(event_id: int):
    """Delete a recurring event"""
    recurring_events_service.delete_recurring_event(event_id)
    return RedirectResponse(url="/admin", status_code=303)
