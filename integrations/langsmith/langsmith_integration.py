"""
LangSmith Integration Module for Bug Bash Copilot

This module provides LangSmith tracing and monitoring capabilities for the multi-agent workflow.
It includes custom decorators, metrics collection, and enhanced logging for better observability.
"""

import os
import functools
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import json

# Try importing LangSmith with robust error handling
LANGSMITH_AVAILABLE = False
Client = None
traceable = None
wrap_openai = None

try:
    print("📊 Attempting to load LangSmith...")
    import langsmith
    from langsmith import Client
    from langsmith.run_helpers import traceable
    from langsmith.wrappers import wrap_openai
    LANGSMITH_AVAILABLE = True
    print("📊 LangSmith package loaded successfully")
        
except ImportError as e:
    print(f"⚠️ LangSmith not installed: {e}")
    LANGSMITH_AVAILABLE = False
    
except Exception as e:
    print(f"⚠️ LangSmith initialization error: {e}")
    LANGSMITH_AVAILABLE = False

# Create dummy implementations if LangSmith is not available
if not LANGSMITH_AVAILABLE:
    print("📊 Using dummy LangSmith implementations")
    
    def traceable(name: str = None, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class Client:
        def __init__(self, *args, **kwargs):
            pass
        
        def create_run(self, *args, **kwargs):
            return None
        
        def update_run(self, *args, **kwargs):
            return None
        
        def list_projects(self):
            return []
        
        def create_project(self, *args, **kwargs):
            return None
    
    def wrap_openai(client):
        return client

# Import configuration with error handling
try:
    from config_package import (
        LANGCHAIN_TRACING_V2,
        LANGCHAIN_ENDPOINT, 
        LANGCHAIN_API_KEY,
        LANGCHAIN_PROJECT
    )
except ImportError as e:
    print(f"⚠️ Config import error: {e}")
    LANGCHAIN_TRACING_V2 = "false"
    LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY = None
    LANGCHAIN_PROJECT = "BugBashCopilot"


class LangSmithIntegration:
    """Main class for handling LangSmith integration"""
    
    def __init__(self):
        self.client = None
        self.project_name = LANGCHAIN_PROJECT or "BugBashCopilot"
        self.enabled = self._initialize_langsmith()
        
    def _initialize_langsmith(self) -> bool:
        """Initialize LangSmith client and set environment variables"""
        if not LANGSMITH_AVAILABLE:
            print("📊 LangSmith: Not available (package not installed or import failed)")
            return False
            
        if not LANGCHAIN_API_KEY:
            print("📊 LangSmith: Not configured (missing LANGCHAIN_API_KEY)")
            return False
        
        try:
            # Set environment variables for LangSmith
            os.environ["LANGCHAIN_TRACING_V2"] = str(LANGCHAIN_TRACING_V2).lower()
            os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT or "https://api.smith.langchain.com"
            os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = self.project_name
            
            # Initialize client
            self.client = Client()
            
            # Check if project exists, create if not
            try:
                # Try to get project info
                projects = self.client.list_projects()
                project_exists = any(p.name == self.project_name for p in projects)
                
                if not project_exists:
                    print(f"📊 Creating new LangSmith project: {self.project_name}")
                    self.client.create_project(project_name=self.project_name)
                else:
                    print(f"📊 Using existing LangSmith project: {self.project_name}")
                    
            except Exception as e:
                print(f"⚠️ Could not verify/create LangSmith project: {e}")
                # Continue anyway, project might exist or be created automatically
            
            print("✅ LangSmith integration initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize LangSmith: {e}")
            return False
    
    def get_dashboard_url(self) -> str:
        """Get the dashboard URL for the current project"""
        base_url = "https://smith.langchain.com"
        if self.enabled and self.project_name:
            return f"{base_url}/projects/p/{self.project_name}"
        return base_url
    
    def log_agent_execution(self, agent_name: str, input_data: Any, output_data: Any, 
                          execution_time: float, metadata: Dict[str, Any] = None):
        """Log agent execution details"""
        if not self.enabled:
            return
            
        try:
            log_data = {
                "agent_name": agent_name,
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "input_size": len(str(input_data)) if input_data else 0,
                "output_size": len(str(output_data)) if output_data else 0,
                "metadata": metadata or {}
            }
            
            # You can add custom logging logic here
            print(f"📊 Agent '{agent_name}' executed in {execution_time:.2f}s")
            
        except Exception as e:
            print(f"⚠️ Failed to log agent execution: {e}")


def trace_agent_execution(agent_name: str = None):
    """Decorator for tracing agent execution with LangSmith"""
    def decorator(func: Callable) -> Callable:
        if not LANGSMITH_AVAILABLE:
            return func
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            # Use the agent name or function name
            name = agent_name or func.__name__
            
            try:
                # Use LangSmith traceable if available
                if LANGSMITH_AVAILABLE and traceable:
                    traced_func = traceable(name=f"agent_{name}")(func)
                    result = traced_func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Log execution details
                try:
                    integration = LangSmithIntegration()
                    integration.log_agent_execution(
                        agent_name=name,
                        input_data={"args_count": len(args), "kwargs_keys": list(kwargs.keys())},
                        output_data={"result_type": type(result).__name__},
                        execution_time=execution_time
                    )
                except Exception as e:
                    print(f"⚠️ Failed to log execution: {e}")
                
                return result
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                print(f"❌ Agent '{name}' failed after {execution_time:.2f}s: {e}")
                raise
                
        return wrapper
    
    return decorator


def trace_workflow_execution(func: Callable) -> Callable:
    """Decorator for tracing entire workflow execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not LANGSMITH_AVAILABLE:
            return func(*args, **kwargs)
            
        try:
            if traceable:
                traced_func = traceable(name=f"workflow_{func.__name__}")(func)
                return traced_func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            print(f"⚠️ Workflow tracing error: {e}")
            return func(*args, **kwargs)
    
    return wrapper


def configure_llm_tracing(llm):
    """Configure LLM for LangSmith tracing"""
    if not LANGSMITH_AVAILABLE or not wrap_openai:
        print("📊 LLM tracing: Using standard LLM (LangSmith not available)")
        return llm
    
    try:
        # For OpenAI models, wrap with LangSmith
        if hasattr(llm, 'client') and hasattr(llm.client, '_client'):
            # This is likely an OpenAI client, wrap it
            wrapped_client = wrap_openai(llm.client._client)
            llm.client._client = wrapped_client
            print("📊 LLM tracing: OpenAI client wrapped with LangSmith")
        else:
            print("📊 LLM tracing: LLM type not recognized for wrapping")
        
        return llm
        
    except Exception as e:
        print(f"⚠️ Failed to configure LLM tracing: {e}")
        return llm


def get_langsmith_dashboard_url() -> str:
    """Get LangSmith dashboard URL"""
    try:
        integration = LangSmithIntegration()
        return integration.get_dashboard_url()
    except Exception:
        return "https://smith.langchain.com"
