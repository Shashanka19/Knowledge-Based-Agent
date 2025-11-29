"""
Firebase Database Component for KnowledgeBase Agent
Handles metadata storage and retrieval using Firebase Firestore
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("Firebase SDK not available. Using local JSON storage as fallback.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataStorageInterface:
    """Abstract interface for metadata storage implementations"""
    
    def create_document(self, document_data: Dict[str, Any]) -> str:
        """Create document metadata"""
        raise NotImplementedError
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID"""
        raise NotImplementedError
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all document metadata"""
        raise NotImplementedError
    
    def update_document(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update document metadata"""
        raise NotImplementedError
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document metadata"""
        raise NotImplementedError
    
    def log_query(self, query_data: Dict[str, Any]) -> str:
        """Log query information"""
        raise NotImplementedError
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        raise NotImplementedError


class FirebaseMetadataDB(MetadataStorageInterface):
    """Firebase Firestore implementation for metadata storage"""
    
    def __init__(self, service_account_path: str, project_id: str):
        """
        Initialize Firebase metadata database
        
        Args:
            service_account_path: Path to Firebase service account JSON file
            project_id: Firebase project ID
        """
        if not FIREBASE_AVAILABLE:
            raise ImportError("Firebase SDK not installed. Install with: pip install firebase-admin")
        
        self.project_id = project_id
        
        # Initialize Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
        
        # Initialize Firestore client
        self.db = firestore.client()
        
        # Collection names
        self.documents_collection = "documents"
        self.queries_collection = "queries"
        
        logger.info(f"Initialized Firebase Firestore for project: {project_id}")
    
    def create_document(self, document_data: Dict[str, Any]) -> str:
        """Create document metadata in Firestore"""
        try:
            # Add timestamp
            document_data['created_at'] = firestore.SERVER_TIMESTAMP
            document_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Add to Firestore
            doc_ref = self.db.collection(self.documents_collection).add(document_data)
            doc_id = doc_ref[1].id
            
            logger.info(f"Created document metadata with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error creating document metadata: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID"""
        try:
            doc_ref = self.db.collection(self.documents_collection).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all document metadata"""
        try:
            docs_ref = self.db.collection(self.documents_collection)
            docs = docs_ref.stream()
            
            documents = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                documents.append(data)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def update_document(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update document metadata"""
        try:
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection(self.documents_collection).document(doc_id)
            doc_ref.update(update_data)
            
            logger.info(f"Updated document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document metadata"""
        try:
            doc_ref = self.db.collection(self.documents_collection).document(doc_id)
            doc_ref.delete()
            
            logger.info(f"Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def log_query(self, query_data: Dict[str, Any]) -> str:
        """Log query information"""
        try:
            query_data['timestamp'] = firestore.SERVER_TIMESTAMP
            
            query_ref = self.db.collection(self.queries_collection).add(query_data)
            query_id = query_ref[1].id
            
            logger.info(f"Logged query with ID: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Error logging query: {e}")
            raise
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        try:
            queries_ref = self.db.collection(self.queries_collection)
            queries = queries_ref.stream()
            
            total_queries = 0
            categories = {}
            popular_queries = {}
            
            for query in queries:
                data = query.to_dict()
                total_queries += 1
                
                # Count categories
                category = data.get('category_filter', 'general')
                categories[category] = categories.get(category, 0) + 1
                
                # Count popular queries
                question = data.get('question', '')
                if question:
                    popular_queries[question] = popular_queries.get(question, 0) + 1
            
            # Get top 10 popular queries
            sorted_queries = sorted(popular_queries.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_queries": total_queries,
                "categories_searched": categories,
                "popular_queries": [{"question": q[0], "count": q[1]} for q in sorted_queries]
            }
            
        except Exception as e:
            logger.error(f"Error getting query stats: {e}")
            return {
                "total_queries": 0,
                "categories_searched": {},
                "popular_queries": []
            }


class LocalJSONMetadataDB(MetadataStorageInterface):
    """Local JSON file implementation for metadata storage (fallback)"""
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize local JSON metadata database
        
        Args:
            data_dir: Directory to store JSON files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.documents_file = os.path.join(data_dir, "documents.json")
        self.queries_file = os.path.join(data_dir, "queries.json")
        
        # Initialize files if they don't exist
        for file_path in [self.documents_file, self.queries_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
        
        logger.info(f"Initialized local JSON metadata storage in: {data_dir}")
    
    def _load_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def _save_json(self, file_path: str, data: List[Dict[str, Any]]) -> bool:
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False
    
    def create_document(self, document_data: Dict[str, Any]) -> str:
        """Create document metadata in JSON file"""
        try:
            documents = self._load_json(self.documents_file)
            
            # Generate ID
            doc_id = f"doc_{len(documents) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Add metadata
            document_data['id'] = doc_id
            document_data['created_at'] = datetime.now().isoformat()
            document_data['updated_at'] = datetime.now().isoformat()
            
            # Add to list
            documents.append(document_data)
            
            # Save
            self._save_json(self.documents_file, documents)
            
            logger.info(f"Created document metadata with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error creating document metadata: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID"""
        try:
            documents = self._load_json(self.documents_file)
            
            for doc in documents:
                if doc.get('id') == doc_id:
                    return doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all document metadata"""
        try:
            return self._load_json(self.documents_file)
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def update_document(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update document metadata"""
        try:
            documents = self._load_json(self.documents_file)
            
            for i, doc in enumerate(documents):
                if doc.get('id') == doc_id:
                    documents[i].update(update_data)
                    documents[i]['updated_at'] = datetime.now().isoformat()
                    break
            else:
                return False
            
            self._save_json(self.documents_file, documents)
            logger.info(f"Updated document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document metadata"""
        try:
            documents = self._load_json(self.documents_file)
            
            for i, doc in enumerate(documents):
                if doc.get('id') == doc_id:
                    del documents[i]
                    break
            else:
                return False
            
            self._save_json(self.documents_file, documents)
            logger.info(f"Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def log_query(self, query_data: Dict[str, Any]) -> str:
        """Log query information"""
        try:
            queries = self._load_json(self.queries_file)
            
            # Generate ID
            query_id = f"query_{len(queries) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Add metadata
            query_data['id'] = query_id
            query_data['timestamp'] = datetime.now().isoformat()
            
            # Add to list
            queries.append(query_data)
            
            # Save
            self._save_json(self.queries_file, queries)
            
            logger.info(f"Logged query with ID: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Error logging query: {e}")
            raise
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        try:
            queries = self._load_json(self.queries_file)
            
            total_queries = len(queries)
            categories = {}
            popular_queries = {}
            
            for query in queries:
                # Count categories
                category = query.get('category_filter', 'general')
                categories[category] = categories.get(category, 0) + 1
                
                # Count popular queries
                question = query.get('question', '')
                if question:
                    popular_queries[question] = popular_queries.get(question, 0) + 1
            
            # Get top 10 popular queries
            sorted_queries = sorted(popular_queries.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_queries": total_queries,
                "categories_searched": categories,
                "popular_queries": [{"question": q[0], "count": q[1]} for q in sorted_queries]
            }
            
        except Exception as e:
            logger.error(f"Error getting query stats: {e}")
            return {
                "total_queries": 0,
                "categories_searched": {},
                "popular_queries": []
            }


def get_metadata_db() -> MetadataStorageInterface:
    """
    Get configured metadata database based on environment variables
    
    Returns:
        MetadataStorageInterface: Configured metadata database
    """
    db_type = os.getenv("METADATA_DB_TYPE", "local").lower()
    
    if db_type == "firebase" and FIREBASE_AVAILABLE:
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        
        if not service_account_path or not project_id:
            logger.warning("Firebase configuration missing. Falling back to local JSON storage.")
            return LocalJSONMetadataDB()
        
        if not os.path.exists(service_account_path):
            logger.warning(f"Firebase service account file not found: {service_account_path}. Falling back to local JSON storage.")
            return LocalJSONMetadataDB()
        
        try:
            return FirebaseMetadataDB(service_account_path, project_id)
        except Exception as e:
            logger.warning(f"Failed to initialize Firebase: {e}. Falling back to local JSON storage.")
            return LocalJSONMetadataDB()
    
    else:
        data_dir = os.getenv("LOCAL_DATA_DIR", "./data")
        return LocalJSONMetadataDB(data_dir)