from __future__ import annotations

import random
from typing import Any, Dict, Optional, Tuple

from Backend.services.logging_service import Logger
from Backend.services.question_service import generate_question

log = Logger("TestService")


# -----------------------------
# Helpers
# -----------------------------

def _parse_subchapter_ref(item: Any) -> Optional[Tuple[int, int]]:
    """
    Accepts:
      - "1:2" (chapter:subchapter)
      - {"id":"1:2"} or {"chapter_number":1,"subchapter_number":2}
      - (chapter, subchapter) tuple/list
    Returns (chapter_number, subchapter_number) or None.
    """
    if item is None:
        return None

    # dict form
    if isinstance(item, dict):
        if "chapter_number" in item and "subchapter_number" in item:
            try:
                return int(item["chapter_number"]), int(item["subchapter_number"])
            except Exception:
                return None

        raw = str(item.get("id") or "")
        if ":" in raw:
            a, b = raw.split(":", 1)
            try:
                return int(a), int(b)
            except Exception:
                return None
        return None

    # tuple/list form
    if isinstance(item, (tuple, list)) and len(item) == 2:
        try:
            return int(item[0]), int(item[1])
        except Exception:
            return None

    # string form "1:2"
    if isinstance(item, str) and ":" in item:
        a, b = item.split(":", 1)
        try:
            return int(a), int(b)
        except Exception:
            return None

    return None


def _get_randomized_options(difficulty: str) -> Dict[str, Any]:
    """
    Generic numeric options used by some handlers (ex: CSP).
    Safe defaults. Extra keys will simply be ignored by handlers that don't need them.
    """
    rules = {
        "easy": {
            "vars": (2, 4),
            "constraints": (1, 6),
            "domain_min": (1, 4),
            "domain_max": (2, 5),
        },
        "medium": {
            "vars": (2, 6),
            "constraints": (1, 12),
            "domain_min": (1, 8),
            "domain_max": (2, 10),
        },
        "hard": {
            "vars": (2, 8),
            "constraints": (1, 20),
            "domain_min": (1, 10),
            "domain_max": (2, 12),
        },
    }

    r = rules.get(difficulty, rules["medium"])
    dom_min = random.randint(*r["domain_min"])
    dom_max = random.randint(max(dom_min, r["domain_max"][0]), r["domain_max"][1])

    return {
        "num_vars": random.randint(*r["vars"]),
        "num_constraints": random.randint(*r["constraints"]),
        "domain_min": dom_min,
        "domain_max": dom_max,
    }


def _try_generate_question_with_retries(
    chapter_number: int,
    subchapter_number: int,
    difficulty: str,
    retries: int = 5,
) -> Dict[str, Any]:
    """
    Tries multiple times to generate a question for the same subchapter.
    If it crashes or returns ok=false, it retries with fresh randomized options.
    """
    last_error: str = "unknown error"

    for attempt in range(1, retries + 1):
        options = _get_randomized_options(difficulty)

        payload = {
            "chapter_number": chapter_number,
            "subchapter_number": subchapter_number,
            "difficulty": difficulty,
            "options": options,
        }

        try:
            res = generate_question(payload)
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            log.warn(
                "generate_question crashed (retrying)",
                {
                    "chapter_number": chapter_number,
                    "subchapter_number": subchapter_number,
                    "difficulty": difficulty,
                    "attempt": attempt,
                    "error": last_error,
                },
            )
            continue

        if res.get("ok"):
            return res

        last_error = str(res.get("error") or "ok=false")
        log.warn(
            "generate_question returned ok=false (retrying)",
            {
                "chapter_number": chapter_number,
                "subchapter_number": subchapter_number,
                "difficulty": difficulty,
                "attempt": attempt,
                "error": last_error,
            },
        )

    return {"ok": False, "error": f"Failed after {retries} retries. Last: {last_error}"}


# -----------------------------
# Public API
# -----------------------------

def generate_test(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Robust test generation:
      - generates exactly num_questions total (not num_questions * subchapters)
      - picks a random selected subchapter per question
      - retries when a generator fails (ex: N-Queens instance generation failure)
      - returns partial failure message if it cannot reach num_questions within limits
    """
    num_questions = int(data.get("num_questions", 0))
    difficulty = (data.get("difficulty") or "medium").strip()
    subchapters = data.get("subchapters", [])

    if num_questions <= 0:
        return {"ok": False, "error": "Invalid input: num_questions must be >= 1.", "error_code": "BAD_INPUT"}

    if not isinstance(subchapters, list) or not subchapters:
        return {"ok": False, "error": "Invalid input: subchapters must be a non-empty list.", "error_code": "BAD_INPUT"}

    # Parse subchapter refs once
    parsed: list[Tuple[int, int]] = []
    for s in subchapters:
        ref = _parse_subchapter_ref(s)
        if ref is None:
            log.warn("Skipping invalid subchapter ref", {"raw": s})
            continue
        parsed.append(ref)

    if not parsed:
        return {"ok": False, "error": "No valid subchapters selected.", "error_code": "BAD_INPUT"}

    test_questions: list[Dict[str, Any]] = []

    # Global limits to avoid infinite loops
    per_question_retries = 5
    max_total_attempts = num_questions * 10  # tries across the whole test

    attempts = 0
    while len(test_questions) < num_questions and attempts < max_total_attempts:
        attempts += 1

        chapter_number, subchapter_number = random.choice(parsed)

        res = _try_generate_question_with_retries(
            chapter_number=chapter_number,
            subchapter_number=subchapter_number,
            difficulty=difficulty,
            retries=per_question_retries,
        )

        if res.get("ok"):
            # generate_question usually returns {"ok":True, "question":{...}}
            test_questions.append(res.get("question") or res)
        else:
            # failed after retries; continue and try another input/subchapter
            log.warn(
                "Failed to generate question after retries (continuing)",
                {
                    "chapter_number": chapter_number,
                    "subchapter_number": subchapter_number,
                    "difficulty": difficulty,
                    "error": res.get("error"),
                },
            )

    if len(test_questions) < num_questions:
        return {
            "ok": False,
            "error": f"Could only generate {len(test_questions)}/{num_questions} questions. "
                     f"Some generators failed repeatedly (see logs).",
            "error_code": "GENERATION_FAILED",
            "partial_test": test_questions,
        }

    return {"ok": True, "test": test_questions}


def fetch_test_details(test_id: str) -> Dict[str, Any]:
    try:
        test_details = {
            "test_id": test_id,
            "questions": [
                {"question_id": 1, "content": "Sample Question 1"},
                {"question_id": 2, "content": "Sample Question 2"},
            ],
        }
        return {"ok": True, "test_details": test_details}
    except Exception as e:
        log.error("Error fetching test details", exc=e)
        return {"ok": False, "error": "Internal server error", "error_code": "INTERNAL"}
