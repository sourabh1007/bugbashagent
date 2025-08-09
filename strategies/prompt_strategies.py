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
- **EXECUTABLE CODE**: The generated code will be automatically built and executed after generation

CRITICAL REQUIREMENTS:
1. **Complete Implementation**: Write actual functional code, not templates or TODO comments
2. **Real Business Logic**: Implement the actual functionality described in each scenario
3. **Error Handling**: Include proper error handling and validation
4. **Production Quality**: Code should be deployable and runnable
5. **Complete Files**: Generate ALL necessary source files, configuration files, and dependencies
6. **EXECUTABLE ENTRY POINT**: Include a main method/function that can be executed to demonstrate the functionality
7. **OUTPUT GENERATION**: The main execution should produce visible output to show that the functionality works

TESTING GUIDELINES:
- **NO DUMMY TESTS**: Only create test files if you can provide real, meaningful test implementations
- **NO PLACEHOLDER TESTS**: Avoid generic "simulate some work" or "add your test logic here" content
- **REAL ASSERTIONS**: Test methods must include actual validation of functionality
- **FOCUS ON APPLICATION**: Prioritize complete application code over test boilerplate
- If tests are needed, they must test actual functionality with proper setup and assertions

EXECUTION REQUIREMENTS:
- **MAIN ENTRY POINT**: Include a clear main method/function that demonstrates all scenarios
- **CONSOLE OUTPUT**: Generate informative output that shows each scenario being executed
- **ERROR HANDLING**: Handle exceptions gracefully with meaningful error messages
- **COMPLETION STATUS**: Show when execution completes successfully

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

## Expected Output
[Describe what output the application will generate when executed]

Generate a COMPLETE, production-ready application with full implementation of all scenarios that will be automatically executed after generation.
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

EXECUTION REQUIREMENTS:
- **Program.cs MUST contain a Main method** that demonstrates all scenarios
- Main method should execute each scenario and produce console output
- Use Console.WriteLine() to show progress and results
- Handle exceptions with try-catch blocks and meaningful error messages
- Show completion status at the end

EXAMPLE MAIN METHOD:
```csharp
using System;

namespace {{{{product_name}}}}
{{
    class Program
    {{
        static void Main(string[] args)
        {{
            Console.WriteLine("Starting {{{{product_name}}}} Application...");
            
            try
            {{
                // Execute each scenario with clear output
                Console.WriteLine("\\n=== Executing Scenarios ===");
                
                // Scenario implementation calls here
                ExecuteScenario1();
                ExecuteScenario2();
                // ... more scenarios
                
                Console.WriteLine("\\n=== All Scenarios Completed Successfully ===");
            }}
            catch (Exception ex)
            {{
                Console.WriteLine($"Error: {{ex.Message}}");
            }}
        }}
        
        // Individual scenario methods with real implementation
        static void ExecuteScenario1()
        {{
            Console.WriteLine("Executing Scenario 1...");
            // Real implementation here
            Console.WriteLine("Scenario 1 completed.");
        }}
    }}
}}
```

FOCUS: Create a complete, runnable {framework_name} application that fully implements all scenarios with real business logic and executable Main method.
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
[Complete .csproj with {framework_name} dependencies and proper configuration for .NET {dotnet_version}]
```

### Program.cs
```csharp
[Complete main application entry point with executable Main method that demonstrates all scenarios]
[Must include Console.WriteLine statements showing execution progress]
[Must handle exceptions and show completion status]
```

### Models/
```csharp
[Complete data models and entities required for the application]
```

### Services/
```csharp  
[Complete business logic services implementing all scenarios with real functionality]
```

### Additional Files
```csharp
[All other necessary source files for a complete, functional, executable application]
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

APPLICATION STRUCTURE:
- Create complete {build_file} with Maven configuration for Java {java_version}
- Dependencies: {dependencies}
- Create application classes in src/main/java/ directory
- Implement actual business logic for each scenario
- Each scenario gets a complete, functional implementation
- Include proper imports and package declarations
- Create main class with executable main method

IMPLEMENTATION REQUIREMENTS:
- Write REAL, working Java code that implements the described functionality
- Include proper error handling and validation
- Use appropriate Java best practices and design patterns
- Create complete classes with full method implementations
- No placeholder code or TODO comments

EXECUTION REQUIREMENTS:
- **Main.java MUST contain a main method** that demonstrates all scenarios
- Main method should execute each scenario and produce console output
- Use System.out.println() to show progress and results
- Handle exceptions with try-catch blocks and meaningful error messages
- Show completion status at the end

EXAMPLE MAIN CLASS:
```java
package com.{{{{product_name}}}};

public class Main {{
    public static void main(String[] args) {{
        System.out.println("Starting {{{{product_name}}}} Application...");
        
        try {{
            // Execute each scenario with clear output
            System.out.println("\\n=== Executing Scenarios ===");
            
            // Scenario implementation calls here
            executeScenario1();
            executeScenario2();
            // ... more scenarios
            
            System.out.println("\\n=== All Scenarios Completed Successfully ===");
        }} catch (Exception ex) {{
            System.err.println("Error: " + ex.getMessage());
            ex.printStackTrace();
        }}
    }}
    
    // Individual scenario methods with real implementation
    private static void executeScenario1() {{
        System.out.println("Executing Scenario 1...");
        // Real implementation here
        System.out.println("Scenario 1 completed.");
    }}
}}
```

FOCUS: Create a complete, runnable Java application that fully implements all scenarios with real business logic and executable main method.
"""
        
        project_structure = f"""
[Generate ALL necessary files for a complete Java application]
- {build_file} (Maven configuration)
- src/main/java/com/{{{{product_name}}}}/Main.java (main entry point)
- src/main/java/com/{{{{product_name}}}}/models/ (data models)
- src/main/java/com/{{{{product_name}}}}/services/ (business logic)
- src/main/resources/ (configuration files)
- README.md (with run instructions)
"""
        
        file_templates = f"""
### {build_file}
```xml
[Complete pom.xml with all necessary dependencies for Java {java_version}]
```

### src/main/java/com/{{{{product_name}}}}/Main.java
```java
[Complete main class with executable main method that demonstrates all scenarios]
[Must include System.out.println statements showing execution progress]
[Must handle exceptions and show completion status]
```

### Application Classes
```java
[Complete business logic classes implementing all scenarios with real functionality]
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

EXECUTION REQUIREMENTS:
- **main.py MUST contain executable code** that demonstrates all scenarios
- Main execution should run each scenario and produce console output
- Use print() statements to show progress and results
- Handle exceptions with try-except blocks and meaningful error messages
- Show completion status at the end
- Include if __name__ == "__main__": guard

EXAMPLE MAIN EXECUTION:
```python
def main():
    print("Starting {{{{product_name}}}} Application...")
    
    try:
        # Execute each scenario with clear output
        print("\\n=== Executing Scenarios ===")
        
        # Scenario implementation calls here
        execute_scenario_1()
        execute_scenario_2()
        # ... more scenarios
        
        print("\\n=== All Scenarios Completed Successfully ===")
    except Exception as ex:
        print(f"Error: {{ex}}")
        raise

def execute_scenario_1():
    print("Executing Scenario 1...")
    # Real implementation here
    print("Scenario 1 completed.")

if __name__ == "__main__":
    main()
```

FOCUS: Create a complete, runnable Python application that fully implements all scenarios with real business logic and executable main function.
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
[Complete requirements.txt or setup.py with all necessary dependencies for Python {python_version}]
```

### main.py
```python
[Complete main application entry point with executable main function that demonstrates all scenarios]
[Must include print() statements showing execution progress]
[Must handle exceptions and show completion status]
[Must include if __name__ == "__main__": guard]
```

### src/
```python
[Complete application modules implementing all scenarios with real functionality]
```

### models/
```python
[Complete data models and classes required for the application]
```

### services/
```python
[Complete business logic services implementing all scenarios with real functionality]
```

### Additional Files
```python
[All other necessary Python files for a complete, functional, executable application]
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

APPLICATION STRUCTURE:
- Create complete {build_file} with configuration for Node.js {node_version}
- Dependencies: {dependencies}
- Create application modules and files
- Implement actual business logic for each scenario
- Each scenario gets a complete, functional implementation
- Include proper imports/requires
- Create main application entry point

IMPLEMENTATION REQUIREMENTS:
- Write REAL, working JavaScript/Node.js code that implements the described functionality
- Include proper error handling and validation
- Use appropriate JavaScript best practices and design patterns
- Create complete functions and classes with full implementations
- No placeholder code or TODO comments
- Include configuration files and package.json

EXECUTION REQUIREMENTS:
- **main.js or index.js MUST contain executable code** that demonstrates all scenarios
- Main execution should run each scenario and produce console output
- Use console.log() statements to show progress and results
- Handle exceptions with try-catch blocks and meaningful error messages
- Show completion status at the end

EXAMPLE MAIN EXECUTION:
```javascript
async function main() {{
    console.log("Starting {{{{product_name}}}} Application...");
    
    try {{
        // Execute each scenario with clear output
        console.log("\\n=== Executing Scenarios ===");
        
        // Scenario implementation calls here
        await executeScenario1();
        await executeScenario2();
        // ... more scenarios
        
        console.log("\\n=== All Scenarios Completed Successfully ===");
    }} catch (error) {{
        console.error("Error:", error.message);
        process.exit(1);
    }}
}}

async function executeScenario1() {{
    console.log("Executing Scenario 1...");
    // Real implementation here
    console.log("Scenario 1 completed.");
}}

// Run the application
main();
```

FOCUS: Create a complete, runnable JavaScript/Node.js application that fully implements all scenarios with real business logic and executable main function.
"""
        
        project_structure = f"""
[Generate ALL necessary files for a complete JavaScript/Node.js application]
- {build_file} (npm configuration)
- index.js or main.js (main entry point)
- src/ (source code modules)
- models/ (data models)
- services/ (business logic)
- utils/ (utility functions)
- README.md (with run instructions)
"""
        
        file_templates = f"""
### {build_file}
```json
[Complete package.json with all necessary dependencies for Node.js {node_version}]
```

### index.js or main.js
```javascript
[Complete main application entry point with executable main function that demonstrates all scenarios]
[Must include console.log statements showing execution progress]
[Must handle exceptions and show completion status]
```

### Application Modules
```javascript
[Complete business logic modules implementing all scenarios with real functionality]
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

APPLICATION STRUCTURE:
- Create {build_file} file for module management with Go {go_version}
- Create application source files with .go extension
- Implement actual business logic for each scenario
- Each scenario gets a complete, functional implementation
- Include proper package declarations and imports
- Create main package with executable main function

IMPLEMENTATION REQUIREMENTS:
- Write REAL, working Go code that implements the described functionality
- Include proper error handling and validation
- Use appropriate Go best practices and design patterns
- Create complete functions and types with full implementations
- No placeholder code or TODO comments

EXECUTION REQUIREMENTS:
- **main.go MUST contain a main function** that demonstrates all scenarios
- Main execution should run each scenario and produce console output
- Use fmt.Println() statements to show progress and results
- Handle errors with proper Go error handling patterns
- Show completion status at the end

EXAMPLE MAIN EXECUTION:
```go
package main

import (
    "fmt"
    "log"
)

func main() {{
    fmt.Println("Starting {{{{product_name}}}} Application...")
    
    // Execute each scenario with clear output
    fmt.Println("\\n=== Executing Scenarios ===")
    
    // Scenario implementation calls here
    if err := executeScenario1(); err != nil {{
        log.Fatal("Scenario 1 failed:", err)
    }}
    
    if err := executeScenario2(); err != nil {{
        log.Fatal("Scenario 2 failed:", err)
    }}
    
    fmt.Println("\\n=== All Scenarios Completed Successfully ===")
}}

func executeScenario1() error {{
    fmt.Println("Executing Scenario 1...")
    // Real implementation here
    fmt.Println("Scenario 1 completed.")
    return nil
}}
```

FOCUS: Create a complete, runnable Go application that fully implements all scenarios with real business logic and executable main function.
"""
        
        project_structure = f"""
[Generate ALL necessary files for a complete Go application]
- {build_file} (Go module file)
- main.go (main entry point)
- models/ (data structures)
- services/ (business logic)
- utils/ (utility functions)
- README.md (with run instructions)
"""
        
        file_templates = f"""
### {build_file}
```
[Complete go.mod file for Go {go_version}]
```

### main.go
```go
[Complete main application with executable main function that demonstrates all scenarios]
[Must include fmt.Println statements showing execution progress]
[Must handle errors with proper Go error handling patterns]
[Must show completion status]
```

### Application Files
```go
[Complete business logic implementing all scenarios with real functionality]
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

APPLICATION STRUCTURE:
- Create {build_file} for project configuration with Rust {rust_version}
- Create application source files in src/ directory
- Implement actual business logic for each scenario
- Each scenario gets a complete, functional implementation
- Include proper use statements and module declarations
- Create main function in src/main.rs

IMPLEMENTATION REQUIREMENTS:
- Write REAL, working Rust code that implements the described functionality
- Include proper error handling with Result types
- Use appropriate Rust best practices and design patterns
- Create complete functions and structs with full implementations
- No placeholder code or TODO comments
- Follow Rust safety and ownership principles

EXECUTION REQUIREMENTS:
- **src/main.rs MUST contain a main function** that demonstrates all scenarios
- Main execution should run each scenario and produce console output
- Use println!() macro to show progress and results
- Handle errors with proper Result handling and ? operator
- Show completion status at the end

EXAMPLE MAIN EXECUTION:
```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {{
    println!("Starting {{{{product_name}}}} Application...");
    
    // Execute each scenario with clear output
    println!("\\n=== Executing Scenarios ===");
    
    // Scenario implementation calls here
    execute_scenario_1()?;
    execute_scenario_2()?;
    // ... more scenarios
    
    println!("\\n=== All Scenarios Completed Successfully ===");
    Ok(())
}}

fn execute_scenario_1() -> Result<(), Box<dyn std::error::Error>> {{
    println!("Executing Scenario 1...");
    // Real implementation here
    println!("Scenario 1 completed.");
    Ok(())
}}
```

FOCUS: Create a complete, runnable Rust application that fully implements all scenarios with real business logic and executable main function.
"""
        
        project_structure = f"""
[Generate ALL necessary files for a complete Rust application]
- {build_file} (Cargo configuration)
- src/main.rs (main entry point)
- src/lib.rs (library code, if needed)
- src/models/ (data structures)
- src/services/ (business logic)
- README.md (with run instructions)
"""
        
        file_templates = f"""
### {build_file}
```toml
[Complete Cargo.toml with all necessary dependencies for Rust {rust_version}]
```

### src/main.rs
```rust
[Complete main application with executable main function that demonstrates all scenarios]
[Must include println! statements showing execution progress]
[Must handle errors with proper Result handling]
[Must show completion status]
```

### Application Files
```rust
[Complete business logic implementing all scenarios with real functionality]
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
