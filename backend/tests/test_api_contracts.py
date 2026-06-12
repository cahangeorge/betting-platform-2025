from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.deps import get_current_user
from app.api.v1 import data as data_api
from app.api.v1 import tickets as tickets_api
from app.schemas.data import ScrapeJobCreateRequest
from app.schemas.ticket import TicketCreateRequest


@pytest.mark.asyncio
async def test_get_current_user_requires_authentication_without_token():
    request = Request({"type": "http", "headers": []})

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request=request, db=object(), access_token=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"


@pytest.mark.asyncio
async def test_ticket_creation_maps_domain_validation_errors(monkeypatch):
    async def fake_create_ticket(**kwargs):
        raise ValueError("Insufficient bankroll balance")

    monkeypatch.setattr(tickets_api, "create_ticket", fake_create_ticket)

    with pytest.raises(HTTPException) as exc_info:
        await tickets_api.create_new_ticket(
            body=TicketCreateRequest(
                ticket_type="single",
                stake=10,
                bankroll_id=5,
                legs=[{"match_id": 1, "market": "1x2", "selection": "home", "odds": 2.0}],
            ),
            db=object(),
            user=SimpleNamespace(id=12),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Insufficient bankroll balance"


@pytest.mark.asyncio
async def test_ticket_creation_maps_domain_permission_errors(monkeypatch):
    async def fake_create_ticket(**kwargs):
        raise PermissionError("Bankroll 5 does not belong to the current user")

    monkeypatch.setattr(tickets_api, "create_ticket", fake_create_ticket)

    with pytest.raises(HTTPException) as exc_info:
        await tickets_api.create_new_ticket(
            body=TicketCreateRequest(
                ticket_type="single",
                stake=10,
                bankroll_id=5,
                legs=[{"match_id": 1, "market": "1x2", "selection": "home", "odds": 2.0}],
            ),
            db=object(),
            user=SimpleNamespace(id=12),
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Bankroll 5 does not belong to the current user"


@pytest.mark.asyncio
async def test_scrape_execute_maps_lookup_errors_to_404(monkeypatch):
    async def fake_execute_scrape_job(db, job_id):
        raise LookupError(f"ScrapeJob {job_id} not found")

    monkeypatch.setattr(data_api, "execute_scrape_job", fake_execute_scrape_job)

    with pytest.raises(HTTPException) as exc_info:
        await data_api.run_scrape_job(
            job_id=999,
            db=object(),
            user=SimpleNamespace(id=12),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "ScrapeJob 999 not found"


@pytest.mark.asyncio
async def test_scrape_start_returns_created_job(monkeypatch):
    fake_job = SimpleNamespace(
        id=44,
        job_type="oddsportal",
        status="pending",
        league="Premier League",
        params={"sport": "football"},
        started_at=None,
        completed_at=None,
        error=None,
        created_at=None,
    )

    async def fake_create_scrape_job(db, job_type, league, params):
        assert job_type == "oddsportal"
        assert league == "Premier League"
        assert params == {"sport": "football"}
        return fake_job

    monkeypatch.setattr(data_api, "create_scrape_job", fake_create_scrape_job)

    result = await data_api.start_scrape_job(
        body=ScrapeJobCreateRequest(job_type="oddsportal", league="Premier League", params={"sport": "football"}),
        db=object(),
        user=SimpleNamespace(id=12),
    )

    assert result is fake_job
