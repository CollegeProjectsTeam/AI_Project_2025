import sys
import json
from persistence.dbConnex import db
from core.search_strategies.n_queens_problem.n_queens_instance_generator import NQueensInstanceGenerator
from core.question_generator import QuestionGenerator

class TestingConsole:
    """Console for generating problem instances and questions (currently supports N-Queens)."""

    def __init__(self):
        self.db = db
        self.qgen = QuestionGenerator()

    def choose_from_list(self, prompt, items):
        if not items:
            print("No items available.")
            return None
        for item in items:
            print(f"{item[0]}. {item[1]}")
        while True:
            sel = input(prompt).strip()
            if sel.lower() in ("q", "quit", "exit"):
                return None
            try:
                sel_num = int(sel)
                if any(item[0] == sel_num for item in items):
                    return sel_num
                print("Invalid number, choose one listed.")
            except ValueError:
                print("Enter numeric value.")

    def run(self):
        while True:
            print("\n=== Testing Console ===")
            print("1. Generate")
            print("2. Exit")
            choice = input("Select option: ").strip()

            if choice == "2":
                print("Goodbye!")
                sys.exit(0)
            if choice != "1":
                print("Invalid option.")
                continue

            chapters = self.db.execute_query(
                "SELECT chapter_number, chapter_name FROM chapters ORDER BY chapter_number;", fetch=True
            )
            ch_num = self.choose_from_list("Select chapter number (or q to cancel): ", chapters)
            if ch_num is None:
                continue

            subchapters = self.db.execute_query(
                "SELECT subchapter_number, subchapter_name FROM subchapters "
                "WHERE chapter_id=(SELECT id FROM chapters WHERE chapter_number=%s) "
                "ORDER BY subchapter_number;",
                (ch_num,), fetch=True
            )
            sub_num = self.choose_from_list("Select subchapter number (or q to cancel): ", subchapters)
            if sub_num is None:
                continue

            sub_name = next(s[1] for s in subchapters if s[0] == sub_num)
            if "n-queen" not in sub_name.lower():
                print("Only N-Queens subchapter is supported for now.")
                continue

            try:
                board_size = int(input("Enter board size N (default 4): ") or 4)
                num_queens = int(input("Enter number of queens (default N): ") or board_size)
                if num_queens > board_size:
                    print("Number of queens cannot exceed board size.")
                    continue
            except ValueError:
                print("Invalid number entered.")
                continue

            instance = NQueensInstanceGenerator.generate(board_size, num_queens)

            print("\n--- Generated N-Queens Instance ---")
            print("{")
            for k, v in instance.items():
                if k == "board":
                    print(f'  "{k}": [')
                    for row in v:
                        print(f"    {row},")
                    print("  ]")
                else:
                    print(f'  "{k}": {json.dumps(v)},')
            print("}")
            print("-----------------------------------")

            save = input("Save this instance to DB? (y/n): ").strip().lower()
            if save == "y":
                template = self.db.execute_query(
                    "SELECT id FROM question_templates "
                    "WHERE subchapter_id=(SELECT id FROM subchapters "
                    "WHERE chapter_id=(SELECT id FROM chapters WHERE chapter_number=%s) "
                    "AND subchapter_number=%s) LIMIT 1;",
                    (ch_num, sub_num), fetch=True
                )
                if not template:
                    print("No template found for this subchapter. Cannot save instance.")
                    continue
                template_id = template[0][0]

                instance_id = self.db.execute_query(
                    "INSERT INTO problem_instances (template_id, instance_params) VALUES (%s, %s) RETURNING id;",
                    (template_id, json.dumps(instance)), fetch=True
                )[0][0]
                instance["instance_id"] = instance_id
                print(f"Instance saved in DB with ID {instance_id}")

            generate_q = input("Generate question from this instance? (y/n): ").strip().lower()
            if generate_q == "y":
                self.qgen.generate_question(ch_num, sub_num, instance, save=True)