from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import uuid

from Backend.services.logging_service import Logger

log = Logger("RuntimeStore")


@dataclass
class QAItem:
    id: str
    chapter_number: int
    subchapter_number: int
    question_text: str
    correct_answer: str
    meta: Dict[str, Any]


class RuntimeStore:
    def __init__(self):
        self._items: Dict[str, QAItem] = {}
        log.ok("RuntimeStore initialized")

    def put(
        self,
        chapter_number: int,
        subchapter_number: int,
        question_text: str,
        correct_answer: str,
        meta: Dict[str, Any],
    ) -> QAItem:
        qid = str(uuid.uuid4())

        if qid in self._items:
            log.warn("Generated qid already exists (unexpected)", {"qid": qid})

        item = QAItem(
            id=qid,
            chapter_number=chapter_number,
            subchapter_number=subchapter_number,
            question_text=question_text,
            correct_answer=correct_answer,
            meta=meta or {},
        )

        self._items[qid] = item

        qtype = (item.meta or {}).get("type")
        log.ok(
            "Stored QAItem",
            {
                "qid": qid,
                "chapter_number": chapter_number,
                "subchapter_number": subchapter_number,
                "type": qtype,
                "count": len(self._items),
            },
        )

        return item

    def get(self, qid: str) -> Optional[QAItem]:
        qid = (qid or "").strip()
        if not qid:
            log.warn("Get called with empty qid")
            return None

        item = self._items.get(qid)
        if item is None:
            log.warn("QAItem not found", {"qid": qid, "count": len(self._items)})
            return None

        qtype = (item.meta or {}).get("type")
        log.info(
            "QAItem loaded",
            {"qid": qid, "type": qtype, "chapter_number": item.chapter_number, "subchapter_number": item.subchapter_number},
        )
        return item


store = RuntimeStore()
