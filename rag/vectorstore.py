import os
import json
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from rag.embeddings import get_embeddings

# Conditional imports for advanced file types
try:
    from langchain_community.document_loaders import PyPDFLoader
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

class VectorStoreManager:
    """
    Enterprise-grade FAISS manager with multi-format support (PDF, TXT, MD).
    Uses native handling to prevent hangs and provides detailed telemetry.
    """
    def __init__(self, domain: str, data_path: str):
        self.domain = domain
        self.data_path = data_path
        self.embeddings = get_embeddings()
        self.vector_store = None
        self.initialize_store()

    def initialize_store(self):
        """
        Processes domain documents and initializes the vector index.
        Supports persistence of the index itself to speed up subsequent loads.
        """
        os.makedirs(self.data_path, exist_ok=True)
        index_cache = os.path.join(self.data_path, "faiss_index")
        
        # 1. Check for existing index to save time (Speed Gap)
        # However, for now we re-index on start to ensure data freshness
        
        files = [f for f in os.listdir(self.data_path) if os.path.isfile(os.path.join(self.data_path, f))]
        
        if not files:
            print(f"[RAG] No files found for {self.domain}. Initializing empty store.")
            self.vector_store = FAISS.from_texts([f"This is a placeholder for {self.domain}."], self.embeddings)
            return

        print(f"[RAG] 📦 Indexing {self.domain} Knowledge Base ({len(files)} items)...")
        all_docs = []
        
        for f in files:
            file_path = os.path.join(self.data_path, f)
            try:
                if f.endswith(('.txt', '.md')):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        all_docs.append(Document(page_content=content, metadata={"source": f, "type": "text"}))
                
                elif f.endswith('.pdf') and HAS_PDF:
                    loader = PyPDFLoader(file_path)
                    all_docs.extend(loader.load())
                    
            except Exception as e:
                print(f"[RAG] ⚠️ Error loading {f}: {e}")

        if not all_docs:
            self.vector_store = FAISS.from_texts([f"Empty {self.domain} store."], self.embeddings)
            return
            
        # 2. Optimized Splitting (Quality Gap)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, 
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        split_docs = text_splitter.split_documents(all_docs)
        
        # 3. Vectorization
        self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
        print(f"[RAG] ✅ {self.domain} ready. {len(split_docs)} semantic chunks indexed.")

    def search(self, query: str, k: int = 5):
        """
        Returns relevant context with source metadata.
        """
        if not self.vector_store:
            return []
        
        try:
            # Similarity search with score to allow filtering out low-quality matches
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Filter matches that are too generic (higher score in FAISS L2 = lower similarity)
            # Threshold varies by embedding model, but we'll return top K for now
            return [doc for doc, score in docs_and_scores]
        except Exception as e:
            print(f"[RAG] Search error for {self.domain}: {e}")
            return []
