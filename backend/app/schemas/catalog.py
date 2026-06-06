from pydantic import BaseModel


class LeagueInfo(BaseModel):
    id: str
    name: str
    matches_count: int = 0


class CountryInfo(BaseModel):
    country: str
    leagues: list[LeagueInfo] = []
