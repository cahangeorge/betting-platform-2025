from fastapi import APIRouter

from app.api.v1 import auth, bankroll, data, jobs, matches, predictions, tickets

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
v1_router.include_router(matches.router, prefix="/matches", tags=["matches"])
v1_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
v1_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
v1_router.include_router(data.router, prefix="/data", tags=["data"])
v1_router.include_router(bankroll.router, prefix="/bankroll", tags=["bankroll"])
v1_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
