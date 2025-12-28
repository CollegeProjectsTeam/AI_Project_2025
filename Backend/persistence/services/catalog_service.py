from Backend.persistence.dbConnex import db
from Backend.persistence.queries.catalog_queries import q_chapters, q_subchapters

def get_catalog():
    chapters = db.execute_query(q_chapters(), fetch=True) or []
    subs = db.execute_query(q_subchapters(), fetch=True) or []

    by_id = {}
    for ch_id, ch_num, ch_name in chapters:
        by_id[ch_id] = {
            "id": ch_id,
            "chapter_number": ch_num,
            "chapter_name": ch_name,
            "subchapters": []
        }

    for chapter_id, sub_num, sub_name in subs:
        item = by_id.get(chapter_id)
        if item is not None:
            item["subchapters"].append({
                "subchapter_number": sub_num,
                "subchapter_name": sub_name
            })

    return {"chapters": list(by_id.values())}
