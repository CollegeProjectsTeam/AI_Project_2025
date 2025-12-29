from Backend.services.evaluators.registry import EVALUATORS

from Backend.services.evaluators.nqueens_evaluator import evaluate_nqueens
from Backend.services.evaluators.nash_pure_evaluator import evaluate_nash_pure
from Backend.services.evaluators.nash_mixed_evaluator import evaluate_nash_mixed
from Backend.services.evaluators.nash_combined_evaluator import evaluate_nash_combined

__all__ = [
    "EVALUATORS",
    "evaluate_nqueens",
    "evaluate_nash_pure",
    "evaluate_nash_mixed",
    "evaluate_nash_combined",
]
