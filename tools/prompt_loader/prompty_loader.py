"""
Prompt Loader Utility

This module provides utilities to load and process .prompty files with dynamic variable replacement.
"""

import os
import yaml
import re
from typing import Dict, Any, Optional
from pathlib import Path
from langchain.prompts import PromptTemplate


class PromptyLoader:
    """Loads and processes .prompty files with metadata and variable replacement"""
    
    def __init__(self, prompts_base_path: str = None):
        """
        Initialize the PromptyLoader
        
        Args:
            prompts_base_path: Base path for prompts directory. If None, uses default relative path.
        """
        if prompts_base_path is None:
            # Default to prompts directory relative to project root
            current_dir = Path(__file__).parent.parent.parent
            self.prompts_base_path = current_dir / "prompts"
        else:
            self.prompts_base_path = Path(prompts_base_path)
    
    def load_prompty(self, agent_name: str, prompt_name: str) -> Dict[str, Any]:
        """
        Load a .prompty file and parse its metadata and content
        
        Args:
            agent_name: Name of the agent (e.g., 'document_analyzer', 'code_generator')
            prompt_name: Name of the prompt file without .prompty extension
            
        Returns:
            Dictionary containing metadata and content
        """
        prompty_path = self.prompts_base_path / agent_name / f"{prompt_name}.prompty"
        
        if not prompty_path.exists():
            raise FileNotFoundError(f"Prompty file not found: {prompty_path}")
        
        with open(prompty_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split metadata and prompt content
        if content.startswith('---'):
            # Find the end of the YAML frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                prompt_content = parts[2].strip()
            else:
                raise ValueError(f"Invalid prompty format in {prompty_path}")
        else:
            raise ValueError(f"Prompty file must start with YAML frontmatter: {prompty_path}")
        
        # Parse YAML metadata
        try:
            metadata = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in prompty file {prompty_path}: {e}")
        
        return {
            "metadata": metadata,
            "content": prompt_content,
            "path": str(prompty_path)
        }
    
    def create_prompt_template(self, agent_name: str, prompt_name: str, 
                             additional_variables: Optional[Dict[str, Any]] = None) -> PromptTemplate:
        """
        Create a LangChain PromptTemplate from a .prompty file
        
        Args:
            agent_name: Name of the agent
            prompt_name: Name of the prompt file
            additional_variables: Additional variables to include in the template
            
        Returns:
            LangChain PromptTemplate object
        """
        prompty_data = self.load_prompty(agent_name, prompt_name)
        content = prompty_data["content"]
        metadata = prompty_data["metadata"]
        
        # Extract input variables from metadata
        input_variables = []
        if "inputs" in metadata:
            input_variables = list(metadata["inputs"].keys())
        
        # Add any additional variables
        if additional_variables:
            for var_name in additional_variables:
                if var_name not in input_variables:
                    input_variables.append(var_name)
        
        # Auto-detect variables in the template if not specified in metadata
        if not input_variables:
            # Find all {{variable}} patterns in the content
            pattern = r'\{\{(\w+)\}\}'
            found_variables = re.findall(pattern, content)
            input_variables = list(set(found_variables))
        
        return PromptTemplate(
            input_variables=input_variables,
            template=content,
            template_format="jinja2"
        )
    
    def get_prompt_metadata(self, agent_name: str, prompt_name: str) -> Dict[str, Any]:
        """
        Get only the metadata from a .prompty file
        
        Args:
            agent_name: Name of the agent
            prompt_name: Name of the prompt file
            
        Returns:
            Metadata dictionary
        """
        prompty_data = self.load_prompty(agent_name, prompt_name)
        return prompty_data["metadata"]
    
    def list_prompts(self, agent_name: str) -> list:
        """
        List all available prompts for an agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of prompt names (without .prompty extension)
        """
        agent_path = self.prompts_base_path / agent_name
        if not agent_path.exists():
            return []
        
        prompts = []
        for file_path in agent_path.glob("*.prompty"):
            prompts.append(file_path.stem)
        
        return sorted(prompts)
    
    def validate_prompty(self, agent_name: str, prompt_name: str) -> Dict[str, Any]:
        """
        Validate a .prompty file structure and content
        
        Args:
            agent_name: Name of the agent
            prompt_name: Name of the prompt file
            
        Returns:
            Validation result with status and any issues
        """
        try:
            prompty_data = self.load_prompty(agent_name, prompt_name)
            metadata = prompty_data["metadata"]
            content = prompty_data["content"]
            
            issues = []
            
            # Check required metadata fields
            required_fields = ["name", "description"]
            for field in required_fields:
                if field not in metadata:
                    issues.append(f"Missing required metadata field: {field}")
            
            # Check if content is not empty
            if not content.strip():
                issues.append("Prompt content is empty")
            
            # Check for variable consistency
            if "inputs" in metadata:
                declared_vars = set(metadata["inputs"].keys())
                content_vars = set(re.findall(r'\{\{(\w+)\}\}', content))
                
                # Variables in content but not declared
                undeclared = content_vars - declared_vars
                if undeclared:
                    issues.append(f"Variables used in content but not declared: {undeclared}")
                
                # Variables declared but not used
                unused = declared_vars - content_vars
                if unused:
                    issues.append(f"Variables declared but not used: {unused}")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "metadata": metadata,
                "variable_count": len(re.findall(r'\{\{(\w+)\}\}', content))
            }
            
        except Exception as e:
            return {
                "valid": False,
                "issues": [str(e)],
                "metadata": {},
                "variable_count": 0
            }


# Convenience function for quick access
def load_prompt_template(agent_name: str, prompt_name: str, 
                        prompts_base_path: str = None) -> PromptTemplate:
    """
    Quick function to load a prompt template
    
    Args:
        agent_name: Name of the agent
        prompt_name: Name of the prompt file
        prompts_base_path: Base path for prompts directory
        
    Returns:
        LangChain PromptTemplate object
    """
    loader = PromptyLoader(prompts_base_path)
    return loader.create_prompt_template(agent_name, prompt_name)
