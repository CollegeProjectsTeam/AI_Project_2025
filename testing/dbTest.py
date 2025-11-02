from persistence.dbConnex import db

def db_insert_testing():
    db.execute_query(
        "INSERT INTO chapters (chapter_number, chapter_name) VALUES (%s, %s)",
        (0, "Database Testing")
    )

def db_read_testing():
    chapters = db.execute_query(
        "SELECT * FROM chapters WHERE chapter_number = 0",
        fetch=True
    )

    print(chapters)
