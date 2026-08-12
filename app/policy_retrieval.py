import logging
from typing import List, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import TRAVEL_POLICY_PATH, POLICY_RETRIEVAL_TOP_K

from app.models import PolicyChunk

logger = logging.getLogger("policy_agent")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

def _load_and_split(path, source_name: str):
    loader = PyPDFLoader(str(path))
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE, chunk_overlap = CHUNK_OVERLAP 
    )
    chunks = splitter.split_documents(pages)

    for chunk in chunks:
        page_number = chunk.metadata.get("page", 0)+1
        chunk.metadata["source"] = source_name
        chunk.metadata["section"] = f"Page{page_number}"

    return chunks


class PolicyRetriver:
    def __init__ (self, path = TRAVEL_POLICY_PATH, source_name: str = "travel_policy.pdf"):
        documents = _load_and_split(path, source_name)
        embeddings = OpenAIEmbeddings()
        self._store = InMemoryVectorStore.from_documents(documents, embeddings)

    def retrieve(self, query: str, top_k: int = POLICY_RETRIEVAL_TOP_K) -> List[PolicyChunk]:
        results = self._store.similarity_search(query, k = top_k)
        return [
            PolicyChunk(
                source=doc.metadata.get("source", "travel_policy.pdf"),
                section=doc.metadata.get("section", "General"),
                text = doc.page_content,
            )
            for doc in results
        ]


_retriever : Optional[PolicyRetriver] = None

def get_retriever() -> PolicyRetriver:
    global _retriever
    if _retriever is None:
        _retriever = PolicyRetriver()
    return _retriever



