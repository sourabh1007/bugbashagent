# Integrations

This folder contains all external system integrations for the Bug Bash Agent.

## 📁 Structure

```
integrations/
├── 📁 azure_openai/           # Azure OpenAI client integration
│   ├── client.py              # Main Azure OpenAI client wrapper
│   └── __init__.py           # Package exports
├── 📁 langsmith/             # LangSmith monitoring integration
│   ├── langsmith_integration.py  # Main LangSmith integration
│   ├── setup_langsmith.py    # LangSmith setup utilities
│   └── __init__.py           # Package exports
├── 📁 web/                   # Web content fetching
│   ├── client.py             # Web client for URL fetching
│   └── __init__.py           # Package exports
├── 📁 file_processing/       # File format processing
│   ├── processor.py          # Multi-format file processor
│   └── __init__.py           # Package exports
└── __init__.py              # Main integrations package
```

## 🔧 Available Integrations

### Azure OpenAI
- **Purpose**: Centralized Azure OpenAI client management
- **Features**: Client creation, configuration validation, error handling
- **Usage**: `from integrations import get_azure_openai_client`

### LangSmith
- **Purpose**: Monitoring and tracing of LLM interactions
- **Features**: Agent tracing, workflow monitoring, performance analytics
- **Usage**: `from integrations import trace_agent_execution`

### Web Client
- **Purpose**: Fetch content from web URLs
- **Features**: HTML parsing, content extraction, error handling
- **Usage**: `from integrations import fetch_url_content`

### File Processing
- **Purpose**: Process various file formats
- **Features**: Text files, PDF (optional), DOCX (optional), code files
- **Usage**: `from integrations import process_file`

## 📦 Dependencies

### Required
- `langchain-openai`: Azure OpenAI client
- `langsmith`: LangSmith monitoring
- `requests`: Web content fetching

### Optional
- `beautifulsoup4`: Enhanced HTML parsing
- `PyPDF2`: PDF file processing
- `python-docx`: DOCX file processing

## 🚀 Usage Examples

### Azure OpenAI
```python
from integrations import get_azure_openai_client, check_azure_config

# Check configuration
if check_azure_config():
    # Get client with default settings
    llm = get_azure_openai_client()
    
    # Get client with custom settings
    llm = get_azure_openai_client(temperature=0.5, max_tokens=4000)
```

### LangSmith Tracing
```python
from integrations import trace_agent_execution

@trace_agent_execution
def my_agent_function(input_data):
    # Agent logic here
    return result
```

### Web Content
```python
from integrations import fetch_url_content

result = fetch_url_content("https://example.com")
if result.get('text_content'):
    print(f"Content: {result['text_content'][:100]}...")
```

### File Processing
```python
from integrations import process_file

result = process_file("document.pdf")
if result.get('processed'):
    print(f"Content: {result['content'][:100]}...")
```

## 🛠️ Adding New Integrations

1. Create a new folder under `integrations/`
2. Implement the integration in the folder
3. Add `__init__.py` with exports
4. Update main `integrations/__init__.py` to include the new integration
5. Update this README with documentation

## 🔧 Configuration

All integrations use environment variables from the `.env` file:

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment

# LangSmith (Optional)
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=BugBashAgent
```
