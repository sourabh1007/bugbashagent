"""
Rust specific prompt generation strategy
"""

from typing import Dict, Any
from .base_strategy import PromptGenerationStrategy


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
