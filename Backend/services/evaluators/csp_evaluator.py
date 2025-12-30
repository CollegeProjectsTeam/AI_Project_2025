from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

from Backend.services import Logger
from Backend.core.constrain_satisfaction_problems.instance_solver import CSPSolver

log = Logger("Eval.CSP")


def _parse_assignment(answer: Any) -> Tuple[Optional[Dict[str, int]], bool]:
    """
    Accepta mai multe formate:
      - dict: {"A":1,"B":3}
      - JSON string: '{"A":1,"B":3}'
      - string cu perechi: 'A=1, B=3' / 'A 1 B 3' / '(A,1) (B,3)'
    Return: (assignment, ok)
    """
    if answer is None:
        return None, False

    # direct dict
    if isinstance(answer, dict):
        out: Dict[str, int] = {}
        for k, v in answer.items():
            try:
                out[str(k)] = int(v)
            except Exception:
                continue
        return (out, True) if out else (None, False)

    s = str(answer or "").strip()
    if not s:
        return None, False

    # try JSON
    if s.startswith("{") and s.endswith("}"):
        try:
            obj = json.loads(s)
            if isinstance(obj, dict):
                out: Dict[str, int] = {}
                for k, v in obj.items():
                    try:
                        out[str(k)] = int(v)
                    except Exception:
                        continue
                return (out, True) if out else (None, False)
        except Exception:
            pass

    # parse pairs like A=1, B:2, C 3 etc.
    # capture var names (letters/underscores) followed by int
    pairs = re.findall(r"([A-Za-z_]\w*)\s*[:=]?\s*(-?\d+)", s)
    if not pairs:
        return None, False

    out2: Dict[str, int] = {}
    for var, num in pairs:
        try:
            out2[str(var)] = int(num)
        except Exception:
            continue

    return (out2, True) if out2 else (None, False)


def _expected_from_item(item: Any) -> Tuple[Optional[bool], Optional[Dict[str, int]]]:
    """
    Intoarce (found, solution) daca le gaseste in meta/correct_answer.
    """
    meta = getattr(item, "meta", None) or {}

    # 1) din meta.solution (daca o pui in meta)
    sol = meta.get("solution")
    if isinstance(sol, dict):
        found = sol.get("found")
        solution = sol.get("solution")
        if isinstance(found, bool) and (isinstance(solution, dict) or solution is None):
            if isinstance(solution, dict):
                norm: Dict[str, int] = {}
                for k, v in solution.items():
                    try:
                        norm[str(k)] = int(v)
                    except Exception:
                        continue
                return found, norm
            return found, None

    # 2) din correct_answer (daca ai salvat json sau string dict)
    corr = getattr(item, "correct_answer", None)
    if corr is None:
        return None, None

    s = str(corr).strip()
    if not s:
        return None, None

    # prefer json
    if s.startswith("{") and s.endswith("}"):
        try:
            obj = json.loads(s.replace("'", '"'))  # tolerate python dict string
            if isinstance(obj, dict):
                found = obj.get("found")
                solution = obj.get("solution")
                if isinstance(found, bool):
                    if isinstance(solution, dict):
                        norm2: Dict[str, int] = {}
                        for k, v in solution.items():
                            try:
                                norm2[str(k)] = int(v)
                            except Exception:
                                continue
                        return found, norm2
                    if solution is None:
                        return found, None
        except Exception:
            pass

    return None, None


def _try_solve_from_meta(item: Any) -> Tuple[Optional[bool], Optional[Dict[str, int]], Optional[str]]:
    meta = getattr(item, "meta", None) or {}

    inst = meta.get("instance")
    if not isinstance(inst, dict):
        # uneori ai meta.instance.instance (daca ai pus payload complet)
        if isinstance(meta.get("payload"), dict):
            inst = meta["payload"].get("instance")

    if not isinstance(inst, dict):
        return None, None, "missing instance in meta"

    # rebuild full payload for solver (settings are optional, solver has defaults)
    payload = {
        "inference": (meta.get("settings") or {}).get("inference", "NONE"),
        "var_heuristic": (meta.get("settings") or {}).get("var_heuristic", "FIXED"),
        "value_heuristic": (meta.get("settings") or {}).get("value_heuristic", "NONE"),
        "consistency": (meta.get("settings") or {}).get("consistency", "NONE"),
        "ask_for": (meta.get("settings") or {}).get("ask_for", "TRACE_UNTIL_SOLUTION"),
        "instance": inst,
    }

    solved = CSPSolver.solve(payload, strict=True)
    if not solved.get("ok"):
        return None, None, str(solved.get("error") or "csp solver failed")

    found = bool(solved.get("found"))
    sol = solved.get("solution")
    if isinstance(sol, dict):
        norm: Dict[str, int] = {}
        for k, v in sol.items():
            try:
                norm[str(k)] = int(v)
            except Exception:
                continue
        return found, norm, None

    return found, None, None


def _build_explanation(
    expected_found: bool,
    expected_solution: Optional[Dict[str, int]],
    user_assignment: Optional[Dict[str, int]],
    meta: Dict[str, Any],
) -> str:
    settings = meta.get("settings") or {}

    def _fmt_asg(asg: Optional[Dict[str, int]]) -> str:
        if not asg:
            return "{}"
        return json.dumps(asg, ensure_ascii=False, sort_keys=True)

    lines = [
        "Constraint Satisfaction Problems (CSP) are solved via Backtracking with optional optimizations.",
        "Supported optimizations here:",
        "- MRV (Minimum Remaining Values) for variable selection",
        "- LCV (Least Constraining Value) for value ordering",
        "- FC (Forward Checking) for inference",
        "- AC-3 (Arc Consistency) for consistency enforcement",
        "",
        'Answer format accepted: JSON assignment like {"A":1,"B":3} or text like A=1, B=3.',
        "",
        f"Expected solution found = {expected_found}",
        f"Expected solution = {_fmt_asg(expected_solution) if expected_solution is not None else 'None'}",
        f"Received solution = {_fmt_asg(user_assignment)}",
        "",
        f"Settings = {json.dumps(settings, ensure_ascii=False, sort_keys=True)}",
    ]
    return "\n".join(lines)


def evaluate_csp(item: Any, answer: Any, reveal: bool = False) -> Dict[str, Any]:
    qid = getattr(item, "id", None)
    meta = getattr(item, "meta", None) or {}

    user_asg, ok_parse = _parse_assignment(answer)
    if not ok_parse:
        log.info("Invalid CSP answer format", {"qid": qid, "answer": str(answer or "")})
        return {
            "ok": False,
            "error": 'Invalid answer format. Use JSON like {"A":1,"B":3} or text like "A=1, B=3".',
        }

    exp_found, exp_solution = _expected_from_item(item)

    if exp_found is None:
        exp_found2, exp_solution2, err = _try_solve_from_meta(item)
        if err is not None:
            log.warn("CSP evaluator missing expected answer", {"qid": qid, "error": err})
            return {"ok": False, "error": "csp evaluator missing expected answer"}
        exp_found, exp_solution = exp_found2, exp_solution2

    # scoring:
    # - daca problema NU are solutie: user trebuie sa spuna "none"/{}? (nu avem format explicit)
    # - deocamdata evaluam strict: daca are solutie, assignment trebuie sa fie exact acelasi (ok pentru generatorul tau)
    if not exp_found:
        # Acceptam doua raspunsuri: gol/None/"none" (dar parser nu accepta "none")
        # Ca sa fie consistent: cerem FE sa trimita {"_no_solution":1} sau ceva.
        # Pentru moment, consideram incorect daca user trimite o asignare.
        correct = False
        score = 0.0
    else:
        correct = isinstance(exp_solution, dict) and (user_asg == exp_solution)
        score = 100.0 if correct else 0.0

    resp: Dict[str, Any] = {"ok": True, "correct": correct, "score": score}

    if reveal or not correct:
        resp["correct_answer"] = {"found": exp_found, "solution": exp_solution}
        resp["received"] = {"assignment": user_asg}
        resp["explanation"] = _build_explanation(
            expected_found=bool(exp_found),
            expected_solution=exp_solution,
            user_assignment=user_asg,
            meta=meta,
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