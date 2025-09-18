#!/usr/bin/env python3
"""
Bug Bash Copilot - AI-Powered Code Quality Assessment

This application demonstrates a multi-agent workflow for automated bug detection and quality assessment:
1. Document Analyzer - Analyzes requirements and extracts key information
2. Code Generator - Generates code based on the analyzed requirements  
3. Test Runner - Executes comprehensive testing and quality analysis

Each agent passes its output to the next agent in sequence for complete quality assessment.
"""

import os
import sys

# Import integrations
from integrations import (
    get_azure_openai_client,
    get_agent_azure_openai_client,
    check_azure_config,
    get_missing_azure_config,
    setup_langsmith,
    configure_llm_tracing,
    LangSmithIntegration
)

# Import specific configuration items
from config_package import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    MODEL_NAME,
    TEMPERATURE,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT
)
from workflow import AgentWorkflow




def get_user_input():
    """Get requirements input from user - supports text input or file path"""
    print("🤖 Bug Bash Copilot - AI-Powered Quality Assessment")
    print("=" * 52)
    
    print("\nChoose input method:")
    print("1. Enter text directly")
    print("2. Provide local file path")
    print("3. Provide URL (if supported)")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        # Direct text input
        requirements = input("\nEnter your project requirements or description: ").strip()
        if not requirements:
            print("❌ No requirements provided. Exiting.")
            sys.exit(1)
        return requirements
    
    elif choice == "2":
        # File path input
        file_path = input("\nEnter local file path (txt, md, pdf, docx): ").strip()
        
        if not file_path:
            print("❌ No file path provided. Exiting.")
            sys.exit(1)
        
        # Handle Windows path separators and quoted paths
        file_path = file_path.strip('"\'')
        file_path = os.path.expanduser(file_path)  # Handle ~ in Unix paths
        file_path = os.path.abspath(file_path)     # Convert to absolute path
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        print(f"📄 Reading file: {file_path}")
        return read_file_content(file_path)
    
    elif choice == "3":
        # URL input with full implementation
        url = input("\nEnter URL (http/https): ").strip()
        
        if not url:
            print("❌ No URL provided. Exiting.")
            sys.exit(1)
        
        # Validate URL format
        if not (url.startswith('http://') or url.startswith('https://')):
            print("❌ Please provide a valid URL starting with http:// or https://")
            return get_user_input()  # Recurse to try again
        
        print(f"🌐 Fetching content from: {url}")
        return fetch_url_content(url)
    
    else:
        print("❌ Invalid choice. Please enter 1, 2, or 3.")
        return get_user_input()  # Recurse to try again


def read_file_content(file_path: str) -> str:
    """Read content from various file formats"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.txt', '.md', '.py', '.cs', '.js', '.java', '.go', '.rs']:
            # Plain text files
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Successfully read {len(content)} characters from {file_extension} file")
            return content
        
        elif file_extension == '.pdf':
            # PDF files
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    content = ""
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
                print(f"✅ Successfully extracted {len(content)} characters from PDF")
                return content
            except ImportError:
                print("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")
                print("Reading as text file instead...")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        
        elif file_extension in ['.docx', '.doc']:
            # Word documents
            try:
                from docx import Document
                doc = Document(file_path)
                content = ""
                for paragraph in doc.paragraphs:
                    content += paragraph.text + "\n"
                print(f"✅ Successfully extracted {len(content)} characters from Word document")
                return content
            except ImportError:
                print("⚠️ python-docx not installed. Install with: pip install python-docx")
                print("Please convert to .txt or .md format and try again.")
                sys.exit(1)
        
        elif file_extension == '.json':
            # JSON files
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            content = json.dumps(json_data, indent=2)
            print(f"✅ Successfully read JSON file with {len(content)} characters")
            return content
        
        else:
            # Try as plain text
            print(f"⚠️ Unknown file extension {file_extension}. Trying to read as plain text...")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            print(f"✅ Successfully read {len(content)} characters as plain text")
            return content
            
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {str(e)}")
        sys.exit(1)


def fetch_url_content(url: str) -> str:
    """Fetch content from URL with support for various content types"""
    try:
        # Try to import requests
        try:
            import requests
        except ImportError:
            print("⚠️ requests library not found. Installing...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
        
        print(f"🌐 Fetching content from URL...")
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request with timeout
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get content type
        content_type = response.headers.get('content-type', '').lower()
        
        print(f"✅ Successfully fetched content (Content-Type: {content_type})")
        
        # Handle different content types
        if 'application/json' in content_type:
            # JSON content
            try:
                import json
                json_data = response.json()
                content = json.dumps(json_data, indent=2)
                print(f"📄 Processed as JSON: {len(content)} characters")
                return content
            except:
                # Fallback to text if JSON parsing fails
                content = response.text
                print(f"⚠️ JSON parsing failed, using as text: {len(content)} characters")
                return content
        
        elif 'text/html' in content_type:
            # HTML content - extract text
            content = response.text
            
            # Try to extract meaningful text from HTML
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text_content = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                cleaned_content = '\n'.join(chunk for chunk in chunks if chunk)
                
                print(f"📄 Extracted text from HTML: {len(cleaned_content)} characters")
                return cleaned_content
                
            except ImportError:
                print("⚠️ BeautifulSoup not available for HTML parsing. Using raw HTML.")
                print("Install with: pip install beautifulsoup4")
                print(f"📄 Raw HTML content: {len(content)} characters")
                return content
        
        elif 'text/plain' in content_type or 'text/markdown' in content_type:
            # Plain text or markdown
            content = response.text
            print(f"📄 Plain text content: {len(content)} characters")
            return content
        
        else:
            # Unknown content type - try as text
            content = response.text
            print(f"📄 Unknown content type, treating as text: {len(content)} characters")
            return content
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout: URL took longer than 30 seconds to respond")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Could not connect to {url}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error {e.response.status_code}: {e.response.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error fetching URL {url}: {str(e)}")
        sys.exit(1)



def main():
    """Main application entry point"""
    try:
        # Check configuration
        check_azure_config()
        
        # Get user input
        requirements = get_user_input()
        
        # Initialize distinct Azure OpenAI LLMs per agent (merged later in workflow)
        print("\n🔧 Initializing Azure OpenAI Language Models (per agent)...")
        document_llm = get_agent_azure_openai_client(
            "document_analyzer",
            temperature=TEMPERATURE
        )
        code_llm = get_agent_azure_openai_client(
            "code_generator",
            temperature=TEMPERATURE
        )

        # Choose default llm for backward compatibility (first agent)
        llm = document_llm
        
        # Configure LLM for LangSmith tracing
        llm = configure_llm_tracing(llm)
        
        # Create and execute workflow
        print("🚀 Starting Bug Bash Copilot quality assessment workflow...")
        workflow = AgentWorkflow(llm, code_llm=code_llm)
        results = workflow.execute_workflow(requirements)

        # Display summary
        print("\n" + workflow.get_workflow_summary(results))

        # Display final output if successful
        if results['workflow_status'] == 'completed':
            print("\n📋 FINAL CODE EXECUTION REPORT:")
            print("=" * 60)
            # Use the new formatted report instead of raw dictionary
            formatted_report = workflow.format_final_execution_report(results['final_output'])
            print(formatted_report)
            print(f"\n📂 All intermediate and final outputs saved in:")
            print(f"   {results['output_folder']}")
        else:
            print(f"\n📂 Partial outputs saved in:")
            print(f"   {results['output_folder']}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n❌ Application error: {str(e)}")
        print(f"Debug traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
