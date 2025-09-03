"""
File Processing Integration

This module provides utilities for processing various file formats.
"""

import os
from typing import Optional, Dict, Any, Union
from pathlib import Path

# Optional imports with fallbacks
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PyPDF2 = None
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    Document = None
    DOCX_AVAILABLE = False


class FileProcessor:
    """Processes various file formats and extracts text content."""
    
    def __init__(self):
        """Initialize file processor."""
        self.supported_formats = {
            '.txt': self._read_text,
            '.md': self._read_text,
            '.py': self._read_text,
            '.js': self._read_text,
            '.ts': self._read_text,
            '.cs': self._read_text,
            '.java': self._read_text,
            '.go': self._read_text,
            '.rs': self._read_text,
            '.json': self._read_text,
            '.yaml': self._read_text,
            '.yml': self._read_text,
            '.xml': self._read_text,
            '.html': self._read_text,
            '.css': self._read_text,
            '.sql': self._read_text,
        }
        
        # Add conditional format support
        if PDF_AVAILABLE:
            self.supported_formats['.pdf'] = self._read_pdf
        
        if DOCX_AVAILABLE:
            self.supported_formats['.docx'] = self._read_docx
    
    def process_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process a file and extract its content.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dict containing file content and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'file_path': str(file_path),
                'error': 'File not found',
                'content': None,
                'file_type': None,
                'size': None
            }
        
        file_extension = file_path.suffix.lower()
        file_size = file_path.stat().st_size
        
        result = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_type': file_extension,
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2)
        }
        
        if file_extension in self.supported_formats:
            try:
                content = self.supported_formats[file_extension](file_path)
                result['content'] = content
                result['char_count'] = len(content) if content else 0
                result['processed'] = True
            except Exception as e:
                result['error'] = f"Error processing file: {str(e)}"
                result['content'] = None
                result['processed'] = False
        else:
            result['error'] = f"Unsupported file format: {file_extension}"
            result['content'] = None
            result['processed'] = False
            result['supported_formats'] = list(self.supported_formats.keys())
        
        return result
    
    def _read_text(self, file_path: Path) -> str:
        """Read text-based files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _read_pdf(self, file_path: Path) -> str:
        """Read PDF files (requires PyPDF2)."""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 not available for PDF processing")
        
        text_content = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
        
        return '\n'.join(text_content)
    
    def _read_docx(self, file_path: Path) -> str:
        """Read DOCX files (requires python-docx)."""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not available for DOCX processing")
        
        doc = Document(str(file_path))
        text_content = []
        
        for paragraph in doc.paragraphs:
            text_content.append(paragraph.text)
        
        return '\n'.join(text_content)
    
    def get_supported_formats(self) -> list:
        """Get list of supported file formats."""
        return list(self.supported_formats.keys())
    
    def is_supported(self, file_path: Union[str, Path]) -> bool:
        """Check if a file format is supported."""
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats


def process_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to process a single file.
    
    Args:
        file_path: Path to the file to process
        
    Returns:
        Dict containing file content and metadata
    """
    processor = FileProcessor()
    return processor.process_file(file_path)


def get_file_dependencies() -> Dict[str, bool]:
    """
    Get status of file processing dependencies.
    
    Returns:
        Dict with dependency availability status
    """
    dependencies = {}
    
    try:
        import PyPDF2
        dependencies['PyPDF2'] = True
    except ImportError:
        dependencies['PyPDF2'] = False
    
    try:
        from docx import Document
        dependencies['python-docx'] = True
    except ImportError:
        dependencies['python-docx'] = False
    
    return dependencies


def get_supported_extensions() -> list:
    """
    Get list of all supported file extensions.
    
    Returns:
        List of supported file extensions
    """
    processor = FileProcessor()
    return processor.get_supported_formats()
