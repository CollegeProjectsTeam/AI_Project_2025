from Backend.services.evaluators.registry import EVALUATORS

from Backend.services.evaluators.nqueens_evaluator import evaluate_nqueens
from Backend.services.evaluators.nash_pure_evaluator import evaluate_nash_pure
from Backend.services.evaluators.nash_mixed_evaluator import evaluate_nash_mixed
from Backend.services.evaluators.nash_combined_evaluator import evaluate_nash_combined
from Backend.services.evaluators.minmax_evaluator import evaluate_minmax
from Backend.services.evaluators.csp_evaluator import evaluate_csp

__all__ = [
    "EVALUATORS",
    "evaluate_nqueens",
    "evaluate_nash_pure",
    "evaluate_nash_mixed",
    "evaluate_nash_combined",
    "evaluate_minmax",
    "evaluate_csp",
]
