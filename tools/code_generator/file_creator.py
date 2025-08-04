"""
File Creator Tool

This module handles creating individual code files with proper extensions and content.
"""

import os
from typing import Optional


class FileCreator:
    """Tool for creating code files with appropriate extensions and directory structure"""
    
    def __init__(self):
        self.extension_map = {
            'csharp': '.cs',
            'c#': '.cs',
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'go': '.go',
            'rust': '.rs',
            'php': '.php',
            'ruby': '.rb',
            'html': '.html',
            'css': '.css',
            'json': '.json',
            'xml': '.xml',
            'yaml': '.yml',
            'yml': '.yml',
            'sql': '.sql',
            'bash': '.sh',
            'powershell': '.ps1',
            'dockerfile': '',
            'makefile': '',
            'gitignore': '.gitignore'
        }
    
    def create_file(self, project_dir: str, filename: str, content: str, language: str = 'text') -> Optional[str]:
        """
        Create a code file with the given content
        
        Args:
            project_dir: Base directory for the project
            filename: Name of the file to create
            content: Content to write to the file
            language: Programming language for determining file extension
            
        Returns:
            Path to the created file, or None if creation failed
        """
        try:
            # Determine file extension if not present
            if '.' not in filename and filename.lower() not in ['dockerfile', 'makefile']:
                ext = self.extension_map.get(language.lower(), '.txt')
                filename = f"{filename}{ext}"
            
            # Handle special cases
            if filename.lower() == 'gitignore':
                filename = '.gitignore'
            
            # Create subdirectories if filename contains path separators
            file_path = os.path.join(project_dir, filename)
            parent_dir = os.path.dirname(file_path)
            
            if parent_dir and parent_dir != project_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            # Write file content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return file_path
            
        except Exception as e:
            print(f"Error creating file {filename}: {str(e)}")
            return None
    
    def create_directory(self, base_dir: str, path: str) -> bool:
        """
        Create a directory structure
        
        Args:
            base_dir: Base directory
            path: Relative path to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            full_path = os.path.join(base_dir, path)
            os.makedirs(full_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {str(e)}")
            return False
    
    def get_language_extension(self, language: str) -> str:
        """Get the file extension for a given language"""
        return self.extension_map.get(language.lower(), '.txt')
    
    def is_valid_filename(self, filename: str) -> bool:
        """Check if a filename is valid"""
        if not filename or filename.strip() == '':
            return False
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            if char in filename:
                return False
        
        # Check for reserved names on Windows
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
        if filename.upper().split('.')[0] in reserved_names:
            return False
        
        return True
