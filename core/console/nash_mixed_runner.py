# core/console/nash_mixed_runner.py

from core.game_theory.NashInstanceGenerator import NashInstanceGenerator
from core.console.db_utils import save_to_database


def run_nash_mixed(ch_num, sub_num, db, qgen):
    print("\n--- Nash Equilibrium (Mixed) [WIP] ---")
    m = int(input("Number of strategies for Player 1 (rows m, 2-3): ").strip() or "2")
    if m < 2:
        m = 2
    if m > 3:
        m = 3

    n = int(input("Number of strategies for Player 2 (cols n, 2-3): ").strip() or "2")
    if n < 2:
        n = 2
    if n > 3:
        n = 3

    instance = NashInstanceGenerator.generate_mixed_game(
        m, n, payoff_min=-9, payoff_max=9
    )
    ascii_game = NashInstanceGenerator.instance_to_text(instance)
    instance["instance_text"] = ascii_game

    print("\nGenerated Game (mixed-only expected):\n")
    print(ascii_game)

    templ_instance = {"instance": ascii_game}
    question_text = qgen.generate_question(ch_num, sub_num, templ_instance)

    print("\n[INFO] Solver pentru Nash mixt nu este încă integrat în interfață.")
    print("[INFO] Jocul este construit astfel încât să aibă EN mixt și să nu aibă EN pur.")

    correct_answer_str = "Nash mixt existent (detalii de probabilități – solver extern)."

    save = input("Save this instance & question to DB anyway? (y/n): ").strip().lower()
    if save == "y":
        save_to_database(
            db, ch_num, sub_num, instance, question_text, correct_answer_str
        )
