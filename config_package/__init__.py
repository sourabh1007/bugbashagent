"""
Configuration package for Bug Bash Copilot
"""

import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# LangSmith Configuration
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "BugBashCopilot")

# Model settings
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-35-turbo")
try:
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
except (ValueError, TypeError):
    TEMPERATURE = 0.7

# Agent settings
DOCUMENT_ANALYZER_NAME = "Document Analyzer"
CODE_GENERATOR_NAME = "Code Generator"

# Import package versions
try:
    from .package_versions import PackageVersions
except ImportError as e:
    print(f"Warning: Could not import PackageVersions: {e}")
    PackageVersions = None
