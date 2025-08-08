"""
Simplified Go Project Generator

Only creates minimal project structure, lets LLM generate actual implementation files.
No dummy test files are created automatically.
"""

import os
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class GoProjectGenerator(BaseProjectGenerator):
    """Simplified generator for Go projects - no automatic test file generation"""
    
    def __init__(self):
        super().__init__()
        self.language = 'go'
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate minimal Go project structure - only essential files, no dummy tests"""
        created_files = {}
        
        # Create essential project files for Go
        # 1. Create go.mod file (essential for Go projects)
        module_name = product_name.lower().replace(' ', '-').replace('_', '-')
        go_mod_content = self._create_go_mod_content(module_name)
        go_mod_file = os.path.join(project_dir, "go.mod")
        with open(go_mod_file, 'w', encoding='utf-8') as f:
            f.write(go_mod_content)
        created_files["go_mod"] = go_mod_file
        
        # 2. Create .gitignore for Go projects
        gitignore_content = """# Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, built with `go test -c`
*.test

# Output of the go coverage tool
*.out

# Dependency directories
vendor/

# Go workspace file
go.work"""
        gitignore_file = os.path.join(project_dir, ".gitignore")
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        created_files["gitignore"] = gitignore_file
        
        # 3. Create README with project instructions
        readme_file = os.path.join(project_dir, "README.md")
        readme_content = self._create_project_readme(product_name, module_name, scenarios)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_go_mod_content(self, module_name: str) -> str:
        """Create go.mod file content with common Go dependencies"""
        go_version = self.get_language_version('go')
        packages = self.get_packages_for_language(self.language)
        
        require_lines = []
        for package_name, version in packages.items():
            # Format Go import path with version
            if '/' in package_name:
                require_lines.append(f"    {package_name} {version}")
            else:
                require_lines.append(f"    github.com/{package_name} {version}")
        
        require_section = '\n'.join(require_lines)
        
        return f'''module {module_name}

go {go_version}

require (
{require_section}
)'''
    
    def _create_project_readme(self, product_name: str, module_name: str, scenarios: List[str]) -> str:
        """Create project README"""
        scenarios_list = '\n'.join(f'{i+1}. **{scenario}**' for i, scenario in enumerate(scenarios))
        
        return f'''# {product_name} - Go Application

This is a Go application for **{product_name}**.

## 📋 Functional Requirements

{scenarios_list}

## 🚀 Building and Running

### Prerequisites
- Go 1.21 or higher

### Building
```bash
# Initialize module (if needed)
go mod init {module_name}

# Download dependencies
go mod tidy

# Build the project
go build

# Run the application
go run main.go

# Or run the built binary
./{module_name}    # On Linux/macOS
./{module_name}.exe # On Windows
```

### Development
```bash
# Format code
go fmt ./...

# Run tests (when test files are created)
go test ./...

# Run tests with verbose output
go test -v ./...

# Check for race conditions
go test -race ./...
```

## 📖 Project Overview

This project implements the functional requirements listed above using Go.

Real implementation files will be created only when the LLM generates actual, meaningful code.
No dummy or placeholder test files are automatically created.

---
*Generated for {product_name}*
'''
