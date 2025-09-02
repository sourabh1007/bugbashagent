#!/usr/bin/env python3
"""
Command-line interface for BugBashAgent with file path support

Usage:
    python run_with_file.py --file "path/to/document.txt"
    python run_with_file.py --file "C:\Documents\SDK_Guide.md" --language C#
    python run_with_file.py --text "Your requirements here"
    python run_with_file.py --url "https://example.com/api-docs"
"""

import os
import sys
import argparse
from pathlib import Path
from langchain_openai import AzureChatOpenAI
from config_package import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    MODEL_NAME,
    TEMPERATURE
)
from workflow import AgentWorkflow


def read_file_content(file_path: str) -> str:
    """Read content from various file formats"""
    try:
        file_path = Path(file_path).resolve()
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension in ['.txt', '.md', '.py', '.cs', '.js', '.java', '.go', '.rs', '.yml', '.yaml', '.json']:
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
                # Try reading as text
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
                raise
        
        else:
            # Try as plain text
            print(f"⚠️ Unknown file extension {file_extension}. Trying to read as plain text...")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            print(f"✅ Successfully read {len(content)} characters as plain text")
            return content
            
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {str(e)}")
        raise


def fetch_url_content(url: str) -> str:
    """Fetch content from URL with support for various content types"""
    try:
        # Try to import requests
        try:
            import requests
        except ImportError:
            print("⚠️ requests library not found. Installing...")
            import subprocess
            import sys
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
        raise
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Could not connect to {url}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error {e.response.status_code}: {e.response.reason}")
        raise
    except Exception as e:
        print(f"❌ Error fetching URL {url}: {str(e)}")
        raise


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="BugBashAgent - AI-Powered Code Generation from Documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using a local file
  python run_with_file.py --file "docs/api-guide.md" --language Python
  
  # Using a Windows file path
  python run_with_file.py --file "C:\\Documents\\SDK_Documentation.txt"
  
  # Using direct text input
  python run_with_file.py --text "Create tests for Azure Cosmos DB SDK"
  
  # Using a URL
  python run_with_file.py --url "https://docs.microsoft.com/azure/cosmos-db"
  
  # With custom output directory
  python run_with_file.py --file "input.md" --output "my_output"
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file', '-f',
        type=str,
        help='Path to local file (txt, md, pdf, docx, json, etc.)'
    )
    input_group.add_argument(
        '--text', '-t',
        type=str,
        help='Direct text input'
    )
    input_group.add_argument(
        '--url', '-u',
        type=str,
        help='URL to fetch content from'
    )
    
    # Optional parameters
    parser.add_argument(
        '--language', '-l',
        type=str,
        default='C#',
        choices=['C#', 'Python', 'JavaScript', 'Java', 'Go', 'Rust'],
        help='Target programming language (default: C#)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Custom output directory name'
    )
    
    parser.add_argument(
        '--max-scenarios',
        type=int,
        default=25,
        help='Maximum number of scenarios to generate (default: 25)'
    )
    
    parser.add_argument(
        '--max-attempts',
        type=int,
        default=3,
        help='Maximum compilation attempts (default: 3)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    try:
        # Get input content
        if args.file:
            print(f"📄 Reading file: {args.file}")
            input_content = read_file_content(args.file)
        elif args.text:
            print("📝 Using direct text input")
            input_content = args.text
        elif args.url:
            print(f"🌐 Fetching content from: {args.url}")
            input_content = fetch_url_content(args.url)
        
        if not input_content.strip():
            print("❌ No content found in input")
            sys.exit(1)
        
        print(f"✅ Input content length: {len(input_content)} characters")
        
        # Check Azure configuration
        missing_configs = []
        if not AZURE_OPENAI_API_KEY:
            missing_configs.append("AZURE_OPENAI_API_KEY")
        if not AZURE_OPENAI_ENDPOINT:
            missing_configs.append("AZURE_OPENAI_ENDPOINT")
        if not AZURE_OPENAI_DEPLOYMENT_NAME:
            missing_configs.append("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if missing_configs:
            print("❌ Error: Missing Azure OpenAI configuration!")
            print("Please set the following environment variables or in .env file:")
            for config_name in missing_configs:
                print(f"  {config_name}")
            sys.exit(1)
        
        # Initialize LLM
        print("\n🔧 Initializing Azure OpenAI Language Model...")
        llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=TEMPERATURE
        )
        
        # Create and execute workflow
        print(f"🚀 Starting code generation for {args.language}...")
        workflow = AgentWorkflow(llm)
        
        # Set custom output folder if specified
        if args.output:
            workflow.custom_output_name = args.output
        
        # Execute workflow
        results = workflow.execute_workflow(input_content)
        
        # Display results
        print("\n" + "="*60)
        print("📊 WORKFLOW SUMMARY")
        print("="*60)
        
        status = results['workflow_status']
        print(f"Status: {status.upper()}")
        
        if status == 'completed':
            print("✅ Code generation completed successfully!")
        else:
            print("❌ Code generation failed or incomplete")
        
        print(f"📂 Output folder: {results.get('output_folder', 'N/A')}")
        
        # Show agent results
        for i, agent_output in enumerate(results.get('agent_outputs', []), 1):
            agent_name = agent_output.get('agent', f'Agent {i}')
            agent_status = agent_output.get('status', 'unknown')
            status_icon = "✅" if agent_status == 'success' else "❌"
            print(f"  {i}. {status_icon} {agent_name}: {agent_status}")
        
        # Show compilation details for Code Generator
        for agent_output in results.get('agent_outputs', []):
            if agent_output.get('agent') == 'Code Generator':
                code_output = agent_output.get('output', {})
                if isinstance(code_output, dict):
                    attempts = code_output.get('compilation_attempts', [])
                    if attempts:
                        print(f"\n🔧 Compilation attempts: {len(attempts)}")
                        final_status = code_output.get('status', 'unknown')
                        if final_status == 'success':
                            successful_attempt = code_output.get('successful_attempt', len(attempts))
                            print(f"✅ Compilation successful on attempt {successful_attempt}")
                        else:
                            print(f"❌ Compilation failed after {len(attempts)} attempts")
                
                break
        
        # Final output location
        if results.get('output_folder'):
            print(f"\n📁 All files saved to: {results['output_folder']}")
            
            # List key files if they exist
            output_path = Path(results['output_folder'])
            if output_path.exists():
                key_files = list(output_path.glob("*.md")) + list(output_path.glob("*.txt"))
                if key_files:
                    print("📄 Key output files:")
                    for file in key_files[:5]:  # Show first 5 files
                        print(f"  - {file.name}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        if args.verbose:
            import traceback
            print(f"\n❌ Error: {str(e)}")
            print(f"Debug traceback:\n{traceback.format_exc()}")
        else:
            print(f"\n❌ Error: {str(e)}")
            print("Use --verbose flag for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()
