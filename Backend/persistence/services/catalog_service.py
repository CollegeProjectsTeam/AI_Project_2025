from __future__ import annotations

from Backend.services.logging_service import Logger
from Backend.persistence.dbConnex import db
from Backend.persistence.queries.catalog_queries import q_chapters, q_subchapters

log = Logger("CatalogService")


def get_catalog() -> dict:
    try:
        chapters = db.execute(q_chapters(), fetch=True) or []
        subs = db.execute(q_subchapters(), fetch=True) or []
    except Exception as e:
        log.error("Failed to load catalog", exc=e)
        return {"chapters": []}

    by_id: dict[int, dict] = {}

    for ch_id, ch_num, ch_name in chapters:
        by_id[ch_id] = {
            "id": ch_id,
            "chapter_number": ch_num,
            "chapter_name": ch_name,
            "subchapters": [],
        }

    missing_chapters = 0
    for chapter_id, sub_num, sub_name in subs:
        item = by_id.get(chapter_id)
        if item is None:
            missing_chapters += 1
            continue
        item["subchapters"].append(
            {
                "subchapter_number": sub_num,
                "subchapter_name": sub_name,
            }
        )

    log.ok(
        "Catalog loaded",
        {
            "chapters": len(by_id),
            "subchapters": len(subs),
            "subchapters_without_chapter": missing_chapters,
        },
    )

    if missing_chapters:
        log.warn("Some subchapters reference missing chapters", {"count": missing_chapters})

    return {"chapters": list(by_id.values())}
