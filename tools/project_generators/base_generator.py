"""
Base Project Generator

Contains the base class for all language-specific project generators.
"""

import os
from typing import Dict, List, Any
from ..file_management.file_creator import FileCreator
from config_package.package_versions import PackageVersions


class BaseProjectGenerator:
    """Base class for language-specific project generators"""
    
    def __init__(self):
        self.file_creator = FileCreator()
        self.package_versions = PackageVersions()
    
    def get_language_version(self, language: str) -> str:
        """Get the configured runtime version for a language"""
        return self.package_versions.get_language_version(language)
    
    def get_packages_for_language(self, language: str, analyzer_output: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get combined packages: test frameworks + detected dependencies based on analyzer output"""
        # Get test framework packages
        test_packages = self.package_versions.get_test_packages_with_cosmosdb(language, analyzer_output)
        
        # Get scenario-based dependencies if analyzer output is provided
        if analyzer_output:
            detected_dependencies = self.package_versions.detect_dependencies_from_scenario(analyzer_output)
            scenario_packages = detected_dependencies.get(language.lower(), {})
            
            # Merge test packages with detected packages
            combined_packages = {**test_packages, **scenario_packages}
            return combined_packages
        else:
            return test_packages
    
    def get_test_framework_for_language(self, language: str) -> str:
        """Get the primary test framework for a language"""
        return self.package_versions.get_primary_test_framework(language)
    
    def get_cosmosdb_version(self) -> str:
        """Get the current CosmosDB version (either from analyzer or default)"""
        return self.package_versions.get_cosmosdb_version()
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str, analyzer_output: Dict[str, Any] = None) -> Dict[str, str]:
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
