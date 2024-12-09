import os
import pickle
import shutil
import sqlite3
from typing import Union

import pandas as pd
from tqdm import tqdm


class MetaStore:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_database(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
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
                parent_item BLOB,
                embedded BOOL DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
        print(f"Created database: {self.db_path}")

    def delete_database_and_folder(self) -> None:
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(os.path.dirname(self.db_path)):
            shutil.rmtree(os.path.dirname(self.db_path))

    def populate_database(self, items: list) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Validate items
        for item in items:
            if not all(
                hasattr(item, attr)
                for attr in [
                    "key",
                    "get_title",
                    "get_tags",
                    "get_creators",
                    "get_url",
                    "get_pdf_path",
                    "item",
                    "parent_item",
                ]
            ):
                raise AttributeError(
                    f"Item {item} is missing one or more required attributes."
                )

        # Populate database
        for item in tqdm(items):
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

    def read_database(
        self, as_dataframe: bool = True
    ) -> Union[list | pd.DataFrame]:
        conn = sqlite3.connect(self.db_path)
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
                "embedded": row[8],
            }
            results.append(item)

        conn.close()
        return pd.DataFrame(results) if as_dataframe else results

    def update_embedded_value_by_key(
        self, keys: Union[list[str] | str]
    ) -> None:
        if isinstance(keys, str):
            keys = [keys]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for key in keys:
            cursor.execute(
                """
                UPDATE library
                SET embedded = 1
                WHERE key = ?
                """,
                (key,),
            )

        conn.commit()
        conn.close()
