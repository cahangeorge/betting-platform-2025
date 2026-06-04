from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.ticket import BetPlacement, Settlement, Ticket, TicketBatch, TicketLeg
from app.models.user import User
from app.schemas.ticket import (
    BetPlacementResponse,
    SettlementResponse,
    TicketBatchResponse,
    TicketCreateRequest,
    TicketDetailResponse,
    TicketLegResponse,
    TicketResponse,
)
from app.services.ticket_engine import create_ticket, place_bet, settle_ticket

router = APIRouter()


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Ticket).where(Ticket.user_id == user.id)
    if status:
        stmt = stmt.where(Ticket.status == status)
    stmt = stmt.order_by(Ticket.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=TicketResponse, status_code=201)
async def create_new_ticket(
    body: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticket = await create_ticket(
        db=db,
        user_id=user.id,
        ticket_type=body.ticket_type,
        stake=body.stake,
        bankroll_id=body.bankroll_id,
        legs_data=body.legs,
    )
    return ticket


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.legs), selectinload(Ticket.placements))
        .where(Ticket.id == ticket_id, Ticket.user_id == user.id)
    )
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("/{ticket_id}/place", response_model=BetPlacementResponse)
async def place_ticket(
    ticket_id: int,
    bookmaker: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == user.id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    placement = await place_bet(db, ticket_id, bookmaker)
    return placement


@router.post("/{ticket_id}/settle", response_model=SettlementResponse)
async def settle_ticket_endpoint(
    ticket_id: int,
    outcome: str,
    return_amount: float = 0.0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == user.id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    result_data = await settle_ticket(db, ticket_id, outcome, return_amount)
    return result_data


@router.get("/batches", response_model=list[TicketBatchResponse])
async def list_batches(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(TicketBatch).order_by(TicketBatch.created_at.desc()).limit(50)
    result = await db.execute(stmt)
    return result.scalars().all()
