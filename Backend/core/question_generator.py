from __future__ import annotations

import json
import re
from typing import Any, Dict

from Backend.services.logging_service import Logger

log = Logger("QuestionGenerator")


class QuestionGenerator:
    """
    Tiny template renderer for question templates.

    - Backward compatible: render_question(template_text, instance_dict)
    - Improved: safe placeholder replacement for any {key} in template (keeps unknown placeholders as-is)
    - Pretty prints dict/list values when injected
    """

    def render_question(self, template_text: str, instance: Dict[str, Any]) -> str:
        """
        Backward-compatible wrapper.

        Historically you called:
            render_question(template_text, {"problem_name": ..., "instance": ...})

        This now uses the generalized render_template underneath.
        """
        if not isinstance(template_text, str) or not template_text.strip():
            log.warn("render_question called with empty template_text")
            return ""

        if not isinstance(instance, dict):
            log.warn("render_question called with non-dict instance", {"type": type(instance).__name__})
            instance = {}

        instance_str = self._instance_to_string(instance)

        vars_map = dict(instance or {})
        vars_map["instance"] = instance_str  # ensure {instance} always becomes formatted string

        text = self.render_template(template_text, vars_map)

        log.ok("Question rendered", {"len": len(text)})
        return text

    def render_template(self, template_text: str, vars_map: Dict[str, Any] | None) -> str:
        """
        Safe formatter for templates that may contain:
          {problem_name}, {instance}, {options}, {ask_for}, {statement}, etc.
        """
        if not isinstance(template_text, str) or not template_text.strip():
            log.warn("render_template called with empty template_text")
            return ""

        vars_map = vars_map or {}

        class _SafeDict(dict):
            def __missing__(self, key: str) -> str:
                return "{" + key + "}"

        def _fmt(v: Any) -> str:
            # already prepared multiline string (like instance_str)
            if isinstance(v, str):
                return v
            if isinstance(v, (dict, list)):
                return json.dumps(v, ensure_ascii=False, indent=2)
            return str(v)

        safe = _SafeDict({k: _fmt(v) for k, v in vars_map.items()})

        try:
            out = (template_text or "").format_map(safe)
        except Exception as ex:
            log.warn("Template format failed, returning raw template", {"error": str(ex)})
            out = template_text or ""

        out = self._cleanup_trailing_commas(out)
        return out.strip()

    def _instance_to_string(self, instance: Dict[str, Any]) -> str:
        raw_instance = instance.get("instance")

        # If you already provide an ASCII table string (Nash), keep it as-is.
        if isinstance(raw_instance, str):
            s = raw_instance.rstrip("\n")
            return "\n" + s + "\n"

        # If instance["instance"] is dict/list, pretty print it.
        if isinstance(raw_instance, (dict, list)):
            return "\n" + json.dumps(raw_instance, ensure_ascii=False, indent=2) + "\n"

        return self._pretty_instance(instance)

    @staticmethod
    def _cleanup_trailing_commas(text: str) -> str:
        # If some older templates include manual JSON-ish snippets
        text = re.sub(r"\n}\n\s*,\s*(?=\w)", "\n}\n", text)
        text = re.sub(r"\n]\n\s*,\s*(?=\w)", "\n]\n", text)
        return text

    @staticmethod
    def _pretty_instance(instance: Dict[str, Any]) -> str:
        lines = ["{"]

        for k, v in (instance or {}).items():
            if k == "board" and isinstance(v, list):
                lines.extend(QuestionGenerator._format_board(v))
                continue
            lines.append(f'  "{k}": {json.dumps(v, ensure_ascii=False)},')

        if lines and lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]

        lines.append("}")
        return "\n" + "\n".join(lines) + "\n"

    @staticmethod
    def _format_board(board: list) -> list[str]:
        lines = ['  "board": [']
        for row in board:
            if isinstance(row, list):
                lines.append(f"    {row},")
            else:
                lines.append(f"    {json.dumps(row, ensure_ascii=False)},")
        if lines and lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]
        lines.append("  ],")
        return lines
