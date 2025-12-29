from __future__ import annotations

from typing import Any, Dict

from Backend.services import Logger
from Backend.core.search_strategies.n_queens_problem.n_queens_answear import (
    AlgorithmComparator,
    string_name,
)

log = Logger("Eval.NQueens")


def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _nq_user_to_key(ans: Any) -> str | None:
    raw = "" if ans is None else str(ans).strip()
    if not raw:
        return None

    keys = getattr(AlgorithmComparator, "ALGORITHM_ORDER", [])

    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(keys):
            return keys[idx]
        return None

    user = _norm(raw)
    if user in keys:
        return user

    label_map = {string_name(k).strip().lower(): k for k in keys}
    return label_map.get(user)


def _fmt_ms(ms: float | None) -> str:
    if ms is None:
        return "—"
    if ms < 1:
        return f"{ms:.3f} ms"
    if ms < 100:
        return f"{ms:.2f} ms"
    return f"{ms:.0f} ms"


def _status_label(status: str | None) -> str:
    m = {
        "solved": "solved",
        "no_solution": "no solution",
        "missing_file": "missing file",
        "missing_entrypoint": "missing solve_nqueens",
        "import_error": "import error",
        "runtime_error": "runtime error",
    }
    return m.get(status or "", status or "unknown")


def evaluate_nqueens(*, item: Any, answer: Any, reveal: bool) -> Dict[str, Any]:
    correct_key = _norm(str(item.correct_answer or ""))
    user_key = _nq_user_to_key(answer)

    meta = item.meta or {}
    cmp_info = meta.get("nqueens_comparison") or {}
    timings = cmp_info.get("timings") or []

    score = 100.0 if (user_key is not None and user_key == correct_key) else 0.0
    correct = (score == 100.0)

    user_label = string_name(user_key) if user_key else None
    correct_label = string_name(correct_key) if correct_key else None

    if user_key is None:
        message = "Nu am putut interpreta raspunsul. Scrie numele algoritmului sau indexul lui (1..N)."
    elif correct:
        message = f"Corect! Ai ales {user_label}."
    else:
        message = f"Gresit. Ai ales {user_label}, dar raspunsul corect era {correct_label}."

    lines: list[str] = []
    fastest_name = cmp_info.get("fastest_algorithm")
    fastest_time_s = cmp_info.get("fastest_time_s")
    if fastest_name is not None and fastest_time_s is not None:
        lines.append(f"Cel mai rapid: {fastest_name} ({fastest_time_s:.6f} s)")

    if timings:
        lines.append("Timpi rulare (sortati descrescator):")
        for t in timings:
            name = t.get("name") or t.get("key") or "Unknown"
            status = _status_label(t.get("status"))
            ms = t.get("time_ms")
            pct = t.get("pct_of_fastest")

            if ms is None:
                note = t.get("note")
                if note:
                    lines.append(f"- {name}: {status} ({note})")
                else:
                    lines.append(f"- {name}: {status}")
            else:
                pct_txt = f", {pct:.2f}% din fastest" if isinstance(pct, (int, float)) else ""
                lines.append(f"- {name}: {_fmt_ms(ms)} ({status}{pct_txt})")

    resp: Dict[str, Any] = {
        "ok": True,
        "correct": correct,
        "score": score,

        "message": message,
        "user_answer_key": user_key,
        "user_answer": user_label,
        "correct_answer_key": correct_key,
        "correct_answer": correct_label,

        "nqueens_comparison": {
            "fastest_algorithm_key": cmp_info.get("fastest_algorithm_key"),
            "fastest_algorithm": cmp_info.get("fastest_algorithm"),
            "fastest_time_s": cmp_info.get("fastest_time_s"),
            "sorted_by": "time_desc",
            "timings": timings,
        },

        "explanation_lines": lines,
    }

    if reveal:
        resp["correct_answer"] = correct_label

    log.info(
        "NQueens evaluated",
        ctx={
            "user_key": user_key,
            "correct_key": correct_key,
            "score": score,
            "timings_count": len(timings),
        },
    )
    return resp
