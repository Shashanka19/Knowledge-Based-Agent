"""
Model Loader Component for KnowledgeBase Agent
Handles loading and configuration of different LLM models (OpenAI GPT, Claude, Gemini)
"""

import os
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from langchain_openai import OpenAI, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseLanguageModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelInterface(ABC):
    """Abstract interface for language model implementations"""
    
    @abstractmethod
    def get_model(self) -> BaseLanguageModel:
        """Get the language model instance"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name"""
        pass


class OpenAIModel(ModelInterface):
    """OpenAI GPT model implementation"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo", temperature: float = 0.0):
        """
        Initialize OpenAI model
        
        Args:
            api_key: OpenAI API key
            model_name: Name of the OpenAI model
            temperature: Temperature for response generation
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        
        # Set API key
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize model based on type
        self.model = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        logger.info(f"Initialized OpenAI model: {model_name}")
    
    def get_model(self) -> BaseLanguageModel:
        """Get the OpenAI model instance"""
        return self.model
    
    def get_model_name(self) -> str:
        """Get the OpenAI model name"""
        return self.model_name


class ClaudeModel(ModelInterface):
    """Anthropic Claude model implementation"""
    
    def __init__(self, api_key: str, model_name: str = "claude-2", temperature: float = 0.0):
        """
        Initialize Claude model
        
        Args:
            api_key: Anthropic API key
            model_name: Name of the Claude model
            temperature: Temperature for response generation
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        
        # Set API key
        os.environ["ANTHROPIC_API_KEY"] = api_key
        
        # Initialize model
        self.model = ChatAnthropic(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        logger.info(f"Initialized Claude model: {model_name}")
    
    def get_model(self) -> BaseLanguageModel:
        """Get the Claude model instance"""
        return self.model
    
    def get_model_name(self) -> str:
        """Get the Claude model name"""
        return self.model_name


class GeminiModel(ModelInterface):
    """Google Gemini model implementation"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", temperature: float = 0.0):
        """
        Initialize Gemini model
        
        Args:
            api_key: Google API key
            model_name: Name of the Gemini model
            temperature: Temperature for response generation
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        
        # Set API key
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Initialize model
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key
        )
        
        logger.info(f"Initialized Gemini model: {model_name}")
    
    def get_model(self) -> BaseLanguageModel:
        """Get the Gemini model instance"""
        return self.model
    
    def get_model_name(self) -> str:
        """Get the Gemini model name"""
        return self.model_name


class ModelFactory:
    """Factory class to create model instances"""
    
    # Model configurations
    MODEL_CONFIGS = {
        "openai": {
            "gpt-3.5-turbo": {"class": OpenAIModel, "default_temp": 0.0},
            "gpt-4": {"class": OpenAIModel, "default_temp": 0.0},
            "gpt-4-turbo": {"class": OpenAIModel, "default_temp": 0.0},
            "text-davinci-003": {"class": OpenAIModel, "default_temp": 0.0},
        },
        "claude": {
            "claude-2": {"class": ClaudeModel, "default_temp": 0.0},
            "claude-3-sonnet": {"class": ClaudeModel, "default_temp": 0.0},
            "claude-3-opus": {"class": ClaudeModel, "default_temp": 0.0},
            "claude-instant": {"class": ClaudeModel, "default_temp": 0.0},
        },
        "gemini": {
            "gemini-pro": {"class": GeminiModel, "default_temp": 0.0},
            "gemini-pro-vision": {"class": GeminiModel, "default_temp": 0.0},
        }
    }
    
    @staticmethod
    def create_model(provider: str, model_name: str, api_key: str, temperature: Optional[float] = None) -> ModelInterface:
        """
        Create model instance based on provider and model name
        
        Args:
            provider: Model provider ('openai', 'claude', 'gemini')
            model_name: Name of the specific model
            api_key: API key for the provider
            temperature: Temperature for response generation
            
        Returns:
            ModelInterface: Model instance
        """
        provider = provider.lower()
        
        if provider not in ModelFactory.MODEL_CONFIGS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = ModelFactory.MODEL_CONFIGS[provider]
        
        if model_name not in provider_config:
            raise ValueError(f"Unsupported model {model_name} for provider {provider}")
        
        model_config = provider_config[model_name]
        model_class = model_config["class"]
        
        if temperature is None:
            temperature = model_config["default_temp"]
        
        return model_class(
            api_key=api_key,
            model_name=model_name,
            temperature=temperature
        )
    
    @staticmethod
    def get_available_models() -> Dict[str, list]:
        """Get all available models grouped by provider"""
        return {
            provider: list(models.keys())
            for provider, models in ModelFactory.MODEL_CONFIGS.items()
        }


def get_model() -> ModelInterface:
    """
    Get configured model instance based on environment variables
    
    Returns:
        ModelInterface: Configured model instance
    """
    provider = os.getenv("MODEL_PROVIDER", "openai").lower()
    model_name = os.getenv("MODEL_NAME")
    temperature = float(os.getenv("MODEL_TEMPERATURE", "0.0"))
    
    # Get API key based on provider
    api_key = None
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not model_name:
            model_name = "gpt-3.5-turbo"
    elif provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not model_name:
            model_name = "claude-2"
    elif provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not model_name:
            model_name = "gemini-pro"
    
    if not api_key:
        raise ValueError(f"API key not found for provider: {provider}")
    
    return ModelFactory.create_model(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        temperature=temperature
    )


def get_embedding_model():
    """Get embedding model for vector store operations"""
    from langchain_openai import OpenAIEmbeddings
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for embeddings")
    
    return OpenAIEmbeddings(api_key=api_key)