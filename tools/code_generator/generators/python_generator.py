"""
Python Project Generator

Generates Python projects with proper module structure, requirements, and pytest tests.
"""

import os
from typing import Dict, List, Any
from .base_generator import BaseProjectGenerator


class PythonProjectGenerator(BaseProjectGenerator):
    """Generator for Python projects"""
    
    def __init__(self):
        super().__init__()
        self.language = 'python'
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str, analyzer_output: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate minimal Python project structure - only essential files, no dummy tests"""
        created_files = {}
        
        # Create essential project files for Python
        # 1. Create requirements.txt with common packages and configured versions
        requirements_content = self._create_requirements_content(analyzer_output)
        requirements_file = os.path.join(project_dir, "requirements.txt")
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files["requirements"] = requirements_file
        
        # 2. Create setup.py for packaging
        setup_content = self._create_setup_py_content(product_name)
        setup_file = os.path.join(project_dir, "setup.py")
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(setup_content)
        created_files["setup"] = setup_file
        
        # 3. Create __init__.py for package structure
        init_file = os.path.join(project_dir, "__init__.py")
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('"""Project package initialization"""')
        created_files["init"] = init_file
        
        # 4. Create README with project instructions
        readme_file = os.path.join(project_dir, "README.md")
        readme_content = self._create_project_readme(product_name, scenarios)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_requirements_content(self, analyzer_output: Dict[str, Any] = None) -> str:
        """Create requirements.txt content with configured package versions, including CosmosDB if needed"""
        packages = self.get_packages_for_language(self.language, analyzer_output)
        
        requirements_lines = []
        for package_name, version in packages.items():
            if '>=' in version or '==' in version or '~=' in version:
                requirements_lines.append(f"{package_name}{version}")
            else:
                requirements_lines.append(f"{package_name}>={version}")
        
        return '\n'.join(requirements_lines)
    
    def _create_setup_py_content(self, product_name: str) -> str:
        """Create setup.py for Python package"""
        package_name = product_name.lower().replace(' ', '_').replace('-', '_')
        python_version = self.get_language_version('python')
        
        return f'''from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    description="{product_name} - Python Application",
    packages=find_packages(),
    python_requires=">={python_version}",
    install_requires=[
        # Dependencies will be loaded from requirements.txt
    ],
    entry_points={{
        "console_scripts": [
            "{package_name}=main:main",
        ],
    }},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)'''
    
    def _create_project_readme(self, product_name: str, scenarios: List[str]) -> str:
        """Create project README"""
        package_name = product_name.lower().replace(' ', '_').replace('-', '_')
        scenarios_list = '\\n'.join(f'{i+1}. **{scenario}**' for i, scenario in enumerate(scenarios))
        
        return f'''# {product_name} - Python Application

This is a Python application for **{product_name}**.

## 📋 Functional Requirements

{scenarios_list}

## 🚀 Installation and Running

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Running
```bash
# Run the application
python main.py

# Or if installed as package
{package_name}
```

## 📖 Project Overview

This project implements the functional requirements listed above using Python.

Real implementation files will be created only when the LLM generates actual, meaningful code.
No dummy or placeholder test files are automatically created.

---
*Generated for {product_name}*
'''

