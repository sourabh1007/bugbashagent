"""
Azure OpenAI Client Integration

This module provides a centralized Azure OpenAI client for the Bug Bash Agent.
"""

import os
from typing import Optional, Dict, Any
from langchain_openai import AzureChatOpenAI
from config_package import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
)


class AzureOpenAIClient:
    """Centralized Azure OpenAI client for the Bug Bash Agent."""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 endpoint: Optional[str] = None,
                 api_version: Optional[str] = None,
                 deployment_name: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 8000):
        """
        Initialize Azure OpenAI client.
        
        Args:
            api_key: Azure OpenAI API key (defaults to env var)
            endpoint: Azure OpenAI endpoint (defaults to env var)
            api_version: Azure OpenAI API version (defaults to env var)
            deployment_name: Azure OpenAI deployment name (defaults to env var)
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens for response
        """
        self.api_key = api_key or AZURE_OPENAI_API_KEY
        self.endpoint = endpoint or AZURE_OPENAI_ENDPOINT
        self.api_version = api_version or AZURE_OPENAI_API_VERSION
        self.deployment_name = deployment_name or AZURE_OPENAI_DEPLOYMENT_NAME
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Validate configuration
        self._validate_config()
        
        # Initialize the LangChain client
        self._client = None
    
    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        missing_configs = []
        
        if not self.api_key:
            missing_configs.append("AZURE_OPENAI_API_KEY")
        if not self.endpoint:
            missing_configs.append("AZURE_OPENAI_ENDPOINT")
        if not self.deployment_name:
            missing_configs.append("AZURE_OPENAI_DEPLOYMENT_NAME")
        if not self.api_version:
            missing_configs.append("AZURE_OPENAI_API_VERSION")
        
        if missing_configs:
            raise ValueError(f"Missing Azure OpenAI configuration: {', '.join(missing_configs)}")
    
    def get_client(self, **kwargs) -> AzureChatOpenAI:
        """
        Get or create Azure OpenAI client.
        
        Args:
            **kwargs: Additional parameters to override defaults
            
        Returns:
            AzureChatOpenAI: Configured Azure OpenAI client
        """
        # Merge default parameters with overrides
        params = {
            "azure_endpoint": self.endpoint,
            "api_key": self.api_key,
            "api_version": self.api_version,
            "azure_deployment": self.deployment_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        params.update(kwargs)
        
        return AzureChatOpenAI(**params)
    
    @property
    def client(self) -> AzureChatOpenAI:
        """Get cached client instance."""
        if self._client is None:
            self._client = self.get_client()
        return self._client
    
    def create_client_with_settings(self, temperature: float = None, max_tokens: int = None) -> AzureChatOpenAI:
        """
        Create a new client with specific settings.
        
        Args:
            temperature: Override temperature
            max_tokens: Override max tokens
            
        Returns:
            AzureChatOpenAI: New client with specified settings
        """
        overrides = {}
        if temperature is not None:
            overrides["temperature"] = temperature
        if max_tokens is not None:
            overrides["max_tokens"] = max_tokens
            
        return self.get_client(**overrides)


def get_azure_openai_client(**kwargs) -> AzureChatOpenAI:
    """
    Convenience function to get an Azure OpenAI client.
    
    Args:
        **kwargs: Parameters to override defaults
        
    Returns:
        AzureChatOpenAI: Configured Azure OpenAI client
    """
    client_manager = AzureOpenAIClient()
    return client_manager.get_client(**kwargs)


def check_azure_config() -> bool:
    """
    Check if Azure OpenAI configuration is properly set up.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    try:
        client_manager = AzureOpenAIClient()
        return True
    except ValueError:
        return False


def get_missing_azure_config() -> list:
    """
    Get list of missing Azure OpenAI configuration items.
    
    Returns:
        list: List of missing configuration keys
    """
    missing_configs = []
    
    if not AZURE_OPENAI_API_KEY:
        missing_configs.append("AZURE_OPENAI_API_KEY")
    if not AZURE_OPENAI_ENDPOINT:
        missing_configs.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_DEPLOYMENT_NAME:
        missing_configs.append("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    return missing_configs
