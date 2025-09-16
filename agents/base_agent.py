from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, Optional
import os
from datetime import datetime


class AgentStatus:
    """Agent status constants and helper methods"""
    PENDING = "pending"
    STARTING = "starting"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    FAILED = "failed"
    
    @staticmethod
    def get_emoji(status: str) -> str:
        """Get emoji for status"""
        emoji_map = {
            AgentStatus.PENDING: "⏳",
            AgentStatus.STARTING: "🔄",
            AgentStatus.RUNNING: "🔄",
            AgentStatus.SUCCESS: "✅",
            AgentStatus.ERROR: "❌",
            AgentStatus.FAILED: "❌"
        }
        return emoji_map.get(status, "❓")


class BaseAgent(ABC):
    """Base class for all agents with callback support for UI updates"""
    
    def __init__(self, name: str, llm: Any):
        self.name = name
        self.llm = llm
        self.prompt_log_folder = None  # Will be set by workflow
        self.status_callback: Optional[Callable] = None  # Callback for status updates
        self.progress_callback: Optional[Callable] = None  # Callback for progress updates
        self.current_status = AgentStatus.PENDING
        self.current_progress = 0.0
        self.status_message = ""
    
    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the agent's main functionality"""
        pass
    
    def set_status_callback(self, callback: Optional[Callable] = None):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def set_progress_callback(self, callback: Optional[Callable] = None):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def update_status(self, status: str, message: str = "", progress: float = None):
        """Update agent status and notify callbacks"""
        self.current_status = status
        self.status_message = message
        
        if progress is not None:
            self.current_progress = progress
        
        # Log the status update
        emoji = AgentStatus.get_emoji(status)
        log_message = f"{emoji} {status.upper()}"
        if message:
            log_message += f": {message}"
        if progress is not None:
            log_message += f" ({progress:.1f}%)"
        
        self.log(log_message)
        
        # Notify callbacks
        if self.status_callback:
            try:
                self.status_callback(
                    agent_name=self.name,
                    status=status,
                    message=message,
                    progress=progress
                )
            except Exception as e:
                self.log(f"❌ Error in status callback: {str(e)}")
        
        if progress is not None and self.progress_callback:
            try:
                self.progress_callback(
                    agent_name=self.name,
                    progress=progress,
                    message=message
                )
            except Exception as e:
                self.log(f"❌ Error in progress callback: {str(e)}")
    
    def update_progress(self, progress: float, message: str = ""):
        """Update progress without changing status"""
        self.current_progress = progress
        if message:
            self.status_message = message
        
        # Log progress update
        self.log(f"📊 Progress: {progress:.1f}% - {message}")
        
        # Notify progress callback (this will emit separate progress events)
        if self.progress_callback:
            try:
                self.progress_callback(
                    agent_name=self.name,
                    progress=progress,
                    message=message
                )
            except Exception as e:
                self.log(f"❌ Error in progress callback: {str(e)}")
        
        # Also notify status callback for backward compatibility
        if self.status_callback:
            try:
                self.status_callback(
                    agent_name=self.name,
                    status=self.current_status,
                    message=message,
                    progress=progress
                )
            except Exception as e:
                self.log(f"❌ Error in status callback: {str(e)}")
    
    def log(self, message: str):
        """Log agent activity"""
        print(f"[{self.name}] {message}")
    
    def execute_with_status(self, input_data: str) -> Dict[str, Any]:
        """Execute with automatic status updates"""
        try:
            # Update status to starting
            self.update_status(AgentStatus.STARTING, "Initializing agent execution", 0.0)
            
            # Update to running
            self.update_status(AgentStatus.RUNNING, "Processing input data", 10.0)
            
            # Execute the actual agent logic
            result = self.execute(input_data)
            
            # Check if execution was successful
            if isinstance(result, dict) and result.get("status") == "error":
                self.update_status(
                    AgentStatus.ERROR, 
                    result.get("error", "Unknown error occurred"), 
                    100.0
                )
            else:
                self.update_status(AgentStatus.SUCCESS, "Execution completed successfully", 100.0)
            
            return result
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.update_status(AgentStatus.ERROR, error_msg, 100.0)
            return {
                "agent": self.name,
                "status": "error",
                "error": str(e),
                "output": None
            }
    
    def set_prompt_log_folder(self, folder_path: str):
        """Set the folder path for logging prompts"""
        self.prompt_log_folder = folder_path
        # Create prompts subfolder
        prompts_folder = os.path.join(folder_path, "prompts")
        os.makedirs(prompts_folder, exist_ok=True)
    
    def log_prompt_to_file(self, prompt_content: str, prompt_type: str, scenario_info: str = None):
        """Log the actual prompt sent to LLM with all placeholders filled"""
        if not self.prompt_log_folder:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            
            # Create a clean filename
            clean_agent_name = self.name.lower().replace(" ", "_")
            scenario_suffix = f"_{scenario_info}" if scenario_info else ""
            filename = f"{timestamp}_{clean_agent_name}_{prompt_type}{scenario_suffix}.txt"
            
            prompts_folder = os.path.join(self.prompt_log_folder, "prompts")
            filepath = os.path.join(prompts_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"AGENT: {self.name}\n")
                f.write(f"PROMPT TYPE: {prompt_type}\n")
                f.write(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                if scenario_info:
                    f.write(f"SCENARIO: {scenario_info}\n")
                f.write("=" * 80 + "\n")
                f.write("ACTUAL PROMPT SENT TO LLM:\n")
                f.write("=" * 80 + "\n\n")
                f.write(prompt_content)
                f.write("\n\n" + "=" * 80 + "\n")
                f.write("END OF PROMPT\n")
            
            self.log(f"📝 Logged prompt to: prompts/{filename}")
            
        except Exception as e:
            self.log(f"❌ Error logging prompt: {str(e)}")
