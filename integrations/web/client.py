"""
Web Client Integration

This module provides web content fetching utilities.
"""

import requests
from typing import Optional, Dict, Any
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BeautifulSoup = None
    BS4_AVAILABLE = False


class WebClient:
    """Simple web client for fetching content."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize web client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BugBashAgent/1.0 (Web Content Analyzer)'
        })
    
    def fetch_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dict containing content, status, and metadata
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            result = {
                'url': url,
                'status_code': response.status_code,
                'content_type': content_type,
                'raw_content': response.text,
                'headers': dict(response.headers)
            }
            
            # Parse HTML content if BeautifulSoup is available
            if BS4_AVAILABLE and 'html' in content_type:
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    result['title'] = soup.title.string if soup.title else 'No title'
                    result['text_content'] = soup.get_text(strip=True)
                    result['parsed'] = True
                except Exception as e:
                    result['parse_error'] = str(e)
                    result['text_content'] = response.text
                    result['parsed'] = False
            else:
                result['text_content'] = response.text
                result['parsed'] = False
                if not BS4_AVAILABLE and 'html' in content_type:
                    result['warning'] = 'BeautifulSoup not available for HTML parsing'
            
            return result
            
        except requests.RequestException as e:
            return {
                'url': url,
                'error': str(e),
                'status_code': None,
                'content_type': None,
                'raw_content': None,
                'text_content': None
            }
    
    def fetch_multiple_urls(self, urls: list) -> Dict[str, Any]:
        """
        Fetch content from multiple URLs.
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            Dict mapping URLs to their fetch results
        """
        results = {}
        for url in urls:
            results[url] = self.fetch_url(url)
        return results


def fetch_url_content(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Convenience function to fetch content from a single URL.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Dict containing content and metadata
    """
    client = WebClient(timeout=timeout)
    return client.fetch_url(url)


def is_web_content_available() -> bool:
    """
    Check if web content fetching capabilities are available.
    
    Returns:
        bool: True if requests is available, False otherwise
    """
    try:
        import requests
        return True
    except ImportError:
        return False


def get_web_dependencies() -> Dict[str, bool]:
    """
    Get status of web-related dependencies.
    
    Returns:
        Dict with dependency availability status
    """
    dependencies = {}
    
    try:
        import requests
        dependencies['requests'] = True
    except ImportError:
        dependencies['requests'] = False
    
    try:
        from bs4 import BeautifulSoup
        dependencies['beautifulsoup4'] = True
    except ImportError:
        dependencies['beautifulsoup4'] = False
    
    return dependencies
