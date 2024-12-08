from zotgpt.zotero import (
    ZoteroItem,
    collection_constructor,
    get_pdf_item_from_item_key,
    get_pdf_items_from_collection_key,
    make_zotero_client,
)

if __name__ == "__main__":
    zot = make_zotero_client()

    collections = collection_constructor(zot)
    collections.get_collection_count()
    collections.print_collections()
    collections.get_collection_dict()

    collection_key = "SL5SIIMD"
    collection_key = "IBWXQ7U3"
    collection = collections.get_collection_by_key(collection_key)

    pdf_items = get_pdf_items_from_collection_key(zot, collection_key)
    pdf_zot_items = [ZoteroItem(zot, item) for item in pdf_items]

    for idx, x in enumerate(pdf_zot_items):
        print(f"{idx=} | {x.key} | {x.get_title()}\n")
        # if x.parent_item_title == "" or x.parent_item_title is None:
        #     print(f"ERROR : {x.key} | {x.get_url()}\n")

    creators_work = {}
    for idx, x in enumerate(pdf_zot_items):
        for creator in x.get_creators():
            if creator not in creators_work:
                creators_work[creator] = {}
                creators_work[creator]["count"] = 1
                creators_work[creator]["keys"] = [x.key]
            else:
                creators_work[creator]["count"] += 1
                creators_work[creator]["keys"].append(x.key)

    collection.add_items(pdf_zot_items)
    collection.get_item_count()

    item = collection.items[0]
    item.parent_item_title
    item.get_pdf_root_path()
    item.get_pdf_path()

    item_key = "446PVAFU"
    item_key = "VZVATVKP"
    item_key = "ZRPTUR3W"
    item_key = "22TS3QH8"
    pdf_item = get_pdf_item_from_item_key(zot, item_key)
    pot = ZoteroItem(zot, pdf_item)
