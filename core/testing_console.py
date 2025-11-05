import sys
import json
from core.search_strategies.n_queens_problem.n_queens_answear import AlgorithmComparator
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
                while True:
                    board_size = int(input("Enter board size N>=4 (default 4): ") or 4)
                    if board_size < 4:
                        print("Board size must be at least 4.")
                        continue
                    break
                # num_queens = int(input("Enter number of queens (default N): ") or board_size)
                # if num_queens > board_size:
                #     print("Number of queens cannot exceed board size.")
                #     continue
            except ValueError:
                print("Invalid number entered.")
                continue

            instance = NQueensInstanceGenerator.generate(board_size)

            
            # print("\n--- Generated N-Queens Instance ---")
            # print("{")
            # for k, v in instance.items():
            #     if k == "board":
            #         print(f'  "{k}": [')
            #         for row in v:
            #             print(f"    {row},")
            #         print("  ]")
            #     else:
            #         print(f'  "{k}": {json.dumps(v)},')
            # print("}")
            # print("-----------------------------------")

            # Generate question from the instance
            #self.qgen.generate_question(ch_num, sub_num, instance)
            question_text = self.qgen.generate_question(ch_num, sub_num, instance)

            board_for_solver = instance.get("board")

            # Compare algorithms and get the fastest one
            comparison_result = AlgorithmComparator.compare_algorithms(board_for_solver)

            # Handle case where no algorithm provides a solution
            if comparison_result is None:
                print("No valid solution could be found for this instance.")
                continue

            fastest_algorithm = comparison_result["fastest_algorithm"]
            fastest_time = comparison_result["execution_time"]
            fastest_solution = comparison_result["solution"]
            report_string = comparison_result["report"]
            correct_answer = fastest_algorithm
            time_percentages = comparison_result["time_percentages"]
            times_vector = comparison_result["times_vector"]

            algorithm_order = [
                'Best First Search',  
                'Depth First Search',
                'Uniform Cost Search',
                'Iterative Deepening DFS',
                'Backtracking',
                'Bidirectional Search',
                'Greedy Best First',
                'Hill Climbing',
                'Simulated Annealing',
                'Beam Search',
                'A*'
            ]

            print("What do you think is the answer?")
            print(""" 
                1.BFS
                2.DFS
                3.Uniform Cost Search
                4.IDDFS
                5.Backtracking
                6.Bidirectional Search
                7.Greedy Best First 
                8.Hill Climbing 
                9.Simulated Annealing
                10.Beam Search
                11.A*""")
            
            while True:
                user_answer = input("Your answer: ").strip().lower()
                if user_answer in [str(i) for i in range(1, 12)]:
                    user_answer = int(user_answer)
                    break
                print("Invalid answer. Please enter a number between 1 and 11.")

            chosen_algorithm = algorithm_order[user_answer - 1]
            chosen_percentage = time_percentages[user_answer - 1]    

            if fastest_algorithm == 'Best First Search' and user_answer == '1':
                print("Correct! The answer is Best First Search. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Depth First Search' and user_answer == '2':
                print("Correct! The answer is Depth First Search. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Uniform Cost Search' and user_answer == '3':
                print("Correct! The answer is Uniform Cost Search. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Iterative Deepening DFS' and user_answer == '4':
                print("Correct! The answer is Iterative Deepening DFS. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Backtracking' and user_answer == '5':
                print("Correct! The answer is Backtracking. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Bidirectional Search' and user_answer == '6':
                print("Correct! The answer is Bidirectional Search. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Greedy Best First' and user_answer == '7':
                print("Correct! The answer is Greedy Best First. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Hill Climbing' and user_answer == '8':
                print("Correct! The answer is Hill Climbing. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Simulated Annealing' and user_answer == '9':
                print("Correct! The answer is Simulated Annealing. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'Beam Search' and user_answer == '10':
                print("Correct! The answer is Beam Search. ({chosen_percentage:.2f}% of the best time")
            elif fastest_algorithm == 'A*' and user_answer == '11':
                print("Correct! The answer is A*.")
            else:
                print(f"Incorrect. The correct answer was: {fastest_algorithm}.")
                if chosen_percentage is not None:
                    print(f"Your algorithm ({chosen_algorithm}) took {chosen_percentage:.2f}% of the best time.")
                else:
                    print(f"Your algorithm ({chosen_algorithm}) took 0% of the best time.")

            #print(f"Fastest Algorithm: {fastest_algorithm} (Time: {fastest_time:.6f}s)")

            # Ask if the user wants to see the answer
            # show_answer = input("Do you want to see the answer? (y/n): ").strip().lower()
            # if show_answer == 'y':
            #     print("Answer:")
            #     print(fastest_algorithm, fastest_solution)

            print("Do you want to see the explication of the answer? (y/n): ")
            show_explication = input().strip().lower()
            if show_explication == "y":
                print("Explication:")
                print(f"Solution: {fastest_solution}")
                print(report_string)

            save = input("Save this instance to DB? (y/n): ").strip().lower()
            if save == "y":
                # get template_id
                template = self.db.execute_query(
                    """
                    SELECT qt.id 
                    FROM question_templates qt
                    JOIN subchapters sc ON qt.subchapter_id = sc.id
                    JOIN chapters c ON sc.chapter_id = c.id
                    WHERE c.chapter_number=%s AND sc.subchapter_number=%s LIMIT 1;
                    """,
                    (ch_num, sub_num), fetch=True
                )
                if not template:
                    print("No template found for this subchapter. Cannot save instance.")
                    continue
                template_id = template[0][0]

                # 2. save instance to problem_instances 
                result = self.db.execute_query(
                    "INSERT INTO problem_instances (template_id, instance_params) VALUES (%s, %s) RETURNING id;",
                    (template_id, json.dumps(instance)), fetch=True
                )
                if result:
                    instance_id = result[0][0]
                    instance["instance_id"] = instance_id
                    print(f"Instance saved in DB with ID {instance_id}")
                else:
                    print("Error saving problem instance to DB.")
                    continue
                # 3. save question-answer (using instance_id)
                placeholder_answer = correct_answer

                # Modify access to ID for safety
                qa_result = self.db.execute_query(
                    """
                    INSERT INTO questions_answers
                    (instance_id, generated_question, correct_answer, variables_used)
                    VALUES (%s, %s, %s, %s) RETURNING id;
                    """,
                    (
                        instance_id,
                        question_text,
                        placeholder_answer,
                        json.dumps(instance)
                    ),
                    fetch=True
                )

                # check if insertion was successful
                if qa_result:
                    qa_id = qa_result[0][0]
                    print(f"Question-answer saved in DB with ID {qa_id}")
                else:
                    print("Error saving question-answer to DB.")


            
                # placeholder_answer = correct_answer
                # qa_id = self.db.execute_query(
                #     """
                #     INSERT INTO questions_answers
                #     (instance_id, generated_question, correct_answer, variables_used)
                #     VALUES (%s, %s, %s, %s) RETURNING id;
                #     """,
                #     (
                #         instance.get("instance_id"),
                #         question_text,
                #         placeholder_answer,
                #         json.dumps(instance)
                #     ),
                #     fetch=True
                # )[0][0]
                # print(f"Question-answer saved in DB with ID {qa_id}")








                # template = self.db.execute_query(
                #     "SELECT id FROM question_templates "
                #     "WHERE subchapter_id=(SELECT id FROM subchapters "
                #     "WHERE chapter_id=(SELECT id FROM chapters WHERE chapter_number=%s) "
                #     "AND subchapter_number=%s) LIMIT 1;",
                #     (ch_num, sub_num), fetch=True
                # )
                # if not template:
                #     print("No template found for this subchapter. Cannot save instance.")
                #     continue
                # template_id = template[0][0]

                # instance_id = self.db.execute_query(
                #     "INSERT INTO problem_instances (template_id, instance_params) VALUES (%s, %s) RETURNING id;",
                #     (template_id, json.dumps(instance)), fetch=True
                # )[0][0]
                # instance["instance_id"] = instance_id
                # print(f"Instance saved in DB with ID {instance_id}")

                # # Save the answer
                # self.db.execute_query(
                #     "INSERT INTO questions_answers (instance_id, answer) VALUES (%s, %s);",
                #     (instance_id, json.dumps({"algorithm": fastest_algorithm, "solution": fastest_solution}))
                # )
                # print("Answer saved in DB.")

            # generate_q = input("Generate question from this instance? (y/n): ").strip().lower()
            # if generate_q == "y":
            #     self.qgen.generate_question(ch_num, sub_num, instance, save=True)