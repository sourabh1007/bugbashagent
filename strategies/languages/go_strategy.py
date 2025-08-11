"""
Go specific prompt generation strategy
"""

from typing import Dict, Any
from .base_strategy import PromptGenerationStrategy


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
            language='{{language}}',
            product_name='{{product_name}}',
            version='{{version}}',
            scenarios='{{scenarios}}',
            setup_info='{{setup_info}}',
            language_specific_instructions=language_instructions,
            project_structure=project_structure,
            file_templates=file_templates,
            build_instructions=build_instructions,
            test_execution=test_execution
        )
