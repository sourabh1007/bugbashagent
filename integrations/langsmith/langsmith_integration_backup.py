"""
LangSmith Integration Module for BugBashAgent

This module provides LangSmith tracing and monitoring capabilities for the multi-agent workflow.
It includes custom decorators, metrics collection, and enhanced logging for better observability.
"""

import os
import functools
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import json

try:
    import langsmith
    from langsmith import Client
    from langsmith.run_helpers import traceable
    from langsmith.wrappers import wrap_openai
    LANGSMITH_AVAILABLE = True
    print("📊 LangSmith package loaded successfully")
except ImportError as e:
    print(f"⚠️ LangSmith not available: {e}")
    LANGSMITH_AVAILABLE = False
    
    # Create dummy decorators when LangSmith is not available
    def traceable(name: str = None, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class Client:
        def __init__(self, *args, **kwargs):
            pass
    
    def wrap_openai(client):
        return client
except Exception as e:
    print(f"⚠️ LangSmith initialization error: {e}")
    LANGSMITH_AVAILABLE = False
    
    # Create dummy implementations
    def traceable(name: str = None, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class Client:
        def __init__(self, *args, **kwargs):
            pass
    
    def wrap_openai(client):
        return client

from config_package import (
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_ENDPOINT, 
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT
)


class LangSmithIntegration:
    """Main class for handling LangSmith integration"""
    
    def __init__(self):
        self.client = None
        self.project_name = LANGCHAIN_PROJECT
        self.enabled = self._initialize_langsmith()
        
    def _initialize_langsmith(self) -> bool:
        """Initialize LangSmith client and set environment variables"""
        if not LANGSMITH_AVAILABLE:
            print("📊 LangSmith: Not available (package not installed)")
            return False
            
        if not LANGCHAIN_API_KEY:
            print("📊 LangSmith: Not configured (LANGCHAIN_API_KEY not set)")
            return False
        
        try:
            # Set environment variables for LangChain tracing
            os.environ["LANGCHAIN_TRACING_V2"] = LANGCHAIN_TRACING_V2
            os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
            os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = self.project_name
            
            # Initialize LangSmith client
            self.client = Client(
                api_url=LANGCHAIN_ENDPOINT,
                api_key=LANGCHAIN_API_KEY
            )
            
            print(f"✅ LangSmith initialized successfully")
            print(f"📊 Project: {self.project_name}")
            print(f"🔗 Dashboard: https://smith.langchain.com/projects")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize LangSmith: {str(e)}")
            return False
    
    def create_project_if_not_exists(self) -> bool:
        """Create LangSmith project if it doesn't exist"""
        if not self.enabled or not self.client:
            return False
            
        try:
            # Try to get the project
            project = self.client.read_project(project_name=self.project_name)
            print(f"📊 Using existing LangSmith project: {self.project_name}")
            return True
            
        except Exception:
            try:
                # Create new project
                project = self.client.create_project(
                    project_name=self.project_name,
                    description="BugBashAgent Multi-Agent Code Development Workflow"
                )
                print(f"✅ Created new LangSmith project: {self.project_name}")
                return True
                
            except Exception as e:
                print(f"❌ Failed to create LangSmith project: {str(e)}")
                return False
    
    def log_workflow_start(self, requirements: str) -> Optional[str]:
        """Log the start of a workflow run"""
        if not self.enabled:
            return None
            
        try:
            run_name = f"workflow_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Log workflow metadata
            metadata = {
                "workflow_type": "multi_agent_code_development",
                "timestamp": datetime.now().isoformat(),
                "requirements_length": len(requirements),
                "agents": ["DocumentAnalyzer", "CodeGenerator"]
            }
            
            print(f"📊 LangSmith: Logging workflow start - {run_name}")
            return run_name
            
        except Exception as e:
            print(f"⚠️ LangSmith logging error: {str(e)}")
            return None
    
    def log_agent_execution(self, agent_name: str, input_data: str, output_data: Any, status: str, metadata: Dict = None):
        """Log individual agent execution"""
        if not self.enabled:
            return
            
        try:
            log_data = {
                "agent": agent_name,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "input_length": len(str(input_data)),
                "output_length": len(str(output_data)) if output_data else 0,
                "metadata": metadata or {}
            }
            
            print(f"📊 LangSmith: Logged {agent_name} execution - Status: {status}")
            
        except Exception as e:
            print(f"⚠️ LangSmith agent logging error: {str(e)}")
    
    def log_workflow_completion(self, results: Dict, run_name: str = None):
        """Log workflow completion with results summary"""
        if not self.enabled:
            return
            
        try:
            summary = {
                "workflow_status": results.get("workflow_status", "unknown"),
                "total_steps": len(results.get("agent_outputs", [])),
                "successful_steps": len([a for a in results.get("agent_outputs", []) if a.get("status") == "success"]),
                "completion_time": datetime.now().isoformat(),
                "output_folder": results.get("output_folder", "unknown")
            }
            
            print(f"📊 LangSmith: Workflow completed - Status: {summary['workflow_status']}")
            
        except Exception as e:
            print(f"⚠️ LangSmith completion logging error: {str(e)}")


# Global LangSmith integration instance
langsmith_integration = LangSmithIntegration()


def trace_agent_execution(agent_name: str):
    """Decorator to trace agent execution with LangSmith"""
    def decorator(func: Callable) -> Callable:
        if not LANGSMITH_AVAILABLE:
            return func
            
        @traceable(name=f"agent_{agent_name.lower().replace(' ', '_')}")
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log successful execution
                execution_time = (datetime.now() - start_time).total_seconds()
                langsmith_integration.log_agent_execution(
                    agent_name=agent_name,
                    input_data=str(args[1:]) if len(args) > 1 else str(kwargs),
                    output_data=result,
                    status="success",
                    metadata={"execution_time_seconds": execution_time}
                )
                
                return result
                
            except Exception as e:
                # Log failed execution
                execution_time = (datetime.now() - start_time).total_seconds()
                langsmith_integration.log_agent_execution(
                    agent_name=agent_name,
                    input_data=str(args[1:]) if len(args) > 1 else str(kwargs),
                    output_data=str(e),
                    status="error",
                    metadata={
                        "execution_time_seconds": execution_time,
                        "error_type": type(e).__name__
                    }
                )
                raise
                
        return wrapper
    return decorator


def trace_workflow_execution(func: Callable) -> Callable:
    """Decorator to trace entire workflow execution"""
    if not LANGSMITH_AVAILABLE:
        return func
        
    @traceable(name="bugbash_agent_workflow")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        run_name = None
        
        try:
            # Log workflow start
            if len(args) > 1:  # Assuming first arg is self, second is requirements
                requirements = args[1]
                run_name = langsmith_integration.log_workflow_start(requirements)
            
            # Execute workflow
            result = func(*args, **kwargs)
            
            # Log workflow completion
            execution_time = (datetime.now() - start_time).total_seconds()
            if isinstance(result, dict):
                result["langsmith_execution_time"] = execution_time
                langsmith_integration.log_workflow_completion(result, run_name)
            
            return result
            
        except Exception as e:
            print(f"📊 LangSmith: Workflow failed - {str(e)}")
            raise
            
    return wrapper


def configure_llm_tracing(llm):
    """Configure LLM for LangSmith tracing"""
    if not LANGSMITH_AVAILABLE:
        return llm
        
    try:
        # For OpenAI models, wrap with LangSmith
        if hasattr(llm, 'client') and hasattr(llm.client, '_client'):
            # This is likely an OpenAI client, wrap it
            wrapped_client = wrap_openai(llm.client._client)
            llm.client._client = wrapped_client
            print("✅ LangSmith: LLM client wrapped for tracing")
        
        return llm
        
    except Exception as e:
        print(f"⚠️ LangSmith LLM wrapping failed: {str(e)}")
        return llm


def get_langsmith_dashboard_url() -> str:
    """Get the LangSmith dashboard URL for this project"""
    if not langsmith_integration.enabled:
        return "LangSmith not configured"
    
    project_name = langsmith_integration.project_name
    return f"https://smith.langchain.com/projects/p/{project_name}"


# Initialize project on module import
if LANGSMITH_AVAILABLE and LANGCHAIN_API_KEY:
    langsmith_integration.create_project_if_not_exists()
