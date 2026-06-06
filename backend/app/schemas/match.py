from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


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
    start_time: str | None = None
    league: str | None = None
    season: str | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def map_fields(cls, data):
        """Map ORM fields to API fields."""
        if hasattr(data, "match_date"):
            md = data.match_date
            data_dict = {}
            for k in ("id", "external_id", "home_team", "away_team", "home_score", "away_score", "status", "season", "created_at", "updated_at"):
                data_dict[k] = getattr(data, k, None)
            data_dict["start_time"] = md.isoformat() if md else None
            data_dict["league"] = getattr(data, "competition", None)
            return data_dict
        if isinstance(data, dict):
            if "match_date" in data and "start_time" not in data:
                md = data.pop("match_date")
                data["start_time"] = md.isoformat() if md else None
            if "competition" in data and "league" not in data:
                data["league"] = data.pop("competition")
            return data
        return data


class MatchDetailResponse(MatchResponse):
    odds: list[OddsEntryResponse] = []
    stats: list[MatchStatResponse] = []
    sources: list[MatchSourceResponse] = []


class MatchListResponse(BaseModel):
    matches: list[MatchResponse]
    total: int
    page: int = 1
    per_page: int = 50
