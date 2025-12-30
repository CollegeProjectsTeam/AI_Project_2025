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
    if code == "FIXED":
        return "Fixed order"
    return code


def _label_value_heuristic(code: str) -> str:
    code = (code or "").upper()
    if code == "LCV":
        return "LCV (Least Constraining Value)"
    if code == "NONE":
        return "No value ordering"
    return code


def _label_ask_for(code: str) -> str:
    code = (code or "").upper()
    if code == "TRACE_UNTIL_SOLUTION":
        return "Show the full backtracking trace until a solution is found (or failure)."
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

        inference = str(options.get("inference") or "FC").strip().upper()
        consistency = str(options.get("consistency") or "NONE").strip().upper()
        var_heuristic = str(options.get("var_heuristic") or "FIXED").strip().upper()
        value_heuristic = str(options.get("value_heuristic") or "LCV").strip().upper()

        if inference not in ("NONE", "FC"):
            inference = "FC"
        if consistency not in ("NONE", "AC3"):
            consistency = "NONE"
        if var_heuristic not in ("FIXED", "MRV"):
            var_heuristic = "FIXED"
        if value_heuristic not in ("NONE", "LCV"):
            value_heuristic = "LCV"

        num_vars = clamp_int(options.get("num_vars"), 2, 8, 3)

        max_pairs = num_vars * (num_vars - 1) // 2
        max_constraints = max(1, 2 * max_pairs)
        num_constraints = clamp_int(options.get("num_constraints"), 1, max_constraints, 3)

        domain_min_size = clamp_int(options.get("domain_min_size"), 1, 10, 2)
        domain_max_size = clamp_int(options.get("domain_max_size"), domain_min_size, 12, 4)

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

        ask_for = "TRACE_UNTIL_SOLUTION"

        payload = CSPInstanceGenerator.generate_random_payload(
            cfg,
            inference=inference,
            var_heuristic=var_heuristic,
            value_heuristic=value_heuristic,
            consistency=consistency,
            ask_for=ask_for,
            fixed_order=True,
        )

        inst = payload.get("instance") or {}
        inst_display = _display_instance(inst)
        inst_text = json.dumps(inst_display, ensure_ascii=False, indent=2)

        lines = []
        lines.append("Given the variables, domains and constraints, solve the CSP using Backtracking.")
        lines.append("")
        lines.append("Options:")

        lines.append(f"- Inference: {_label_inference(inference)}")

        if consistency != "NONE":
            lines.append(f"- Consistency: {_label_consistency(consistency)}")

        if var_heuristic != "FIXED":
            lines.append(f"- Variable heuristic: {_label_var_heuristic(var_heuristic)}")

        lines.append(f"- Value heuristic: {_label_value_heuristic(value_heuristic)}")
        lines.append("")
        lines.append("Task:")
        lines.append(f"- {_label_ask_for(ask_for)}")
        lines.append("")
        lines.append("Instance:")
        lines.append(inst_text)

        question_text = "\n".join(lines)

        solved = CSPSolver.solve(payload, strict=True)
        if not solved.get("ok"):
            log.warn("CSP solver failed", {"error": solved.get("error")})
            return {"ok": False, "error": "csp solver failed"}

        found = bool(solved.get("found"))
        solution = solved.get("solution")
        stats = solved.get("stats") or {}

        solution_pack = {"found": found, "solution": solution, "stats": stats}
        correct_answer = json.dumps(solution_pack, ensure_ascii=False)

        meta = {
            "type": "csp",
            "answer_format": "json",
            "settings": {
                "inference": inference,
                "var_heuristic": var_heuristic,
                "value_heuristic": value_heuristic,
                "consistency": consistency,
                "ask_for": ask_for,
            },
            "instance": inst,
            "solution": solution_pack,
        }

        qa = store.put(ch_num, sub_num, question_text, correct_answer, meta)

        log.info(
            "CSP question generated",
            {
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