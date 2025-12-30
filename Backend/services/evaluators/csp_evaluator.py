from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

from Backend.services import Logger
from Backend.core.constrain_satisfaction_problems.instance_solver import CSPSolver

log = Logger("Eval.CSP")

Assignment = Dict[str, int]


_NONE_TOKENS = {"none", "no", "nu", "n/a"}


def _coerce_assignment_dict(d: Dict[Any, Any]) -> Optional[Assignment]:
    out: Assignment = {}
    for k, v in (d or {}).items():
        try:
            out[str(k)] = int(v)
        except Exception:
            continue
    return out or None


def _try_parse_json_dict(s: str) -> Optional[Assignment]:
    if not (s.startswith("{") and s.endswith("}")):
        return None
    try:
        obj = json.loads(s)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    return _coerce_assignment_dict(obj)


def _try_parse_pairs(s: str) -> Optional[Assignment]:
    pairs = re.findall(r"([A-Za-z_]\w*)\s*[:=]?\s*(-?\d+)", s)
    if not pairs:
        return None
    out: Assignment = {}
    for var, num in pairs:
        try:
            out[str(var)] = int(num)
        except Exception:
            continue
    return out or None


def _parse_assignment(answer: Any) -> Tuple[Optional[Assignment], bool]:
    """
    Accepta mai multe formate:
      - dict: {"A":1,"B":3}
      - JSON string: '{"A":1,"B":3}'
      - string cu perechi: 'A=1, B=3' / 'A 1 B 3' / '(A,1) (B,3)'
      - none/no/nu: semnaleaza ca nu exista solutie
    Return: (assignment|None, ok)
    """
    if answer is None:
        return None, False

    if isinstance(answer, dict):
        asg = _coerce_assignment_dict(answer)
        return (asg, True) if asg is not None else (None, False)

    s = str(answer or "").strip()
    if not s:
        return None, False

    if s.lower() in _NONE_TOKENS:
        return None, True

    asg = _try_parse_json_dict(s)
    if asg is not None:
        return asg, True

    asg = _try_parse_pairs(s)
    if asg is not None:
        return asg, True

    return None, False

def _read_expected_from_meta_solution(meta: Dict[str, Any]) -> Tuple[Optional[bool], Optional[Assignment]]:
    sol = meta.get("solution")
    if not isinstance(sol, dict):
        return None, None

    found = sol.get("found")
    solution = sol.get("solution")

    if not isinstance(found, bool):
        return None, None

    if solution is None:
        return found, None

    if isinstance(solution, dict):
        norm = _coerce_assignment_dict(solution)
        return found, norm

    return found, None


def _read_expected_from_correct_answer(corr: Any) -> Tuple[Optional[bool], Optional[Assignment]]:
    if corr is None:
        return None, None

    s = str(corr).strip()
    if not s:
        return None, None

    if not (s.startswith("{") and s.endswith("}")):
        return None, None

    try:
        obj = json.loads(s.replace("'", '"'))  # tolerate python dict string
    except Exception:
        return None, None

    if not isinstance(obj, dict):
        return None, None

    found = obj.get("found")
    solution = obj.get("solution")

    if not isinstance(found, bool):
        return None, None

    if solution is None:
        return found, None

    if isinstance(solution, dict):
        return found, (_coerce_assignment_dict(solution) or {})
    return found, None


def _expected_from_item(item: Any) -> Tuple[Optional[bool], Optional[Assignment]]:
    meta = getattr(item, "meta", None) or {}

    found, sol = _read_expected_from_meta_solution(meta)
    if found is not None:
        return found, sol

    corr = getattr(item, "correct_answer", None)
    return _read_expected_from_correct_answer(corr)


def _extract_instance_from_meta(meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    inst = meta.get("instance")
    if isinstance(inst, dict):
        return inst

    payload = meta.get("payload")
    if isinstance(payload, dict) and isinstance(payload.get("instance"), dict):
        return payload["instance"]

    return None


def _build_solver_payload(meta: Dict[str, Any], inst: Dict[str, Any]) -> Dict[str, Any]:
    settings = meta.get("settings") or {}
    return {
        "inference": settings.get("inference", "NONE"),
        "var_heuristic": settings.get("var_heuristic", "FIXED"),
        "value_heuristic": settings.get("value_heuristic", "NONE"),
        "consistency": settings.get("consistency", "NONE"),
        "ask_for": settings.get("ask_for", "TRACE_UNTIL_SOLUTION"),
        "instance": inst,
    }


def _try_solve_from_meta(item: Any) -> Tuple[Optional[bool], Optional[Assignment], Optional[str]]:
    meta = getattr(item, "meta", None) or {}
    inst = _extract_instance_from_meta(meta)
    if inst is None:
        return None, None, "missing instance in meta"

    payload = _build_solver_payload(meta, inst)

    solved = CSPSolver.solve(payload, strict=True)
    if not solved.get("ok"):
        return None, None, str(solved.get("error") or "csp solver failed")

    found = bool(solved.get("found"))
    sol = solved.get("solution")

    if isinstance(sol, dict):
        return found, (_coerce_assignment_dict(sol) or {}), None

    return found, None, None


def _fmt_asg_json(asg: Optional[Assignment]) -> str:
    if asg is None:
        return "none"
    if not asg:
        return "{}"
    return json.dumps(asg, ensure_ascii=False, sort_keys=True)


def _fmt_asg_text(asg: Optional[Assignment]) -> str:
    if not asg:
        return "none"
    keys = sorted(asg.keys())
    return ", ".join([f"{k}={asg[k]}" for k in keys])


def _build_explanation(
    expected_found: bool,
    expected_solution: Optional[Assignment],
    user_assignment: Optional[Assignment],
) -> str:
    lines = [
        "Constraint Satisfaction Problems (CSP) are solved via Backtracking with optional optimizations.",
        "Supported optimizations here:",
        "- MRV (Minimum Remaining Values) for variable selection",
        "- LCV (Least Constraining Value) for value ordering",
        "- FC (Forward Checking) for inference",
        "- AC-3 (Arc Consistency) for consistency enforcement",
        "",
        'Answer format accepted: JSON assignment like {"A":1,"B":3} or text like A=1, B=3, or "none" if no solution exists.',
        "",
        f"Expected solution found = {expected_found}",
        f"Expected solution = {_fmt_asg_json(expected_solution) if expected_found else 'none'}",
        f"Received solution = {_fmt_asg_json(user_assignment)}",
    ]
    return "\n".join(lines)


def _score(exp_found: bool, exp_solution: Optional[Assignment], user_asg: Optional[Assignment]) -> Tuple[bool, float]:
    if not exp_found:
        correct = user_asg is None
        return correct, (100.0 if correct else 0.0)

    correct = isinstance(exp_solution, dict) and (user_asg == exp_solution)
    return correct, (100.0 if correct else 0.0)


def evaluate_csp(item: Any, answer: Any, reveal: bool = False) -> Dict[str, Any]:
    qid = getattr(item, "id", None)
    meta = getattr(item, "meta", None) or {}

    user_asg, ok_parse = _parse_assignment(answer)
    if not ok_parse:
        log.info("Invalid CSP answer format", {"qid": qid, "answer": str(answer or "")})
        return {
            "ok": False,
            "error": 'Invalid answer format. Use JSON like {"A":1,"B":3} or text like "A=1, B=3", or "none".',
        }

    exp_found, exp_solution = _expected_from_item(item)
    if exp_found is None:
        exp_found2, exp_solution2, err = _try_solve_from_meta(item)
        if err is not None:
            log.warn("CSP evaluator missing expected answer", {"qid": qid, "error": err})
            return {"ok": False, "error": "csp evaluator missing expected answer"}
        exp_found, exp_solution = exp_found2, exp_solution2

    correct, score = _score(bool(exp_found), exp_solution, user_asg)

    resp: Dict[str, Any] = {"ok": True, "correct": correct, "score": score}

    if reveal or not correct:
        resp["correct_answer"] = {"found": exp_found, "solution": exp_solution}
        resp["correct_answer_text"] = "none" if not exp_found else _fmt_asg_text(exp_solution)
        resp["received"] = {"assignment": user_asg}
        resp["received_text"] = "none" if user_asg is None else _fmt_asg_text(user_asg)
        resp["explanation"] = _build_explanation(
            expected_found=bool(exp_found),
            expected_solution=exp_solution,
            user_assignment=user_asg,
        )

    log.info(
        "CSP evaluated",
        {
            "qid": qid,
            "correct": correct,
            "score": score,
            "received": user_asg,
            "expected_found": exp_found,
            "expected_solution": exp_solution,
        },
    )

    return resp