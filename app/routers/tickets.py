from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import (
    STATUSES,
    TicketCreate,
    TicketCreateResponse,
    TicketDetail,
    TicketListItem,
    TicketUpdate,
    TicketUpdateResponse,
)

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post(
    "",
    response_model=TicketCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    try:
        ticket = crud.create_ticket(db, payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return ticket


@router.get("", response_model=list[TicketListItem])
def list_tickets(
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    if status_filter and status_filter not in STATUSES:
        raise HTTPException(
            status_code=422,
            detail="Status must be Open, In Progress, or Closed",
        )
    return crud.list_tickets(db, status_filter, search)


@router.get("/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}", response_model=TicketUpdateResponse)
def update_ticket(
    ticket_id: str,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
):
    if payload.status is None and payload.notes is None:
        raise HTTPException(
            status_code=422,
            detail="Provide a status or note to update the ticket",
        )

    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = crud.update_ticket(db, ticket, payload)
    return {"success": True, "updated_at": ticket.updated_at}
