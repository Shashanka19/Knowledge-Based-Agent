"""
Components package for KnowledgeBase Agent
"""

from .vector_store import get_vector_store, VectorStoreFactory
from .model_loader import get_model, get_embedding_model, ModelFactory
from .ingest import create_document_processor, DocumentProcessor
from .query import create_query_engine, create_advanced_query_engine, QueryEngine
from .firebase_db import get_metadata_db, FirebaseMetadataDB, LocalJSONMetadataDB

__all__ = [
    'get_vector_store', 'VectorStoreFactory',
    'get_model', 'get_embedding_model', 'ModelFactory',
    'create_document_processor', 'DocumentProcessor',
    'create_query_engine', 'create_advanced_query_engine', 'QueryEngine',
    'get_metadata_db', 'FirebaseMetadataDB', 'LocalJSONMetadataDB'
]