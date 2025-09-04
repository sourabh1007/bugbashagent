"""
Integrations Package

This package contains all external system integrations for the Bug Bash Agent.
"""

from .azure_openai.client import (
    AzureOpenAIClient,
    get_azure_openai_client,
    get_agent_azure_openai_client,
    check_azure_config,
    get_missing_azure_config
)

from .langsmith.langsmith_integration import (
    LangSmithIntegration,
    trace_agent_execution,
    trace_workflow_execution,
    configure_llm_tracing,
    get_langsmith_dashboard_url
)

from .langsmith.setup_langsmith import main as setup_langsmith

from .web.client import (
    WebClient,
    fetch_url_content,
    is_web_content_available,
    get_web_dependencies
)

from .file_processing.processor import (
    FileProcessor,
    process_file,
    get_file_dependencies,
    get_supported_extensions
)

__all__ = [
    # Azure OpenAI
    'AzureOpenAIClient',
    'get_azure_openai_client',
    'get_agent_azure_openai_client',
    'check_azure_config',
    'get_missing_azure_config',
    
    # LangSmith
    'LangSmithIntegration',
    'trace_agent_execution',
    'trace_workflow_execution',
    'configure_llm_tracing',
    'get_langsmith_dashboard_url',
    'setup_langsmith',
    
    # Web
    'WebClient',
    'fetch_url_content',
    'is_web_content_available',
    'get_web_dependencies',
    
    # File Processing
    'FileProcessor',
    'process_file',
    'get_file_dependencies',
    'get_supported_extensions',
]
