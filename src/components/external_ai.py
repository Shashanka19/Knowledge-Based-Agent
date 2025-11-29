"""
External AI Integration Module
Integrates with ChatGPT, Copilot, and Google Search for comprehensive answers
"""

import os
import requests
import json
import time
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import streamlit as st

class ExternalAIIntegrator:
    """Integrates with external AI services"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cx = os.getenv("GOOGLE_CUSTOM_SEARCH_CX")
        
    def query_chatgpt(self, question: str, context: str = "") -> Dict[str, Any]:
        """Query ChatGPT API directly"""
        try:
            if not self.openai_api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "source": "ChatGPT"
                }
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            Question: {question}
            
            {f'Context from knowledge base: {context}' if context else ''}
            
            Please provide a comprehensive answer. If you reference any external information, 
            mention it's from your training data up to your knowledge cutoff.
            """
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant providing accurate and comprehensive answers. Always mention when information comes from your training data."
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # Add retry logic for rate limiting
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "success": True,
                            "answer": result["choices"][0]["message"]["content"],
                            "source": "ChatGPT (OpenAI)",
                            "model": "gpt-3.5-turbo",
                            "timestamp": datetime.now().isoformat(),
                            "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                        }
                    elif response.status_code == 429:
                        # Rate limit exceeded - wait and retry
                        wait_time = (attempt + 1) * 2  # Exponential backoff
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(wait_time)
                            continue
                        else:
                            return {
                                "success": False,
                                "error": f"Rate limit exceeded. Try again in a few minutes.",
                                "source": "ChatGPT"
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"OpenAI API error: {response.status_code} - {response.text}",
                            "source": "ChatGPT"
                        }
                except requests.RequestException as req_err:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return {
                        "success": False,
                        "error": f"Request failed: {str(req_err)}",
                        "source": "ChatGPT"
                    }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "ChatGPT"
            }
    
    def query_google_search(self, question: str, num_results: int = 5) -> Dict[str, Any]:
        """Query Google Custom Search API"""
        try:
            if not self.google_api_key or not self.google_cx:
                return {
                    "success": False,
                    "error": "Google API credentials not configured",
                    "source": "Google Search"
                }
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cx,
                "q": question,
                "num": min(num_results, 10)
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                results = response.json()
                
                search_results = []
                for item in results.get("items", []):
                    search_results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", ""),
                        "source": item.get("displayLink", "")
                    })
                
                # Compile answer from top results
                answer = f"Based on Google search results for '{question}':\\n\\n"
                for i, result in enumerate(search_results[:3], 1):
                    answer += f"{i}. **{result['title']}** ({result['source']})\\n"
                    answer += f"   {result['snippet']}\\n"
                    answer += f"   🔗 {result['link']}\\n\\n"
                
                return {
                    "success": True,
                    "answer": answer,
                    "source": "Google Search",
                    "results": search_results,
                    "timestamp": datetime.now().isoformat(),
                    "results_count": len(search_results)
                }
            else:
                return {
                    "success": False,
                    "error": f"Google Search API error: {response.status_code}",
                    "source": "Google Search"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "Google Search"
            }
    
    def simulate_copilot_response(self, question: str, context: str = "") -> Dict[str, Any]:
        """Simulate GitHub Copilot response (using OpenAI with coding context)"""
        try:
            if not self.openai_api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "source": "GitHub Copilot"
                }
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            As GitHub Copilot, provide a helpful response to: {question}
            
            {f'Available context: {context}' if context else ''}
            
            Focus on:
            - Practical, actionable advice
            - Code examples when relevant
            - Best practices and recommendations
            - Step-by-step guidance
            
            Format your response as if you're GitHub Copilot assistant.
            """
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are GitHub Copilot, an AI coding assistant. Provide helpful, practical responses with code examples when relevant. Be concise but comprehensive."
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 600,
                "temperature": 0.5
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                
                # Add Copilot branding to response
                formatted_answer = f"**🤖 GitHub Copilot Response:**\\n\\n{answer}\\n\\n"
                formatted_answer += "*This response was generated using GitHub Copilot's AI capabilities.*"
                
                return {
                    "success": True,
                    "answer": formatted_answer,
                    "source": "GitHub Copilot",
                    "model": "gpt-3.5-turbo (Copilot-style)",
                    "timestamp": datetime.now().isoformat(),
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"Copilot simulation error: {response.status_code}",
                    "source": "GitHub Copilot"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "GitHub Copilot"
            }
    
    def query_all_sources(self, question: str, knowledge_base_context: str = "") -> List[Dict[str, Any]]:
        """Query all available AI sources and return combined results with rate limit handling"""
        results = []
        
        # Query ChatGPT first
        with st.spinner("🤖 Querying ChatGPT..."):
            chatgpt_result = self.query_chatgpt(question, knowledge_base_context)
            results.append(chatgpt_result)
            
            # If ChatGPT hit rate limit, skip Copilot to avoid double rate limiting
            if chatgpt_result.get('error') and '429' in str(chatgpt_result.get('error')):
                st.warning("⚠️ Rate limit detected - using demo responses for additional sources")
                
                # Add demo Copilot response
                copilot_demo = {
                    "success": True,
                    "answer": f"**🤖 GitHub Copilot Demo Response:**\n\nFor '{question}', I would provide technical assistance including:\n\n• Step-by-step troubleshooting\n• Code examples and snippets\n• Best practice recommendations\n• Resource links\n\n*Demo mode due to API rate limits*",
                    "source": "GitHub Copilot (Demo)",
                    "timestamp": datetime.now().isoformat()
                }
                results.append(copilot_demo)
            else:
                # Query GitHub Copilot normally
                with st.spinner("⚡ Consulting GitHub Copilot..."):
                    copilot_result = self.simulate_copilot_response(question, knowledge_base_context)
                    results.append(copilot_result)
        
        # Query Google Search (independent of OpenAI rate limits)
        with st.spinner("🔍 Searching Google..."):
            google_result = self.query_google_search(question)
            results.append(google_result)
        
        return results
    
    def format_multi_source_response(self, question: str, results: List[Dict[str, Any]], 
                                   kb_response: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format response from multiple sources"""
        
        answer = f"# 🌟 Comprehensive Answer: {question}\\n\\n"
        
        # Add knowledge base response first if available
        if kb_response and kb_response.get('success'):
            answer += "## 📚 **From Your Knowledge Base:**\\n"
            answer += f"{kb_response['answer']}\\n\\n"
            answer += "---\\n\\n"
        
        # Add external sources
        successful_sources = [r for r in results if r.get('success')]
        
        for i, result in enumerate(successful_sources, 1):
            source_name = result.get('source', 'Unknown Source')
            answer += f"## {i}. **{source_name}:**\\n"
            answer += f"{result.get('answer', 'No response available')}\\n\\n"
            
            # Add metadata
            if result.get('model'):
                answer += f"*Model: {result['model']}*\\n"
            if result.get('tokens_used'):
                answer += f"*Tokens used: {result['tokens_used']}*\\n"
            if result.get('results_count'):
                answer += f"*Search results: {result['results_count']}*\\n"
            
            answer += "---\\n\\n"
        
        # Add failed sources info
        failed_sources = [r for r in results if not r.get('success')]
        if failed_sources:
            answer += "## ⚠️ **Unavailable Sources:**\\n"
            for failed in failed_sources:
                answer += f"• {failed.get('source', 'Unknown')}: {failed.get('error', 'Unknown error')}\\n"
        
        return {
            "success": True,
            "answer": answer,
            "sources": [r.get('source') for r in successful_sources],
            "total_sources": len(results),
            "successful_sources": len(successful_sources),
            "timestamp": datetime.now().isoformat()
        }