import random
from Backend.core.game_theory.NashPureSolver import NashPureSolver
from Backend.core.game_theory.NashMixedSolver import NashMixedSolver


class NashInstanceGenerator:
    @staticmethod
    def _random_payoffs(m, n, payoff_min=-9, payoff_max=9):
        return [
            [
                [random.randint(payoff_min, payoff_max), random.randint(payoff_min, payoff_max)]
                for _ in range(n)
            ]
            for _ in range(m)
        ]

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

    @staticmethod
    def _rps_3x3():
        a1 = ["A1", "A2", "A3"]
        b1 = ["B1", "B2", "B3"]
        p1 = [
            [0, -1, 1],
            [1, 0, -1],
            [-1, 1, 0]
        ]
        payoffs = []
        for i in range(3):
            row = []
            for j in range(3):
                row.append([p1[i][j], -p1[i][j]])
            payoffs.append(row)
        return {
            "problem_name": "Nash Equilibrium (Mixed)",
            "actions_p1": a1,
            "actions_p2": b1,
            "payoffs": payoffs,
            "mixed_equilibrium": {
                "p1": [1 / 3, 1 / 3, 1 / 3],
                "p2": [1 / 3, 1 / 3, 1 / 3]
            }
        }

    @staticmethod
    def generate_mixed_game(size, payoff_min=-9, payoff_max=9):
        if size < 2:
            raise ValueError("size must be >= 2")

        m = n = size

        while True:
            actions_p1 = [f"A{i+1}" for i in range(m)]
            actions_p2 = [f"B{j+1}" for j in range(n)]
            payoffs = NashInstanceGenerator._random_payoffs(m, n, payoff_min, payoff_max)

            pure_eq = NashPureSolver.find_nash_pure(payoffs)
            if pure_eq:
                continue

            mixed_eq = NashMixedSolver.solve(payoffs)
            if mixed_eq is None:
                continue

            return {
                "problem_name": "Nash Equilibrium (Mixed)",
                "actions_p1": actions_p1,
                "actions_p2": actions_p2,
                "payoffs": payoffs,
                "mixed_equilibrium": mixed_eq
            }

    @staticmethod
    def generate_combined_game(size, payoff_min=-9, payoff_max=9):
        if size < 2:
            raise ValueError("size must be >= 2")

        if size == 3:
            actions_p1 = ["A1", "A2", "A3"]
            actions_p2 = ["B1", "B2", "B3"]

            base = NashInstanceGenerator._rps_3x3()["payoffs"]
            payoffs = [
                [base[0][0], base[0][1], base[0][2]],
                [base[1][0], base[1][1], base[1][2]],
                [base[2][0], base[2][1], base[2][2]],
            ]

            payoffs[0][0] = [9, 9]
            payoffs[1][0] = [0, 2]
            payoffs[2][0] = [0, 2]
            payoffs[0][1] = [2, 0]
            payoffs[0][2] = [2, 0]

            pure_eq = NashPureSolver.find_nash_pure(payoffs)
            mixed_eq = NashMixedSolver.solve(payoffs)

            return {
                "problem_name": "Nash Equilibrium (Combined)",
                "actions_p1": actions_p1,
                "actions_p2": actions_p2,
                "payoffs": payoffs,
                "pure_equilibria": pure_eq,
                "mixed_equilibrium": mixed_eq
            }

        m = n = size
        actions_p1 = [f"A{i+1}" for i in range(m)]
        actions_p2 = [f"B{j+1}" for j in range(n)]
        payoffs = NashInstanceGenerator._random_payoffs(m, n, payoff_min, payoff_max)

        pure_eq = NashPureSolver.find_nash_pure(payoffs)
        mixed_eq = NashMixedSolver.solve(payoffs)

        return {
            "problem_name": "Nash Equilibrium (Combined)",
            "actions_p1": actions_p1,
            "actions_p2": actions_p2,
            "payoffs": payoffs,
            "pure_equilibria": pure_eq,
            "mixed_equilibrium": mixed_eq
        }

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
            rows += f"{a:<6} | " + " | ".join(row_cells) + "\n"

        return header + separator + rows
