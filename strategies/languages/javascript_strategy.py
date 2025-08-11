"""
JavaScript specific prompt generation strategy
"""

from typing import Dict, Any
from .base_strategy import PromptGenerationStrategy


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
