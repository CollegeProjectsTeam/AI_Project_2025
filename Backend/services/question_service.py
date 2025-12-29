from __future__ import annotations

import inspect
from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.question_generator import QuestionGenerator
from Backend.core.search_strategies.n_queens_problem.n_queens_instance_generator import (
    NQueensInstanceGenerator,
)
from Backend.core.search_strategies.n_queens_problem.n_queens_answear import (
    AlgorithmComparator,
    string_name,
)
from Backend.core.game_theory.nash.NashInstanceGenerator import NashInstanceGenerator
from Backend.core.game_theory.nash.NashPureSolver import NashPureSolver
from Backend.persistence.services.question_template_service import get_template_text
from Backend.services import Logger

qgen = QuestionGenerator()
log = Logger("QuestionService")


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


def _call_game_generator(fn, size: int, payoff_min: int, payoff_max: int):
    sig = inspect.signature(fn)
    params = sig.parameters
    kwargs = {}

    if "size" in params:
        kwargs["size"] = size
    if "m" in params:
        kwargs["m"] = size
    if "n" in params:
        kwargs["n"] = size
    if "rows" in params:
        kwargs["rows"] = size
    if "cols" in params:
        kwargs["cols"] = size

    if "payoff_min" in params:
        kwargs["payoff_min"] = payoff_min
    if "payoff_max" in params:
        kwargs["payoff_max"] = payoff_max

    if "min_payoff" in params:
        kwargs["min_payoff"] = payoff_min
    if "max_payoff" in params:
        kwargs["max_payoff"] = payoff_max

    try:
        return fn(**kwargs)
    except TypeError:
        if len(params) == 1:
            return fn(size)
        if len(params) >= 2:
            try:
                return fn(size, size, payoff_min=payoff_min, payoff_max=payoff_max)
            except TypeError:
                return fn(size, size)


def generate_question(payload: Dict[str, Any]) -> Dict[str, Any]:
    ch_num = int(payload.get("chapter_number") or 0)
    sub_num = int(payload.get("subchapter_number") or 0)
    options = payload.get("options") or {}

    if ch_num <= 0 or sub_num <= 0:
        return {"ok": False, "error": "chapter_number and subchapter_number are required"}

    template_text = get_template_text(ch_num, sub_num)
    if not template_text:
        return {"ok": False, "error": "no template found for this chapter/subchapter"}

    # =========================
    # N-Queens (1,1)
    # =========================
    if (ch_num, sub_num) == (1, 1):
        n = _clamp_int(options.get("n"), 4, 12, 4)

        instance = NQueensInstanceGenerator.generate(n)
        question_text = qgen.render_question(template_text, instance)

        comp = AlgorithmComparator.compare_algorithms(instance["board"])
        if comp is None:
            return {"ok": False, "error": "no valid solution found by any algorithm"}

        algo_keys = getattr(AlgorithmComparator, "ALGORITHM_ORDER", [])
        algo_labels = [string_name(k) for k in algo_keys]

        correct = comp["fastest_algorithm_key"]

        # NEW: store comparison details for explanation on /check
        meta = {
            "type": "nqueens",
            "n": n,
            "answer_option_keys": algo_keys,
            "answer_options": algo_labels,

            # old fields (keep if FE uses them)
            "choices": comp.get("times_vector"),
            "percentages": comp.get("time_percentages"),

            # new explanation payload
            "nqueens_comparison": {
                "fastest_algorithm_key": comp.get("fastest_algorithm_key"),
                "fastest_algorithm": comp.get("fastest_algorithm"),
                "fastest_time_s": round(float(comp.get("execution_time") or 0.0), 6),
                "sorted_by": "time_desc",
                "timings": comp.get("timings") or [],
            },
        }

        log.info(
            "NQueens question generated",
            ctx={
                "n": n,
                "correct": correct,
                "timings_count": len(meta["nqueens_comparison"]["timings"]),
            },
        )

        qa = store.put(ch_num, sub_num, question_text, correct, meta)
        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {
                    "type": "nqueens",
                    "n": n,
                    "answer_option_keys": algo_keys,
                    "answer_options": algo_labels,
                },
            },
        }

    # =========================
    # nash Pure (2,1)
    # =========================
    if (ch_num, sub_num) == (2, 1):
        m = _clamp_int(options.get("m"), 2, 5, 2)
        n = _clamp_int(options.get("n"), 2, 5, 2)

        inst = NashInstanceGenerator.generate_pure_game(m, n, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)

        question_text = qgen.render_question(template_text, {"instance": ascii_game})

        nash_list = NashPureSolver.find_nash_pure(inst["payoffs"])
        correct = "none" if not nash_list else ", ".join([f"({i+1},{j+1})" for i, j in nash_list])

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

    # =========================
    # nash Mixed (2,2)
    # =========================
    if (ch_num, sub_num) == (2, 2):
        size = _clamp_int(options.get("size"), 2, 3, 2)

        inst = _call_game_generator(
            NashInstanceGenerator.generate_mixed_game,
            size=size,
            payoff_min=-9,
            payoff_max=9,
        )

        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        question_text = qgen.render_question(template_text, {"instance": ascii_game})

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

    # =========================
    # nash Combined (2,3)
    # =========================
    if (ch_num, sub_num) == (2, 3):
        size = _clamp_int(options.get("size"), 2, 3, 2)

        inst = _call_game_generator(
            NashInstanceGenerator.generate_combined_game,
            size=size,
            payoff_min=-9,
            payoff_max=9,
        )

        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        question_text = qgen.render_question(template_text, {"instance": ascii_game})

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
