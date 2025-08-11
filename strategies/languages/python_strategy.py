"""
Python specific prompt generation strategy
"""

from typing import Dict, Any
from .base_strategy import PromptGenerationStrategy


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
