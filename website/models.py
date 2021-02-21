from datetime import datetime
from typing import List, Set

from pydantic import BaseModel


class TimeSlotIn(BaseModel):
    start: datetime
    capacity: int


class TimeSlotDB(BaseModel):
    start: datetime
    capacity: int
    attendes: Set[str]
    id: int

    def to_out(self):
        as_dict = self.dict()
        as_dict['attending'] = len(self.attendes)
        del as_dict['attendes']
        return TimeSlotOut(**as_dict)


class TimeSlotOut(BaseModel):
    start: datetime
    capacity: int
    attending: int
    id: int


class SlotRange(BaseModel):
    """Represent a rectangle of slots"""
    start: datetime
    end: datetime
    capacity: int
    duration: int = 5


class CommandeDB(BaseModel):
    color: str
    size: str
    name: str
    surname: str
