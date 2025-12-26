# core/console/menu_controller.py

def choose_from_list(prompt, items):
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


def choose_chapter(db):
    chapters = db.execute_query(
        "SELECT chapter_number, chapter_name FROM chapters ORDER BY chapter_number;",
        fetch=True,
    )
    return choose_from_list("Select chapter number: ", chapters)


def choose_subchapter(db, chapter_number):
    subchapters = db.execute_query(
        """
        SELECT subchapter_number, subchapter_name FROM subchapters
        WHERE chapter_id=(SELECT id FROM chapters WHERE chapter_number=%s)
        ORDER BY subchapter_number;
        """,
        (chapter_number,),
        fetch=True,
    )
    return choose_from_list("Select subchapter number: ", subchapters)


def get_subchapter_name(db, chapter_number, subchapter_number):
    result = db.execute_query(
        """
        SELECT sc.subchapter_name
        FROM subchapters sc
        JOIN chapters c ON sc.chapter_id = c.id
        WHERE c.chapter_number=%s AND sc.subchapter_number=%s
        LIMIT 1;
        """,
        (chapter_number, subchapter_number),
        fetch=True,
    )
    if not result:
        return ""
    return result[0][0]
