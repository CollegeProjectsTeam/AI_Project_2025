# core/testing_console.py
import sys

from persistence.dbConnex import db
from core.question_generator import QuestionGenerator

from core.console import menu_controller
from core.console import nqueens_runner
from core.console import nash_pure_runner
from core.console import nash_mixed_runner
from core.console import nash_combined_runner


class TestingConsole:
    def __init__(self):
        self.db = db
        self.qgen = QuestionGenerator()

    def run(self):
        while True:
            print("\n=== Testing Console ===")
            print("1. Generate Question")
            print("2. Exit")
            choice = input("Select option: ").strip()

            if choice == "2":
                print("Goodbye!")
                sys.exit(0)
            if choice != "1":
                print("Invalid option.")
                continue

            ch_num = menu_controller.choose_chapter(self.db)
            if ch_num is None:
                continue

            sub_num = menu_controller.choose_subchapter(self.db, ch_num)
            if sub_num is None:
                continue

            sub_name = menu_controller.get_subchapter_name(
                self.db, ch_num, sub_num
            ).lower()

            if "n-queen" in sub_name:
                nqueens_runner.run_nqueens(ch_num, sub_num, self.db, self.qgen)
            elif "nash equilibrium (pure)" in sub_name:
                nash_pure_runner.run_nash_pure(ch_num, sub_num, self.db, self.qgen)
            elif "nash equilibrium (mixed)" in sub_name:
                nash_mixed_runner.run_nash_mixed(ch_num, sub_num, self.db, self.qgen)
            elif "nash equilibrium (combined)" in sub_name:
                nash_combined_runner.run_nash_combined(
                    ch_num, sub_num, self.db, self.qgen
                )
            else:
                print("This subchapter is not implemented yet.")
