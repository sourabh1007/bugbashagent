#!/usr/bin/env python3
"""
Streamlit UI for Multi-Agent Code Development Workflow

This application provides a web interface for monitoring and interacting with
the multi-agent workflow system including Document Analyzer, Code Generator, and Test Runner.
"""

import os
import json
import time
import threading
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional

# Only import streamlit when we know we're in the right context
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Import data visualization libraries
try:
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    pd = px = go = None


def process_uploaded_file(uploaded_file) -> str:
    """
    Process uploaded file using FileProcessor to extract text content.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        str: Extracted text content from the file or error message
    """
    try:
        # Import FileProcessor
        from integrations.file_processing.processor import FileProcessor, get_file_dependencies
        
        # Check file extension
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Check if required dependencies are available for this file type
        deps = get_file_dependencies()
        if file_ext == '.pdf' and not deps.get('PyPDF2', False):
            return "❌ PDF processing requires PyPDF2. Please install it with: pip install PyPDF2>=3.0.1"
        elif file_ext == '.docx' and not deps.get('python-docx', False):
            return "❌ DOCX processing requires python-docx. Please install it with: pip install python-docx>=1.2.0"
        
        # Create a temporary file to process the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            # Write uploaded content to temp file
            file_content = uploaded_file.getvalue()
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process the file using FileProcessor
            processor = FileProcessor()
            result = processor.process_file(tmp_file_path)
            
            if result.get('processed', False):
                content = result.get('content', '')
                if not content or content.strip() == '':
                    return f"⚠️ File processed successfully but no readable text content found in {uploaded_file.name}. The file might be empty, corrupted, or contain only images/graphics."
                
                # Validate content quality
                if len(content.strip()) < 10:
                    return f"⚠️ Very little text content found in {uploaded_file.name} ({len(content)} characters). Please verify the file contains readable text."
                
                return content.strip()
            else:
                error_msg = result.get('error', 'Unknown error')
                
                # Provide more helpful error messages
                if 'Unsupported file format' in error_msg:
                    supported_formats = result.get('supported_formats', [])
                    return f"❌ File type {file_ext} is not supported. Supported formats: {', '.join(supported_formats)}"
                elif 'not available' in error_msg.lower():
                    return f"❌ Processing library not available for {file_ext} files. Please install required dependencies."
                else:
                    return f"❌ Error processing {uploaded_file.name}: {error_msg}"
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except:
                pass  # Ignore cleanup errors
                
    except ImportError as e:
        missing_module = str(e).split("'")[1] if "'" in str(e) else "required module"
        return f"❌ File processing not available: Missing {missing_module}. Please install required dependencies (PyPDF2, python-docx)."
    except Exception as e:
        return f"❌ Unexpected error processing {uploaded_file.name}: {str(e)}"


class StreamlitWorkflowRunner:
    """Handles the workflow execution with Streamlit integration"""
    
    def __init__(self):
        self.workflow = None
        self.current_results = None
        self.execution_thread = None
        self.is_running = False
        self.agent_statuses = {}  # Track individual agent statuses
        self.workflow_status = "idle"
        self.current_agent = None
        self.current_step = 0
        self.total_steps = 3
        
    def initialize_workflow(self):
        """Initialize the workflow with LLM clients"""
        try:
            # Import workflow components only when needed
            from workflow import AgentWorkflow
            from integrations import (
                get_azure_openai_client,
                get_agent_azure_openai_client,
                check_azure_config,
                configure_llm_tracing
            )
            from config_package import TEMPERATURE
            
            # Check Azure configuration
            check_azure_config()
            
            # Initialize LLMs
            document_llm = get_agent_azure_openai_client("document_analyzer", temperature=TEMPERATURE)
            code_llm = get_agent_azure_openai_client("code_generator", temperature=TEMPERATURE)
            
            # Configure tracing
            llm = configure_llm_tracing(document_llm)
            
            # Create workflow
            self.workflow = AgentWorkflow(llm, code_llm=code_llm)
            
            # Set up callbacks
            self.workflow.set_status_callback(self._workflow_status_callback)
            self.workflow.set_agent_status_callback(self._agent_status_callback)
            
            return True
            
        except Exception as e:
            if st:
                st.error(f"Failed to initialize workflow: {str(e)}")
            else:
                print(f"Failed to initialize workflow: {str(e)}")
            return False
    
    def run_workflow_async(self, requirements: str):
        """Run workflow in a separate thread"""
        def run():
            try:
                self.is_running = True
                self.current_results = self.workflow.execute_workflow(requirements)
                self.is_running = False
            except Exception as e:
                self.current_results = {
                    "workflow_status": "error",
                    "error": str(e),
                    "agent_outputs": []
                }
                self.is_running = False
        
        self.execution_thread = threading.Thread(target=run)
        self.execution_thread.start()
    
    def _workflow_status_callback(self, workflow_status: str, message: str = "", 
                                current_agent: str = None, current_step: int = None, 
                                total_steps: int = None):
        """Callback for workflow status updates"""
        self.workflow_status = workflow_status
        self.current_agent = current_agent
        if current_step is not None:
            self.current_step = current_step
        if total_steps is not None:
            self.total_steps = total_steps
    
    def _agent_status_callback(self, agent_name: str, status: str, message: str = "", progress: float = None):
        """Callback for individual agent status updates"""
        self.agent_statuses[agent_name] = {
            "status": status,
            "message": message,
            "progress": progress or 0.0,
            "last_updated": datetime.now()
        }
    
    def get_current_status(self):
        """Get current workflow and agent status"""
        return {
            "workflow_status": self.workflow_status,
            "current_agent": self.current_agent,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "agent_statuses": self.agent_statuses.copy(),
            "is_running": self.is_running
        }


def setup_page_config():
    """Configure Streamlit page settings"""
    if not st:
        return
        
    st.set_page_config(
        page_title="Multi-Agent Code Development",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def load_custom_css():
    """Load custom CSS for professional and attractive styling"""
    st.markdown("""
    <style>
    /* Import Google Fonts for better typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .subtitle {
        text-align: center;
        margin-bottom: 3rem;
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
    .workflow-chain {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Agent Cards */
    .agent-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .agent-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: #64748b;
        transition: all 0.3s ease;
    }
    
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .success-card::before {
        background: linear-gradient(135deg, #10b981, #059669);
    }
    
    .error-card::before {
        background: linear-gradient(135deg, #ef4444, #dc2626);
    }
    
    .running-card::before {
        background: linear-gradient(135deg, #f59e0b, #d97706);
    }
    
    .pending-card::before {
        background: linear-gradient(135deg, #6b7280, #4b5563);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem 0;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status-error {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    
    .status-running {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    
    .status-pending {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Progress styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    /* Workflow status */
    .workflow-status {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        text-align: center;
        margin: 1.5rem 0;
        border: 2px solid;
        font-size: 1.1rem;
    }
    
    .status-completed {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        color: #166534;
        border-color: #16a34a;
    }
    
    .status-failed {
        background: linear-gradient(135deg, #fef2f2, #fecaca);
        color: #991b1b;
        border-color: #dc2626;
    }
    
    .status-running {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e;
        border-color: #f59e0b;
    }
    
    /* Input sections */
    .input-section {
        background: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
        border: none;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        border-radius: 8px;
        font-weight: 500;
        padding: 0 1.5rem;
    }
    
    /* File upload area */
    .stFileUploader {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stFileUploader:hover {
        border-color: #667eea;
        background: #f8fafc;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the professional main header"""
    st.markdown("""
    <div class="animate-fade-in">
        <h1 class="main-header">🤖 Multi-Agent Code Development Workflow</h1>
        <div class="subtitle">
            <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">
                Intelligent AI-powered development lifecycle automation
            </p>
            <p style="margin-bottom: 1rem;">
                Powered by <strong>LangChain</strong>, <strong>Azure OpenAI</strong>, and <strong>LangSmith</strong>
            </p>
        </div>
        <div class="workflow-chain">
            <div style="display: flex; justify-content: center; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    📄 Document Analyzer
                </div>
                <div style="font-size: 1.5rem; color: #64748b;">→</div>
                <div style="background: linear-gradient(135deg, #f093fb, #f5576c); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    🔨 Code Generator
                </div>
                <div style="font-size: 1.5rem; color: #64748b;">→</div>
                <div style="background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    🧪 Test Runner
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_input_section():
    """Render the enhanced input section for requirements"""
    st.markdown("""
    <div class="input-section animate-fade-in">
        <h2 style="color: #1e293b; font-weight: 600; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
            📝 Project Requirements Input
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Input method selection with better styling
    st.markdown("**Choose your preferred input method:**")
    input_method = st.radio(
        "",
        ["✍️ Direct Text Input", "📁 File Upload", "📚 Load from Previous Run"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    requirements = ""
    
    if input_method == "✍️ Direct Text Input":
        st.markdown("**📝 Enter your project requirements:**")
        requirements = st.text_area(
            "",
            height=150,
            placeholder="Describe what you want to build in detail...\n\nExample: 'Create a Python web scraper that extracts product data from e-commerce sites with error handling, rate limiting, and CSV export functionality.'",
            label_visibility="collapsed"
        )
    
    elif input_method == "📁 File Upload":
        # Show file processing capabilities
        with st.expander("📁 File Processing Capabilities", expanded=False):
            try:
                from integrations.file_processing.processor import get_file_dependencies, get_supported_extensions
                
                deps = get_file_dependencies()
                supported_exts = get_supported_extensions()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Dependencies Status")
                    st.write("✅ PyPDF2 (PDF support):" if deps.get('PyPDF2', False) else "❌ PyPDF2 (PDF support):", deps.get('PyPDF2', False))
                    st.write("✅ python-docx (DOCX support):" if deps.get('python-docx', False) else "❌ python-docx (DOCX support):", deps.get('python-docx', False))
                
                with col2:
                    st.subheader("Supported Formats")
                    st.write(f"**{len(supported_exts)} formats supported:**")
                    st.write(", ".join(supported_exts))
                    
            except Exception as e:
                st.warning(f"Unable to check file processing capabilities: {str(e)}")
        
        uploaded_file = st.file_uploader(
            "Upload requirements file",
            type=['txt', 'md', 'pdf', 'docx'],
            help="Supported formats: TXT, MD, PDF, DOCX - All formats will be automatically processed to extract text content"
        )
        
        if uploaded_file is not None:
            # Show file info
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.info(f"📄 **{uploaded_file.name}** ({file_size_mb:.2f} MB) - Processing...")
            
            try:
                # Use the FileProcessor for comprehensive file handling
                requirements = process_uploaded_file(uploaded_file)
                
                # Check if the result is an error message
                if requirements and not requirements.startswith("❌") and not requirements.startswith("⚠️"):
                    st.success(f"✅ Successfully extracted {len(requirements)} characters from {uploaded_file.name}")
                    
                    # Show file processing stats
                    words = len(requirements.split())
                    lines = requirements.count('\n') + 1
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Characters", f"{len(requirements):,}")
                    with col2:
                        st.metric("Words", f"{words:,}")
                    with col3:
                        st.metric("Lines", f"{lines:,}")
                    
                    with st.expander("Preview extracted content", expanded=False):
                        st.text_area("File Content Preview", 
                                   requirements[:1000] + "..." if len(requirements) > 1000 else requirements,
                                   height=200, disabled=True)
                elif requirements:
                    # Show error/warning messages from FileProcessor
                    if requirements.startswith("❌"):
                        st.error(requirements)
                    else:
                        st.warning(requirements)
                    requirements = ""  # Clear requirements so workflow doesn't start
                else:
                    st.error("No content could be extracted from the file. Please check the file format and content.")
                    requirements = ""
                        
            except Exception as e:
                st.error(f"Unexpected error processing file: {str(e)}")
                requirements = ""
    
    elif input_method == "📚 Load from Previous Run":
        # List previous workflow outputs
        workflows_dir = "workflow_outputs"
        if os.path.exists(workflows_dir):
            workflow_folders = [f for f in os.listdir(workflows_dir) if os.path.isdir(os.path.join(workflows_dir, f))]
            workflow_folders.sort(reverse=True)  # Most recent first
            
            if workflow_folders:
                selected_folder = st.selectbox("Select previous workflow:", workflow_folders)
                
                if selected_folder:
                    summary_file = os.path.join(workflows_dir, selected_folder, "00_workflow_summary.txt")
                    if os.path.exists(summary_file):
                        try:
                            with open(summary_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Extract initial input from summary
                                for line in content.split('\n'):
                                    if line.startswith('Initial Input:'):
                                        requirements = line.replace('Initial Input:', '').strip()
                                        break
                            
                            if requirements:
                                st.success(f"✅ Loaded requirements from {selected_folder}")
                                with st.expander("Preview loaded requirements"):
                                    st.text(requirements)
                        except Exception as e:
                            st.error(f"Error loading previous run: {str(e)}")
            else:
                st.info("No previous workflow runs found.")
        else:
            st.info("No workflow outputs directory found.")
    
    return requirements


def render_agent_status_card(agent_name: str, status: str, output_summary: str = "", 
                           execution_time: float = 0, step_number: int = 0):
    """Render a professional status card for an agent"""
    
    # Agent icons mapping
    agent_icons = {
        "Document Analyzer": "📄",
        "Code Generator": "🔨", 
        "Test Runner": "🧪"
    }
    
    # Determine card style and status badge based on status
    if status == "success":
        card_class = "agent-card success-card animate-fade-in"
        status_badge = "status-badge status-success"
        status_emoji = "✅"
        status_text = "COMPLETED"
    elif status == "error" or status == "failed":
        card_class = "agent-card error-card animate-fade-in"
        status_badge = "status-badge status-error"
        status_emoji = "❌"
        status_text = "FAILED"
    elif status == "running":
        card_class = "agent-card running-card animate-fade-in"
        status_badge = "status-badge status-running"
        status_emoji = "🔄"
        status_text = "RUNNING"
    else:
        card_class = "agent-card pending-card animate-fade-in"
        status_badge = "status-badge status-pending"
        status_emoji = "⏳"
        status_text = "PENDING"
    
    agent_icon = agent_icons.get(agent_name, "🤖")
    
    # Render enhanced card
    with st.container():
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin: 0; color: #1e293b; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">{agent_icon}</span>
                        Step {step_number}: {agent_name}
                    </h3>
                </div>
                <div class="{status_badge}">
                    {status_emoji} {status_text}
                </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 1rem; color: #64748b; font-size: 0.9rem;">
                <div style="display: flex; align-items: center; gap: 0.25rem;">
                    <span>⏱️</span>
                    <span>{f"{execution_time:.2f}s" if execution_time > 0 else "Not started"}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.25rem;">
                    <span>📊</span>
                    <span>Status: {status.title()}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display output summary with enhanced styling
        if output_summary:
            if "✅" in output_summary:
                st.success(f"**Success:** {output_summary.replace('✅ ', '')}")
            elif "❌" in output_summary:
                st.error(f"**Error:** {output_summary.replace('❌ ', '')}")
            elif "🔄" in output_summary:
                st.info(f"**Processing:** {output_summary.replace('🔄 ', '')}")
            elif "�" in output_summary:
                st.info(f"**Starting:** {output_summary.replace('� ', '')}")
            elif "⏳" in output_summary:
                st.info(f"**Waiting:** {output_summary.replace('⏳ ', '')}")
            else:
                with st.expander("📋 Details", expanded=False):
                    st.text(output_summary)


def render_workflow_progress(results: Dict[str, Any], is_running: bool = False, runner_status: Dict[str, Any] = None):
    """Render enhanced workflow progress and agent status"""
    st.markdown("""
    <div class="animate-fade-in" style="margin: 2rem 0;">
        <h2 style="color: #1e293b; font-weight: 600; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
            🚀 Workflow Execution Progress
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Use callback data if available, otherwise fall back to results
    if runner_status and runner_status.get("agent_statuses"):
        # Use real-time callback data
        agent_statuses = runner_status["agent_statuses"]
        current_step = runner_status.get("current_step", 0)
        total_steps = runner_status.get("total_steps", 3)
        workflow_status = runner_status.get("workflow_status", "idle")
        
        # Calculate progress based on real-time data
        completed_agents = len([s for s in agent_statuses.values() if s.get("status") == "success"])
        if workflow_status == "running" and current_step > 0:
            # Add partial progress for current agent
            current_agent_progress = 0.0
            current_agent_name = runner_status.get("current_agent")
            if current_agent_name and current_agent_name in agent_statuses:
                current_agent_progress = agent_statuses[current_agent_name].get("progress", 0.0) / 100.0
            progress = (completed_agents + current_agent_progress) / total_steps
        else:
            progress = completed_agents / total_steps
        
        progress = min(progress, 1.0)
        st.progress(progress)
        
        # Display real-time status
        if workflow_status == "completed":
            st.markdown('<div class="workflow-status status-completed">✅ Workflow Completed Successfully</div>', 
                       unsafe_allow_html=True)
        elif workflow_status in ["failed", "error"]:
            st.markdown('<div class="workflow-status status-failed">❌ Workflow Failed</div>', 
                       unsafe_allow_html=True)
        elif workflow_status == "running":
            current_agent = runner_status.get("current_agent", "Unknown")
            st.markdown(f'<div class="workflow-status status-running">🔄 Running: {current_agent}</div>', 
                       unsafe_allow_html=True)
        
        # Render real-time agent status cards
        agent_names = ["Document Analyzer", "Code Generator", "Test Runner"]
        for i, agent_name in enumerate(agent_names, 1):
            if agent_name in agent_statuses:
                agent_status = agent_statuses[agent_name]
                status = agent_status.get("status", "pending")
                message = agent_status.get("message", "")
                progress_pct = agent_status.get("progress", 0.0)
                
                # Create a better output summary for real-time display
                output_summary = ""
                if status == "success":
                    output_summary = f"✅ {message}" if message else "✅ Execution completed successfully"
                elif status == "running":
                    if progress_pct > 0:
                        output_summary = f"🔄 {message} ({progress_pct:.1f}%)" if message else f"🔄 In progress ({progress_pct:.1f}%)"
                    else:
                        output_summary = f"🔄 {message}" if message else "🔄 Processing..."
                elif status == "starting":
                    output_summary = f"🚀 {message}" if message else "🚀 Starting up..."
                elif status in ["error", "failed"]:
                    output_summary = f"❌ {message}" if message else "❌ Execution failed"
                else:
                    output_summary = message if message else "⏳ Waiting..."
                
                render_agent_status_card(
                    agent_name, 
                    status, 
                    output_summary, 
                    step_number=i
                )
            else:
                # Agent hasn't started yet
                render_agent_status_card(agent_name, "pending", "⏳ Waiting to start...", step_number=i)
    
    elif results:
        # Fall back to original results-based rendering
        agent_outputs = results.get("agent_outputs", [])
        total_agents = 3  # Document Analyzer, Code Generator, Test Runner
        completed_agents = len([a for a in agent_outputs if a.get("status") == "success"])
        
        progress = (completed_agents + 0.5) / total_agents if is_running else completed_agents / total_agents
        progress = min(progress, 1.0)
        
        st.progress(progress)
        
        # Workflow status
        workflow_status = results.get("workflow_status", "unknown")
        if workflow_status == "completed":
            st.markdown('<div class="workflow-status status-completed">✅ Workflow Completed Successfully</div>', 
                       unsafe_allow_html=True)
        elif workflow_status == "failed" or workflow_status == "error":
            st.markdown('<div class="workflow-status status-failed">❌ Workflow Failed</div>', 
                       unsafe_allow_html=True)
        elif is_running:
            st.markdown('<div class="workflow-status status-running">🔄 Workflow Running...</div>', 
                       unsafe_allow_html=True)
        
        # Agent status cards
        agent_names = ["Document Analyzer", "Code Generator", "Test Runner"]
        
        for i, agent_name in enumerate(agent_names, 1):
            if i <= len(agent_outputs):
                agent_result = agent_outputs[i-1]
                status = agent_result.get("status", "unknown")
                
                # Create output summary
                output_summary = ""
                if status == "success":
                    output = agent_result.get("output", {})
                    if isinstance(output, dict):
                        if "scenarios" in output:
                            scenarios_count = len(output["scenarios"])
                            output_summary = f"✅ Extracted {scenarios_count} unique scenarios"
                        elif "output" in output and isinstance(output["output"], dict):
                            # For Code Generator
                            if output["output"].get("compilation_attempts"):
                                attempts = len(output["output"]["compilation_attempts"])
                                successful = sum(1 for a in output["output"]["compilation_attempts"] 
                                               if a.get("status") == "success")
                                if successful > 0:
                                    output_summary = f"✅ Code generated successfully ({attempts} attempts, {successful} successful)"
                                else:
                                    output_summary = f"❌ Code generation failed ({attempts} attempts)"
                            # For Test Runner
                            elif output["output"].get("execution_summary"):
                                summary = output["output"]["execution_summary"]
                                total_tests = summary.get("total_tests", 0)
                                passed = summary.get("passed_tests", 0)
                                success_rate = summary.get("success_rate", 0)
                                output_summary = f"✅ Tests completed: {passed}/{total_tests} passed ({success_rate:.1f}%)"
                            else:
                                output_summary = "✅ Execution completed successfully"
                        else:
                            output_summary = "✅ Execution completed successfully"
                    else:
                        output_summary = "✅ Execution completed successfully"
                elif status in ["error", "failed"]:
                    error_msg = agent_result.get("error", "Unknown error")
                    output_summary = f"❌ Error: {error_msg[:100]}{'...' if len(error_msg) > 100 else ''}"
                else:
                    output_summary = f"🔄 Status: {status}"
                
                render_agent_status_card(agent_name, status, output_summary, step_number=i)
            elif is_running and i == len(agent_outputs) + 1:
                # Currently running agent
                render_agent_status_card(agent_name, "running", "Processing...", step_number=i)
            else:
                # Pending agent
                render_agent_status_card(agent_name, "pending", "Waiting...", step_number=i)
    
    else:
        # No results yet
        st.info("No workflow execution in progress. Enter requirements and click 'Start Workflow' to begin.")


def render_results_section(results: Dict[str, Any]):
    """Render detailed results and outputs"""
    if not results or not results.get("agent_outputs"):
        return
    
    st.header("📊 Detailed Results")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📈 Analytics", "📁 Outputs", "🔧 Debug"])
    
    with tab1:
        render_summary_tab(results)
    
    with tab2:
        render_analytics_tab(results)
    
    with tab3:
        render_outputs_tab(results)
    
    with tab4:
        render_debug_tab(results)


def render_summary_tab(results: Dict[str, Any]):
    """Render the summary tab"""
    st.subheader("Workflow Summary")
    
    # Enhanced key metrics with professional styling
    col1, col2, col3, col4 = st.columns(4)
    
    workflow_status = results.get("workflow_status", "Unknown").title()
    status_icon = "✅" if workflow_status == "Completed" else "❌" if workflow_status == "Failed" else "🔄"
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Workflow Status</div>
            <div class="metric-value" style="color: {'#10b981' if workflow_status == 'Completed' else '#ef4444' if workflow_status == 'Failed' else '#f59e0b'};">
                {status_icon} {workflow_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        agent_outputs = results.get("agent_outputs", [])
        successful_agents = len([a for a in agent_outputs if a.get("status") == "success"])
        completion_percentage = int((successful_agents / 3) * 100) if successful_agents > 0 else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Agents Completed</div>
            <div class="metric-value" style="color: #10b981;">
                {successful_agents}/3
            </div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">
                {completion_percentage}% Complete
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        output_folder = results.get("output_folder", "")
        if output_folder:
            folder_name = os.path.basename(output_folder)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Output Location</div>
                <div class="metric-value" style="font-size: 1.2rem; color: #6366f1;">
                    📁 {folder_name[:15]}{'...' if len(folder_name) > 15 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Output Location</div>
                <div class="metric-value" style="font-size: 1.2rem; color: #64748b;">
                    📁 Not Created
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        saved_files = results.get("saved_files", [])
        files_count = len(saved_files)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Generated Files</div>
            <div class="metric-value" style="color: #8b5cf6;">
                📄 {files_count}
            </div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">
                {'Files Ready' if files_count > 0 else 'No Files Yet'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Agent details
    st.subheader("Agent Execution Details")
    
    for i, agent_output in enumerate(results.get("agent_outputs", []), 1):
        with st.expander(f"Step {i}: {agent_output.get('agent', 'Unknown Agent')}"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                status = agent_output.get("status", "unknown")
                if status == "success":
                    st.success(f"✅ {status.title()}")
                else:
                    st.error(f"❌ {status.title()}")
            
            with col2:
                output = agent_output.get("output", {})
                if isinstance(output, dict):
                    st.json(output, expanded=False)
                else:
                    st.text(str(output)[:500] + "..." if len(str(output)) > 500 else str(output))
    
    # Add test reports highlight section
    render_test_reports_highlight(results)

def render_test_reports_highlight(results: Dict[str, Any]):
    """Render a highlight section for test reports in the summary tab"""
    output_folder = results.get("output_folder")
    if not output_folder or not os.path.exists(output_folder):
        return
    
    # Check for UI-optimized test report
    ui_report_path = os.path.join(output_folder, "test_report_ui.md")
    test_report_path = os.path.join(output_folder, "test_report.md")
    
    report_to_show = None
    if os.path.exists(ui_report_path):
        report_to_show = ui_report_path
    elif os.path.exists(test_report_path):
        report_to_show = test_report_path
    
    if report_to_show:
        st.subheader("🧪 Test Results Summary")
        
        try:
            with open(report_to_show, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Display the test report content
            st.markdown(content)
            
            # Add an info message about detailed reports
            st.info("� View detailed test reports and download options in the **📁 Outputs** tab above.")
                
        except Exception as e:
            st.error(f"Error loading test report: {str(e)}")


def render_analytics_tab(results: Dict[str, Any]):
    """Render the analytics tab with visualizations"""
    st.subheader("Workflow Analytics")
    
    agent_outputs = results.get("agent_outputs", [])
    if not agent_outputs:
        st.info("No analytics data available yet.")
        return
    
    # Execution timeline
    st.subheader("📈 Execution Timeline")
    
    # Create timeline data
    timeline_data = []
    for i, agent_output in enumerate(agent_outputs):
        timeline_data.append({
            'Agent': agent_output.get('agent', f'Agent {i+1}'),
            'Status': agent_output.get('status', 'unknown'),
            'Step': i + 1
        })
    
    if timeline_data:
        df = pd.DataFrame(timeline_data)
        
        # Create a timeline chart
        fig = px.bar(df, x='Step', y=['Status'], color='Status',
                    title="Agent Execution Status",
                    color_discrete_map={
                        'success': '#28a745',
                        'error': '#dc3545',
                        'failed': '#dc3545'
                    })
        st.plotly_chart(fig, use_container_width=True)
    
    # Success rate pie chart
    st.subheader("📊 Success Rate")
    
    col1, col2 = st.columns(2)
    
    with col1:
        success_count = len([a for a in agent_outputs if a.get("status") == "success"])
        total_count = len(agent_outputs)
        
        fig = go.Figure(data=[go.Pie(
            labels=['Successful', 'Failed'], 
            values=[success_count, total_count - success_count],
            hole=.3,
            marker_colors=['#28a745', '#dc3545']
        )])
        fig.update_layout(title_text="Agent Success Rate")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Agent performance metrics
        if agent_outputs:
            agent_names = [a.get('agent', 'Unknown') for a in agent_outputs]
            agent_status = [1 if a.get('status') == 'success' else 0 for a in agent_outputs]
            
            fig = px.bar(x=agent_names, y=agent_status, 
                        title="Agent Performance",
                        labels={'x': 'Agent', 'y': 'Success (1) / Failure (0)'},
                        color=agent_status,
                        color_continuous_scale=['red', 'green'])
            st.plotly_chart(fig, use_container_width=True)


def render_test_reports_section(output_folder: str):
    """Render test reports section with Markdown display"""
    st.subheader("🧪 Test Reports")
    
    # Look for test report files
    test_report_files = []
    report_patterns = ['test_report.md', 'test_report_ui.md', 'test_results.json']
    
    for pattern in report_patterns:
        filepath = os.path.join(output_folder, pattern)
        if os.path.exists(filepath):
            test_report_files.append({
                'name': pattern,
                'path': filepath,
                'type': 'markdown' if pattern.endswith('.md') else 'json'
            })
    
    if not test_report_files:
        st.info("No test reports generated yet. Test reports will appear here after running the workflow.")
        return
    
    # Create tabs for different report types
    report_tabs = st.tabs([f"📄 {file['name']}" for file in test_report_files])
    
    for tab, report_file in zip(report_tabs, test_report_files):
        with tab:
            try:
                with open(report_file['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if report_file['type'] == 'markdown':
                    # Display Markdown content
                    st.markdown(content)
                    
                    # Add download button
                    st.download_button(
                        label=f"📥 Download {report_file['name']}",
                        data=content,
                        file_name=report_file['name'],
                        mime='text/markdown'
                    )
                else:
                    # Display JSON content
                    try:
                        json_content = json.loads(content)
                        st.json(json_content)
                        
                        # Add download button
                        st.download_button(
                            label=f"📥 Download {report_file['name']}",
                            data=content,
                            file_name=report_file['name'],
                            mime='application/json'
                        )
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format in test results file")
                        st.text(content)
                
            except Exception as e:
                st.error(f"Error reading {report_file['name']}: {str(e)}")
    
    st.divider()

def render_outputs_tab(results: Dict[str, Any]):
    """Render the outputs tab showing generated files and test reports"""
    st.subheader("Generated Files and Outputs")
    
    output_folder = results.get("output_folder")
    if not output_folder or not os.path.exists(output_folder):
        st.warning("Output folder not found or doesn't exist yet.")
        return
    
    # Check for test reports first
    render_test_reports_section(output_folder)
    
    # List all files in output folder
    try:
        files = []
        for root, dirs, filenames in os.walk(output_folder):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, output_folder)
                file_size = os.path.getsize(filepath)
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                files.append({
                    'File': rel_path,
                    'Size (bytes)': file_size,
                    'Modified': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'Full Path': filepath
                })
        
        if files:
            df = pd.DataFrame(files)
            
            # File browser
            selected_file = st.selectbox("Select file to view:", df['File'].tolist())
            
            if selected_file:
                selected_row = df[df['File'] == selected_file].iloc[0]
                filepath = selected_row['Full Path']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{selected_row['Size (bytes)']} bytes")
                with col2:
                    st.metric("Last Modified", selected_row['Modified'])
                with col3:
                    file_ext = os.path.splitext(selected_file)[1]
                    st.metric("File Type", file_ext or "No extension")
                
                # File content viewer
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Determine content type and display appropriately
                    if selected_file.endswith('.json'):
                        try:
                            json_content = json.loads(content)
                            st.json(json_content)
                        except:
                            st.code(content, language='json')
                    elif selected_file.endswith('.md'):
                        st.markdown(content)
                    elif selected_file.endswith(('.py', '.js', '.ts', '.cs', '.java')):
                        lang = selected_file.split('.')[-1]
                        st.code(content, language=lang)
                    else:
                        st.text(content)
                        
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
            
            # Files table
            st.subheader("All Generated Files")
            st.dataframe(df[['File', 'Size (bytes)', 'Modified']], use_container_width=True)
            
        else:
            st.info("No files generated yet.")
            
    except Exception as e:
        st.error(f"Error listing output files: {str(e)}")


def render_debug_tab(results: Dict[str, Any]):
    """Render debug information"""
    st.subheader("Debug Information")
    
    # Raw results JSON
    with st.expander("Raw Results JSON"):
        st.json(results)
    
    # Environment info
    with st.expander("Environment Information"):
        st.write("**Python Version:**", os.sys.version)
        st.write("**Working Directory:**", os.getcwd())
        st.write("**Output Directory:**", results.get("output_folder", "Not set"))
    
    # Configuration status
    with st.expander("Configuration Status"):
        try:
            from config_package import (
                AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, 
                AZURE_OPENAI_DEPLOYMENT_NAME, LANGCHAIN_API_KEY
            )
            st.write("**Azure OpenAI Endpoint:**", "✅ Configured" if AZURE_OPENAI_ENDPOINT else "❌ Missing")
            st.write("**Azure OpenAI API Key:**", "✅ Configured" if AZURE_OPENAI_API_KEY else "❌ Missing")
            st.write("**Deployment Name:**", "✅ Configured" if AZURE_OPENAI_DEPLOYMENT_NAME else "❌ Missing")
            st.write("**LangChain API Key:**", "✅ Configured" if LANGCHAIN_API_KEY else "❌ Missing")
        except Exception as e:
            st.error(f"Error checking configuration: {str(e)}")


def main():
    """Main Streamlit application"""
    # Page setup
    setup_page_config()
    load_custom_css()
    render_header()
    
    # Initialize session state
    if 'workflow_runner' not in st.session_state:
        st.session_state.workflow_runner = StreamlitWorkflowRunner()
    
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None
    
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False
    
    # Enhanced Professional Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 1.5rem;">
            <h2 style="color: #1e293b; font-weight: 600; margin: 0;">⚡ Control Panel</h2>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0.5rem 0 0 0;">Workflow Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuration status with enhanced styling
        st.markdown("**🔧 System Configuration**")
        try:
            from integrations import check_azure_config
            check_azure_config()
            st.success("✅ Azure OpenAI Connected")
            st.markdown("""
            <div style="background: #dcfce7; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #10b981; margin: 0.5rem 0;">
                <small style="color: #166534;">🌐 LangChain & LangSmith Ready</small>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Configuration Error")
            with st.expander("Error Details"):
                st.code(str(e))
            st.stop()
        
        st.markdown("---")
        
        # Control buttons with better organization
        st.markdown("**⚙️ Live Controls**")
        
        col1, col2 = st.columns(2)
        with col1:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=st.session_state.auto_refresh, help="Updates every 2 seconds")
            st.session_state.auto_refresh = auto_refresh
        
        with col2:
            if st.button("🔄 Refresh", help="Manual refresh"):
                st.rerun()
        
        if st.button("🗑️ Clear All Results", type="secondary", use_container_width=True):
            st.session_state.workflow_results = None
            st.session_state.workflow_runner.current_results = None
            st.rerun()
        
        st.markdown("---")
        
        # Workflow history with enhanced styling
        st.markdown("**📜 Workflow History**")
        workflows_dir = "workflow_outputs"
        if os.path.exists(workflows_dir):
            workflow_folders = [f for f in os.listdir(workflows_dir) if os.path.isdir(os.path.join(workflows_dir, f))]
            workflow_folders.sort(reverse=True)
            
            if workflow_folders:
                st.markdown(f"*{len(workflow_folders)} previous workflows found*")
                
                for i, folder in enumerate(workflow_folders[:3]):  # Show last 3
                    # Parse folder name for better display
                    try:
                        parts = folder.split('_')
                        if len(parts) >= 3:
                            project_name = parts[0].title()
                            date_part = f"{parts[1]}_{parts[2]}"
                        else:
                            project_name = folder[:15]
                            date_part = "Recent"
                    except:
                        project_name = folder[:15]
                        date_part = "Recent"
                    
                    if st.button(
                        f"📁 {project_name}",
                        key=f"hist_{folder}",
                        help=f"Created: {date_part}",
                        use_container_width=True
                    ):
                        st.info("📋 Workflow loading will be available in the next update")
                
                if len(workflow_folders) > 3:
                    st.markdown(f"*...and {len(workflow_folders) - 3} more*")
            else:
                st.info("No workflows yet")
        else:
            st.info("📂 No workflow directory found")
        
        # System info
        st.markdown("---")
        with st.expander("ℹ️ System Info"):
            st.markdown("""
            **Framework:** Streamlit + LangChain  
            **AI Model:** Azure OpenAI GPT-4  
            **Languages:** 7 supported  
            **Version:** 2.0.0  
            """)
            
            # Current session info
            if st.session_state.workflow_runner.is_running:
                st.markdown("**Status:** 🔄 Workflow Active")
            else:
                st.markdown("**Status:** ⏸️ Ready")
    
    # Main content
    requirements = render_input_section()
    
    # Enhanced workflow controls with professional styling
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h3 style="color: #1e293b; font-weight: 600; margin-bottom: 1rem;">🎮 Workflow Controls</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Control buttons with enhanced layout
    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
    
    with col1:
        # Main start button with enhanced styling
        is_ready = bool(requirements and not st.session_state.workflow_runner.is_running)
        button_text = "🚀 Start AI Workflow" if is_ready else ("⏳ Workflow Running..." if st.session_state.workflow_runner.is_running else "📝 Enter Requirements First")
        
        start_workflow = st.button(
            button_text,
            disabled=not is_ready,
            type="primary",
            use_container_width=True,
            help="Begin the 3-agent development workflow"
        )
    
    with col2:
        if st.session_state.workflow_runner.is_running and st.button("⏹️ Stop", help="Stop current workflow", use_container_width=True):
            st.warning("⚠️ Stop functionality will be available in the next update")
    
    with col3:
        if st.session_state.workflow_results and st.button("💾 Export", help="Export workflow results", use_container_width=True):
            st.success("✅ Results are automatically saved to the output folder")
    
    with col4:
        if st.button("❓ Help", help="View help and documentation", use_container_width=True):
            with st.expander("📚 Quick Help", expanded=True):
                st.markdown("""
                **Getting Started:**
                1. 📝 Enter your project requirements
                2. � Click 'Start AI Workflow'
                3. 👀 Monitor progress in real-time
                4. 📊 Review results and generated files
                
                **Tips:**
                - Be specific in your requirements
                - Include technology preferences
                - Mention any special constraints
                """)
    
    # Status indicator bar
    if st.session_state.workflow_runner.is_running:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #fef3c7, #fde68a); padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b; margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🔄</span>
                <strong>Workflow is actively running...</strong>
                <span style="margin-left: auto; font-size: 0.9rem; color: #92400e;">Monitor progress below</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif requirements:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #dcfce7, #bbf7d0); padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981; margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">✅</span>
                <strong>Ready to start workflow</strong>
                <span style="margin-left: auto; font-size: 0.9rem; color: #166534;">Click 'Start AI Workflow' to begin</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Start workflow
    if start_workflow and requirements:
        # Initialize workflow
        if st.session_state.workflow_runner.initialize_workflow():
            st.session_state.workflow_runner.run_workflow_async(requirements)
            st.success("🚀 Workflow started! Monitor progress below.")
            time.sleep(1)  # Give it a moment to start
            st.rerun()
    
    # Update results from workflow runner
    if st.session_state.workflow_runner.current_results:
        st.session_state.workflow_results = st.session_state.workflow_runner.current_results
    
    # Get current status from workflow runner
    current_status = st.session_state.workflow_runner.get_current_status()
    
    # Render progress and results with real-time data
    render_workflow_progress(
        st.session_state.workflow_results, 
        st.session_state.workflow_runner.is_running,
        current_status
    )
    
    if st.session_state.workflow_results:
        render_results_section(st.session_state.workflow_results)
    
    # Auto-refresh logic
    if st.session_state.auto_refresh and st.session_state.workflow_runner.is_running:
        time.sleep(2)
        st.rerun()


if __name__ == "__main__":
    # Only run if Streamlit is available and we're in the right context
    if STREAMLIT_AVAILABLE and st is not None:
        try:
            # Check if we have a valid Streamlit context
            main()
        except Exception as e:
            print(f"Error running Streamlit app: {str(e)}")
            print("Please run this script with: streamlit run streamlit_app.py")
    else:
        print("Streamlit not available or not running in proper context.")
        print("Please run this script with: streamlit run streamlit_app.py")
