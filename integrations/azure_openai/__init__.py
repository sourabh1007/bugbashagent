"""
Azure OpenAI Integration Package

This package provides Azure OpenAI client management and utilities.
"""

from .client import (
    AzureOpenAIClient,
    get_azure_openai_client,
    check_azure_config,
    get_missing_azure_config
)

__all__ = [
    'AzureOpenAIClient',
    'get_azure_openai_client',
    'check_azure_config',
    'get_missing_azure_config',
]
