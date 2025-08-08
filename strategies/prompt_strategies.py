"""
Strategy pattern implementation for language-specific prompt generation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from patterns.language_config import LanguageConfig


class PromptGenerationStrategy(ABC):
    """Abstract base class for prompt generation strategies"""
    
    def __init__(self, config: LanguageConfig):
        self.config = config
    
    @abstractmethod
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        """Generate a language-specific prompt"""
        pass
    
    def get_base_template(self) -> str:
        """Get the base template common to all languages"""
        return """
You are an expert {language} developer creating a complete, production-ready application.

Product Name: {product_name}
Version: {version}

Functional Requirements to implement:
{scenarios}

Project Setup Information:
{setup_info}

Your task is to generate a COMPLETE, functional {language} application with:
- Full implementation of all required functionality based on the scenarios
- Production-ready code with proper error handling
- Complete project structure with source code and configuration files
- Actual working implementation, not just templates or placeholders
- Real business logic implementation for each scenario

CRITICAL REQUIREMENTS:
1. **Complete Implementation**: Write actual functional code, not templates or TODO comments
2. **Real Business Logic**: Implement the actual functionality described in each scenario
3. **Error Handling**: Include proper error handling and validation
4. **Production Quality**: Code should be deployable and runnable
5. **Complete Files**: Generate ALL necessary source files, configuration files, and dependencies

TESTING GUIDELINES:
- **NO DUMMY TESTS**: Only create test files if you can provide real, meaningful test implementations
- **NO PLACEHOLDER TESTS**: Avoid generic "simulate some work" or "add your test logic here" content
- **REAL ASSERTIONS**: Test methods must include actual validation of functionality
- **FOCUS ON APPLICATION**: Prioritize complete application code over test boilerplate
- If tests are needed, they must test actual functionality with proper setup and assertions

{language_specific_instructions}

RESPONSE FORMAT:
## Application Structure
{project_structure}

## Complete Source Code Files
{file_templates}

## Build Instructions
{build_instructions}

## Run Instructions
{test_execution}

Generate a COMPLETE, production-ready application with full implementation of all scenarios.
"""


class CSharpPromptStrategy(PromptGenerationStrategy):
    """Strategy for generating C# prompts"""
    
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        base = self.get_base_template()
        
        dotnet_version = context.get('dotnet_version', '8.0')
        framework_name = self.config.framework.name
        framework_version = self.config.framework.version
        dependencies = ', '.join(self.config.framework.dependencies)
        tests_dir = self.config.project_structure['tests']
        test_method_pattern = self.config.framework.test_method_pattern
        example_template = self.config.framework.example_template
        build_file = self.config.build_file
        test_file_pattern = self.config.framework.test_file_pattern
        build_commands = '\n'.join([f'- {cmd}' for cmd in self.config.build_commands])
        test_commands = '\n'.join([f'- {cmd}' for cmd in self.config.test_commands])
        
        language_instructions = f"""
FRAMEWORK: {framework_name} {framework_version}

APPLICATION STRUCTURE:
- Create complete {{{{product_name}}}}.csproj with .NET {dotnet_version} framework
- Dependencies: {dependencies}
- Create source code classes in {tests_dir} directory
- Implement actual business logic for each scenario
- Each scenario gets a complete, functional implementation
- Include proper namespace and using statements
- Add configuration files, models, controllers, services as needed

IMPLEMENTATION REQUIREMENTS:
- Write REAL, working code that implements the described functionality
- Include proper error handling and validation
- Use appropriate design patterns and best practices
- Create complete classes with full method implementations
- No placeholder code or TODO comments

EXAMPLE IMPLEMENTATION:
```csharp{example_template}
```

FOCUS: Create a complete, runnable {framework_name} application that fully implements all scenarios with real business logic.
"""
        
        project_structure = f"""
[Generate ALL necessary files for a complete application]
- {{{{product_name}}}}.csproj (with all dependencies)
- Program.cs (main entry point)
- Controllers/ (if web application)
- Models/ (data models)
- Services/ (business logic)
- Configuration files (appsettings.json, etc.)
- README.md (with run instructions)
"""
        
        # Replace template variables in test_file_pattern to avoid format conflicts
        safe_test_file_pattern = test_file_pattern.replace('{product_name}', 'ProductName')
        
        file_templates = f"""
### {{{{product_name}}}}.csproj
```xml
[Complete .csproj with {framework_name} dependencies and proper configuration]
```

### Program.cs
```csharp
[Complete main application entry point with real implementation]
```

### Models/
```csharp
[Complete data models and entities required for the application]
```

### Services/
```csharp  
[Complete business logic services implementing all scenarios]
```

### Additional Files
```csharp
[All other necessary source files for a complete, functional application]
```
"""
        
        build_instructions = build_commands
        
        test_execution = test_commands
        
        return base.format(
            language='{language}',
            product_name='{product_name}',
            version='{version}',
            scenarios='{scenarios}',
            setup_info='{setup_info}',
            language_specific_instructions=language_instructions,
            project_structure=project_structure,
            file_templates=file_templates,
            build_instructions=build_instructions,
            test_execution=test_execution
        )


class JavaPromptStrategy(PromptGenerationStrategy):
    """Strategy for generating Java prompts"""
    
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        base = self.get_base_template()
        
        java_version = context.get('java_version', '17')
        framework_name = self.config.framework.name
        framework_version = self.config.framework.version
        dependencies = ', '.join(self.config.framework.dependencies)
        tests_dir = self.config.project_structure['tests']
        test_method_pattern = self.config.framework.test_method_pattern
        example_template = self.config.framework.example_template
        build_file = self.config.build_file
        build_commands = '\n'.join([f'- {cmd}' for cmd in self.config.build_commands])
        test_commands = '\n'.join([f'- {cmd}' for cmd in self.config.test_commands])
        
        language_instructions = f"""
FRAMEWORK: {framework_name} {framework_version}

PROJECT STRUCTURE:
- Create complete {build_file} with Maven configuration for Java {java_version}
- Dependencies: {dependencies}
- Create test classes in {tests_dir} directory
- Use descriptive class names following Java conventions
- Each test method follows pattern: {test_method_pattern}
- Include proper imports and annotations
- Use @Test, @BeforeEach, @AfterEach as needed

EXAMPLE TEST METHOD:
```java{example_template}
```
"""
        
        project_structure = f"""
[List ALL files and directories]
- {build_file}
- {tests_dir}*.java files
- src/main/java/ directory structure
"""
        
        file_templates = f"""
### {build_file}
```xml
[Complete pom.xml with JUnit 5 dependencies]
```

### Test Classes
```java
[Complete test classes with imports, annotations, and ALL test methods]
```
"""
        
        build_instructions = build_commands
        test_execution = test_commands
        
        return base.format(
            language='{language}',
            product_name='{product_name}',
            version='{version}',
            scenarios='{scenarios}',
            setup_info='{setup_info}',
            language_specific_instructions=language_instructions,
            project_structure=project_structure,
            file_templates=file_templates,
            build_instructions=build_instructions,
            test_execution=test_execution
        )


class PythonPromptStrategy(PromptGenerationStrategy):
    """Strategy for generating Python prompts"""
    
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        base = self.get_base_template()
        
        python_version = context.get('python_version', '3.11')
        framework_name = self.config.framework.name
        framework_version = self.config.framework.version
        dependencies = ', '.join(self.config.framework.dependencies)
        tests_dir = self.config.project_structure['tests']
        test_method_pattern = self.config.framework.test_method_pattern
        test_file_pattern = self.config.framework.test_file_pattern
        example_template = self.config.framework.example_template
        build_file = self.config.build_file
        build_commands = '\n'.join([f'- {cmd}' for cmd in self.config.build_commands])
        test_commands = '\n'.join([f'- {cmd}' for cmd in self.config.test_commands])
        
        language_instructions = f"""
FRAMEWORK: {framework_name} {framework_version}

APPLICATION STRUCTURE:
- Create complete {build_file} with dependencies for Python {python_version}
- Dependencies: {dependencies}
- Create application modules and packages
- Implement actual business logic for each scenario
- Each scenario gets a complete, functional implementation
- Include proper imports and error handling
- Create main application entry point

IMPLEMENTATION REQUIREMENTS:
- Write REAL, working Python code that implements the described functionality
- Include proper error handling and validation
- Use appropriate Python best practices and design patterns
- Create complete classes and functions with full implementations
- No placeholder code or TODO comments
- Include configuration files, requirements.txt, and setup files

EXAMPLE IMPLEMENTATION:
```python{example_template}
```

FOCUS: Create a complete, runnable Python application that fully implements all scenarios with real business logic.
"""
        
        project_structure = f"""
[Generate ALL necessary files for a complete Python application]
- {build_file} (with all dependencies)
- main.py (application entry point)
- src/ (source code modules)
- config/ (configuration files)
- models/ (data models)
- services/ (business logic)
- utils/ (utility functions)
- README.md (with run instructions)
"""
        
        file_templates = f"""
### {build_file}
```
[Complete requirements.txt or setup.py with all necessary dependencies]
```

### main.py
```python
[Complete main application entry point with real implementation]
```

### src/
```python
[Complete application modules implementing all scenarios]
```

### models/
```python
[Complete data models and classes required for the application]
```

### services/
```python
[Complete business logic services implementing all scenarios]
```

### Additional Files
```python
[All other necessary Python files for a complete, functional application]
```
"""
        
        build_instructions = build_commands
        test_execution = test_commands
        
        return base.format(
            language='{language}',
            product_name='{product_name}',
            version='{version}',
            scenarios='{scenarios}',
            setup_info='{setup_info}',
            language_specific_instructions=language_instructions,
            project_structure=project_structure,
            file_templates=file_templates,
            build_instructions=build_instructions,
            test_execution=test_execution
        )


class JavaScriptPromptStrategy(PromptGenerationStrategy):
    """Strategy for generating JavaScript prompts"""
    
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        base = self.get_base_template()
        
        node_version = context.get('node_version', '18')
        framework_name = self.config.framework.name
        framework_version = self.config.framework.version
        dependencies = ', '.join(self.config.framework.dependencies)
        tests_dir = self.config.project_structure['tests']
        test_file_pattern = self.config.framework.test_file_pattern
        example_template = self.config.framework.example_template
        build_file = self.config.build_file
        build_commands = '\n'.join([f'- {cmd}' for cmd in self.config.build_commands])
        test_commands = '\n'.join([f'- {cmd}' for cmd in self.config.test_commands])
        
        language_instructions = f"""
FRAMEWORK: {framework_name} {framework_version}

PROJECT STRUCTURE:
- Create complete {build_file} with configuration for Node.js {node_version}
- Dependencies: {dependencies}
- Create test files in {tests_dir} directory
- Use descriptive file names: {test_file_pattern}
- Each test function follows Jest conventions
- Include proper imports/requires
- Use describe/it blocks for organization

EXAMPLE TEST:
```javascript{example_template}
```
"""
        
        project_structure = f"""
[List ALL files and directories]
- {build_file}
- {tests_dir}*.js files
- Source code directory structure
"""
        
        file_templates = f"""
### {build_file}
```json
[Complete package.json with Jest dependencies]
```

### Test Files
```javascript
[Complete test files with imports, describe blocks, and ALL test cases]
```
"""
        
        build_instructions = build_commands
        test_execution = test_commands
        
        return base.format(
            language='{language}',
            product_name='{product_name}',
            version='{version}',
            scenarios='{scenarios}',
            setup_info='{setup_info}',
            language_specific_instructions=language_instructions,
            project_structure=project_structure,
            file_templates=file_templates,
            build_instructions=build_instructions,
            test_execution=test_execution
        )


class GoPromptStrategy(PromptGenerationStrategy):
    """Strategy for generating Go prompts"""
    
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        base = self.get_base_template()
        
        go_version = context.get('go_version', '1.21')
        framework_name = self.config.framework.name
        framework_version = self.config.framework.version
        build_file = self.config.build_file
        test_method_pattern = self.config.framework.test_method_pattern
        example_template = self.config.framework.example_template
        build_commands = '\n'.join([f'- {cmd}' for cmd in self.config.build_commands])
        test_commands = '\n'.join([f'- {cmd}' for cmd in self.config.test_commands])
        
        language_instructions = f"""
FRAMEWORK: {framework_name} (Go {go_version})

PROJECT STRUCTURE:
- Create {build_file} file for module management
- Create test files with _test.go suffix
- Use descriptive test function names: {test_method_pattern}
- Follow Go testing conventions
- Use table-driven tests where appropriate

EXAMPLE TEST:
```go
package main

import (
    "testing"
){example_template}
```
"""
        
        project_structure = f"""
[List ALL files and directories]
- {build_file}
- *_test.go files
- Source code *.go files
"""
        
        file_templates = f"""
### {build_file}
```
[Complete go.mod file]
```

### Test Files
```go
[Complete test files with package declaration, imports, and ALL test functions]
```
"""
        
        build_instructions = build_commands
        test_execution = test_commands
        
        return base.format(
            language='{language}',
            product_name='{product_name}',
            version='{version}',
            scenarios='{scenarios}',
            setup_info='{setup_info}',
            language_specific_instructions=language_instructions,
            project_structure=project_structure,
            file_templates=file_templates,
            build_instructions=build_instructions,
            test_execution=test_execution
        )


class RustPromptStrategy(PromptGenerationStrategy):
    """Strategy for generating Rust prompts"""
    
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        base = self.get_base_template()
        
        rust_version = context.get('rust_version', '1.70')
        framework_name = self.config.framework.name
        framework_version = self.config.framework.version
        build_file = self.config.build_file
        example_template = self.config.framework.example_template
        build_commands = '\n'.join([f'- {cmd}' for cmd in self.config.build_commands])
        test_commands = '\n'.join([f'- {cmd}' for cmd in self.config.test_commands])
        
        language_instructions = f"""
FRAMEWORK: {framework_name} (Rust {rust_version})

PROJECT STRUCTURE:
- Create {build_file} for project configuration
- Create test modules in src/lib.rs or separate test files
- Use #[cfg(test)] and #[test] attributes
- Follow Rust testing conventions
- Use assert! and assert_eq! macros

EXAMPLE TEST:
```rust{example_template}
```
"""
        
        project_structure = f"""
[List ALL files and directories]
- {build_file}
- src/lib.rs or src/main.rs
- tests/ directory with test files
"""
        
        file_templates = f"""
### {build_file}
```toml
[Complete Cargo.toml with dependencies]
```

### Test Files
```rust
[Complete test modules with #[cfg(test)], use statements, and ALL test functions]
```
"""
        
        build_instructions = build_commands
        test_execution = test_commands
        
        return base.format(
            language='{language}',
            product_name='{product_name}',
            version='{version}',
            scenarios='{scenarios}',
            setup_info='{setup_info}',
            language_specific_instructions=language_instructions,
            project_structure=project_structure,
            file_templates=file_templates,
            build_instructions=build_instructions,
            test_execution=test_execution
        )
