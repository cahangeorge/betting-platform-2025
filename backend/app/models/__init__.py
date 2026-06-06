from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.user import User, Session
from app.models.match import Match, OddsEntry, MatchStat, MatchSource
from app.models.prediction import PredictionRun, ModelPrediction, EnsemblePrediction, PredictionSession, Prediction
from app.models.ticket import Ticket, TicketBatch, TicketLeg, BetPlacement, Settlement
from app.models.scrape import ScrapeJob, ScrapedDataset
from app.models.bankroll import Bankroll, BookmakerAccount, LedgerEntry
from app.models.job import ScheduledJob
from app.models.strategy import Strategy
from app.models.todo import Todo

__all__ = [
    "Base",
    "User",
    "Session",
    "Match",
    "OddsEntry",
    "MatchStat",
    "MatchSource",
    "PredictionRun",
    "ModelPrediction",
    "EnsemblePrediction",
    "PredictionSession",
    "Prediction",
    "Ticket",
    "TicketBatch",
    "TicketLeg",
    "BetPlacement",
    "Settlement",
    "ScrapeJob",
    "ScrapedDataset",
    "Bankroll",
    "BookmakerAccount",
    "LedgerEntry",
    "ScheduledJob",
    "Strategy",
    "Todo",
]
