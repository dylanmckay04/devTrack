from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ReminderCreate(BaseModel):
    application_id: Optional[int] = None
    message: str
    remind_at: datetime


class ReminderOut(BaseModel):
    id: int
    owner_id: int
    application_id: Optional[int]
    message: str
    remind_at: datetime
    sent: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)