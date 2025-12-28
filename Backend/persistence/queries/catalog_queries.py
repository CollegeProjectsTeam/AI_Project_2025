def q_chapters():
    return "SELECT id, chapter_number, chapter_name FROM chapters ORDER BY chapter_number;"

def q_subchapters():
    return """
    SELECT sc.chapter_id, sc.subchapter_number, sc.subchapter_name
    FROM subchapters sc
    JOIN chapters c ON sc.chapter_id = c.id
    ORDER BY c.chapter_number, sc.subchapter_number;
    """
