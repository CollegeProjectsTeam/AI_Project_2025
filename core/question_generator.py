import json
from persistence.dbConnex import db


class QuestionGenerator:
    def __init__(self):
        self.db = db

    def render_question(self, template_text: str, instance: dict) -> str:
        if "instance" in instance and isinstance(instance["instance"], str):
            instance_str = "\n" + instance["instance"].rstrip("\n") + "\n"
        else:
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

        text = template_text
        text = text.replace("{problem_name}", instance.get("problem_name", ""))
        text = text.replace("{instance}", instance_str)

        return text

    def generate_question(self, chapter_number: int, subchapter_number: int, instance: dict):
        """Generate and return a question string from DB template."""
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

        return question_text
