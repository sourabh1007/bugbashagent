"""
Base strategy class for language-specific prompt generation
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
