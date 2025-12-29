from __future__ import annotations

from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.services import Logger
from Backend.services.evaluators.registry import EVALUATORS

log = Logger("EvaluationService")


def evaluate_answer(payload: Dict[str, Any]) -> Dict[str, Any]:
    qid = (payload.get("question_id") or "").strip()
    answer = payload.get("answer")
    reveal = bool(payload.get("reveal") or False)

    log.info(f"evaluate_answer called qid={qid!r} reveal={reveal}")

    if not qid:
        log.info("Missing question_id in payload")
        return {"ok": False, "error": "question_id is required"}

    item = store.get(qid)
    if item is None:
        log.info(f"Unknown question_id={qid!r}")
        return {"ok": False, "error": "unknown question_id"}

    meta = item.meta or {}
    qtype = meta.get("type")
    log.info(f"Loaded question qid={qid!r} type={qtype!r}")

    evaluator = EVALUATORS.get(qtype)
    if evaluator is None:
        log.info(f"Unsupported question type={qtype!r} qid={qid!r}")
        return {"ok": False, "error": "unsupported question type"}

    try:
        resp = evaluator(item=item, answer=answer, reveal=reveal)
        log.info(
            f"Evaluation done qid={qid!r} type={qtype!r} "
            f"ok={resp.get('ok')} score={resp.get('score', None)} correct={resp.get('correct', None)}"
        )
        return resp
    except Exception as ex:
        log.error(f"Evaluation error qid={qid!r} type={qtype!r}: {ex}")
        return {"ok": False, "error": "evaluation failed"}
