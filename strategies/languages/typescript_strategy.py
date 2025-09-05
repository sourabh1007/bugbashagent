"""
TypeScript specific prompt generation strategy
"""

from typing import Dict, Any
from .base_strategy import PromptGenerationStrategy


class TypeScriptPromptStrategy(PromptGenerationStrategy):
    """Strategy for generating TypeScript prompts"""
    
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
FRAMEWORK: {framework_name} {framework_version} with TypeScript

APPLICATION STRUCTURE:
- Create complete {build_file} with TypeScript configuration for Node.js {node_version}
- Create tsconfig.json with strict TypeScript configuration
- Dependencies: {dependencies}
- Create application modules and files with proper TypeScript types
- Implement actual business logic for each scenario with type safety
- Each scenario gets a complete, functional implementation with interfaces/types
- Include proper imports and type definitions
- Create main application entry point with full type annotations

IMPLEMENTATION REQUIREMENTS:
- Write REAL, working TypeScript code that implements the described functionality
- Include comprehensive type definitions and interfaces
- Use appropriate TypeScript best practices and design patterns
- Create complete functions and classes with full implementations and type safety
- No placeholder code or TODO comments
- Include configuration files (tsconfig.json, package.json)
- Use strict TypeScript compilation settings

TYPESCRIPT REQUIREMENTS:
- Define interfaces for all data structures
- Use proper type annotations for all functions and variables
- Implement generic types where appropriate
- Use union types, intersection types, and type guards as needed
- Enable strict mode in tsconfig.json
- Use proper async/await typing with Promise<T>

EXECUTION REQUIREMENTS:
- **index.ts or main.ts MUST contain executable code** that demonstrates all scenarios
- Main execution should run each scenario and produce console output
- Use console.log() statements to show progress and results
- Handle exceptions with try-catch blocks and meaningful error messages
- Show completion status at the end
- Compile to JavaScript for execution

EXAMPLE MAIN EXECUTION:
```typescript
interface ScenarioResult {{
    name: string;
    success: boolean;
    data?: any;
    error?: string;
}}

async function main(): Promise<void> {{
    console.log("Starting {{{{product_name}}}} Application...");
    
    try {{
        // Execute each scenario with clear output
        console.log("\\n=== Executing Scenarios ===");
        
        const results: ScenarioResult[] = [];
        
        // Scenario implementation calls here
        results.push(await executeScenario1());
        results.push(await executeScenario2());
        // ... more scenarios
        
        // Display results summary
        console.log("\\n=== Execution Summary ===");
        results.forEach(result => {{
            console.log(`${{result.name}}: ${{result.success ? '✓' : '✗'}}`);
            if (result.error) console.log(`  Error: ${{result.error}}`);
        }});
        
        console.log("\\n=== All Scenarios Completed Successfully ===");
    }} catch (error) {{
        console.error("Error:", (error as Error).message);
        process.exit(1);
    }}
}}

async function executeScenario1(): Promise<ScenarioResult> {{
    console.log("Executing Scenario 1...");
    try {{
        // Real implementation here with proper types
        console.log("Scenario 1 completed.");
        return {{ name: "Scenario 1", success: true }};
    }} catch (error) {{
        return {{ name: "Scenario 1", success: false, error: (error as Error).message }};
    }}
}}

// Run the application
main().catch(console.error);
```

FOCUS: Create a complete, runnable TypeScript application that fully implements all scenarios with real business logic, comprehensive type safety, and executable main function.
"""
        
        project_structure = f"""
[Generate ALL necessary files for a complete TypeScript/Node.js application]
- {build_file} (npm configuration with TypeScript dependencies)
- tsconfig.json (TypeScript compiler configuration)
- index.ts or main.ts (main entry point with types)
- src/ (TypeScript source code modules)
- types/ (custom type definitions)
- models/ (data models with interfaces)
- services/ (business logic with type safety)
- utils/ (utility functions with types)
- dist/ (compiled JavaScript output)
- README.md (with build and run instructions)
"""
        
        file_templates = f"""
### {build_file}
```json
[Complete package.json with TypeScript dependencies for Node.js {node_version}]
[Include typescript, ts-node, @types/node, and build scripts]
```

### tsconfig.json
```json
[Complete TypeScript configuration with strict settings]
[Include proper target, module, and output directory settings]
```

### index.ts or main.ts
```typescript
[Complete main application entry point with full type annotations]
[Must include console.log statements showing execution progress]
[Must handle exceptions with proper typing and show completion status]
[Include proper interfaces and type definitions]
```

### TypeScript Modules
```typescript
[Complete business logic modules implementing all scenarios with comprehensive type safety]
[Include interfaces, types, and proper error handling]
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
