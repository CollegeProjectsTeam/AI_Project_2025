from __future__ import annotations

import json
import re
from typing import Any, Dict

from Backend.services.logging_service import Logger

log = Logger("QuestionGenerator")


class QuestionGenerator:
    def render_question(self, template_text: str, instance: Dict[str, Any]) -> str:
        if not isinstance(template_text, str) or not template_text.strip():
            log.warn("render_question called with empty template_text")
            return ""

        if not isinstance(instance, dict):
            log.warn("render_question called with non-dict instance", {"type": type(instance).__name__})
            instance = {}

        instance_str = self._instance_to_string(instance)
        text = self._apply_placeholders(template_text, instance, instance_str)
        text = self._cleanup_trailing_commas(text)

        log.ok(
            "Question rendered",
            {"problem_name": instance.get("problem_name"), "len": len(text)},
        )
        return text

    def _instance_to_string(self, instance: Dict[str, Any]) -> str:
        raw_instance = instance.get("instance")
        if isinstance(raw_instance, str):
            return "\n" + raw_instance.rstrip("\n") + "\n"
        return self._pretty_instance(instance)

    @staticmethod
    def _apply_placeholders(template_text: str, instance: Dict[str, Any], instance_str: str) -> str:
        text = template_text
        text = text.replace("{problem_name}", str(instance.get("problem_name", "")))
        text = text.replace("{instance}", instance_str)
        return text

    @staticmethod
    def _cleanup_trailing_commas(text: str) -> str:
        text = re.sub(r"\n}\n\s*,\s*(?=\w)", "\n}\n", text)
        text = re.sub(r"\n]\n\s*,\s*(?=\w)", "\n]\n", text)
        return text

    @staticmethod
    def _pretty_instance(instance: Dict[str, Any]) -> str:
        lines = ["{"]

        for k, v in instance.items():
            if k == "board" and isinstance(v, list):
                lines.extend(QuestionGenerator._format_board(v))
                continue
            lines.append(f'  "{k}": {json.dumps(v)},')

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
                lines.append(f"    {json.dumps(row)},")
        if lines and lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]
        lines.append("  ],")
        return lines