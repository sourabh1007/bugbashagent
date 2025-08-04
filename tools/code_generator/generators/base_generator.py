"""
Base Project Generator

Contains the base class for all language-specific project generators.
"""

import os
from typing import Dict, List
from ..file_creator import FileCreator


class BaseProjectGenerator:
    """Base class for language-specific project generators"""
    
    def __init__(self):
        self.file_creator = FileCreator()
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate project structure and files"""
        raise NotImplementedError("Subclasses must implement generate_project")
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use in code"""
        return name.replace(' ', '').replace('-', '').replace('_', '')
    
    def _create_readme(self, project_dir: str, product_name: str, scenarios: List[str], 
                      setup_instructions: str, run_instructions: str, test_instructions: str,
                      generated_content: str) -> str:
        """Create a README file for the project"""
        readme_content = f"""# {product_name}

{product_name} is a software project generated with comprehensive functionality and test coverage.

## Scenarios Implemented

{chr(10).join([f'- {scenario}' for scenario in scenarios])}

## Setup Instructions

{setup_instructions}

## Running the Application

{run_instructions}

## Running Tests

{test_instructions}

## Generated Content

Below is the complete output from the AI code generator:

{generated_content}
"""
        
        readme_file = os.path.join(project_dir, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return readme_file
