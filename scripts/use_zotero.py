from zotgpt.zotero import ZoteroItem, ZoteroWrapper, make_zotero_client

if __name__ == "__main__":
    # Instantiate Client
    zc = make_zotero_client()
    # Instantiate Wrapper base on Client
    zot = ZoteroWrapper(zc)
    # Get Collections from Wrapper
    collections = zot.get_collections()
    # Get the first collection Key
    collection_key = collections[0]["key"]
    # Load all items with a pdf from the collection
    pdf_items = zot.get_pdf_items_from_collection_key(collection_key)
    # Turn the items into ZoteroItem objects
    pdf_zot_items = [ZoteroItem(zc, item) for item in pdf_items]
    # Get the first ZoteroItem
    zot_item = pdf_zot_items[0]
    # Explore ZoteroItem
    zot_item.get_title()
    zot_item.get_pdf_path()
    zot_item.get_url()
    zot_item.get_tags()
    zot_item.get_creators()
    # Get the data from a specific item if it has a pdf
    zot.get_pdf_item_from_item_key("63EBWXN9")

    # Exploration
    item = zot.get_pdf_item_from_item_key("63EBWXN9")
    zi = ZoteroItem(zc, item)
    zi.get_url()
    zc.item("FJDDQVSG")
