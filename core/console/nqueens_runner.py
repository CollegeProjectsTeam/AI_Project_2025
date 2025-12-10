# core/console/nqueens_runner.py

from core.search_strategies.n_queens_problem.n_queens_instance_generator import (
    NQueensInstanceGenerator,
)
from core.search_strategies.n_queens_problem.n_queens_answear import (
    AlgorithmComparator,
)
from core.console.db_utils import save_to_database


def run_nqueens(ch_num, sub_num, db, qgen):
    try:
        while True:
            board_size = int(input("Enter board size N>=4 (default 4): ") or 4)
            if board_size < 4:
                print("Board size must be at least 4.")
                continue
            break
    except ValueError:
        print("Invalid number entered.")
        return

    instance = NQueensInstanceGenerator.generate(board_size)
    question_text = qgen.generate_question(ch_num, sub_num, instance)

    board_for_solver = instance.get("board")
    comparison_result = AlgorithmComparator.compare_algorithms(board_for_solver)

    if comparison_result is None:
        print("No valid solution found by any algorithm.")
        return

    fastest_alg = comparison_result["fastest_algorithm"]
    report = comparison_result["report"]
    percentages = comparison_result["time_percentages"]

    print("\nWhat do you think is the answer?")
    print(
        """
            1. BFS
            2. DFS
            3. Uniform Cost Search
            4. IDDFS
            5. Backtracking
            6. Bidirectional Search
            7. Greedy Best First
            8. Hill Climbing
            9. Simulated Annealing
            10. Beam Search
            11. A*
        """
    )

    algorithms = [
        "Best First Search",
        "Depth First Search",
        "Uniform Cost Search",
        "Iterative Deepening DFS",
        "Backtracking",
        "Bidirectional Search",
        "Greedy Best First",
        "Hill Climbing",
        "Simulated Annealing",
        "Beam Search",
        "A*",
    ]

    while True:
        ans = input("Your answer (1-11): ").strip()
        if ans in [str(i) for i in range(1, 12)]:
            ans = int(ans)
            break
        print("Please enter a number between 1 and 11.")

    chosen = algorithms[ans - 1]
    chosen_percent = percentages[ans - 1]

    if chosen == fastest_alg:
        print(f"Correct! {chosen} ({chosen_percent:.2f}% of fastest)")
    else:
        print(f"Incorrect. Correct answer = {fastest_alg}")

    show = input("Show explanation? (y/n): ").strip().lower()
    if show == "y":
        print("\n--- Explanation ---")
        print(report)

    save = input("Save to database? (y/n): ").strip().lower()
    if save == "y":
        save_to_database(db, ch_num, sub_num, instance, question_text, fastest_alg)
