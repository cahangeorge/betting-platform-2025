from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scrape import ScrapeJob
from app.services.python_bridge import BridgeError, run_oddsharvester


async def create_scrape_job(
    db: AsyncSession,
    job_type: str,
    league: str | None = None,
    params: dict | None = None,
) -> ScrapeJob:
    job = ScrapeJob(
        job_type=job_type,
        status="pending",
        league=league,
        params=params,
    )
    db.add(job)
    await db.flush()
    return job


async def execute_scrape_job(db: AsyncSession, job_id: int) -> ScrapeJob:
    job = await db.get(ScrapeJob, job_id)
    if not job:
        raise ValueError(f"ScrapeJob {job_id} not found")

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    await db.flush()

    try:
        if job.job_type == "oddsportal":
            args = ["--sport", (job.params or {}).get("sport", "football"),
                    "--command", (job.params or {}).get("command", "upcoming")]
            if job.league:
                args.extend(["--league", job.league])
            output = await run_oddsharvester(args)
            job.status = "completed"
            job.output = output
        else:
            job.status = "completed"

        job.completed_at = datetime.now(timezone.utc)
    except BridgeError as e:
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.now(timezone.utc)

    await db.flush()
    return job
