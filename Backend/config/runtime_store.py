from dataclasses import dataclass
from typing import Any, Dict, Optional
import uuid

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

    def put(self, chapter_number: int, subchapter_number: int, question_text: str, correct_answer: str, meta: Dict[str, Any]):
        qid = str(uuid.uuid4())
        item = QAItem(
            id=qid,
            chapter_number=chapter_number,
            subchapter_number=subchapter_number,
            question_text=question_text,
            correct_answer=correct_answer,
            meta=meta or {}
        )
        self._items[qid] = item
        return item

    def get(self, qid: str) -> Optional[QAItem]:
        return self._items.get(qid)

store = RuntimeStore()
