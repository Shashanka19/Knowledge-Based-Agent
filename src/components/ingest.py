"""
Document Ingestion Component for KnowledgeBase Agent
Handles document upload, text extraction, chunking, and embedding storage
"""

import os
import logging
import hashlib
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .vector_store import get_vector_store
from .model_loader import get_embedding_model
from .firebase_db import get_metadata_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document processing and ingestion"""
    
    def __init__(self):
        """Initialize document processor with dependencies"""
        self.vector_store = get_vector_store()
        self.embedding_model = get_embedding_model()
        self.metadata_db = get_metadata_db()
        
        # Text splitter configuration
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Supported file types
        self.supported_extensions = {".pdf", ".docx", ".txt"}
        
        logger.info("Initialized DocumentProcessor")
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if file is supported and accessible
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if file is valid
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in self.supported_extensions:
            logger.error(f"Unsupported file type: {file_extension}")
            return False
        
        return True
    
    def extract_text(self, file_path: str) -> List[Document]:
        """
        Extract text from document based on file type
        
        Args:
            file_path: Path to the document
            
        Returns:
            List[Document]: List of extracted documents
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid file: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == ".pdf":
                loader = PyPDFLoader(file_path)
            elif file_extension == ".docx":
                loader = Docx2txtLoader(file_path)
            elif file_extension == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            documents = loader.load()
            logger.info(f"Extracted text from {len(documents)} pages/sections")
            return documents
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List[Document]: List of chunked documents
        """
        try:
            chunked_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Split documents into {len(chunked_docs)} chunks")
            return chunked_docs
            
        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            raise
    
    def generate_document_id(self, content: str, filename: str) -> str:
        """
        Generate unique document ID based on content hash
        
        Args:
            content: Document content
            filename: Original filename
            
        Returns:
            str: Unique document ID
        """
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{Path(filename).stem}_{content_hash[:8]}"
    
    def prepare_metadata(self, document: Document, filename: str, chunk_index: int) -> Dict[str, Any]:
        """
        Prepare metadata for document chunk
        
        Args:
            document: Document chunk
            filename: Original filename
            chunk_index: Index of the chunk
            
        Returns:
            Dict[str, Any]: Metadata dictionary
        """
        base_metadata = {
            "filename": filename,
            "chunk_index": chunk_index,
            "chunk_size": len(document.page_content),
            "upload_timestamp": datetime.now().isoformat(),
            "document_id": self.generate_document_id(document.page_content, filename)
        }
        
        # Add any existing metadata from document
        if hasattr(document, 'metadata') and document.metadata:
            base_metadata.update(document.metadata)
        
        return base_metadata
    
    def process_and_store(self, file_path: str, category: str = "general") -> Dict[str, Any]:
        """
        Process document and store in vector database
        
        Args:
            file_path: Path to the document file
            category: Category for the document (e.g., 'HR', 'Policies', 'SOPs')
            
        Returns:
            Dict[str, Any]: Processing results
        """
        filename = Path(file_path).name
        
        try:
            # Extract text from document
            st.info(f"📄 Extracting text from {filename}...")
            documents = self.extract_text(file_path)
            
            if not documents:
                raise ValueError("No content extracted from document")
            
            # Chunk documents
            st.info("✂️ Splitting document into chunks...")
            chunked_docs = self.chunk_documents(documents)
            
            # Prepare documents for storage
            processed_docs = []
            document_ids = []
            
            for i, chunk in enumerate(chunked_docs):
                # Generate metadata
                metadata = self.prepare_metadata(chunk, filename, i)
                metadata["category"] = category
                
                # Create new document with metadata
                processed_doc = Document(
                    page_content=chunk.page_content,
                    metadata=metadata
                )
                
                processed_docs.append(processed_doc)
                document_ids.append(metadata["document_id"])
            
            # Store in vector database
            st.info("🔄 Generating embeddings and storing in vector database...")
            vector_ids = self.vector_store.add_documents(processed_docs)
            
            # Store metadata in database
            document_info = {
                "filename": filename,
                "category": category,
                "total_chunks": len(processed_docs),
                "upload_timestamp": datetime.now().isoformat(),
                "file_size": os.path.getsize(file_path),
                "file_type": Path(file_path).suffix.lower(),
                "vector_ids": vector_ids,
                "document_ids": document_ids
            }
            
            # Save to metadata database
            metadata_id = self.metadata_db.create_document(document_info)
            
            result = {
                "success": True,
                "filename": filename,
                "chunks_created": len(processed_docs),
                "metadata_id": metadata_id,
                "message": f"Successfully processed {filename} into {len(processed_docs)} chunks"
            }
            
            logger.info(f"Successfully processed document: {filename}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing {filename}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "filename": filename,
                "error": error_msg,
                "message": error_msg
            }
    
    def process_uploaded_files(self, uploaded_files: List[Any], category: str = "general") -> List[Dict[str, Any]]:
        """
        Process multiple uploaded files from Streamlit
        
        Args:
            uploaded_files: List of Streamlit uploaded files
            category: Category for the documents
            
        Returns:
            List[Dict[str, Any]]: Processing results for each file
        """
        results = []
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        for uploaded_file in uploaded_files:
            try:
                # Save uploaded file temporarily
                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process the file
                result = self.process_and_store(file_path, category)
                results.append(result)
                
                # Clean up temporary file
                os.remove(file_path)
                
            except Exception as e:
                error_result = {
                    "success": False,
                    "filename": uploaded_file.name,
                    "error": str(e),
                    "message": f"Failed to process {uploaded_file.name}: {str(e)}"
                }
                results.append(error_result)
                logger.error(f"Error processing uploaded file {uploaded_file.name}: {e}")
        
        return results
    
    def get_document_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored documents
        
        Returns:
            Dict[str, Any]: Document statistics
        """
        try:
            docs = self.metadata_db.get_all_documents()
            
            total_docs = len(docs)
            total_chunks = sum(doc.get('total_chunks', 0) for doc in docs)
            
            categories = {}
            for doc in docs:
                category = doc.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            file_types = {}
            for doc in docs:
                file_type = doc.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "categories": categories,
                "file_types": file_types,
                "documents": docs
            }
            
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "categories": {},
                "file_types": {},
                "documents": []
            }


def create_document_processor() -> DocumentProcessor:
    """Create and return document processor instance"""
    return DocumentProcessor()