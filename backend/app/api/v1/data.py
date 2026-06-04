from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.scrape import ScrapeJob, ScrapedDataset
from app.models.user import User
from app.schemas.data import ScrapeJobCreateRequest, ScrapeJobResponse, ScrapedDatasetResponse
from app.services.scraper import create_scrape_job, execute_scrape_job

router = APIRouter()


@router.post("/scrape", response_model=ScrapeJobResponse, status_code=201)
async def start_scrape_job(
    body: ScrapeJobCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = await create_scrape_job(db, body.job_type, body.league, body.params)
    return job


@router.post("/scrape/{job_id}/execute", response_model=ScrapeJobResponse)
async def run_scrape_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = await execute_scrape_job(db, job_id)
    return job


@router.get("/scrape", response_model=list[ScrapeJobResponse])
async def list_scrape_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(ScrapeJob).order_by(ScrapeJob.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/datasets", response_model=list[ScrapedDatasetResponse])
async def list_datasets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(ScrapedDataset).order_by(ScrapedDataset.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/datasets/{dataset_id}", response_model=ScrapedDatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dataset = await db.get(ScrapedDataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset
