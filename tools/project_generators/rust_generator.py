"""
Simplified Rust Project Generator

Only creates minimal project structure, lets LLM generate actual implementation files.
No dummy test files are created automatically.
"""

import os
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class RustProjectGenerator(BaseProjectGenerator):
    """Simplified generator for Rust projects - no automatic test file generation"""
    
    def __init__(self):
        super().__init__()
        self.language = 'rust'
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate minimal Rust project structure - only essential files, no dummy tests"""
        created_files = {}
        
        # Create essential project files for Rust
        # 1. Create Cargo.toml file (essential for Rust projects)
        package_name = product_name.lower().replace(' ', '_').replace('-', '_')
        cargo_toml_content = self._create_cargo_toml_content(package_name, product_name)
        cargo_toml_file = os.path.join(project_dir, "Cargo.toml")
        with open(cargo_toml_file, 'w', encoding='utf-8') as f:
            f.write(cargo_toml_content)
        created_files["cargo_toml"] = cargo_toml_file
        
        # 2. Create src directory structure
        src_dir = os.path.join(project_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        
        # 3. Create .gitignore for Rust projects
        gitignore_content = """/target
**/*.rs.bk
Cargo.lock
.vscode/
.idea/
*.swp
*.swo"""
        gitignore_file = os.path.join(project_dir, ".gitignore")
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        created_files["gitignore"] = gitignore_file
        
        # 4. Create README with project instructions
        readme_file = os.path.join(project_dir, "README.md")
        readme_content = self._create_project_readme(product_name, package_name, scenarios)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_cargo_toml_content(self, package_name: str, product_name: str) -> str:
        """Create Cargo.toml file content with common Rust dependencies"""
        rust_version = self.get_language_version('rust')
        packages = self.get_packages_for_language(self.language)
        
        # Create dependencies section
        dependencies_lines = []
        dev_dependencies_lines = []
        
        # Get the configured test packages to determine which are dev dependencies
        test_packages_config = self.package_versions.get_test_packages_for_language(self.language)
        test_package_names = set(test_packages_config.keys())
        
        for package_name_key, config in packages.items():
            # Check if this package is a test package based on our configuration
            is_test_package = package_name_key in test_package_names
            
            if is_test_package:
                if isinstance(config, dict):
                    if 'features' in config:
                        dev_dependencies_lines.append(f'{package_name_key} = {{ version = "{config["version"]}", features = {config["features"]} }}')
                    else:
                        dev_dependencies_lines.append(f'{package_name_key} = "{config["version"]}"')
                else:
                    dev_dependencies_lines.append(f'{package_name_key} = "{config}"')
            else:
                if isinstance(config, dict):
                    if 'features' in config:
                        dependencies_lines.append(f'{package_name_key} = {{ version = "{config["version"]}", features = {config["features"]} }}')
                    else:
                        dependencies_lines.append(f'{package_name_key} = "{config["version"]}"')
                else:
                    dependencies_lines.append(f'{package_name_key} = "{config}"')
        
        dependencies_section = '\n'.join(dependencies_lines)
        dev_dependencies_section = '\n'.join(dev_dependencies_lines)
        
        # Determine edition based on rust version
        edition = "2021" if float(rust_version) >= 1.56 else "2018"
        
        toml_content = f'''[package]
name = "{package_name}"
version = "0.1.0"
edition = "{edition}"
description = "{product_name} - Rust Application"

[[bin]]
name = "main"
path = "src/main.rs"

[dependencies]
{dependencies_section}'''
        
        if dev_dependencies_section:
            toml_content += f'''

[dev-dependencies]
{dev_dependencies_section}'''
        
        return toml_content
    
    def _create_project_readme(self, product_name: str, package_name: str, scenarios: List[str]) -> str:
        """Create project README"""
        scenarios_list = '\n'.join(f'{i+1}. **{scenario}**' for i, scenario in enumerate(scenarios))
        
        return f'''# {product_name} - Rust Application

This is a Rust application for **{product_name}**.

## 📋 Functional Requirements

{scenarios_list}

## 🚀 Building and Running

### Prerequisites
- Rust 1.70 or higher (install from [rustup.rs](https://rustup.rs/))

### Building
```bash
# Check the project compiles
cargo check

# Build the project  
cargo build

# Build for release
cargo build --release

# Run the application
cargo run

# Run the release build
cargo run --release
```

### Development
```bash
# Format code
cargo fmt

# Lint code
cargo clippy

# Run tests (when test files are created)
cargo test

# Run tests with output
cargo test -- --nocapture

# Generate documentation
cargo doc --open
```

## 📖 Project Overview

This project implements the functional requirements listed above using Rust.

Real implementation files will be created only when the LLM generates actual, meaningful code.
No dummy or placeholder test files are automatically created.

## 🦀 Rust Features

This project is set up to use modern Rust (edition 2021) with:
- Standard library functionality
- Cargo for dependency management and building
- Support for both library and binary targets

---
*Generated for {product_name}*
'''
