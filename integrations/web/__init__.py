"""
Web Integration Package

This package provides web content fetching utilities.
"""

from .client import (
    WebClient,
    fetch_url_content,
    is_web_content_available,
    get_web_dependencies
)

__all__ = [
    'WebClient',
    'fetch_url_content',
    'is_web_content_available',
    'get_web_dependencies',
]
