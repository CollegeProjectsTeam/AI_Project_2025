from __future__ import annotations

from Backend.core.question_generator import QuestionGenerator
from Backend.services.question_handlers.nqueens_handler import NQueensQuestionHandler
from Backend.services.question_handlers.nash_handler import NashQuestionHandler
from Backend.services.question_handlers.minmax_handler import MinMaxQuestionHandler
from Backend.services.question_handlers.csp_handler import CSPQuestionHandler


def build_handlers(qgen: QuestionGenerator):
    return [
        NQueensQuestionHandler(qgen),
        NashQuestionHandler(qgen),
        MinMaxQuestionHandler(qgen),
        CSPQuestionHandler(qgen),
    ]
