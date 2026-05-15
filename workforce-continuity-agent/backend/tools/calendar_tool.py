from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel


class CalendarEvent(BaseModel):
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    employee_id: str
    description: Optional[str] = None


# Mock calendar events
calendar_events: Dict[str, List[CalendarEvent]] = {}


def get_employee_calendar(employee_id: str, date: Optional[str] = None) -> List[CalendarEvent]:
    """Get employee's calendar events for a given date or today"""
    events = calendar_events.get(employee_id, [])
    if date:
        target_date = datetime.fromisoformat(date).date()
        return [e for e in events if e.start_time.date() == target_date]
    return events


def check_employee_availability(employee_id: str, hours_needed: int = 4) -> bool:
    """Check if employee has at least 'hours_needed' hours of free time today"""
    events = get_employee_calendar(employee_id)
    if not events:
        return True

    # Calculate total busy hours
    total_busy = sum(
        (e.end_time - e.start_time).total_seconds() / 3600
        for e in events
    )

    workday_hours = 8  # Assuming 8 hour workday
    return (workday_hours - total_busy) >= hours_needed


def get_available_slots(employee_id: str, date: Optional[str] = None) -> List[tuple]:
    """Get available time slots for an employee"""
    events = get_employee_calendar(employee_id, date)
    if not events:
        # Default 9 AM to 5 PM
        return [(9, 17)]

    # Sort events by start time
    sorted_events = sorted(events, key=lambda e: e.start_time)

    available_slots = []
    current_hour = 9

    for event in sorted_events:
        event_start_hour = event.start_time.hour
        if current_hour < event_start_hour:
            available_slots.append((current_hour, event_start_hour))
        current_hour = max(current_hour, event.end_time.hour)

    if current_hour < 17:
        available_slots.append((current_hour, 17))

    return available_slots


def add_calendar_event(event: CalendarEvent) -> CalendarEvent:
    if event.employee_id not in calendar_events:
        calendar_events[event.employee_id] = []
    calendar_events[event.employee_id].append(event)
    return event


def is_employee_busy(employee_id: str) -> bool:
    """Quick check if employee is currently in a meeting"""
    now = datetime.now()
    events = calendar_events.get(employee_id, [])
    for event in events:
        if event.start_time <= now <= event.end_time:
            return True
    return False


def initialize_calendar() -> None:
    """Initialize some mock calendar data"""
    # Create some busy slots for demo
    now = datetime.now()
    today = now.date()

    # Arjun has a meeting 10-11 AM
    calendar_events["EMP-002"] = [
        CalendarEvent(
            id="CAL-001",
            title="Team Standup",
            start_time=datetime.combine(today, datetime.min.time().replace(hour=10)),
            end_time=datetime.combine(today, datetime.min.time().replace(hour=11)),
            employee_id="EMP-002"
        )
    ]

    # Priya has meetings 2-4 PM
    calendar_events["EMP-003"] = [
        CalendarEvent(
            id="CAL-002",
            title="Design Review",
            start_time=datetime.combine(today, datetime.min.time().replace(hour=14)),
            end_time=datetime.combine(today, datetime.min.time().replace(hour=16)),
            employee_id="EMP-003"
        )
    ]