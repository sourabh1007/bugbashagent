from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, llm: Any):
        self.name = name
        self.llm = llm
    
    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the agent's main functionality"""
        pass
    
    def log(self, message: str):
        """Log agent activity"""
        print(f"[{self.name}] {message}")
