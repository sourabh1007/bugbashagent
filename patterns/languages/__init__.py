"""
Language-specific configurations for test project generation.
Each language has its own configuration file.
"""

from .base import FrameworkConfig, LanguageConfig
from .csharp_config import get_csharp_config
from .java_config import get_java_config
from .python_config import get_python_config
from .javascript_config import get_javascript_config
from .go_config import get_go_config
from .rust_config import get_rust_config

__all__ = [
    'FrameworkConfig',
    'LanguageConfig',
    'get_csharp_config',
    'get_java_config', 
    'get_python_config',
    'get_javascript_config',
    'get_go_config',
    'get_rust_config'
]
