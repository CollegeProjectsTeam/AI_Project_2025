# Backend/services/question_service.py
from __future__ import annotations

from typing import Any, Dict

from Backend.core.question_generator import QuestionGenerator
from Backend.config.runtime_store import store
from Backend.persistence.services.question_template_service import get_template_text

from Backend.core.search_strategies.n_queens_problem.n_queens_instance_generator import (
    NQueensInstanceGenerator,
)
from Backend.core.search_strategies.n_queens_problem.n_queens_answear import (
    AlgorithmComparator,
)

from Backend.core.game_theory.NashInstanceGenerator import NashInstanceGenerator
from Backend.core.game_theory.NashPureSolver import NashPureSolver

qgen = QuestionGenerator()


def _clamp_int(v: Any, lo: int, hi: int, default: int) -> int:
    try:
        x = int(v)
    except Exception:
        return default
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def generate_question(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    One question at a time.
    Expected payload:
      {
        "chapter_number": int,
        "subchapter_number": int,
        "options": {...}
      }
    Returns:
      { "ok": True, "question": {...} } or { "ok": False, "error": "..." }
    """
    ch_num = int(payload.get("chapter_number") or 0)
    sub_num = int(payload.get("subchapter_number") or 0)
    options = payload.get("options") or {}

    if ch_num <= 0 or sub_num <= 0:
        return {"ok": False, "error": "chapter_number and subchapter_number are required"}

    template_text = get_template_text(ch_num, sub_num)
    if not template_text:
        return {"ok": False, "error": "no template found for this chapter/subchapter"}

    # -----------------------
    # 1) N-Queens (Chapter 1, Sub 1)
    # options: { "n": 4 }
    # -----------------------
    if (ch_num, sub_num) == (1, 1):
        n = _clamp_int(options.get("n"), 4, 12, 4)

        instance = NQueensInstanceGenerator.generate(n)
        question_text = qgen.render_question(template_text, instance)

        comp = AlgorithmComparator.compare_algorithms(instance["board"])
        if comp is None:
            return {"ok": False, "error": "no valid solution found by any algorithm"}

        correct = comp["fastest_algorithm"]
        meta = {
            "type": "nqueens",
            "n": n,
            "choices": comp.get("times_vector"),
            "percentages": comp.get("time_percentages"),
        }

        qa = store.put(ch_num, sub_num, question_text, correct, meta)
        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {"type": "nqueens", "n": n},
            },
        }

    # -----------------------
    # 2) Nash Pure (Chapter 2, Sub 1)
    # options: { "m": 2..5, "n": 2..5 }
    # -----------------------
    if (ch_num, sub_num) == (2, 1):
        m = _clamp_int(options.get("m"), 2, 5, 2)
        n = _clamp_int(options.get("n"), 2, 5, 2)

        inst = NashInstanceGenerator.generate_pure_game(m, n, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)

        question_text = qgen.render_question(template_text, {"instance": ascii_game})

        nash_list = NashPureSolver.find_nash_pure(inst["payoffs"])
        if not nash_list:
            correct = "none"
        else:
            correct = ", ".join([f"({i+1},{j+1})" for i, j in nash_list])

        meta = {"type": "nash_pure", "m": m, "n": n, "payoffs": inst["payoffs"]}
        qa = store.put(ch_num, sub_num, question_text, correct, meta)

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

    # -----------------------
    # 3) Nash Mixed (Chapter 2, Sub 2)
    # options: { "size": 2 or 3 }
    # -----------------------
    if (ch_num, sub_num) == (2, 2):
        size = _clamp_int(options.get("size"), 2, 3, 2)

        inst = NashInstanceGenerator.generate_mixed_game(size, size, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)

        question_text = qgen.render_question(template_text, {"instance": ascii_game})

        # Keep answer in meta for now; FE can show later nicely
        correct = "mixed"
        meta = {
            "type": "nash_mixed",
            "size": size,
            "payoffs": inst["payoffs"],
            "mixed_equilibrium": inst.get("mixed_equilibrium"),
        }

        qa = store.put(ch_num, sub_num, question_text, correct, meta)

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

    # -----------------------
    # 4) Nash Combined (Chapter 2, Sub 3)
    # options: { "size": 2 or 3 }
    # -----------------------
    if (ch_num, sub_num) == (2, 3):
        size = _clamp_int(options.get("size"), 2, 3, 2)

        inst = NashInstanceGenerator.generate_combined_game(size, size, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)

        question_text = qgen.render_question(template_text, {"instance": ascii_game})

        # Pure equilibria (as readable coords)
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

    return {"ok": False, "error": "this subchapter is not implemented yet"}
