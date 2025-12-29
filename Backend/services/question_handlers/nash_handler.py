from __future__ import annotations

from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.question_generator import QuestionGenerator
from Backend.core.game_theory.nash.NashInstanceGenerator import NashInstanceGenerator
from Backend.core.game_theory.nash.nash_pure_solver import NashPureSolver
from Backend.services import Logger
from Backend.services.question_handlers.utils import clamp_int, call_game_generator

log = Logger("QH.Nash")


class NashQuestionHandler:
    def __init__(self, qgen: QuestionGenerator):
        self.qgen = qgen

    @staticmethod
    def can_handle(ch_num: int, sub_num: int) -> bool:
        return ch_num == 2 and sub_num in (1, 2, 3)

    def generate(self, ch_num: int, sub_num: int, template_text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        if (ch_num, sub_num) == (2, 1):
            return self._pure(ch_num, sub_num, template_text, options)
        if (ch_num, sub_num) == (2, 2):
            return self._mixed(ch_num, sub_num, template_text, options)
        return self._combined(ch_num, sub_num, template_text, options)

    def _pure(self, ch_num: int, sub_num: int, template_text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        m = clamp_int(options.get("m"), 2, 5, 2)
        n = clamp_int(options.get("n"), 2, 5, 2)

        inst = NashInstanceGenerator.generate_pure_game(m, n, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        question_text = self.qgen.render_question(template_text, {"instance": ascii_game})

        nash_list = NashPureSolver.find_nash_pure(inst["payoffs"])
        correct = "none" if not nash_list else ", ".join([f"({i+1},{j+1})" for i, j in nash_list])

        meta = {"type": "nash_pure", "m": m, "n": n, "payoffs": inst["payoffs"]}
        qa = store.put(ch_num, sub_num, question_text, correct, meta)

        log.info("Nash pure question generated", ctx={"m": m, "n": n, "correct": correct})

        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {"type": "nash_pure", "m": m, "n": n},
            },
        }

    def _mixed(self, ch_num: int, sub_num: int, template_text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        size = clamp_int(options.get("size"), 2, 3, 2)

        inst = call_game_generator(
            NashInstanceGenerator.generate_mixed_game,
            size=size,
            payoff_min=-9,
            payoff_max=9,
        )

        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        question_text = self.qgen.render_question(template_text, {"instance": ascii_game})

        correct = "mixed"
        meta = {
            "type": "nash_mixed",
            "size": size,
            "payoffs": inst["payoffs"],
            "mixed_equilibrium": inst.get("mixed_equilibrium"),
        }

        qa = store.put(ch_num, sub_num, question_text, correct, meta)

        log.info("Nash mixed question generated", ctx={"size": size})

        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {"type": "nash_mixed", "size": size},
            },
        }

    def _combined(self, ch_num: int, sub_num: int, template_text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        size = clamp_int(options.get("size"), 2, 3, 2)

        inst = call_game_generator(
            NashInstanceGenerator.generate_combined_game,
            size=size,
            payoff_min=-9,
            payoff_max=9,
        )

        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        question_text = self.qgen.render_question(template_text, {"instance": ascii_game})

        pure_eq = inst.get("pure_equilibria") or NashPureSolver.find_nash_pure(inst["payoffs"])
        pure_str = "none" if not pure_eq else ", ".join([f"({i+1},{j+1})" for i, j in pure_eq])

        correct = f"pure={pure_str}; mixed=exists"
        meta = {
            "type": "nash_combined",
            "size": size,
            "payoffs": inst["payoffs"],
            "pure_equilibria": pure_eq,
            "mixed_equilibrium": inst.get("mixed_equilibrium"),
        }

        qa = store.put(ch_num, sub_num, question_text, correct, meta)

        log.info("Nash combined question generated", ctx={"size": size})

        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {"type": "nash_combined", "size": size},
            },
        }