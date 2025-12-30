def q_template_text_any():
    return """
    SELECT qt.template_text
    FROM question_templates qt
    JOIN subchapters sc ON qt.subchapter_id = sc.id
    JOIN chapters c ON sc.chapter_id = c.id
    WHERE c.chapter_number=%s AND sc.subchapter_number=%s
    ORDER BY random()
    LIMIT 1;
    """


def q_template_text_by_difficulty():
    return """
    SELECT qt.template_text
    FROM question_templates qt
    JOIN subchapters sc ON qt.subchapter_id = sc.id
    JOIN chapters c ON sc.chapter_id = c.id
    WHERE c.chapter_number=%s AND sc.subchapter_number=%s
      AND qt.difficulty=%s
    ORDER BY random()
    LIMIT 1;
    """


def q_template_id_any():
    return """
    SELECT qt.id
    FROM question_templates qt
    JOIN subchapters sc ON qt.subchapter_id = sc.id
    JOIN chapters c ON sc.chapter_id = c.id
    WHERE c.chapter_number=%s AND sc.subchapter_number=%s
    ORDER BY random()
    LIMIT 1;
    """


def q_template_id_by_difficulty():
    return """
    SELECT qt.id
    FROM question_templates qt
    JOIN subchapters sc ON qt.subchapter_id = sc.id
    JOIN chapters c ON sc.chapter_id = c.id
    WHERE c.chapter_number=%s AND sc.subchapter_number=%s
      AND qt.difficulty=%s
    ORDER BY random()
    LIMIT 1;
    """
