from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScrapeJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_type: str
    status: str = "pending"
    league: str | None = None
    params: dict | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    created_at: datetime


class ScrapeJobCreateRequest(BaseModel):
    job_type: str
    league: str | None = None
    params: dict | None = None


class ScrapedDatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None = None
    source: str
    data: dict
    matches_count: int | None = None
    created_at: datetime
