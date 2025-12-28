from typing import Any, Dict

from Backend.core.question_generator import QuestionGenerator
from Backend.config.runtime_store import store
from Backend.persistence.services.question_template_service import get_template_text

from Backend.core.search_strategies.n_queens_problem.n_queens_instance_generator import NQueensInstanceGenerator
from Backend.core.search_strategies.n_queens_problem.n_queens_answear import AlgorithmComparator

from Backend.core.game_theory.NashInstanceGenerator import NashInstanceGenerator
from Backend.core.game_theory.NashPureSolver import NashPureSolver
from Backend.core.nash_utils import parse_nash_answer, evaluate_nash_answer, format_eq_list

qgen = QuestionGenerator()

def _as_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default

def generate_question(payload: Dict[str, Any]) -> Dict[str, Any]:
    ch = _as_int(payload.get("chapter_number"))
    sc = _as_int(payload.get("subchapter_number"))
    options = payload.get("options") or {}

    if ch <= 0 or sc <= 0:
        return {"ok": False, "error": "chapter_number and subchapter_number are required"}

    template_text = get_template_text(ch, sc)
    if not template_text:
        return {"ok": False, "error": "no template found for this chapter/subchapter"}

    if (ch, sc) == (1, 1):
        n = _as_int(options.get("n"), 4)
        if n < 4:
            n = 4
        instance = NQueensInstanceGenerator.generate(n)
        question_text = qgen.render_question(template_text, instance)
        comp = AlgorithmComparator.compare_algorithms(instance["board"])
        if comp is None:
            return {"ok": False, "error": "no solution found by any algorithm"}
        correct = comp["fastest_algorithm"]
        qa = store.put(ch, sc, "nqueens", question_text, correct, {"n": n, "details": comp})
        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch,
                "subchapter_number": sc,
                "type": "nqueens",
                "question_text": qa.question_text,
                "meta": {"n": n}
            }
        }

    if (ch, sc) == (2, 1):
        m = _as_int(options.get("m"), 2)
        n = _as_int(options.get("n"), 2)
        if m < 2:
            m = 2
        if n < 2:
            n = 2
        if m > 5:
            m = 5
        if n > 5:
            n = 5
        inst = NashInstanceGenerator.generate_pure_game(m, n, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        templ_instance = {"instance": ascii_game}
        question_text = qgen.render_question(template_text, templ_instance)
        nash_list = NashPureSolver.find_nash_pure(inst["payoffs"])
        correct = format_eq_list(nash_list)
        qa = store.put(ch, sc, "nash_pure", question_text, {"m": m, "n": n, "eq": nash_list, "payoffs": inst["payoffs"]}, {"m": m, "n": n})
        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch,
                "subchapter_number": sc,
                "type": "nash_pure",
                "question_text": qa.question_text,
                "meta": {"m": m, "n": n}
            }
        }

    if (ch, sc) == (2, 2):
        size = _as_int(options.get("size"), 2)
        if size not in (2, 3):
            size = 2
        inst = NashInstanceGenerator.generate_mixed_game(size, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        templ_instance = {"instance": ascii_game}
        question_text = qgen.render_question(template_text, templ_instance)
        correct = inst.get("mixed_equilibrium")
        qa = store.put(ch, sc, "nash_mixed", question_text, correct, {"size": size, "payoffs": inst["payoffs"]})
        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch,
                "subchapter_number": sc,
                "type": "nash_mixed",
                "question_text": qa.question_text,
                "meta": {"size": size}
            }
        }

    if (ch, sc) == (2, 3):
        size = _as_int(options.get("size"), 2)
        if size not in (2, 3):
            size = 2
        inst = NashInstanceGenerator.generate_combined_game(size, payoff_min=-9, payoff_max=9)
        ascii_game = NashInstanceGenerator.instance_to_text(inst)
        templ_instance = {"instance": ascii_game}
        question_text = qgen.render_question(template_text, templ_instance)
        pure_eq = inst.get("pure_equilibria") or []
        correct = {"pure": pure_eq, "mixed": inst.get("mixed_equilibrium")}
        qa = store.put(ch, sc, "nash_combined", question_text, correct, {"size": size, "payoffs": inst["payoffs"], "pure": pure_eq})
        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch,
                "subchapter_number": sc,
                "type": "nash_combined",
                "question_text": qa.question_text,
                "meta": {"size": size}
            }
        }

    return {"ok": False, "error": "this subchapter is not implemented yet"}

def check_answer(payload: Dict[str, Any]) -> Dict[str, Any]:
    qid = (payload.get("question_id") or "").strip()
    ans = (payload.get("answer") or "").strip()

    if not qid:
        return {"ok": False, "error": "question_id is required"}

    item = store.get(qid)
    if not item:
        return {"ok": False, "error": "question not found in runtime store"}

    if item.qtype == "nqueens":
        correct = str(item.correct_answer or "").strip().lower()
        user = ans.lower()
        ok = user == correct
        return {
            "ok": True,
            "correct": ok,
            "correct_answer": item.correct_answer
        }

    if item.qtype == "nash_pure":
        meta = item.correct_answer or {}
        payoffs = meta.get("payoffs")
        eq = meta.get("eq") or []
        m = meta.get("m") or 2
        n = meta.get("n") or 2
        user_pairs, user_none = parse_nash_answer(ans, m, n, payoffs)
        score, hits, missing, wrong = evaluate_nash_answer(eq, user_pairs, user_none)
        return {
            "ok": True,
            "correct": score == 100.0,
            "score": score,
            "correct_answer": format_eq_list(eq),
            "details": {
                "hits": hits,
                "missing": missing,
                "wrong": wrong
            }
        }

    return {
        "ok": True,
        "correct": False,
        "error": "checking not implemented for this question type yet"
    }
