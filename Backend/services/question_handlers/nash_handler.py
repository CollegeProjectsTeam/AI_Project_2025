from __future__ import annotations

from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.question_generator import QuestionGenerator
from Backend.core.game_theory.nash.NashInstanceGenerator import NashInstanceGenerator
from Backend.core.game_theory.nash.nash_pure_solver import NashPureSolver
from Backend.services import Logger
from Backend.services.question_handlers.utils import clamp_int

log = Logger("QH.Nash")


class NashQuestionHandler:
    def __init__(self, qgen: QuestionGenerator):
        self.qgen = qgen

    @staticmethod
    def can_handle(ch_num: int, sub_num: int) -> bool:
        # Nash unified subchapter
        return (ch_num, sub_num) == (2, 1)

    def generate(self, ch_num: int, sub_num: int, template_text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        options = options or {}
        difficulty = str(options.get("difficulty") or "medium").strip().lower()
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"

        # Map difficulty -> kind
        if difficulty == "easy":
            kind = "pure"
        elif difficulty == "medium":
            kind = "mixed"
        else:
            kind = "combined"

        if kind == "pure":
            return self._pure(ch_num, sub_num, template_text, options, difficulty)

        # mixed + combined
        return self._square_game(ch_num, sub_num, template_text, options, difficulty, kind)

    def _pure(self, ch_num: int, sub_num: int, template_text: str, options: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
        m = clamp_int(options.get("m"), 2, 5, 2)
        n = clamp_int(options.get("n"), 2, 5, 2)

        inst = NashInstanceGenerator.generate_pure_game(m, n, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)

        question_text = self.qgen.render_template(template_text, {"instance": ascii_game}).strip()

        nash_list = NashPureSolver.find_nash_pure(inst["payoffs"])
        correct = "none" if not nash_list else ", ".join([f"({i+1},{j+1})" for i, j in nash_list])

        meta = {
            "type": "nash",
            "difficulty": difficulty,
            "kind": "pure",
            "m": m,
            "n": n,
            "payoffs": inst.get("payoffs"),
        }

        qa = store.put(ch_num, sub_num, question_text, correct, meta)

        log.info("Nash generated", ctx={"difficulty": difficulty, "kind": "pure", "m": m, "n": n, "correct": correct})

        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {
                    "type": "nash",
                    "difficulty": difficulty,
                    "kind": "pure",
                    "m": m,
                    "n": n,
                },
            },
        }

    def _square_game(
        self,
        ch_num: int,
        sub_num: int,
        template_text: str,
        options: Dict[str, Any],
        difficulty: str,
        kind: str,  # mixed | combined
    ) -> Dict[str, Any]:
        size = clamp_int(options.get("size"), 2, 3, 2)

        if kind == "mixed":
            inst = NashInstanceGenerator.generate_mixed_game(size, payoff_min=-9, payoff_max=9)
        else:
            inst = NashInstanceGenerator.generate_combined_game(size, payoff_min=-9, payoff_max=9)

        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        question_text = self.qgen.render_template(template_text, {"instance": ascii_game}).strip()

        # NOTE: momentan pastram "corect" simplu, pana faci checker dedicat pt mixed/combined.
        if kind == "mixed":
            correct = "mixed"
        else:
            pure_eq = inst.get("pure_equilibria") or NashPureSolver.find_nash_pure(inst["payoffs"])
            pure_str = "none" if not pure_eq else ", ".join([f"({i+1},{j+1})" for i, j in pure_eq])
            correct = f"pure={pure_str}; mixed=exists"

        meta = {
            "type": "nash",
            "difficulty": difficulty,
            "kind": kind,
            "size": size,
            "payoffs": inst.get("payoffs"),
            "pure_equilibria": inst.get("pure_equilibria"),
            "mixed_equilibrium": inst.get("mixed_equilibrium"),
        }

        qa = store.put(ch_num, sub_num, question_text, correct, meta)

        log.info("Nash generated", ctx={"difficulty": difficulty, "kind": kind, "size": size})

        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {
                    "type": "nash",
                    "difficulty": difficulty,
                    "kind": kind,
                    "size": size,
                },
            },
        }
