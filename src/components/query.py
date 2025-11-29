"""
Query Component for KnowledgeBase Agent
Handles the RAG (Retrieval-Augmented Generation) pipeline for answering questions
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from .vector_store import get_vector_store
from .model_loader import get_model
from .firebase_db import get_metadata_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryEngine:
    """Handles question answering using RAG pipeline"""
    
    def __init__(self):
        """Initialize query engine with dependencies"""
        self.vector_store = get_vector_store()
        self.llm_model = get_model()
        self.metadata_db = get_metadata_db()
        
        # Initialize the language model
        self.llm = self.llm_model.get_model()
        
        # Default prompt template for QA
        self.qa_prompt_template = """
Use the following pieces of context to answer the human's question. 
If you don't know the answer based on the provided context, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Helpful Answer:"""
        
        # Create prompt template
        self.prompt = PromptTemplate(
            template=self.qa_prompt_template,
            input_variables=["context", "question"]
        )
        
        logger.info("Initialized QueryEngine")
    
    def retrieve_documents(self, query: str, k: int = 5, category_filter: Optional[str] = None) -> List[Document]:
        """
        Retrieve relevant documents from vector store
        
        Args:
            query: User question/query
            k: Number of documents to retrieve
            category_filter: Optional category to filter by
            
        Returns:
            List[Document]: Retrieved documents
        """
        try:
            # Get documents from vector store
            documents = self.vector_store.similarity_search(query, k=k)
            
            # Filter by category if specified
            if category_filter:
                documents = [
                    doc for doc in documents 
                    if doc.metadata.get('category', '').lower() == category_filter.lower()
                ]
            
            logger.info(f"Retrieved {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def format_context(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            str: Formatted context string
        """
        if not documents:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(documents):
            filename = doc.metadata.get('filename', 'Unknown')
            chunk_index = doc.metadata.get('chunk_index', 0)
            
            context_part = f"[Source {i+1}: {filename} (chunk {chunk_index})]\n{doc.page_content}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def generate_answer(self, query: str, context: str) -> str:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User question
            context: Retrieved context
            
        Returns:
            str: Generated answer
        """
        try:
            # Format prompt with context and question
            formatted_prompt = self.prompt.format(context=context, question=query)
            
            # Generate response
            response = self.llm.invoke(formatted_prompt)
            
            # Extract text from response (handling different response formats)
            if hasattr(response, 'content'):
                answer = response.content
            elif isinstance(response, str):
                answer = response
            else:
                answer = str(response)
            
            logger.info("Generated answer successfully")
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Sorry, I encountered an error while generating the answer: {str(e)}"
    
    def extract_citations(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Extract citation information from documents
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            List[Dict[str, Any]]: Citation information
        """
        citations = []
        
        for i, doc in enumerate(documents):
            citation = {
                "source_number": i + 1,
                "filename": doc.metadata.get('filename', 'Unknown'),
                "chunk_index": doc.metadata.get('chunk_index', 0),
                "category": doc.metadata.get('category', 'general'),
                "upload_timestamp": doc.metadata.get('upload_timestamp', 'Unknown'),
                "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            citations.append(citation)
        
        return citations
    
    def query(self, question: str, k: int = 5, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Main query method that handles the complete RAG pipeline
        
        Args:
            question: User question
            k: Number of documents to retrieve
            category_filter: Optional category filter
            
        Returns:
            Dict[str, Any]: Query response with answer and metadata
        """
        try:
            # Log query
            query_timestamp = datetime.now().isoformat()
            logger.info(f"Processing query: {question}")
            
            # Retrieve relevant documents
            documents = self.retrieve_documents(question, k=k, category_filter=category_filter)
            
            if not documents:
                return {
                    "answer": "I couldn't find any relevant information to answer your question. Please try rephrasing or upload more documents.",
                    "sources": [],
                    "query": question,
                    "timestamp": query_timestamp,
                    "model": self.llm_model.get_model_name(),
                    "success": False
                }
            
            # Format context
            context = self.format_context(documents)
            
            # Generate answer
            answer = self.generate_answer(question, context)
            
            # Extract citations
            citations = self.extract_citations(documents)
            
            # Prepare response
            response = {
                "answer": answer,
                "sources": citations,
                "query": question,
                "timestamp": query_timestamp,
                "model": self.llm_model.get_model_name(),
                "documents_retrieved": len(documents),
                "category_filter": category_filter,
                "success": True
            }
            
            # Log query to database (optional)
            try:
                self.metadata_db.log_query({
                    "question": question,
                    "answer": answer,
                    "documents_retrieved": len(documents),
                    "timestamp": query_timestamp,
                    "model": self.llm_model.get_model_name(),
                    "category_filter": category_filter
                })
            except Exception as e:
                logger.warning(f"Failed to log query: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"Sorry, I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "query": question,
                "timestamp": datetime.now().isoformat(),
                "model": self.llm_model.get_model_name(),
                "success": False,
                "error": str(e)
            }
    
    def get_query_suggestions(self, category: Optional[str] = None) -> List[str]:
        """
        Get suggested queries based on available documents
        
        Args:
            category: Optional category to get suggestions for
            
        Returns:
            List[str]: List of suggested queries
        """
        base_suggestions = [
            "What are the company policies?",
            "How do I submit a vacation request?",
            "What are the working hours?",
            "What is the dress code policy?",
            "How do I access company resources?",
            "What are the benefits provided?",
            "How do I report an issue?",
            "What is the remote work policy?",
            "How do I get IT support?",
            "What are the safety protocols?"
        ]
        
        # Category-specific suggestions
        category_suggestions = {
            "hr": [
                "What is the hiring process?",
                "How do I update my personal information?",
                "What is the performance review process?",
                "How do I request time off?",
                "What are the employee benefits?"
            ],
            "policies": [
                "What is the code of conduct?",
                "What is the data privacy policy?",
                "What are the security guidelines?",
                "What is the expense reimbursement policy?",
                "What is the travel policy?"
            ],
            "sops": [
                "How do I perform system maintenance?",
                "What is the incident response procedure?",
                "How do I deploy new software?",
                "What is the backup procedure?",
                "How do I handle customer complaints?"
            ]
        }
        
        if category and category.lower() in category_suggestions:
            return category_suggestions[category.lower()]
        
        return base_suggestions
    
    def get_search_stats(self) -> Dict[str, Any]:
        """
        Get search statistics from metadata database
        
        Returns:
            Dict[str, Any]: Search statistics
        """
        try:
            return self.metadata_db.get_query_stats()
        except Exception as e:
            logger.error(f"Error getting search stats: {e}")
            return {
                "total_queries": 0,
                "popular_queries": [],
                "categories_searched": {}
            }


class AdvancedQueryEngine(QueryEngine):
    """Advanced query engine with additional features"""
    
    def __init__(self):
        super().__init__()
        
        # More sophisticated prompt templates
        self.detailed_prompt_template = """
You are a helpful assistant that answers questions based on company documents. 
Use the provided context to give detailed, accurate answers.

Instructions:
1. Answer based only on the provided context
2. If information is not in the context, say you don't know
3. Provide specific details when available
4. Use a professional, friendly tone
5. Reference sources when helpful

Context:
{context}

Question: {question}

Detailed Answer:"""
        
        self.detailed_prompt = PromptTemplate(
            template=self.detailed_prompt_template,
            input_variables=["context", "question"]
        )
    
    def query_with_followup(self, question: str, follow_up_questions: List[str] = None, k: int = 5) -> Dict[str, Any]:
        """
        Enhanced query method that can handle follow-up questions
        
        Args:
            question: Main question
            follow_up_questions: Optional follow-up questions
            k: Number of documents to retrieve
            
        Returns:
            Dict[str, Any]: Enhanced response with follow-up answers
        """
        # Get main answer
        main_response = self.query(question, k=k)
        
        if not follow_up_questions:
            return main_response
        
        # Process follow-up questions
        follow_ups = []
        for follow_up in follow_up_questions:
            follow_up_response = self.query(follow_up, k=k)
            follow_ups.append({
                "question": follow_up,
                "answer": follow_up_response["answer"],
                "sources": follow_up_response["sources"]
            })
        
        main_response["follow_ups"] = follow_ups
        return main_response


def create_query_engine() -> QueryEngine:
    """Create and return query engine instance"""
    return QueryEngine()


def create_advanced_query_engine() -> AdvancedQueryEngine:
    """Create and return advanced query engine instance"""
    return AdvancedQueryEngine()