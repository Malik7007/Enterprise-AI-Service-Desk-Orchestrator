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
        self.initialize_store()

    def initialize_store(self):
        """
        Uses SemanticChunker for higher quality document representation.
        """
        os.makedirs(self.data_path, exist_ok=True)
        
        if not os.listdir(self.data_path):
            self.vector_store = FAISS.from_texts([f"This is a placeholder for the {self.domain} knowledge base."], self.embeddings)
            return

        loader = DirectoryLoader(self.data_path, glob="**/*", loader_cls=TextLoader)
        try:
            docs = loader.load()
            if not docs:
                self.vector_store = FAISS.from_texts([f"Empty {self.domain} knowledge base."], self.embeddings)
                return
                
            text_splitter = SemanticChunker(self.embeddings, breakpoint_threshold_type="percentile")
            split_docs = text_splitter.split_documents(docs)
            self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
            print(f"[RAG] Indexed {len(split_docs)} chunks for {self.domain} domain.")
        except Exception as e:
            print(f"[RAG] Error initializing {self.domain} store: {e}")
            self.vector_store = FAISS.from_texts([f"Error in {self.domain} knowledge base."], self.embeddings)

    def search(self, query: str, k: int = 4):
        """
        Performs similarity search.
        """
        if not self.vector_store:
            return []
        return self.vector_store.similarity_search(query, k=k)
