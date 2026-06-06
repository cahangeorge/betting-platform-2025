from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.catalog import CountryInfo, LeagueInfo

router = APIRouter()

CATALOG: list[CountryInfo] = [
    CountryInfo(
        country="Italy",
        leagues=[
            LeagueInfo(id="serie_a", name="Serie A", matches_count=380),
            LeagueInfo(id="serie_b", name="Serie B", matches_count=380),
        ],
    ),
    CountryInfo(
        country="England",
        leagues=[
            LeagueInfo(id="premier_league", name="Premier League", matches_count=380),
            LeagueInfo(id="championship", name="Championship", matches_count=552),
        ],
    ),
    CountryInfo(
        country="Spain",
        leagues=[
            LeagueInfo(id="la_liga", name="La Liga", matches_count=380),
        ],
    ),
    CountryInfo(
        country="Germany",
        leagues=[
            LeagueInfo(id="bundesliga", name="Bundesliga", matches_count=306),
        ],
    ),
    CountryInfo(
        country="France",
        leagues=[
            LeagueInfo(id="ligue_1", name="Ligue 1", matches_count=380),
        ],
    ),
    CountryInfo(
        country="Netherlands",
        leagues=[
            LeagueInfo(id="eredivisie", name="Eredivisie", matches_count=306),
        ],
    ),
    CountryInfo(
        country="Portugal",
        leagues=[
            LeagueInfo(id="primeira_liga", name="Primeira Liga", matches_count=306),
        ],
    ),
    CountryInfo(
        country="Turkey",
        leagues=[
            LeagueInfo(id="super_lig", name="Süper Lig", matches_count=380),
        ],
    ),
    CountryInfo(
        country="Greece",
        leagues=[
            LeagueInfo(id="super_league", name="Super League", matches_count=240),
        ],
    ),
    CountryInfo(
        country="Belgium",
        leagues=[
            LeagueInfo(id="pro_league", name="Pro League", matches_count=340),
        ],
    ),
]


@router.get("/countries", response_model=list[CountryInfo])
async def list_countries(
    _user: User = Depends(get_current_user),
):
    return CATALOG


@router.get("/leagues", response_model=list[LeagueInfo])
async def list_leagues(
    country: str | None = Query(None),
    _user: User = Depends(get_current_user),
):
    if country:
        for c in CATALOG:
            if c.country.lower() == country.lower():
                return c.leagues
        return []
    all_leagues = []
    for c in CATALOG:
        all_leagues.extend(c.leagues)
    return all_leagues


@router.get("/leagues/all", response_model=list[CountryInfo])
async def list_all_leagues(
    _user: User = Depends(get_current_user),
):
    return CATALOG
