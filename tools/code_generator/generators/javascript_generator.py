"""
Simplified JavaScript Project Generator

Only creates minimal project structure, lets LLM generate actual implementation files.
No dummy test files are created automatically.
"""

import os
import json
from typing import Dict, List, Any
from .base_generator import BaseProjectGenerator


class JavaScriptProjectGenerator(BaseProjectGenerator):
    """Simplified generator for JavaScript/Node.js projects - no automatic test file generation"""
    
    def __init__(self):
        super().__init__()
        self.language = 'javascript'
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str, analyzer_output: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate minimal JavaScript/Node.js project structure - only essential files, no dummy tests"""
        created_files = {}
        
        # Create essential project files for JavaScript/Node.js
        # 1. Create package.json with common packages and configured versions
        package_json = self._create_package_json_content(product_name)
        package_json_file = os.path.join(project_dir, "package.json")
        with open(package_json_file, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        created_files["package_json"] = package_json_file
        
        # 2. Create .gitignore for Node.js projects
        gitignore_content = """node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
dist/
build/
*.log"""
        gitignore_file = os.path.join(project_dir, ".gitignore")
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        created_files["gitignore"] = gitignore_file
        
        # 3. Create README with project instructions
        readme_file = os.path.join(project_dir, "README.md")
        readme_content = self._create_project_readme(product_name, scenarios)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_package_json_content(self, product_name: str) -> dict:
        """Create package.json content with configured package versions"""
        packages = self.get_packages_for_language(self.language)
        node_version = self.get_language_version('node')
        
        # Separate dependencies and devDependencies
        dependencies = {}
        dev_dependencies = {}
        
        # Get test packages from configuration to determine dev dependencies
        test_packages_config = self.package_versions.get_test_packages_for_language(self.language)
        test_package_names = set(test_packages_config.keys())
        
        # Additional dev packages (non-test related)
        additional_dev_packages = {'nodemon', 'eslint', 'prettier', 'typescript', '@types/node'}
        
        for package_name, version in packages.items():
            # Check if it's a test package or additional dev package
            if package_name in test_package_names or package_name in additional_dev_packages:
                dev_dependencies[package_name] = version
            else:
                dependencies[package_name] = version
        
        return {
            "name": f"{product_name.lower().replace(' ', '-')}",
            "version": "1.0.0",
            "description": f"{product_name} - JavaScript/Node.js Application",
            "main": "index.js",
            "engines": {
                "node": f">={node_version}.0.0"
            },
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js",
                "build": "echo 'Build process will be implemented based on requirements'",
                "test": f"{self.get_test_framework_for_language(self.language)}",
                "test:watch": f"{self.get_test_framework_for_language(self.language)} --watch",
                "test:coverage": f"{self.get_test_framework_for_language(self.language)} --coverage",
                "lint": "eslint .",
                "lint:fix": "eslint . --fix",
                "format": "prettier --write ."
            },
            "keywords": ["application", "nodejs"],
            "author": "",
            "license": "ISC",
            "dependencies": dependencies,
            "devDependencies": dev_dependencies
        }
    
    def _create_project_readme(self, product_name: str, scenarios: List[str]) -> str:
        """Create project README"""
        package_name = product_name.lower().replace(' ', '-')
        scenarios_list = '\n'.join(f'{i+1}. **{scenario}**' for i, scenario in enumerate(scenarios))
        
        return f'''# {product_name} - JavaScript/Node.js Application

This is a JavaScript/Node.js application for **{product_name}**.

## 📋 Functional Requirements

{scenarios_list}

## 🚀 Installation and Running

### Prerequisites
- Node.js 16 or higher
- npm package manager

### Installation
```bash
# Install dependencies
npm install
```

### Running
```bash
# Run the application
npm start

# Run in development mode (with auto-restart)
npm run dev
```

### Development
```bash
# Build the project (when build process is defined)
npm run build

# Run tests (when test files are created)
npm test
```

## 📖 Project Overview

This project implements the functional requirements listed above using JavaScript/Node.js.

Real implementation files will be created only when the LLM generates actual, meaningful code.
No dummy or placeholder test files are automatically created.

---
*Generated for {product_name}*
'''
