# core/console/nash_pure_runner.py

from core.game_theory.NashInstanceGenerator import NashInstanceGenerator
from core.game_theory.NashPureSolver import NashPureSolver
from core.console.db_utils import save_to_database
from core.console.nash_utils import (
    read_int_in_range,
    parse_nash_answer,
    evaluate_nash_answer,
    format_eq_list,
)


def run_nash_pure(ch_num, sub_num, db, qgen):
    print("\n--- Nash Equilibrium (Pure) ---")
    m = read_int_in_range(
        "Number of strategies for Player 1 (rows m, 2-5): ", 2, 5
    )
    n = read_int_in_range(
        "Number of strategies for Player 2 (cols n, 2-5): ", 2, 5
    )

    instance = NashInstanceGenerator.generate_pure_game(
        m, n, payoff_min=-9, payoff_max=9
    )
    ascii_game = NashInstanceGenerator.instance_to_text(instance)
    instance["instance_text"] = ascii_game

    print("\nGenerated Game:\n")
    print(ascii_game)

    templ_instance = {"instance": ascii_game}
    question_text = qgen.generate_question(ch_num, sub_num, templ_instance)

    payoffs = instance["payoffs"]
    nash_list = NashPureSolver.find_nash_pure(payoffs)

    if not nash_list:
        correct_answer_str = "Nu există echilibru Nash pur."
    else:
        correct_answer_str = ", ".join(
            [f"({i+1},{j+1})" for i, j in nash_list]
        )

    print("Introduceți răspunsul dumneavoastră.")
    print(" Formate acceptate:")
    print("  - 'none' dacă credeți că nu există EN pur")
    print("  - coordonate (linie,coloană): (2,2) sau 2 2  sau 2,2")
    print("  - sau payoff: de ex. (-2,-4) dacă vreți să indicați valoarea dintr-o singură celulă\n")

    ans_str = input("Your answer: ")

    user_pairs, user_said_none = parse_nash_answer(ans_str, m, n, payoffs)
    score, hits, missing, wrong = evaluate_nash_answer(
        nash_list, user_pairs, user_said_none
    )

    print("\n--- Evaluation ---")
    print(f"Score: {score:.2f}%")

    if nash_list:
        print(f"Total pure Nash equilibria: {len(nash_list)}")
        print(f"You correctly identified: {len(hits)}")
        if wrong:
            print(f"Extra wrong positions you claimed: {len(wrong)}")
    else:
        print("Ground truth: nu există EN pur.")
        if user_said_none and not user_pairs:
            print("You correctly answered: none.")
        else:
            print("You claimed some equilibria, but none exist.")

    show_correct = input("\nShow correct answer explicitly? (y/n): ").strip().lower()
    if show_correct == "y":
        print("\nCorrect Answer:", correct_answer_str)
        print("Note: (i,j) means row i, column j in the payoff matrix.")
        if nash_list:
            print(f"All pure Nash equilibria: {format_eq_list(nash_list)}")
            print(f"Your correct EN: {format_eq_list(hits)}")
            print(f"Missing EN: {format_eq_list(missing)}")
            if wrong:
                print(f"Wrong claimed EN: {format_eq_list(wrong)}")

    save = input("\nSave to database? (y/n): ").strip().lower()
    if save == "y":
        save_to_database(
            db, ch_num, sub_num, instance, question_text, correct_answer_str
        )
