"""
File Processing Integration Package

This package provides utilities for processing various file formats.
"""

from .processor import (
    FileProcessor,
    process_file,
    get_file_dependencies,
    get_supported_extensions
)

__all__ = [
    'FileProcessor',
    'process_file',
    'get_file_dependencies',
    'get_supported_extensions',
]
