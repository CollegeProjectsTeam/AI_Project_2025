# core/game_theory/NashInstanceGenerator.py
import random
from core.game_theory.NashPureSolver import NashPureSolver
from core.game_theory.NashMixedSolver import NashMixedSolver


class NashInstanceGenerator:

    @staticmethod
    def _random_payoffs(m, n, payoff_min=-9, payoff_max=9):
        return [
            [
                [random.randint(payoff_min, payoff_max),
                 random.randint(payoff_min, payoff_max)]
                for _ in range(n)
            ]
            for _ in range(m)
        ]

    # ------------------------------------------------------------
    # PURE GENERATOR (fără restricții)
    # ------------------------------------------------------------
    @staticmethod
    def generate_pure_game(m, n, payoff_min=-9, payoff_max=9):
        actions_p1 = [f"A{i+1}" for i in range(m)]
        actions_p2 = [f"B{j+1}" for j in range(n)]
        payoffs = NashInstanceGenerator._random_payoffs(m, n, payoff_min, payoff_max)

        return {
            "problem_name": "Nash Equilibrium (Pure)",
            "actions_p1": actions_p1,
            "actions_p2": actions_p2,
            "payoffs": payoffs
        }

    # ------------------------------------------------------------
    # MIXED GENERATOR
    #  condiții:
    #   - NU există EN pur
    #   - există EN mixt (doar pentru 2×2 implementat acum)
    # ------------------------------------------------------------
    @staticmethod
    def generate_mixed_game(m, n, payoff_min=-9, payoff_max=9):

        if m != 2 or n != 2:
            raise ValueError("Mixed Nash solver is implemented only for 2×2 games.")

        while True:
            actions_p1 = [f"A{i+1}" for i in range(m)]
            actions_p2 = [f"B{j+1}" for j in range(n)]
            payoffs = NashInstanceGenerator._random_payoffs(m, n, payoff_min, payoff_max)

            # 1. Trebuie să NU existe EN pur
            pure_eq = NashPureSolver.find_nash_pure(payoffs)
            if len(pure_eq) != 0:
                continue

            # 2. Trebuie să existe EN mixt
            mixed_eq = NashMixedSolver.solve_2x2(payoffs)
            if mixed_eq is None:
                continue

            return {
                "problem_name": "Nash Equilibrium (Mixed)",
                "actions_p1": actions_p1,
                "actions_p2": actions_p2,
                "payoffs": payoffs,
                "mixed_equilibrium": mixed_eq
            }

    # ------------------------------------------------------------
    # COMBINED GENERATOR
    #  condiții:
    #    - TREBUIE să existe EN PUR
    #    - TREBUIE să existe EN MIXT
    # ------------------------------------------------------------
    @staticmethod
    def generate_combined_game(m, n, payoff_min=-9, payoff_max=9):

        if m != 2 or n != 2:
            raise ValueError("Combined Nash solver is implemented only for 2×2 games.")

        while True:
            actions_p1 = [f"A{i+1}" for i in range(m)]
            actions_p2 = [f"B{j+1}" for j in range(n)]
            payoffs = NashInstanceGenerator._random_payoffs(m, n, payoff_min, payoff_max)

            # EN pur
            pure_eq = NashPureSolver.find_nash_pure(payoffs)
            has_pure = len(pure_eq) > 0
            if not has_pure:
                continue

            # EN mixt
            mixed_eq = NashMixedSolver.solve_2x2(payoffs)
            has_mixed = mixed_eq is not None
            if not has_mixed:
                continue

            # Dacă ambele există → acceptăm jocul
            return {
                "problem_name": "Nash Equilibrium (Combined)",
                "actions_p1": actions_p1,
                "actions_p2": actions_p2,
                "payoffs": payoffs,
                "pure_equilibria": pure_eq,
                "mixed_equilibrium": mixed_eq
            }

    # ------------------------------------------------------------
    # DEFAULT = PURE
    # ------------------------------------------------------------
    @staticmethod
    def generate(m, n, payoff_min=-9, payoff_max=9):
        return NashInstanceGenerator.generate_pure_game(m, n, payoff_min, payoff_max)

    # ------------------------------------------------------------
    # ASCII DISPLAY
    # ------------------------------------------------------------
    @staticmethod
    def instance_to_text(instance):
        p1_actions = instance["actions_p1"]
        p2_actions = instance["actions_p2"]
        payoffs = instance["payoffs"]

        col_width = 9

        header = " " * 6 + " | " + " | ".join(f"{b:^{col_width}}" for b in p2_actions) + "\n"
        separator = "-" * (8 + (col_width + 3) * len(p2_actions)) + "\n"

        rows = ""
        for i, a in enumerate(p1_actions):
            row_cells = []
            for j in range(len(p2_actions)):
                p1v, p2v = payoffs[i][j]
                cell = f"({p1v},{p2v})"
                row_cells.append(f"{cell:^{col_width}}")
            row = f"{a:<6} | " + " | ".join(row_cells) + "\n"
            rows += row

        return header + separator + rows
