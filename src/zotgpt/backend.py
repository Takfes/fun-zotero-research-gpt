from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_document(path, chunk_size=1000, chunk_overlap=200, metadata=None):
    loader = PyPDFLoader(path)
    documents_loaded = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    documents_splitted = text_splitter.split_documents(documents_loaded)
    print(f"* Loaded {len(documents_splitted)} documents from {path}")

    if metadata:
        print(f"* Updating metadata with {metadata}")
        for doc in documents_splitted:
            doc.metadata.update(metadata)

    return documents_splitted
