from __future__ import annotations

import json
from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.constrain_satisfaction_problems.instance_generator import (
    CSPGenConfig,
    CSPInstanceGenerator,
)
from Backend.core.constrain_satisfaction_problems.instance_solver import CSPSolver
from Backend.core.question_generator import QuestionGenerator
from Backend.services import Logger
from Backend.services.question_handlers.utils import clamp_int

log = Logger("QH.CSP")


def _fmt(v: Any) -> str:
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, indent=2)
    return str(v)


def _render_template(template_text: str, vars: Dict[str, Any]) -> str:
    class _SafeDict(dict):
        def __missing__(self, key: str) -> str:
            return "{" + key + "}"

    safe = _SafeDict({k: _fmt(v) for k, v in (vars or {}).items()})
    try:
        return (template_text or "").format_map(safe)
    except Exception as ex:
        log.warn("Template render failed, returning raw template", {"error": str(ex)})
        return (template_text or "")


def _label_inference(code: str) -> str:
    code = (code or "").upper()
    if code == "FC":
        return "Forward Checking"
    if code == "NONE":
        return "No inference"
    return code


def _label_consistency(code: str) -> str:
    code = (code or "").upper()
    if code == "AC3":
        return "AC-3"
    if code == "NONE":
        return "None"
    return code


def _label_var_heuristic(code: str) -> str:
    code = (code or "").upper()
    if code == "MRV":
        return "MRV (Minimum Remaining Values)"
    if code == "NONE":
        return "None"
    return code


def _label_value_heuristic(code: str) -> str:
    code = (code or "").upper()
    if code == "LCV":
        return "LCV (Least Constraining Value)"
    if code == "NONE":
        return "None"
    return code


def _label_ask_for(code: str) -> str:
    code = (code or "").upper()
    if code == "FINAL_ASSIGNMENT":
        return "Find a valid assignment (or report none)."
    return code


def _display_instance(inst: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(inst or {})
    if not out.get("partial_assignment"):
        out.pop("partial_assignment", None)
    return out


class CSPQuestionHandler:
    def __init__(self, qgen: QuestionGenerator):
        self.qgen = qgen

    @staticmethod
    def can_handle(ch_num: int, sub_num: int) -> bool:
        return (ch_num, sub_num) == (3, 1)

    def generate(
        self,
        ch_num: int,
        sub_num: int,
        template_text: str,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        options = options or {}
        difficulty = str(options.get("difficulty") or "medium").strip().lower()
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"

        inference = str(options.get("inference") or "FC").strip().upper()
        consistency = str(options.get("consistency") or "NONE").strip().upper()
        var_heuristic = str(options.get("var_heuristic") or "NONE").strip().upper()
        value_heuristic = str(options.get("value_heuristic") or "LCV").strip().upper()

        # sanitize
        if inference not in ("NONE", "FC"):
            inference = "FC"
        if consistency not in ("NONE", "AC3"):
            consistency = "NONE"
        if var_heuristic not in ("NONE", "MRV"):
            var_heuristic = "NONE"
        if value_heuristic not in ("NONE", "LCV"):
            value_heuristic = "LCV"

        if difficulty == "easy":
            consistency = "NONE"
            value_heuristic = "NONE"

        rules = {
            "easy": {
                "vars": (2, 4, 3),
                "constraints": (1, 6, 3),
                "domMin": (1, 4, 2),
                "domMax": (1, 5, 4),
            },
            "medium": {
                "vars": (2, 6, 4),
                "constraints": (1, 12, 6),
                "domMin": (1, 8, 2),
                "domMax": (1, 10, 5),
            },
            "hard": {
                "vars": (2, 8, 6),
                "constraints": (1, 20, 12),
                "domMin": (1, 10, 2),
                "domMax": (1, 12, 6),
            },
        }
        r = rules.get(difficulty, rules["medium"])

        num_vars = clamp_int(options.get("num_vars"), r["vars"][0], r["vars"][1], r["vars"][2])
        num_constraints = clamp_int(options.get("num_constraints"), r["constraints"][0], r["constraints"][1], r["constraints"][2])

        domain_min_size = clamp_int(options.get("domain_min"), r["domMin"][0], r["domMin"][1], r["domMin"][2])
        domain_max_size = clamp_int(options.get("domain_max"), r["domMax"][0], r["domMax"][1], r["domMax"][2])
        if domain_max_size < domain_min_size:
            domain_max_size = domain_min_size

        cfg = CSPGenConfig(
            num_vars=num_vars,
            value_min=0,
            value_max=9,
            domain_min_size=domain_min_size,
            domain_max_size=domain_max_size,
            num_constraints=num_constraints,
            partial_assign_prob=0.0,
            seed=None,
        )

        ask_for = "FINAL_ASSIGNMENT"

        payload = CSPInstanceGenerator.generate_random_payload(
            cfg,
            inference=inference,
            var_heuristic=var_heuristic,
            value_heuristic=value_heuristic,
            consistency=consistency,
            ask_for=ask_for,
            fixed_order=(var_heuristic == "NONE"),
        )

        inst = payload.get("instance") or {}
        inst_display = _display_instance(inst)

        solved = CSPSolver.solve(payload, strict=True)
        if not solved.get("ok"):
            log.warn("CSP solver failed", {"error": solved.get("error")})
            return {"ok": False, "error": "csp solver failed"}

        found = bool(solved.get("found"))
        solution = solved.get("solution")
        stats = solved.get("stats") or {}

        solution_pack = {"found": found, "solution": solution, "stats": stats}
        correct_answer = json.dumps(solution_pack, ensure_ascii=False)

        settings = {
            "difficulty": difficulty,
            "inference": inference,
            "var_heuristic": var_heuristic,
            "value_heuristic": value_heuristic,
            "consistency": consistency,
            "ask_for": _label_ask_for(ask_for),
        }

        template_vars = {
            "statement": (template_text or "").strip(),
            "options": {
                "inference": inference,
                "consistency": consistency,
                "var_heuristic": var_heuristic,
                "value_heuristic": value_heuristic,
            },
            "ask_for": _label_ask_for(ask_for),
            "instance": inst_display,
            "answer_format": (
                'JSON: {"A":1,"B":3,"C":7}\n'
                "sau text: A=1, B=3, C=7\n"
                "daca nu exista solutie: none"
            ),
        }

        base_text = _render_template(template_text, template_vars).strip() or (
            "Rezolvati CSP-ul folosind Backtracking cu optimizarile mentionate."
        )

        format_help = (
            "\n\nFormat raspuns:\n"
            '- JSON: {"A":1,"B":3,"C":7}\n'
            "- sau text: A=1, B=3, C=7\n"
            "- daca nu exista solutie: none"
        )

        question_text = (base_text + format_help).strip()

        meta = {
            "type": "csp",
            "difficulty": difficulty,
            "answer_format": "assignment_or_json_or_none",
            "settings": settings,
            "instance": inst,
            "solution": solution_pack,
            "template_vars": template_vars,
            "labels": {
                "inference": _label_inference(inference),
                "consistency": _label_consistency(consistency),
                "var_heuristic": _label_var_heuristic(var_heuristic),
                "value_heuristic": _label_value_heuristic(value_heuristic),
            },
        }

        qa = store.put(ch_num, sub_num, question_text, correct_answer, meta)

        log.info(
            "CSP question generated",
            {
                "difficulty": difficulty,
                "found": found,
                "vars": len(inst.get("variables") or []),
                "constraints": len(inst.get("constraints") or []),
                "stats": stats,
            },
        )

        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": meta,
            },
        }
