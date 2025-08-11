"""
Strategy pattern implementation for language-specific prompt generation.
Refactored into modular language-specific files.
"""

from patterns.language_config import LanguageConfig

# Import all strategies from the languages module
from .languages import (
    PromptGenerationStrategy,
    CSharpPromptStrategy,
    JavaPromptStrategy,
    PythonPromptStrategy,
    JavaScriptPromptStrategy,
    GoPromptStrategy,
    RustPromptStrategy
)

# Re-export all strategies for backward compatibility
__all__ = [
    'PromptGenerationStrategy',
    'CSharpPromptStrategy',
    'JavaPromptStrategy', 
    'PythonPromptStrategy',
    'JavaScriptPromptStrategy',
    'GoPromptStrategy',
    'RustPromptStrategy'
]
