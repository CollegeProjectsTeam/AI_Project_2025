# core/console/nash_combined_runner.py

from core.game_theory.NashInstanceGenerator import NashInstanceGenerator
from core.game_theory.NashPureSolver import NashPureSolver
from core.console.db_utils import save_to_database
from core.console.nash_utils import format_eq_list


def run_nash_combined(ch_num, sub_num, db, qgen):
    print("\n--- Nash Equilibrium (Combined) [WIP] ---")
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

    instance = NashInstanceGenerator.generate_combined_game(
        m, n, payoff_min=-9, payoff_max=9
    )
    ascii_game = NashInstanceGenerator.instance_to_text(instance)
    instance["instance_text"] = ascii_game

    print("\nGenerated Game (pure + mixed expected):\n")
    print(ascii_game)

    templ_instance = {"instance": ascii_game}
    question_text = qgen.generate_question(ch_num, sub_num, templ_instance)

    payoffs = instance["payoffs"]
    pure_eq = NashPureSolver.find_nash_pure(payoffs)

    if pure_eq:
        pure_str = format_eq_list(pure_eq)
    else:
        pure_str = "Nu există EN pur (doar mixt)."

    correct_answer_str = (
        f"EN pur: {pure_str} | EN mixt: EXISTĂ (detalii – solver mixt extern)."
    )

    print("\n[INFO] Combined: joc generat astfel încât să aibă și EN pur, și EN mixt.")
    show = input("Show detected pure-Nash positions now? (y/n): ").strip().lower()
    if show == "y":
        print(f"\nPure Nash (detected): {pure_str}")
        if pure_eq:
            print("Note: (i,j) means row i, column j in the payoff matrix.")

    save = input("Save this instance & question to DB? (y/n): ").strip().lower()
    if save == "y":
        save_to_database(
            db, ch_num, sub_num, instance, question_text, correct_answer_str
        )
