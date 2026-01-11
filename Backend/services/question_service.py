from __future__ import annotations

from typing import Any, Dict

from Backend.core.question_generator import QuestionGenerator
from Backend.persistence.services.question_template_service import get_template_text
from Backend.services import Logger
from Backend.services.question_handlers.registry import build_handlers

qgen = QuestionGenerator()
handlers = build_handlers(qgen)
log = Logger("QuestionService")


def _pick_difficulty(options: Dict[str, Any]) -> str:
    d = str((options or {}).get("difficulty") or "medium").strip().lower()
    if d in ("easy", "medium", "hard"):
        return d
    return "medium"


def generate_question(payload: Dict[str, Any]) -> Dict[str, Any]:
    ch_num = int(payload.get("chapter_number") or 0)
    sub_num = int(payload.get("subchapter_number") or 0)
    options = payload.get("options") or {}

    difficulty = _pick_difficulty(options)

    log.info(
        "generate_question called",
        ctx={
            "chapter_number": ch_num,
            "subchapter_number": sub_num,
            "difficulty": difficulty,
            "has_options": bool(options),
        },
    )

    if ch_num <= 0 or sub_num <= 0:
        return {"ok": False, "error": "chapter_number and subchapter_number are required"}

    template_text = get_template_text(ch_num, sub_num, difficulty=difficulty)
    if not template_text:
        return {"ok": False, "error": "no template found for this chapter/subchapter/difficulty"}

    for h in handlers:
        if h.can_handle(ch_num, sub_num):
            resp = h.generate(ch_num, sub_num, template_text, options)
            log.info(
                "generate_question handled",
                ctx={
                    "chapter_number": ch_num,
                    "subchapter_number": sub_num,
                    "difficulty": difficulty,
                    "ok": resp.get("ok"),
                },
            )
            return resp

    log.warn("Subchapter not implemented", {"chapter_number": ch_num, "subchapter_number": sub_num})
    return {"ok": False, "error": "this subchapter is not implemented yet"}
