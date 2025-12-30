from __future__ import annotations

from Backend.services.logging_service import Logger
from Backend.persistence.dbConnex import db
from Backend.persistence.queries.question_template_queries import (
    q_template_text_any,
    q_template_text_by_difficulty,
    q_template_id_any,
    q_template_id_by_difficulty,
)

log = Logger("QuestionTemplateService")


def _norm_difficulty(v) -> str | None:
    if v is None:
        return None
    d = str(v).strip().lower()
    if d in ("easy", "medium", "hard"):
        return d
    return None


def get_template_text(chapter_number: int, subchapter_number: int, difficulty: str | None = None) -> str | None:
    diff = _norm_difficulty(difficulty)

    # 1) try by difficulty (if provided)
    if diff:
        try:
            rows = db.execute(
                q_template_text_by_difficulty(),
                (chapter_number, subchapter_number, diff),
                fetch=True,
            ) or []
        except Exception as e:
            log.error(
                "Failed to load template_text by difficulty",
                {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff},
                exc=e,
            )
            rows = []

        if rows:
            text = rows[0][0]
            log.ok(
                "Template_text loaded (by difficulty)",
                {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff},
            )
            return text

        log.warn(
            "No template_text found for difficulty, falling back to any",
            {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff},
        )

    # 2) fallback any
    try:
        rows = db.execute(
            q_template_text_any(),
            (chapter_number, subchapter_number),
            fetch=True,
        ) or []
    except Exception as e:
        log.error(
            "Failed to load template_text",
            {"chapter_number": chapter_number, "subchapter_number": subchapter_number},
            exc=e,
        )
        return None

    if not rows:
        log.warn(
            "No template_text found",
            {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff},
        )
        return None

    text = rows[0][0]
    log.ok(
        "Template_text loaded (any)",
        {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff},
    )
    return text


def get_template_id(chapter_number: int, subchapter_number: int, difficulty: str | None = None) -> int | None:
    diff = _norm_difficulty(difficulty)

    # 1) try by difficulty (if provided)
    if diff:
        try:
            rows = db.execute(
                q_template_id_by_difficulty(),
                (chapter_number, subchapter_number, diff),
                fetch=True,
            ) or []
        except Exception as e:
            log.error(
                "Failed to load template_id by difficulty",
                {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff},
                exc=e,
            )
            rows = []

        if rows:
            template_id = rows[0][0]
            log.ok(
                "Template_id loaded (by difficulty)",
                {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff, "template_id": template_id},
            )
            return template_id

        log.warn(
            "No template_id found for difficulty, falling back to any",
            {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff},
        )

    # 2) fallback any
    try:
        rows = db.execute(
            q_template_id_any(),
            (chapter_number, subchapter_number),
            fetch=True,
        ) or []
    except Exception as e:
        log.error(
            "Failed to load template_id",
            {"chapter_number": chapter_number, "subchapter_number": subchapter_number},
            exc=e,
        )
        return None

    if not rows:
        log.warn(
            "No template_id found",
            {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff},
        )
        return None

    template_id = rows[0][0]
    log.ok(
        "Template_id loaded (any)",
        {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "difficulty": diff, "template_id": template_id},
    )
    return template_id
