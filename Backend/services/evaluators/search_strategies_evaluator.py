from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from Backend.services import Logger
from Backend.core.search_strategies.algorithm_comparator import AlgorithmComparator, string_name

log = Logger("Eval.SearchStrategies")


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _norm_token(s: str) -> str:
    s = _norm(s)
    return re.sub(r"[\s\-_]+", "", s)


def _status_label(status: str | None) -> str:
    m = {
        "solved": "solved",
        "no_solution": "no solution",
        "missing_file": "missing file",
        "missing_entrypoint": "missing entrypoint",
        "import_error": "import error",
        "runtime_error": "runtime error",
    }
    return m.get(status or "", status or "unknown")


def _fmt_time_s(time_s: float | None) -> str:
    if time_s is None:
        return "—"
    ms = float(time_s) * 1000.0
    if ms < 1:
        return f"{ms:.3f} ms"
    if ms < 100:
        return f"{ms:.2f} ms"
    if ms < 1000:
        return f"{ms:.0f} ms"
    return f"{float(time_s):.3f} s"


def _user_to_key(ans: Any, keys: List[str]) -> Optional[str]:
    raw = "" if ans is None else str(ans).strip()
    if not raw:
        return None

    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(keys):
            return keys[idx]
        return None

    user = _norm(raw)
    if user in keys:
        return user

    label_map = { _norm_token(string_name(k)): k for k in keys }
    return label_map.get(_norm_token(raw))


def _normalize_timings(timings: list[dict], fastest_time_s: float | None) -> list[dict]:
    out: list[dict] = []
    fastest = None
    try:
        fastest = float(fastest_time_s) if fastest_time_s is not None else None
    except Exception:
        fastest = None

    for t in (timings or []):
        ts = t.get("time_s")
        try:
            ts_val = float(ts) if ts is not None else None
        except Exception:
            ts_val = None

        ms = (ts_val * 1000.0) if ts_val is not None else None
        pct = (100.0 * ts_val / fastest) if (ts_val is not None and fastest and fastest > 0) else None

        out.append(
            {
                **t,
                "time_ms": ms,
                "pct_of_fastest": pct,
            }
        )
    return out


def evaluate_search_strategies(*, item: Any, answer: Any, reveal: bool) -> Dict[str, Any]:
    meta = item.meta or {}

    keys = meta.get("answer_option_keys") or list(getattr(AlgorithmComparator, "ALGORITHM_ORDER", []))
    keys = [str(k) for k in keys]

    correct_key = _norm(str(meta.get("fastest_algorithm_key") or item.correct_answer or ""))
    user_key = _user_to_key(answer, keys)

    score = 100.0 if (user_key is not None and _norm(user_key) == correct_key) else 0.0
    correct = (score == 100.0)

    user_label = string_name(user_key) if user_key else None
    correct_label = string_name(correct_key) if correct_key else None

    if user_key is None:
        message = "Nu am putut interpreta raspunsul. Scrie numele algoritmului sau indexul lui (1..N)."
    elif correct:
        message = f"Corect! Ai ales {user_label}."
    else:
        message = f"Gresit. Ai ales {user_label}, dar raspunsul corect era {correct_label}."

    fastest_name = meta.get("fastest_algorithm")
    fastest_time_s = meta.get("execution_time")
    try:
        fastest_time_s = float(fastest_time_s) if fastest_time_s is not None else None
    except Exception:
        fastest_time_s = None

    timings_raw = meta.get("timings") or []
    timings = _normalize_timings(timings_raw, fastest_time_s)

    lines: list[str] = []
    prob = meta.get("problem")
    if prob:
        lines.append(f"Problema: {prob}")

    if fastest_name is not None and fastest_time_s is not None:
        lines.append(f"Cel mai rapid: {fastest_name} ({fastest_time_s:.6f} s)")

    if timings:
        lines.append("Timpi rulare (sortati descrescator):")
        for t in timings:
            name = t.get("name") or t.get("key") or "Unknown"
            status = _status_label(t.get("status"))

            ts = t.get("time_s")
            try:
                ts_val = float(ts) if ts is not None else None
            except Exception:
                ts_val = None

            pct = t.get("pct_of_fastest")
            pct_txt = f", {pct:.2f}% din fastest" if isinstance(pct, (int, float)) else ""

            if ts_val is None:
                note = t.get("note")
                if note:
                    lines.append(f"- {name}: {status} ({note})")
                else:
                    lines.append(f"- {name}: {status}")
            else:
                lines.append(f"- {name}: {_fmt_time_s(ts_val)} ({status}{pct_txt})")

    resp: Dict[str, Any] = {
        "ok": True,
        "correct": correct,
        "score": score,

        "message": message,
        "user_answer_key": user_key,
        "user_answer": user_label,
        "correct_answer_key": correct_key,
        "correct_answer": correct_label,

        "search_strategies_comparison": {
            "problem": meta.get("problem"),
            "fastest_algorithm_key": meta.get("fastest_algorithm_key"),
            "fastest_algorithm": meta.get("fastest_algorithm"),
            "fastest_time_s": fastest_time_s,
            "sorted_by": "time_desc",
            "timings": timings,
        },

        "explanation_lines": lines,
    }

    if reveal:
        resp["correct_answer"] = correct_label

    log.info(
        "Search strategies evaluated",
        ctx={
            "problem": meta.get("problem"),
            "user_key": user_key,
            "correct_key": correct_key,
            "score": score,
            "timings_count": len(timings),
        },
    )
    return resp