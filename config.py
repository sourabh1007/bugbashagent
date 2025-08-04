import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Model settings
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-35-turbo")  # Default to gpt-35-turbo for Azure
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Agent settings
DOCUMENT_ANALYZER_NAME = "Document Analyzer"
CODE_GENERATOR_NAME = "Code Generator"
CODE_EXECUTOR_NAME = "Code Executor"
