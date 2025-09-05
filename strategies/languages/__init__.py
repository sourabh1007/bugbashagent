"""
Language-specific prompt strategies module
"""

from .base_strategy import PromptGenerationStrategy
from .csharp_strategy import CSharpPromptStrategy
from .java_strategy import JavaPromptStrategy
from .python_strategy import PythonPromptStrategy
from .javascript_strategy import JavaScriptPromptStrategy
from .typescript_strategy import TypeScriptPromptStrategy
from .go_strategy import GoPromptStrategy
from .rust_strategy import RustPromptStrategy

__all__ = [
    'PromptGenerationStrategy',
    'CSharpPromptStrategy',
    'JavaPromptStrategy', 
    'PythonPromptStrategy',
    'JavaScriptPromptStrategy',
    'TypeScriptPromptStrategy',
    'GoPromptStrategy',
    'RustPromptStrategy'
]
