"""
"""
from datetime import timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import HTMLResponse

from helper import *
from models import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def template(name, request, **kwargs):
    return templates.TemplateResponse(name, {
        'request': request,
        **kwargs
    })


# ####################### User pages ####################### #

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return template('home.html', request, title="Récupération des pulls MA")


# ####################### API ####################### #

@app.get("/api")
def get_all_slots():
    """Get all the time slots."""
    return list(map(TimeSlotDB.to_out, load_data().values()))


@app.get("/api/slot/{id}", response_model=TimeSlotOut)
def get_time_slot(id: int):
    slots = load_data()
    if id not in slots:
        return HTTPException(404, "Time slot not found")
    return slots[id].to_out()


@app.delete("/api/slot/{id}")
def delete_slot(id: int):
    """Delete an existing time slot."""
    slots = load_data()
    if id not in slots:
        return HTTPException(404, "Time slot not found")

    del slots[id]
    save_data(slots)

@app.put('/api/slot/{id}')
def book_slot(id: int, email: str):
    email = email.lower()
    commands = load_commandes()
    if email.lower() not in commands:
        return HTTPException(status.HTTP_403_FORBIDDEN, "Email is invalid")
    slots = load_data()
    if id not in load_data():
        return HTTPException(status.HTTP_404_NOT_FOUND, "Time slot not found")
    slot = slots[id]
    if len(slot.attendes) >= slot.capacity:
        return HTTPException(status.HTTP_403_FORBIDDEN, "All places are already booked for this slot")

    # Add to the current
    slot.attendes.add(email)
    # Remove reservation for the old slot, if any
    for old_slot in slots.values():
        if email in old_slot.attendes and old_slot is not slot:
            old_slot.attendes.remove(email)
            old_slot = old_slot.to_out()
            break
    else:
        old_slot = None

    save_data(slots)

    return {
        'current': slot.to_out(),
        'previous': old_slot,
    }



@app.put("/api/range")
def create_slot_range(slot_range: SlotRange):
    """Add a renge of slot to book. Doesn't check there are no collisions."""
    slots = load_data()

    delta = slot_range.end - slot_range.start
    days = delta.days
    slots_per_day = delta.seconds // 60 // slot_range.duration
    for doffset in range(days + 1):
        day = slot_range.start + timedelta(days=doffset)
        for moffset in range(slots_per_day + 1):
            start = day + timedelta(minutes=moffset * slot_range.duration)

            id = new_id(slots)
            slots[id] = TimeSlotDB(start=start,
                                   capacity=slot_range.capacity,
                                   attendes=[],
                                   id=id)

    save_data(slots)

    return { 'created': (days + 1) * (slots_per_day + 1)}

@app.get("/api/exists")
def check_command_exists(email: str):
    """Check wether a command exists foor the given email."""
    return email.lower() in load_commandes()

@app.get("/api/booked")
def find_book_time(email: str) -> Optional[int]:
    """Get the ID of the time slot reserved by an email."""
    email = email.lower()
    commandes = load_commandes()
    if email not in commandes:
        return None
    for slot in load_data().values():
        if email in slot.attendes:
            return slot.id
    return None

