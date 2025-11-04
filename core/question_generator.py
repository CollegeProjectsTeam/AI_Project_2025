import json
from persistence.dbConnex import db

class QuestionGenerator:
    """Generate a question from a template and a problem instance."""

    def __init__(self):
        self.db = db

    def render_question(self, template_text: str, instance: dict) -> str:
        """Combine template text with instance JSON."""
        instance_str = "{\n"
        for k, v in instance.items():
            if k == "board":
                instance_str += f'  "{k}": [\n'
                for row in v:
                    instance_str += f"    {row},\n"
                instance_str += "  ]\n"
            else:
                instance_str += f'  "{k}": {json.dumps(v)},\n'
        instance_str += "}"
        return template_text.replace("{problem_name}", instance.get("problem_name", "")) \
                            .replace("{instance}", instance_str)

    def generate_question(self, chapter_number: int, subchapter_number: int, instance: dict, save: bool = True):
        """Generate and optionally save a question for the given instance."""
        template = self.db.execute_query(
            """
            SELECT qt.id, qt.template_text
            FROM question_templates qt
            JOIN subchapters sc ON qt.subchapter_id = sc.id
            JOIN chapters c ON sc.chapter_id = c.id
            WHERE c.chapter_number=%s AND sc.subchapter_number=%s
            LIMIT 1;
            """,
            (chapter_number, subchapter_number),
            fetch=True
        )

        if not template:
            print("No template found for this subchapter.")
            return None

        template_id, template_text = template[0]

        question_text = self.render_question(template_text, instance)
        print("\n--- Generated Question ---")
        print(question_text)
        print("---------------------------")

        # if save:
        #     placeholder_answer = "TO_BE_FILLED_BY_YOUR_ALGORITHM"
        #     qa_id = self.db.execute_query(
        #         """
        #         INSERT INTO questions_answers
        #         (instance_id, generated_question, correct_answer, variables_used)
        #         VALUES (%s, %s, %s, %s) RETURNING id;
        #         """,
        #         (
        #             instance.get("instance_id"),
        #             question_text,
        #             placeholder_answer,
        #             json.dumps(instance)
        #         ),
        #         fetch=True
        #     )[0][0]
        #     print(f"Question-answer saved in DB with ID {qa_id}")

        return question_text
