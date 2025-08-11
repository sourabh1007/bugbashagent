"""
Java specific prompt generation strategy
"""

from typing import Dict, Any
from .base_strategy import PromptGenerationStrategy


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
