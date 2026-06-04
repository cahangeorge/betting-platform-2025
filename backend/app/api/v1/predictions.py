from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.prediction import EnsemblePrediction, ModelPrediction, PredictionRun, PredictionSession, Prediction
from app.models.user import User
from app.schemas.prediction import (
    EnsemblePredictionResponse,
    ModelPredictionResponse,
    PredictionCatalogResponse,
    PredictionRunDetailResponse,
    PredictionRunResponse,
    RunEnsembleRequest,
    RunSingleRequest,
)
from app.services.ensemble import run_ensemble_prediction
from app.services.prediction_engine import PREDICT_MODELS, run_single_prediction

router = APIRouter()


@router.get("/catalog", response_model=PredictionCatalogResponse)
async def get_catalog():
    return PredictionCatalogResponse(
        models=[dict(m) for m in PREDICT_MODELS],
        markets=["1x2", "btts", "ou_2_5"],
    )


@router.post("/run", response_model=dict)
async def create_prediction_run(
    body: RunSingleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await run_single_prediction(
        db=db,
        league=body.league,
        user_id=user.id,
        model_key=body.model_key,
        markets=body.markets,
        sport=body.sport,
        training_limit=body.training_limit,
        target_limit=body.target_limit,
        target_mode=body.target_mode,
        max_goals=body.max_goals,
    )


@router.post("/ensemble", response_model=dict)
async def create_ensemble_run(
    body: RunEnsembleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await run_ensemble_prediction(
        db=db,
        league=body.league,
        user_id=user.id,
        model_keys=body.model_keys,
        markets=body.markets,
        weighting=body.weighting,
        sport=body.sport,
        training_limit=body.training_limit,
        target_limit=body.target_limit,
        target_mode=body.target_mode,
        max_goals=body.max_goals,
    )


@router.get("/runs", response_model=list[PredictionRunResponse])
async def list_prediction_runs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = (
        select(PredictionRun)
        .where(PredictionRun.user_id == user.id)
        .order_by(PredictionRun.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/runs/{run_id}", response_model=PredictionRunDetailResponse)
async def get_prediction_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = (
        select(PredictionRun)
        .options(
            selectinload(PredictionRun.model_predictions),
            selectinload(PredictionRun.ensemble_predictions),
        )
        .where(PredictionRun.id == run_id, PredictionRun.user_id == user.id)
    )
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Prediction run not found")
    return run


@router.delete("/runs/{run_id}", status_code=204)
async def delete_prediction_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(PredictionRun).where(PredictionRun.id == run_id, PredictionRun.user_id == user.id)
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Prediction run not found")
    await db.delete(run)
    await db.flush()
