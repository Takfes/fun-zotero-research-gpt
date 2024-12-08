import os
import pickle
import shutil
import sqlite3

from dotenv import load_dotenv
from tqdm import tqdm

from zotgpt.zotero import (
    ZoteroItem,
    collection_constructor,
    get_pdf_item_from_item_key,
    get_pdf_items_from_collection_key,
    make_zotero_client,
)

if __name__ == "__main__":
    load_dotenv()
    zot = make_zotero_client()

    collections = collection_constructor(zot)
    cd = collections.get_collection_dict()

    collection_key = os.environ["ZOTERO_MAIN_COLLECTION"]
    collection = collections.get_collection_by_key(collection_key)

    pdf_items = get_pdf_items_from_collection_key(zot, collection_key)
    pdf_zot_items = [ZoteroItem(zot, item) for item in pdf_items]

    print(f"collection : {cd[collection_key]}")
    print(f"number of items : {collection.number_of_items}")
    print(f"of which with pdf : {len(pdf_zot_items)}")
    print(
        f"number of missing pdfs : {collection.number_of_items - len(pdf_zot_items)}"
    )

    # for idx, x in enumerate(pdf_zot_items[:10]):
    #     print(idx)
    #     print(f"{x.key}")
    #     print(f"{x.get_title()}")
    #     print(f"{x.get_tags()}")
    #     print(f"{x.get_creators()}")
    #     print(f"{x.get_url()}")
    #     print(f"{x.get_pdf_path()}")
    #     print(x.item)
    #     print(x.parent_item)
    #     print()

    def create_database(db_path: str) -> None:
        db_path = os.path.join(db_path, "sqlite.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS library (
                key TEXT PRIMARY KEY,
                title TEXT,
                tags TEXT,
                creators TEXT,
                url TEXT,
                path TEXT,
                item BLOB,
                parent_item BLOB
            )
        """)
        conn.commit()
        conn.close()

    def delete_database_and_folder(db_path: str) -> None:
        if os.path.exists(db_path):
            os.remove(db_path)
            folder = os.path.dirname(db_path)
            if not os.listdir(folder):
                shutil.rmtree(folder)

    def populate_database(db_path: str, zotero_items: list[ZoteroItem]) -> None:
        db_path = os.path.join(db_path, "sqlite.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for item in tqdm(zotero_items):
            cursor.execute(
                """
                INSERT OR REPLACE INTO library (key, title, tags, creators, url, path, item, parent_item)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item.key,
                    item.get_title(),
                    ",".join(item.get_tags()),
                    ",".join(item.get_creators()),
                    item.get_url(),
                    item.get_pdf_path(),
                    sqlite3.Binary(pickle.dumps(item.item)),
                    sqlite3.Binary(pickle.dumps(item.parent_item)),
                ),
            )

        conn.commit()
        conn.close()

    def read_database(db_path: str) -> list[ZoteroItem]:
        db_path = os.path.join(db_path, "sqlite.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM library")
        rows = cursor.fetchall()

        results = []
        for row in rows:
            item = {
                "key": row[0],
                "title": row[1],
                "tags": row[2].split(","),
                "creators": row[3].split(","),
                "url": row[4],
                "path": row[5],
                "item": pickle.loads(row[6]),
                "parent_item": pickle.loads(row[7]),
            }
            results.append(item)

        conn.close()
        return results

    db_path = os.environ["ZOTERO_APP_SQLITE"]
    create_database(db_path)
    # delete_database_and_folder(db_path)
    populate_database(db_path, pdf_zot_items)
    read_database(db_path)
