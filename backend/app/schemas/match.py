from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OddsEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    bookmaker: str
    market: str
    home_odds: float | None = None
    draw_odds: float | None = None
    away_odds: float | None = None
    timestamp: datetime | None = None
    created_at: datetime


class MatchStatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    source: str
    home_xg: float | None = None
    away_xg: float | None = None
    possession_home: float | None = None
    possession_away: float | None = None
    shots_home: int | None = None
    shots_away: int | None = None
    json_data: dict | None = None
    created_at: datetime


class MatchSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    source: str
    source_id: str | None = None
    url: str | None = None
    created_at: datetime


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str | None = None
    home_team: str
    away_team: str
    home_score: int | None = None
    away_score: int | None = None
    status: str = "scheduled"
    match_date: datetime | None = None
    competition: str | None = None
    season: str | None = None
    created_at: datetime
    updated_at: datetime


class MatchDetailResponse(MatchResponse):
    odds: list[OddsEntryResponse] = []
    stats: list[MatchStatResponse] = []
    sources: list[MatchSourceResponse] = []


class MatchListResponse(BaseModel):
    matches: list[MatchResponse]
    total: int
    page: int = 1
    per_page: int = 50
