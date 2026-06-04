import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match
from app.models.prediction import ModelPrediction, PredictionRun
from app.services.python_bridge import BridgeError, run_penaltyblog

PREDICT_MODELS = [
    {"key": "PoissonGoalsModel", "label": "Poisson", "description": "Independent Poisson goals model."},
    {"key": "BivariatePoissonGoalModel", "label": "Bivariate Poisson", "description": "Karlis-Ntzoufras bivariate Poisson."},
    {"key": "DixonColesGoalModel", "label": "Dixon-Coles", "description": "Poisson with low-score dependency correction."},
    {"key": "NegativeBinomialGoalModel", "label": "Negative Binomial", "description": "Overdispersed Poisson alternative."},
    {"key": "ZeroInflatedPoissonGoalsModel", "label": "Zero-Inflated Poisson", "description": "Poisson with zero-inflation component."},
    {"key": "WeibullCopulaGoalsModel", "label": "Weibull Copula", "description": "Weibull-count goals with copula dependency."},
    {"key": "BayesianGoalModel", "label": "Bayesian Goal", "description": "Bayesian Poisson goals model (MCMC)."},
    {"key": "HierarchicalBayesianGoalModel", "label": "Bayesian Hierarchical", "description": "Hierarchical Bayesian goals model (MCMC)."},
]

MARKET_OUTCOMES = {
    "1x2": ["home", "draw", "away"],
    "btts": ["yes", "no"],
    "ou_2_5": ["over", "under"],
}


async def fetch_training_matches(db: AsyncSession, league: str, sport: str = "football",
                                 limit: int = 380, date_from: str | None = None,
                                 date_to: str | None = None) -> list[Match]:
    stmt = select(Match).where(
        Match.sport == sport,
        Match.home_score.isnot(None),
        Match.away_score.isnot(None),
        Match.competition.ilike(f"%{league}%"),
    )
    if date_from:
        stmt = stmt.where(Match.match_date >= date_from)
    if date_to:
        stmt = stmt.where(Match.match_date <= date_to)
    stmt = stmt.order_by(Match.match_date.asc(), Match.created_at.asc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def fetch_target_matches(db: AsyncSession, league: str, sport: str = "football",
                               target_mode: str = "future", limit: int = 50,
                               target_match_ids: list[int] | None = None,
                               date_from: str | None = None,
                               date_to: str | None = None) -> list[Match]:
    if target_mode == "matches" and target_match_ids:
        stmt = select(Match).where(Match.id.in_(target_match_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    stmt = select(Match).where(Match.sport == sport, Match.competition.ilike(f"%{league}%"))

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if target_mode == "future":
        stmt = stmt.where(Match.home_score.is_(None), Match.match_date >= (date_from or today))
        if date_to:
            stmt = stmt.where(Match.match_date <= date_to)
    else:
        stmt = stmt.where(Match.home_score.isnot(None))
        if date_from:
            stmt = stmt.where(Match.match_date >= date_from)
        if date_to:
            stmt = stmt.where(Match.match_date <= date_to)
        else:
            stmt = stmt.where(Match.match_date < today)

    stmt = stmt.order_by(Match.match_date.asc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


def extract_market_probabilities(grid: dict, market: str) -> list[dict]:
    mapping = {
        "1x2": [
            {"outcome": "home", "probability": float(grid.get("homeWin", 0))},
            {"outcome": "draw", "probability": float(grid.get("draw", 0))},
            {"outcome": "away", "probability": float(grid.get("awayWin", 0))},
        ],
        "btts": [
            {"outcome": "yes", "probability": float(grid.get("bttsYes", 0))},
            {"outcome": "no", "probability": float(grid.get("bttsNo", 0))},
        ],
        "ou_2_5": [
            {"outcome": "over", "probability": float(grid.get("totals", {}).get("over_2_5", 0))},
            {"outcome": "under", "probability": float(grid.get("totals", {}).get("under_2_5", 0))},
        ],
    }
    return mapping.get(market, [])


async def execute_single_model_run(
    db: AsyncSession,
    run_id: int,
    model_key: str,
    league: str,
    markets: list[str],
    sport: str = "football",
    training_limit: int = 380,
    target_limit: int = 50,
    target_mode: str = "future",
    max_goals: int = 10,
) -> dict:
    training = await fetch_training_matches(db, league, sport, training_limit)
    if len(training) < 20:
        raise ValueError(f"Insufficient training data: {len(training)} matches (need >=20)")

    targets = await fetch_target_matches(db, league, sport, target_mode, target_limit)
    if not targets:
        raise ValueError("No target matches found for this selection.")

    goals_home = [m.home_score for m in training]
    goals_away = [m.away_score for m in training]
    teams_home = [m.home_team for m in training]
    teams_away = [m.away_team for m in training]

    written = 0
    failed = 0
    concurrency = 3

    async def predict_one(target: Match) -> None:
        nonlocal written, failed
        try:
            response = await run_penaltyblog({
                "operation": "model_fit_predict",
                "payload": {
                    "model": model_key,
                    "goals_home": goals_home,
                    "goals_away": goals_away,
                    "teams_home": teams_home,
                    "teams_away": teams_away,
                    "prediction": {
                        "home_team": target.home_team,
                        "away_team": target.away_team,
                        "max_goals": max_goals,
                    },
                },
            })
            result = response.get("result", {})
            grid = result.get("prediction")
            if not grid:
                return

            rows = []
            for market in markets:
                for entry in extract_market_probabilities(grid, market):
                    rows.append(ModelPrediction(
                        run_id=run_id,
                        match_id=target.id,
                        market=market,
                        home_prob=grid.get("homeWin", 0),
                        draw_prob=grid.get("draw"),
                        away_prob=grid.get("awayWin", 0),
                    ))
            if rows:
                db.add_all(rows)
                written += len(rows)
        except BridgeError as e:
            failed += 1

    index = 0

    async def worker() -> None:
        nonlocal index
        while index < len(targets):
            i = index
            index += 1
            await predict_one(targets[i])

    workers = [worker() for _ in range(min(concurrency, len(targets)))]
    await asyncio.gather(*workers)

    return {
        "training_matches": len(training),
        "target_matches": len(targets),
        "written": written,
        "failed": failed,
        "markets": markets,
    }


async def run_single_prediction(
    db: AsyncSession,
    league: str,
    model_key: str,
    markets: list[str] = None,
    sport: str = "football",
    training_limit: int = 380,
    target_limit: int = 50,
    target_mode: str = "future",
    max_goals: int = 10,
    user_id: int | None = None,
) -> dict:
    if markets is None:
        markets = ["1x2"]

    run = PredictionRun(
        user_id=user_id,
        model_type=model_key,
        ensemble=False,
        status="running",
        matches_count=0,
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    await db.flush()

    try:
        summary = await execute_single_model_run(
            db, run.id, model_key, league, markets,
            sport, training_limit, target_limit, target_mode, max_goals,
        )
        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.matches_count = summary["target_matches"]
        await db.flush()
        return {"run_id": run.id, "status": run.status}
    except Exception as e:
        run.status = "failed"
        run.completed_at = datetime.now(timezone.utc)
        run.error = str(e)
        await db.flush()
        return {"run_id": run.id, "status": run.status, "error": str(e)}
