import os
import time

from dotenv import load_dotenv

from zotgpt.metastore import MetaStore
from zotgpt.zotero import (
    ZoteroItem,
    ZoteroWrapper,
    make_zotero_client,
)


def main():
    load_dotenv()

    db_path = os.environ["ZOTERO_APP_SQLITE"]
    db = MetaStore(db_path)
    db.delete_database_and_folder()
    db.create_database()

    collection_key = os.environ["ZOTERO_DEFAULT_COLLECTION"]
    zc = make_zotero_client()
    zot = ZoteroWrapper(zc)

    start_time = time.time()
    pdf_items = zot.get_pdf_items_from_collection_key(collection_key)
    print(f"Time to get items: {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    pdf_zot_items = [ZoteroItem(zc, item) for item in pdf_items]
    print(f"Time to get item parents: {time.time() - start_time:.2f} seconds")

    db.populate_database(pdf_zot_items)


if __name__ == "__main__":
    main()
