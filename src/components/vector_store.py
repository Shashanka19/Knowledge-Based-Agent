"""
Vector Store Component for KnowledgeBase Agent
Handles vector database operations using Pinecone or ChromaDB
"""

import os
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from pinecone import Pinecone, ServerlessSpec
import chromadb
from chromadb.config import Settings
try:
    from langchain_pinecone import PineconeVectorStore as LangchainPinecone
except ImportError:
    from langchain_community.vectorstores import Pinecone as LangchainPinecone
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreInterface(ABC):
    """Abstract interface for vector store implementations"""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        pass
    
    @abstractmethod
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs"""
        pass


class PineconeVectorStore(VectorStoreInterface):
    """Pinecone vector store implementation"""
    
    def __init__(self, api_key: str, environment: str, index_name: str = "knowledgebase"):
        """
        Initialize Pinecone vector store
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the Pinecone index
        """
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        # Initialize LangChain wrapper
        self.vectorstore = LangchainPinecone.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings
        )
        
        logger.info(f"Initialized Pinecone vector store with index: {self.index_name}")
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            logger.info(f"Creating new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to Pinecone"""
        try:
            doc_ids = self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to Pinecone")
            return doc_ids
        except Exception as e:
            logger.error(f"Error adding documents to Pinecone: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents in Pinecone"""
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents from Pinecone"""
        try:
            index = self.pc.Index(self.index_name)
            index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from Pinecone")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents from Pinecone: {e}")
            return False


class ChromaVectorStore(VectorStoreInterface):
    """ChromaDB vector store implementation"""
    
    def __init__(self, collection_name: str = "knowledgebase", persist_directory: str = "./data/chroma_db"):
        """
        Initialize ChromaDB vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist ChromaDB data
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        
        # Ensure persist directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize LangChain wrapper
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            client=self.client,
            persist_directory=persist_directory
        )
        
        logger.info(f"Initialized ChromaDB vector store with collection: {collection_name}")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to ChromaDB"""
        try:
            doc_ids = self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return doc_ids
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents in ChromaDB"""
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents from ChromaDB"""
        try:
            self.vectorstore.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents from ChromaDB: {e}")
            return False


class VectorStoreFactory:
    """Factory class to create vector store instances"""
    
    @staticmethod
    def create_vector_store(store_type: str, **kwargs) -> VectorStoreInterface:
        """
        Create vector store instance based on type
        
        Args:
            store_type: Type of vector store ('pinecone' or 'chromadb')
            **kwargs: Additional arguments for store initialization
            
        Returns:
            VectorStoreInterface: Vector store instance
        """
        if store_type.lower() == "pinecone":
            return PineconeVectorStore(**kwargs)
        elif store_type.lower() == "chromadb":
            return ChromaVectorStore(**kwargs)
        else:
            raise ValueError(f"Unsupported vector store type: {store_type}")


def get_vector_store() -> VectorStoreInterface:
    """
    Get configured vector store instance based on environment variables
    
    Returns:
        VectorStoreInterface: Configured vector store
    """
    store_type = os.getenv("VECTOR_STORE_TYPE", "chromadb").lower()
    
    if store_type == "pinecone":
        api_key = os.getenv("PINECONE_API_KEY")
        environment = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
        index_name = os.getenv("PINECONE_INDEX_NAME", "knowledgebase")
        
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        
        return VectorStoreFactory.create_vector_store(
            "pinecone",
            api_key=api_key,
            environment=environment,
            index_name=index_name
        )
    
    elif store_type == "chromadb":
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "knowledgebase")
        persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
        
        return VectorStoreFactory.create_vector_store(
            "chromadb",
            collection_name=collection_name,
            persist_directory=persist_directory
        )
    
    else:
        raise ValueError(f"Unsupported VECTOR_STORE_TYPE: {store_type}")