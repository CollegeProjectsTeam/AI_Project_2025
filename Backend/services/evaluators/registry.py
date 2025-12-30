from __future__ import annotations

from typing import Any, Callable, Dict

from Backend.services.evaluators.nqueens_evaluator import evaluate_nqueens

from Backend.services.evaluators.nash_evaluator import evaluate_nash
from Backend.services.evaluators.nash_pure_evaluator import evaluate_nash_pure
from Backend.services.evaluators.nash_mixed_evaluator import evaluate_nash_mixed
from Backend.services.evaluators.nash_combined_evaluator import evaluate_nash_combined

from Backend.services.evaluators.minmax_evaluator import evaluate_minmax
from Backend.services.evaluators.csp_evaluator import evaluate_csp

EvaluatorFn = Callable[..., Dict[str, Any]]

EVALUATORS: Dict[str, EvaluatorFn] = {
    "nqueens": evaluate_nqueens,

    "nash": evaluate_nash,

    "nash_pure": evaluate_nash_pure,
    "nash_mixed": evaluate_nash_mixed,
    "nash_combined": evaluate_nash_combined,

    "minmax": evaluate_minmax,
    "csp": evaluate_csp,
}
