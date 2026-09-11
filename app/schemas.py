from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


STATUSES = ("Open", "In Progress", "Closed")


class TicketCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=120)
    customer_email: EmailStr
    subject: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5, max_length=10000)

    @field_validator("customer_name", "subject", "description")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value


class TicketCreateResponse(BaseModel):
    ticket_id: str
    created_at: datetime


class TicketListItem(BaseModel):
    ticket_id: str
    customer_name: str
    subject: str
    status: str
    created_at: datetime


class NoteResponse(BaseModel):
    note_text: str
    created_at: datetime


class TicketDetail(BaseModel):
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    notes: list[NoteResponse]


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in STATUSES:
            raise ValueError("Status must be Open, In Progress, or Closed")
        return value

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            return value or None
        return value


class TicketUpdateResponse(BaseModel):
    success: bool
    updated_at: datetime
