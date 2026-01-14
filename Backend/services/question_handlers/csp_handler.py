from __future__ import annotations

"""
csp_handler.py

CSP question handler for Chapter 3, Subchapter 1 (Backtracking).

This handler:
- Reads generation options (difficulty + heuristics + numeric knobs)
- Clamps numeric knobs based on difficulty-specific rules (mirrors FE rules)
- Generates a random CSP instance payload using CSPInstanceGenerator
- Solves it using CSPSolver (strict validation)
- Stores the question + expected solution in the runtime store

Notes:
- `domain_min` / `domain_max` refer to domain *size* limits (how many values per variable),
  not numeric min/max of the values themselves.
- Values are currently generated in the range [0..9] via CSPGenConfig(value_min=0, value_max=9).
"""

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
    """
    Format values for safe template rendering.

    - Dict/list values are JSON pretty-printed (UTF-8, with diacritics).
    - Other values are converted using str().

    Args:
        v: Any value to format.

    Returns:
        A string representation suitable for template insertion.
    """
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, indent=2)
    return str(v)


def _render_template(template_text: str, vars: Dict[str, Any]) -> str:
    """
    Render a Python `.format_map(...)` template using a safe dictionary.

    Missing keys are preserved as `{key}` instead of raising KeyError.

    Args:
        template_text: Template string (may include `{placeholders}`).
        vars: Variables to inject into the template.

    Returns:
        Rendered text, or the raw template text if rendering fails.
    """

    class _SafeDict(dict):
        """Dict that returns `{missing_key}` when a key is missing."""
        def __missing__(self, key: str) -> str:
            return "{" + key + "}"

    safe = _SafeDict({k: _fmt(v) for k, v in (vars or {}).items()})
    try:
        return (template_text or "").format_map(safe)
    except Exception as ex:
        log.warn("Template render failed, returning raw template", {"error": str(ex)})
        return (template_text or "")


def _label_inference(code: str) -> str:
    """
    Convert inference code to a user-friendly label.

    Args:
        code: Inference code (e.g., "FC", "NONE").

    Returns:
        A human-readable label.
    """
    code = (code or "").upper()
    if code == "FC":
        return "Forward Checking"
    if code == "NONE":
        return "No inference"
    return code


def _label_consistency(code: str) -> str:
    """
    Convert consistency code to a user-friendly label.

    Args:
        code: Consistency code (e.g., "AC3", "NONE").

    Returns:
        A human-readable label.
    """
    code = (code or "").upper()
    if code == "AC3":
        return "AC-3"
    if code == "NONE":
        return "None"
    return code


def _label_var_heuristic(code: str) -> str:
    """
    Convert variable heuristic code to a user-friendly label.

    Args:
        code: Variable heuristic code (e.g., "MRV", "NONE").

    Returns:
        A human-readable label.
    """
    code = (code or "").upper()
    if code == "MRV":
        return "MRV (Minimum Remaining Values)"
    if code == "NONE":
        return "None"
    return code


def _label_value_heuristic(code: str) -> str:
    """
    Convert value heuristic code to a user-friendly label.

    Args:
        code: Value heuristic code (e.g., "LCV", "NONE").

    Returns:
        A human-readable label.
    """
    code = (code or "").upper()
    if code == "LCV":
        return "LCV (Least Constraining Value)"
    if code == "NONE":
        return "None"
    return code


def _label_ask_for(code: str) -> str:
    """
    Convert ask_for code to the statement shown to the user.

    Args:
        code: Ask-for code (e.g., "FINAL_ASSIGNMENT").

    Returns:
        The user-facing description.
    """
    code = (code or "").upper()
    if code == "FINAL_ASSIGNMENT":
        return "Find a valid assignment (or report none)."
    return code


def _display_instance(inst: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare an instance for display in the rendered question.

    Currently removes `partial_assignment` if it is empty (to reduce clutter).

    Args:
        inst: Raw instance dict.

    Returns:
        A cleaned copy of the instance dict.
    """
    out = dict(inst or {})
    if not out.get("partial_assignment"):
        out.pop("partial_assignment", None)
    return out


class CSPQuestionHandler:
    """
    Question handler for CSP (Backtracking) exercises.

    This handler is responsible for generating the CSP instance, solving it to obtain
    the expected output, rendering the user-facing prompt, and storing the QA item.
    """

    def __init__(self, qgen: QuestionGenerator):
        """
        Initialize the handler.

        Args:
            qgen: The global QuestionGenerator instance (kept for consistency with other handlers).
        """

        self.qgen = qgen

    @staticmethod
    def can_handle(ch_num: int, sub_num: int) -> bool:
        """
        Check if this handler supports the given chapter/subchapter.

        Args:
            ch_num: Chapter number.
            sub_num: Subchapter number.

        Returns:
            True if this handler can generate questions for the given chapter/subchapter.
        """
        return (ch_num, sub_num) == (3, 1)

    def generate(
        self,
        ch_num: int,
        sub_num: int,
        template_text: str,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
              Generate and store a CSP question.

              The generation uses:
              - FC (Forward Checking) inference (or NONE)
              - MRV / NONE variable heuristic
              - LCV / NONE value heuristic
              - AC3 / NONE consistency (enabled optionally)
              - Numeric knobs: num_vars, num_constraints, domain_min, domain_max
                clamped based on difficulty-specific rules.

              Args:
                  ch_num: Chapter number.
                  sub_num: Subchapter number.
                  template_text: Statement template (format string).
                  options: Options dictionary coming from the frontend.

              Returns:
                  Response dict:
                  - {"ok": True, "question": {...}} on success
                  - {"ok": False, "error": "..."} on failure
              """
        options = options or {}
        difficulty = str(options.get("difficulty") or "medium").strip().lower()
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"

        inference = str(options.get("inference") or "FC").strip().upper()
        consistency = str(options.get("consistency") or "NONE").strip().upper()
        var_heuristic = str(options.get("var_heuristic") or "NONE").strip().upper()
        value_heuristic = str(options.get("value_heuristic") or "LCV").strip().upper()

        # Sanitize / enforce supported codes.
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
                "vars": (2, 3, 3),
                "constraints": (1, 3, 3),
                "domMin": (2, 3, 2),
                "domMax": (2, 5, 3),
            },
            "medium": {
                "vars": (3, 4, 4),
                "constraints": (2, 5, 4),
                "domMin": (2, 8, 3),
                "domMax": (2, 10, 5),
            },
            "hard": {
                "vars": (2, 8, 6),
                "constraints": (1, 20, 12),
                "domMin": (2, 10, 3),
                "domMax": (2, 12, 6),
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
