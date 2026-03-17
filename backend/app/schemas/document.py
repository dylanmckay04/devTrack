from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentOut(BaseModel):
    id: int
    owner_id: int
    application_id: Optional[int]
    filename: str
    r2_key: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
