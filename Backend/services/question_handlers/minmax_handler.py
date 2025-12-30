from __future__ import annotations

from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.question_generator import QuestionGenerator
from Backend.core.game_theory.minmax import MinMaxInstanceGenerator, MinMaxAlphaBetaSolver
from Backend.services import Logger
from Backend.services.question_handlers.utils import clamp_int

log = Logger("QH.MinMax")


class MinMaxQuestionHandler:
    def __init__(self, qgen: QuestionGenerator):
        self.qgen = qgen

    @staticmethod
    def can_handle(ch_num: int, sub_num: int) -> bool:
        # ATENTIE: in FE ai MinMax la (2,2)
        return (ch_num, sub_num) == (2, 2)

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

        # reguli backend (oglindesc FE)
        rules = {
            "easy": {"depth": (1, 3, 2), "branching": (2, 3, 2)},
            "medium": {"depth": (1, 5, 3), "branching": (2, 4, 2)},
            "hard": {"depth": (1, 6, 4), "branching": (2, 4, 3)},
        }
        r = rules.get(difficulty, rules["medium"])

        depth = clamp_int(options.get("depth"), r["depth"][0], r["depth"][1], r["depth"][2])
        branching = clamp_int(options.get("branching"), r["branching"][0], r["branching"][1], r["branching"][2])

        root_player = str(options.get("root_player") or "MAX").strip().upper()
        if root_player not in ("MAX", "MIN"):
            root_player = "MAX"

        # optional: pe easy fortam MAX
        if difficulty == "easy":
            root_player = "MAX"

        instance = MinMaxInstanceGenerator.generate(
            depth=depth,
            branching=branching,
            value_min=-9,
            value_max=9,
            root_player=root_player,
        )

        question_text = (template_text or "").replace("{instance}", "").strip()

        solved = MinMaxAlphaBetaSolver.solve(instance)
        if not solved.get("ok"):
            log.warn("MinMax solver failed", {"error": solved.get("error")})
            return {"ok": False, "error": "minmax solver failed"}

        root_value = int(solved["root_value"])
        leaf_visits = int(solved["leaf_visits"])

        # easy: doar valoarea radacinii (conform template-urilor easy)
        if difficulty == "easy":
            correct_answer = f"{root_value}"
            answer_format = "root_value"
        else:
            correct_answer = f"{root_value} {leaf_visits}"
            answer_format = "root_value leaf_visits"

        tree = instance.get("tree")

        meta = {
            "type": "minmax",
            "difficulty": difficulty,
            "answer_format": answer_format,
            "depth": depth,
            "branching": branching,
            "root_player": root_player,
            "tree": tree,
        }

        qa = store.put(ch_num, sub_num, question_text, correct_answer, meta)

        log.info(
            "MinMax question generated",
            ctx={"difficulty": difficulty, "depth": depth, "branching": branching, "root_player": root_player},
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
