from __future__ import annotations

from Backend.services.logging_service import Logger
from Backend.persistence.dbConnex import db
from Backend.persistence.queries.question_template_queries import q_template_text, q_template_id

log = Logger("QuestionTemplateService")


def get_template_text(chapter_number: int, subchapter_number: int) -> str | None:
    try:
        rows = db.execute(q_template_text(), (chapter_number, subchapter_number), fetch=True) or []
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
            {"chapter_number": chapter_number, "subchapter_number": subchapter_number},
        )
        return None

    text = rows[0][0]
    log.ok(
        "Template_text loaded",
        {"chapter_number": chapter_number, "subchapter_number": subchapter_number},
    )
    return text


def get_template_id(chapter_number: int, subchapter_number: int) -> int | None:
    try:
        rows = db.execute(q_template_id(), (chapter_number, subchapter_number), fetch=True) or []
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
            {"chapter_number": chapter_number, "subchapter_number": subchapter_number},
        )
        return None

    template_id = rows[0][0]
    log.ok(
        "Template_id loaded",
        {"chapter_number": chapter_number, "subchapter_number": subchapter_number, "template_id": template_id},
    )
    return template_id
