from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketLegResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    model_prediction_id: int | None = None
    match_id: int | None = None
    selection: str
    market: str
    odds: float
    bookmaker: str | None = None
    status: str = "pending"
    created_at: datetime


class BetPlacementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    bookmaker: str
    placed_at: datetime
    reference: str | None = None
    status: str = "pending"


class SettlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bet_placement_id: int | None = None
    ticket_id: int | None = None
    settled_at: datetime
    outcome: str
    return_amount: float
    pnl: float


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    bankroll_id: int | None = None
    batch_id: int | None = None
    ticket_type: str = "single"
    stake: float
    total_odds: float
    potential_return: float
    status: str = "open"
    created_at: datetime
    updated_at: datetime


class TicketDetailResponse(TicketResponse):
    legs: list[TicketLegResponse] = []
    placements: list[BetPlacementResponse] = []


class TicketBatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bankroll_id: int | None = None
    name: str | None = None
    strategy: str | None = None
    tickets_count: int = 0
    total_stake: float = 0.0
    created_at: datetime


class TicketCreateRequest(BaseModel):
    ticket_type: str = "single"
    stake: float = 10.0
    bankroll_id: int | None = None
    legs: list[dict] = []
