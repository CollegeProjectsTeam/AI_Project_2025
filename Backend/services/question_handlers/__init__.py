from __future__ import annotations

from Backend.services.question_handlers.registry import build_handlers
from Backend.services.question_handlers.search_strategies_handler import SearchStrategiesQuestionHandler
from Backend.services.question_handlers.nash_handler import NashQuestionHandler
from Backend.services.question_handlers.minmax_handler import MinMaxQuestionHandler
from Backend.services.question_handlers.csp_handler import CSPQuestionHandler

__all__ = [
    "build_handlers",
    "SearchStrategiesQuestionHandler",
    "NashQuestionHandler",
    "MinMaxQuestionHandler",
    "CSPQuestionHandler",
]