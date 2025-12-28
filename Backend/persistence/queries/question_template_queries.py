def q_template_text():
    return """
    SELECT qt.template_text
    FROM question_templates qt
    JOIN subchapters sc ON qt.subchapter_id = sc.id
    JOIN chapters c ON sc.chapter_id = c.id
    WHERE c.chapter_number=%s AND sc.subchapter_number=%s
    LIMIT 1;
    """

def q_template_id():
    return """
    SELECT qt.id
    FROM question_templates qt
    JOIN subchapters sc ON qt.subchapter_id = sc.id
    JOIN chapters c ON sc.chapter_id = c.id
    WHERE c.chapter_number=%s AND sc.subchapter_number=%s
    LIMIT 1;
    """
