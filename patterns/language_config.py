"""
Language-specific configuration manager for test project generation.
Uses modular language configurations from the languages directory.
"""

from typing import Dict, Optional, List
from .languages.base import LanguageConfig
from .languages import (
    get_csharp_config,
    get_java_config,
    get_python_config,
    get_javascript_config,
    get_typescript_config,
    get_go_config,
    get_rust_config
)


class LanguageConfigManager:
    """Manages language-specific configurations using modular approach"""
    
    def __init__(self):
        self._configs = self._initialize_configs()
    
    def _initialize_configs(self) -> Dict[str, LanguageConfig]:
        """Initialize all language configurations"""
        configs = {}
        
        # Load configurations from individual modules
        configs['csharp'] = get_csharp_config()
        configs['java'] = get_java_config()
        configs['python'] = get_python_config()
        configs['javascript'] = get_javascript_config()
        configs['typescript'] = get_typescript_config()
        configs['go'] = get_go_config()
        configs['rust'] = get_rust_config()
        
        # Add aliases
        configs['c#'] = configs['csharp']
        configs['node.js'] = configs['javascript']
        configs['js'] = configs['javascript']
        configs['ts'] = configs['typescript']
        
        return configs
    
    def get_config(self, language: str) -> Optional[LanguageConfig]:
        """Get configuration for a specific language"""
        return self._configs.get(language.lower())
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(set(self._configs.keys()) - {'c#', 'node.js', 'js', 'ts'})  # Remove aliases
    
    def get_all_language_aliases(self) -> List[str]:
        """Get all language names including aliases"""
        return list(self._configs.keys())
