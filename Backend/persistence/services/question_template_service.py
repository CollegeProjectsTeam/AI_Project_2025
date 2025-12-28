from Backend.persistence.dbConnex import db
from Backend.persistence.queries.question_template_queries import q_template_text, q_template_id

def get_template_text(chapter_number: int, subchapter_number: int):
    rows = db.execute_query(q_template_text(), (chapter_number, subchapter_number), fetch=True) or []
    if not rows:
        return None
    return rows[0][0]

def get_template_id(chapter_number: int, subchapter_number: int):
    rows = db.execute_query(q_template_id(), (chapter_number, subchapter_number), fetch=True) or []
    if not rows:
        return None
    return rows[0][0]
