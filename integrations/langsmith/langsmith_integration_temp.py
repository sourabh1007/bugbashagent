"""
Temporary LangSmith Integration (disabled for testing)
"""

LANGSMITH_AVAILABLE = False

class LangSmithIntegration:
    """Dummy LangSmith integration for testing"""
    def __init__(self):
        self.client = None
        self.project_name = "BugBashAgent"
        self.enabled = False
        print("📊 LangSmith: Disabled for testing")
    
    def get_dashboard_url(self):
        return "https://smith.langchain.com"

def trace_agent_execution(agent_name: str = None):
    """Dummy trace decorator"""
    def decorator(func):
        return func
    return decorator

def trace_workflow_execution(func):
    """Dummy trace decorator"""
    return func

def configure_llm_tracing(llm):
    """Dummy configure function"""
    return llm

def get_langsmith_dashboard_url():
    """Get dashboard URL"""
    return "https://smith.langchain.com"
