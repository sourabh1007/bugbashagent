from abc import ABC, abstractmethod
from typing import Any, Dict
import os
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, llm: Any):
        self.name = name
        self.llm = llm
        self.prompt_log_folder = None  # Will be set by workflow
    
    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the agent's main functionality"""
        pass
    
    def log(self, message: str):
        """Log agent activity"""
        print(f"[{self.name}] {message}")
    
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
