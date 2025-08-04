"""
Code Block Extractor Tool

This module handles extracting code blocks from markdown-formatted LLM output.
"""

import re
from typing import List, Tuple


class CodeBlockExtractor:
    """Tool for extracting code blocks from markdown-formatted content"""
    
    def __init__(self):
        # Pattern to match code blocks with filename headers
        self.code_block_pattern = r'###?\s*([^\n]+)\s*\n```(\w+)?\s*\n(.*?)\n```'
        
        # Pattern to match inline code files
        self.inline_code_pattern = r'`([^`]+\.[a-zA-Z0-9]+)`'
        
        # Invalid filename patterns to skip
        self.invalid_filenames = {
            'file contents', 'filename1', 'filename2', 'example', 'sample',
            'code', 'output', 'result', 'content'
        }
    
    def extract_code_blocks(self, content: str) -> List[Tuple[str, str, str]]:
        """
        Extract code blocks from markdown-formatted content
        
        Args:
            content: Markdown content containing code blocks
            
        Returns:
            List of tuples (filename, content, language)
        """
        code_blocks = []
        
        # Find all code blocks with headers
        matches = re.findall(self.code_block_pattern, content, re.DOTALL | re.MULTILINE)
        
        for match in matches:
            filename = match[0].strip()
            language = match[1] if match[1] else 'text'
            code_content = match[2].strip()
            
            # Clean filename (remove markdown formatting)
            filename = self._clean_filename(filename)
            
            # Skip if it's not a valid filename
            if not self._is_valid_filename(filename):
                continue
                
            code_blocks.append((filename, code_content, language))
        
        return code_blocks
    
    def extract_file_references(self, content: str) -> List[str]:
        """
        Extract file references from content (like `filename.ext`)
        
        Args:
            content: Text content to search
            
        Returns:
            List of referenced filenames
        """
        matches = re.findall(self.inline_code_pattern, content)
        return [match for match in matches if self._is_valid_filename(match)]
    
    def extract_class_definitions(self, content: str, language: str) -> List[Tuple[str, str]]:
        """
        Extract class definitions from generated content
        
        Args:
            content: Code content
            language: Programming language
            
        Returns:
            List of tuples (class_name, class_content)
        """
        classes = []
        
        if language.lower() in ['c#', 'csharp']:
            # C# class pattern
            pattern = r'((?:public\s+)?class\s+(\w+).*?^})'
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            classes = [(match[1], match[0]) for match in matches]
            
        elif language.lower() == 'python':
            # Python class pattern
            pattern = r'(class\s+(\w+)(?:\([^)]*\))?:.*?)(?=class\s+\w+|def\s+\w+|$)'
            matches = re.findall(pattern, content, re.DOTALL)
            classes = [(match[1], match[0]) for match in matches]
            
        elif language.lower() in ['javascript', 'typescript']:
            # JavaScript/TypeScript class pattern
            pattern = r'(class\s+(\w+).*?^})'
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            classes = [(match[1], match[0]) for match in matches]
        
        return classes
    
    def extract_function_definitions(self, content: str, language: str) -> List[Tuple[str, str]]:
        """
        Extract function definitions from generated content
        
        Args:
            content: Code content
            language: Programming language
            
        Returns:
            List of tuples (function_name, function_content)
        """
        functions = []
        
        if language.lower() in ['c#', 'csharp']:
            # C# method pattern
            pattern = r'((?:public|private|protected|internal)?\s*(?:static\s+)?(?:async\s+)?\w+\s+(\w+)\s*\([^)]*\)\s*{.*?^})'
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            functions = [(match[1], match[0]) for match in matches]
            
        elif language.lower() == 'python':
            # Python function pattern
            pattern = r'(def\s+(\w+)\([^)]*\):.*?)(?=def\s+\w+|class\s+\w+|$)'
            matches = re.findall(pattern, content, re.DOTALL)
            functions = [(match[1], match[0]) for match in matches]
            
        elif language.lower() in ['javascript', 'typescript']:
            # JavaScript/TypeScript function pattern
            pattern = r'(function\s+(\w+)\s*\([^)]*\)\s*{.*?^})'
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            functions = [(match[1], match[0]) for match in matches]
        
        return functions
    
    def _clean_filename(self, filename: str) -> str:
        """Clean and normalize filename"""
        # Remove markdown formatting
        filename = re.sub(r'[`*#\[\]]', '', filename).strip()
        
        # Remove common prefixes
        prefixes_to_remove = ['file:', 'filename:', 'name:', 'create:', 'generate:']
        for prefix in prefixes_to_remove:
            if filename.lower().startswith(prefix):
                filename = filename[len(prefix):].strip()
        
        return filename
    
    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename is valid and not in the skip list"""
        if not filename or filename.strip() == '':
            return False
        
        # Convert to lowercase for comparison
        filename_lower = filename.lower()
        
        # Skip common placeholder names
        if filename_lower in self.invalid_filenames:
            return False
        
        # Must contain at least one letter or number
        if not re.search(r'[a-zA-Z0-9]', filename):
            return False
        
        return True
    
    def extract_project_dependencies(self, content: str, language: str) -> List[str]:
        """
        Extract project dependencies from generated content
        
        Args:
            content: Generated content
            language: Programming language
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        if language.lower() in ['c#', 'csharp']:
            # Look for PackageReference in csproj content
            pattern = r'<PackageReference\s+Include="([^"]+)"'
            dependencies.extend(re.findall(pattern, content))
            
            # Look for using statements
            using_pattern = r'using\s+([^;]+);'
            using_statements = re.findall(using_pattern, content)
            dependencies.extend([u.strip() for u in using_statements if not u.startswith('System')])
            
        elif language.lower() == 'python':
            # Look for import statements
            import_pattern = r'(?:from\s+(\w+)|import\s+(\w+))'
            matches = re.findall(import_pattern, content)
            for match in matches:
                dep = match[0] if match[0] else match[1]
                if dep and dep not in ['os', 'sys', 're', 'json', 'datetime']:
                    dependencies.append(dep)
        
        elif language.lower() in ['javascript', 'typescript']:
            # Look for require/import statements
            require_pattern = r'(?:require\([\'"]([^\'"]+)[\'"]\)|import.*from\s+[\'"]([^\'"]+)[\'"])'
            matches = re.findall(require_pattern, content)
            for match in matches:
                dep = match[0] if match[0] else match[1]
                if dep and not dep.startswith('./') and not dep.startswith('../'):
                    dependencies.append(dep)
        
        return list(set(dependencies))  # Remove duplicates
