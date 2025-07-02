from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import DocumentSearchPipeline
from haystack import Document
import json
import os

def load_documents(path):
    full_path = os.path.join(os.path.dirname(__file__), "..", path)
    with open(full_path) as f:
        return json.load(f)

def build_pipeline(doc_path="data/haystack_docs.json"):
    docs = load_documents(doc_path)

    # Convert to Document objects
    haystack_docs = [Document(content=doc["content"], meta=doc["meta"]) for doc in docs]

    store = InMemoryDocumentStore(embedding_dim=384)
    store.write_documents(haystack_docs)

    retriever = EmbeddingRetriever(
        document_store=store,
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        use_gpu=False
    )

    store.update_embeddings(retriever)
    return DocumentSearchPipeline(retriever)
