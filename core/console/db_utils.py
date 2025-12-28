# core/console/db_utils.py
import json


def get_template_id(db, chapter, subchapter):
    result = db.execute_query(
        """
        SELECT qt.id
        FROM question_templates qt
        JOIN subchapters sc ON qt.subchapter_id = sc.id
        JOIN chapters c ON sc.chapter_id = c.id
        WHERE c.chapter_number=%s AND sc.subchapter_number=%s
        LIMIT 1;
        """,
        (chapter, subchapter),
        fetch=True,
    )
    if not result:
        return None
    return result[0][0]


def save_to_database(db, ch_num, sub_num, instance, question_text, correct_answer):
    template_id = get_template_id(db, ch_num, sub_num)
    if template_id is None:
        print("No template found for this subchapter.")
        return

    result = db.execute_query(
        """
        INSERT INTO problem_instances (template_id, instance_params)
        VALUES (%s, %s) RETURNING id;
        """,
        (template_id, json.dumps(instance)),
        fetch=True,
    )

    instance_id = result[0][0]
    print(f"Instance saved with ID {instance_id}")

    qa = db.execute_query(
        """
        INSERT INTO questions_answers (instance_id, generated_question, correct_answer, variables_used)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """,
        (instance_id, question_text, correct_answer, json.dumps(instance)),
        fetch=True,
    )

    print(f"QA saved with ID {qa[0][0]}")
