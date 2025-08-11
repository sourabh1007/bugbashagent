"""
C# specific prompt generation strategy
"""

from typing import Dict, Any
from .base_strategy import PromptGenerationStrategy


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
