import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from pyzotero import zotero


def make_zotero_client():
    load_dotenv()
    library_id = os.getenv("ZOTERO_LIBRARY_ID")
    library_type = os.getenv("ZOTERO_LIBRARY_TYPE", "user")
    api_key = os.getenv("ZOTERO_API_KEY")
    return zotero.Zotero(library_id, library_type, api_key)


@dataclass
class ZoteroItem:
    # TODO: Add ROOT PATH dynamically from the environment
    __ROOT_PATH__ = "/Users/takis/Zotero/storage"

    def __init__(self, zotero_client, item):
        self.zotero_client = zotero_client
        self.item: dict = item
        self.key: str = item["data"]["key"]
        self.parent: str = item["data"]["parentItem"]
        self.title: str = item["data"]["title"]
        self.filename: str = item["data"]["filename"]
        self.url: str = item["data"]["url"]
        self.access_date: str = item["data"]["accessDate"]
        self.date_added: str = item["data"]["dateAdded"]
        self.date_modified: str = item["data"]["dateModified"]
        self.has_parent: bool = False
        self.parent_item: dict = None
        self.parent_item_type: str = None
        self.parent_item_date: str = None
        self.parent_item_title: str = None
        self.parent_item_abstract: str = None
        self.parent_item_doi: str = None
        self.parent_item_creators: list = None
        self.parent_item_tags: list = None
        self.parent_item_collections: list = None
        self.__post_init__()

    def __post_init__(self):
        self._get_parent_item()

    def _get_parent_item(self):
        try:
            self.parent_item = self.zotero_client.item(self.parent)
            self.has_parent = True
        except Exception:
            self.parent_item = None
            self.has_parent = False
        if self.has_parent:
            self.parent_item_type = self.parent_item["data"]["itemType"]
            self.parent_item_date = self.parent_item["data"]["date"]
            self.parent_item_title = self.parent_item["data"]["title"]
            self.parent_item_url = self.parent_item["data"]["url"]
            self.parent_item_abstract = self.parent_item["data"]["abstractNote"]
            self.parent_item_doi = self.parent_item["data"]["DOI"]
            self.parent_item_creators = self.parent_item["data"]["creators"]
            self.parent_item_tags = self.parent_item["data"]["tags"]
            self.parent_item_collections = self.parent_item["data"][
                "collections"
            ]

    def get_creators(self) -> list:
        creators = []
        for x in self.parent_item_creators:
            if "name" in x:
                creators.append(x["name"])
            elif ("lastName" in x) and ("firstName" in x):
                creators.append(" ".join([x["firstName"], x["lastName"]]))
            else:
                continue
        return list(set(creators))

    def get_tags(self) -> list:
        return [tag.get("tag") for tag in self.parent_item_tags]

    def get_url(self) -> str:
        return self.url if self.url else self.parent_item_url

    def get_pdf_root_path(self, root_path: str = __ROOT_PATH__) -> str:
        return f"{root_path}/{self.key}"

    def get_pdf_path(self, root_path: str = __ROOT_PATH__) -> str:
        return f"{root_path}/{self.key}/{self.filename}"

    def __repr__(self):
        return f"ZoteroItem(key={self.key!r}, has_parent={self.has_parent!r},\ntitle={self.parent_item_title if self.parent_item_title else self.title!r}"

    def __str__(self):
        return f"ZoteroItem: (Key: {self.key}) (Has_Parent: {self.has_parent}\n(Title: {self.parent_item_title if self.parent_item_title else self.title}))"


@dataclass
class Collection:
    key: str
    name: str
    number_of_items: int
    parent_collection: str = None
    items: list[ZoteroItem] = field(default_factory=list)

    def add_item(self, item: ZoteroItem) -> None:
        if not isinstance(item, ZoteroItem):
            raise TypeError("Only ZoteroItem instances can be added")
        self.items.append(item)

    def add_items(self, items: list[ZoteroItem]) -> None:
        if not all(isinstance(item, ZoteroItem) for item in items):
            raise TypeError("Only ZoteroItem instances can be added")
        self.items.extend(items)

    def get_item_count(self) -> int:
        return len(self.items)

    def __repr__(self):
        return f"Collection(key={self.key!r}, name={self.name!r}, number_of_items={self.number_of_items!r})"

    def __str__(self):
        return f"Collection: (Key: {self.key}) (Name: {self.name}) (Number of Items: {self.number_of_items})"


@dataclass
class Collections:
    collections: list[Collection] = field(default_factory=list)

    def add_collection(self, collection: Collection) -> None:
        self.collections.append(collection)

    def get_collection_by_name(self, name: str) -> Collection:
        for collection in self.collections:
            if collection.name == name:
                return collection
        return None

    def get_collection_by_key(self, key: str) -> Collection:
        for collection in self.collections:
            if collection.key == key:
                return collection
        return None

    def get_collection_count(self) -> int:
        return len(self.collections)

    def print_collections(self) -> None:
        for idx, collection in enumerate(self.collections):
            print(idx, collection)

    def get_collection_dict(self):
        return {
            collection.key: collection.name for collection in self.collections
        }

    def __repr__(self):
        return f"Collections({self.collections!r})"

    def __str__(self):
        return f"Collections: {self.collections}"


def collection_constructor(zotero_client=None):
    my_collections = Collections()
    collections = zotero_client.collections()
    for collection in collections:
        tmp = Collection(
            key=collection["data"]["key"],
            name=collection["data"]["name"],
            number_of_items=collection["meta"]["numItems"],
        )
        my_collections.add_collection(tmp)
    return my_collections


def get_pdf_items_from_collection_key(
    zotero_client, collection_key: str
) -> list:
    start = 0
    limit = 100
    iteration = 1
    pdf_items = []

    while True:
        # Retrieve items from the collection
        print(
            f"{iteration=} - querying {collection_key=} items w/ pagination - {start=}-{start + limit=}"
        )
        items = zotero_client.collection_items(
            collection_key, start=start, limit=limit
        )
        print(f"{iteration=} - retrieved {len(items)} items")
        iteration += 1

        if not items:
            print(f"Finished retrieving items from {collection_key}")
            print(f"Total items retrieved: {len(pdf_items)}")
            break

        # Collecting PDF items from the results
        for item in items:
            if (
                # item.get("data", {}).get("itemType") == "attachment"
                item.get("contentType") == "application/pdf"
                or item.get("links", {}).get("enclosure", {}).get("type")
                == "application/pdf"
                or item.get("attachment", {}).get("attachmentType")
                == "application/pdf"
            ):
                pdf_items.append(item)

        print(f"end {iteration=} contains {len(pdf_items)} PDF items\n")
        start += limit

    return pdf_items


def get_pdf_item_from_item_key(zotero_client, item_key: str) -> dict:
    item = zotero_client.item(item_key)
    if (
        item.get("contentType") == "application/pdf"
        or item.get("links", {}).get("enclosure", {}).get("type")
        == "application/pdf"
        or item.get("attachment", {}).get("attachmentType") == "application/pdf"
    ):
        return item
    else:
        raise ValueError(f"Item with key {item_key} is not a PDF")
