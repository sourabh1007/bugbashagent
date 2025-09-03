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
from langchain_core.language_models import BaseLanguageModel


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
    
    def create_llm_with_prompty_settings(self, base_llm: BaseLanguageModel, 
                                       agent_name: str, prompt_name: str) -> BaseLanguageModel:
        """
        Create an LLM with prompty-specific settings, falling back to base_llm settings
        
        Args:
            base_llm: The base LLM to use as fallback
            agent_name: Name of the agent
            prompt_name: Name of the prompt file
            
        Returns:
            LLM configured with prompty-specific parameters or base_llm if no specific settings
        """
        try:
            metadata = self.get_prompt_metadata(agent_name, prompt_name)
            
            # Check if prompty has model parameters
            if "model" not in metadata or "parameters" not in metadata["model"]:
                return base_llm
            
            prompty_params = metadata["model"]["parameters"]
            
            # Extract relevant parameters
            llm_kwargs = {}
            if "temperature" in prompty_params:
                llm_kwargs["temperature"] = prompty_params["temperature"]
            if "max_tokens" in prompty_params:
                llm_kwargs["max_tokens"] = prompty_params["max_tokens"]
            
            # If no relevant parameters found, return base LLM
            if not llm_kwargs:
                return base_llm
            
            # Create a copy of the base LLM with updated parameters
            # Prefer using model_dump (Pydantic v2) to preserve provider-specific fields
            try:
                if hasattr(base_llm, "model_dump") and callable(getattr(base_llm, "model_dump")):
                    current_params = base_llm.model_dump(exclude_none=True)
                else:
                    # Fallback: copy a conservative set of common attributes
                    attrs_to_copy = [
                        'temperature', 'max_tokens', 'model_name', 'deployment_name', 'openai_api_key',
                        # Azure OpenAI specific
                        'azure_endpoint', 'azure_deployment', 'api_key', 'api_version'
                    ]
                    current_params = {}
                    for attr in attrs_to_copy:
                        if hasattr(base_llm, attr):
                            current_params[attr] = getattr(base_llm, attr)

                # Ensure Azure-specific required fields are preserved when present on the base LLM
                for required_attr in ['azure_endpoint', 'azure_deployment', 'api_key', 'api_version']:
                    if required_attr not in current_params and hasattr(base_llm, required_attr):
                        current_params[required_attr] = getattr(base_llm, required_attr)

                # Update with prompty parameters (e.g., temperature, max_tokens)
                current_params.update(llm_kwargs)

                # Create new LLM instance with updated parameters
                return base_llm.__class__(**current_params)
            except Exception:
                # Fallback to base LLM if we can't create a new instance
                return base_llm
                
        except Exception as e:
            # If anything goes wrong, fallback to base LLM
            print(f"Warning: Could not apply prompty settings for {agent_name}/{prompt_name}: {e}")
            return base_llm
    
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


def create_llm_with_prompty_settings(base_llm: BaseLanguageModel, agent_name: str, 
                                    prompt_name: str, prompts_base_path: str = None) -> BaseLanguageModel:
    """
    Quick function to create an LLM with prompty-specific settings
    
    Args:
        base_llm: The base LLM to use as fallback
        agent_name: Name of the agent
        prompt_name: Name of the prompt file
        prompts_base_path: Base path for prompts directory
        
    Returns:
        LLM configured with prompty-specific parameters or base_llm if no specific settings
    """
    loader = PromptyLoader(prompts_base_path)
    return loader.create_llm_with_prompty_settings(base_llm, agent_name, prompt_name)
