from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import DocumentSearchPipeline
import json

def load_documents(path):
    with open(path) as f:
        return json.load(f)

def build_pipeline(doc_path="data/haystack_documents.json"):
    docs = load_documents(doc_path)

    store = InMemoryDocumentStore(use_bm25=False)
    store.write_documents(docs)

    retriever = EmbeddingRetriever(
        document_store=store,
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        use_gpu=False
    )

    store.update_embeddings(retriever)
    return DocumentSearchPipeline(retriever)
