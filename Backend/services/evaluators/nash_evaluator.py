from __future__ import annotations

from typing import Any, Dict

from Backend.services import Logger
from Backend.services.evaluators.nash_pure_evaluator import evaluate_nash_pure
from Backend.services.evaluators.nash_mixed_evaluator import evaluate_nash_mixed
from Backend.services.evaluators.nash_combined_evaluator import evaluate_nash_combined

log = Logger("Eval.Nash")


def evaluate_nash(*, item: Any, answer: Any, reveal: bool) -> Dict[str, Any]:
    """
    Dispatch evaluator for questions with meta.type == "nash".

    Uses meta.kind:
      - "pure"     -> evaluate_nash_pure
      - "mixed"    -> evaluate_nash_mixed
      - "combined" -> evaluate_nash_combined

    Also contains safe fallbacks if kind is missing.
    """
    meta = item.meta or {}
    kind = str(meta.get("kind") or "").strip().lower()

    log.info(f"Dispatch Nash evaluator kind={kind!r} reveal={reveal}")

    if kind == "pure":
        return evaluate_nash_pure(item=item, answer=answer, reveal=reveal)

    if kind == "mixed":
        return evaluate_nash_mixed(item=item, answer=answer, reveal=reveal)

    if kind == "combined":
        return evaluate_nash_combined(item=item, answer=answer, reveal=reveal)

    if meta.get("pure_equilibria") is not None and meta.get("mixed_equilibrium") is not None:
        log.info("Fallback: choosing NashCombined based on meta keys")
        return evaluate_nash_combined(item=item, answer=answer, reveal=reveal)

    if meta.get("mixed_equilibrium") is not None:
        log.info("Fallback: choosing NashMixed based on meta keys")
        return evaluate_nash_mixed(item=item, answer=answer, reveal=reveal)

    log.info("Fallback: choosing NashPure as default")
    return evaluate_nash_pure(item=item, answer=answer, reveal=reveal)