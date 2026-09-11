from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Note, Ticket


def utc_now():
    return datetime.now(timezone.utc)


def next_ticket_id(db: Session) -> str:
    latest = db.query(Ticket).order_by(Ticket.id.desc()).first()
    next_number = (latest.id + 1) if latest else 1
    return f"TKT-{next_number:03d}"


def create_ticket(db: Session, data):
    for _ in range(3):
        ticket = Ticket(ticket_id=next_ticket_id(db), **data.model_dump())
        db.add(ticket)
        try:
            db.commit()
            db.refresh(ticket)
            return ticket
        except IntegrityError:
            db.rollback()

    raise RuntimeError("Unable to generate a unique ticket ID")


def list_tickets(db: Session, status=None, search=None):
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Ticket.customer_name.ilike(term),
                Ticket.ticket_id.ilike(term),
                Ticket.customer_email.ilike(term),
                Ticket.description.ilike(term),
            )
        )

    return query.order_by(Ticket.created_at.desc()).all()


def get_ticket(db: Session, ticket_id: str):
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


def update_ticket(db: Session, ticket: Ticket, data):
    if data.status is not None:
        ticket.status = data.status

    if data.notes:
        db.add(Note(ticket_id=ticket.ticket_id, note_text=data.notes))

    ticket.updated_at = utc_now()
    db.commit()
    db.refresh(ticket)
    return ticket


def ticket_counts(db: Session):
    rows = (
        db.query(Ticket.status, func.count(Ticket.id))
        .group_by(Ticket.status)
        .all()
    )
    counts = {"Open": 0, "In Progress": 0, "Closed": 0}
    for status, count in rows:
        counts[status] = count
    return counts
