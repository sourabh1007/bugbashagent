"""
Factory pattern for creating language-specific prompt generation strategies.
"""

from typing import Dict, Optional
from patterns.language_config import LanguageConfigManager, LanguageConfig
from strategies.prompt_strategies import (
    PromptGenerationStrategy,
    CSharpPromptStrategy,
    JavaPromptStrategy,
    PythonPromptStrategy,
    JavaScriptPromptStrategy,
    GoPromptStrategy,
    RustPromptStrategy
)


class PromptStrategyFactory:
    """Factory for creating prompt generation strategies"""
    
    def __init__(self):
        self.config_manager = LanguageConfigManager()
        self._strategy_mapping = {
            'csharp': CSharpPromptStrategy,
            'c#': CSharpPromptStrategy,
            'java': JavaPromptStrategy,
            'python': PythonPromptStrategy,
            'javascript': JavaScriptPromptStrategy,
            'node.js': JavaScriptPromptStrategy,
            'js': JavaScriptPromptStrategy,
            'go': GoPromptStrategy,
            'rust': RustPromptStrategy
        }
    
    def create_strategy(self, language: str) -> Optional[PromptGenerationStrategy]:
        """Create a prompt generation strategy for the specified language"""
        language_key = language.lower()
        
        if language_key not in self._strategy_mapping:
            return None
        
        config = self.config_manager.get_config(language_key)
        if not config:
            return None
        
        strategy_class = self._strategy_mapping[language_key]
        return strategy_class(config)
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return self.config_manager.get_supported_languages()
    
    def get_all_language_aliases(self) -> list:
        """Get all language names including aliases"""
        return self.config_manager.get_all_language_aliases()


class GenericPromptStrategy(PromptGenerationStrategy):
    """Generic strategy for unsupported languages"""
    
    def __init__(self, language: str):
        self.language = language
        # Create a minimal config for generic use
        from patterns.language_config import LanguageConfig, FrameworkConfig
        
        generic_framework = FrameworkConfig(
            name="Generic",
            version="latest",
            dependencies=[],
            test_file_pattern="test_{category}.ext",
            test_method_pattern="test_{scenario}",
            example_template="\n// Generic test example\n"
        )
        
        generic_config = LanguageConfig(
            name=language,
            display_name=language.upper(),
            file_extensions=[".txt"],
            framework=generic_framework,
            project_structure={"source": "src/", "tests": "tests/", "config": "./"},
            build_file="build.config",
            build_commands=["build command"],
            test_commands=["test command"],
            imports=[]
        )
        
        super().__init__(generic_config)
    
    def generate_prompt(self, context: Dict) -> str:
        return f"""
You are a test project generation agent for {self.language} language.

Product Name: {{product_name}}
Version: {{version}}

Test Scenarios to implement:
{{scenarios}}

Project Setup Information:
{{setup_info}}

Your task is to generate a COMPLETE, buildable {self.language} test project with:
- Functional test code implementation based on the given scenarios
- Proper project structure and naming conventions for {self.language}
- Complete, compilation-ready code

Generate a complete test project structure with all necessary files and test implementations.

RESPONSE FORMAT:
## Test Project Structure
[List ALL files and directories needed]

## Complete Test File Contents
[All necessary files with complete content]

## Build Instructions
[Step-by-step build commands for {self.language}]

## Test Execution
[Commands to run all tests in {self.language}]
"""
