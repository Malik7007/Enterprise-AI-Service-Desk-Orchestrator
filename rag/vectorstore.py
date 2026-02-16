import os
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from rag.embeddings import get_embeddings

class VectorStoreManager:
    """
    Advanced FAISS manager with Semantic Chunking.
    Ensures that domain-specific knowledge is split based on semantic meaning
    rather than just character count, reducing retrieval context noise.
    """
    def __init__(self, domain: str, data_path: str):
        self.domain = domain
        self.data_path = data_path
        self.embeddings = get_embeddings()
        self.vector_store = None
        self._initialize_store()

    def _initialize_store(self):
        """
        Uses SemanticChunker for higher quality document representation.
        """
        if not os.path.exists(self.data_path) or not os.listdir(self.data_path):
            self.vector_store = FAISS.from_texts(["Placeholder"], self.embeddings)
            return

        loader = DirectoryLoader(self.data_path, glob="**/*.md", loader_cls=TextLoader)
        docs = loader.load()
        
        # Semantic Chunking is more expensive but significantly more accurate for RAG
        # It splits based on sentence embedding similarity
        text_splitter = SemanticChunker(self.embeddings, breakpoint_threshold_type="percentile")
        split_docs = text_splitter.split_documents(docs)
        
        self.vector_store = FAISS.from_documents(split_docs, self.embeddings)

    def search(self, query: str, k: int = 4):
        """
        Performs similarity search. k is increased for better coverage.
        """
        return self.vector_store.similarity_search(query, k=k)
