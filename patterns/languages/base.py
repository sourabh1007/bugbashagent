"""
Base classes for language configuration.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FrameworkConfig:
    """Configuration for a specific testing framework"""
    name: str
    version: str
    dependencies: List[str]
    test_file_pattern: str
    test_method_pattern: str
    example_template: str


@dataclass
class LanguageConfig:
    """Configuration for a specific programming language"""
    name: str
    display_name: str
    file_extensions: List[str]
    framework: FrameworkConfig
    project_structure: Dict[str, str]
    build_file: str
    build_commands: List[str]
    test_commands: List[str]
    imports: List[str]
