"""
Project Structure Parser Tool

This module handles parsing and creating project directory structures from LLM output.
"""

import os
import re
from typing import List, Dict, Optional


class ProjectStructureParser:
    """Tool for parsing and creating project directory structures"""
    
    def __init__(self):
        self.structure_markers = [
            r'##\s*Project\s*Structure\s*\n',
            r'##\s*File\s*Structure\s*\n',
            r'##\s*Directory\s*Structure\s*\n',
            r'##\s*Folder\s*Structure\s*\n'
        ]
    
    def extract_project_structure(self, content: str) -> List[str]:
        """
        Extract project structure from LLM output
        
        Args:
            content: Generated content containing project structure
            
        Returns:
            List of file and directory paths
        """
        structure = []
        
        # Try each structure marker pattern
        for marker_pattern in self.structure_markers:
            match = re.search(marker_pattern + r'(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
            if match:
                structure_text = match.group(1)
                structure = self._parse_structure_text(structure_text)
                if structure:  # If we found a structure, use it
                    break
        
        return structure
    
    def _parse_structure_text(self, structure_text: str) -> List[str]:
        """Parse structure text into a list of paths"""
        paths = []
        lines = structure_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are clearly not paths
            if line.startswith('[') or line.startswith('(') or line.lower().startswith('note'):
                continue
            
            # Extract path from various formats
            path = self._extract_path_from_line(line)
            if path:
                paths.append(path)
        
        return paths
    
    def _extract_path_from_line(self, line: str) -> Optional[str]:
        """Extract file/directory path from a line"""
        # Remove common prefixes and formatting
        line = re.sub(r'^[-*+•]\s*', '', line)  # Remove list markers
        line = re.sub(r'^\d+\.\s*', '', line)   # Remove numbered list markers
        line = re.sub(r'`([^`]+)`', r'\1', line)  # Remove backticks
        line = line.strip()
        
        # Skip empty lines or lines without path-like content
        if not line or len(line) < 2:
            return None
        
        # Look for path patterns
        path_patterns = [
            r'^([^/\\\s]+(?:[/\\][^/\\\s]*)*[/\\]?)$',  # Simple path
            r'^([^/\\\s]+\.[a-zA-Z0-9]+)$',              # Filename with extension
            r'^([a-zA-Z0-9_.-]+[/\\]?)$',                # Directory name
        ]
        
        for pattern in path_patterns:
            match = re.match(pattern, line)
            if match:
                path = match.group(1).strip()
                if self._is_valid_path(path):
                    return path
        
        return None
    
    def _is_valid_path(self, path: str) -> bool:
        """Check if a path is valid"""
        if not path:
            return False
        
        # Skip paths that are clearly descriptions
        description_keywords = ['list', 'files', 'folders', 'create', 'contains', 'include']
        if any(keyword in path.lower() for keyword in description_keywords):
            return False
        
        # Skip very long paths (likely descriptions)
        if len(path) > 100:
            return False
        
        # Must contain valid path characters
        if not re.match(r'^[a-zA-Z0-9_./\\-]+$', path):
            return False
        
        return True
    
    def create_directory_structure(self, base_dir: str, structure: List[str]) -> Dict[str, str]:
        """
        Create directory structure based on parsed information
        
        Args:
            base_dir: Base directory to create structure in
            structure: List of paths to create
            
        Returns:
            Dictionary mapping path types to created paths
        """
        created_paths = {}
        directories_created = []
        files_created = []
        
        for path in structure:
            full_path = os.path.join(base_dir, path)
            
            try:
                # Determine if it's a directory or file
                if self._is_directory_path(path):
                    os.makedirs(full_path, exist_ok=True)
                    directories_created.append(full_path)
                else:
                    # It's a file - create parent directories if needed
                    parent_dir = os.path.dirname(full_path)
                    if parent_dir and parent_dir != base_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                    
                    # Create empty file if it doesn't exist
                    if not os.path.exists(full_path):
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write('')  # Create empty file
                        files_created.append(full_path)
                        
            except Exception as e:
                print(f"Error creating {path}: {str(e)}")
        
        created_paths['directories'] = directories_created
        created_paths['files'] = files_created
        return created_paths
    
    def _is_directory_path(self, path: str) -> bool:
        """Determine if a path represents a directory"""
        # Ends with / or \ 
        if path.endswith('/') or path.endswith('\\'):
            return True
        
        # No file extension and not obviously a file
        if '.' not in os.path.basename(path):
            return True
        
        # Common directory names
        directory_names = [
            'src', 'test', 'tests', 'bin', 'obj', 'dist', 'build', 'docs',
            'assets', 'static', 'public', 'private', 'lib', 'libs', 'vendor',
            'node_modules', 'packages', 'components', 'services', 'models',
            'views', 'controllers', 'utils', 'helpers', 'config', 'scripts'
        ]
        
        if os.path.basename(path).lower() in directory_names:
            return True
        
        return False
    
    def normalize_structure(self, structure: List[str]) -> List[str]:
        """
        Normalize and clean up the structure list
        
        Args:
            structure: Raw structure list
            
        Returns:
            Cleaned and normalized structure list
        """
        normalized = []
        seen = set()
        
        for path in structure:
            # Normalize path separators
            normalized_path = path.replace('\\', '/')
            
            # Remove duplicate slashes
            normalized_path = re.sub(r'/+', '/', normalized_path)
            
            # Remove leading/trailing slashes
            normalized_path = normalized_path.strip('/')
            
            # Skip if we've already seen this path
            if normalized_path in seen or not normalized_path:
                continue
            
            seen.add(normalized_path)
            normalized.append(normalized_path)
        
        # Sort to ensure directories are created before files
        normalized.sort(key=lambda x: (x.count('/'), x))
        
        return normalized
    
    def get_project_metadata(self, structure: List[str]) -> Dict[str, any]:
        """
        Extract metadata about the project from its structure
        
        Args:
            structure: Project structure
            
        Returns:
            Dictionary with project metadata
        """
        metadata = {
            'total_items': len(structure),
            'directories': 0,
            'files': 0,
            'languages': set(),
            'has_tests': False,
            'has_docs': False,
            'frameworks': set()
        }
        
        for path in structure:
            if self._is_directory_path(path):
                metadata['directories'] += 1
                
                # Check for common patterns
                path_lower = path.lower()
                if 'test' in path_lower:
                    metadata['has_tests'] = True
                if 'doc' in path_lower or 'readme' in path_lower:
                    metadata['has_docs'] = True
                    
            else:
                metadata['files'] += 1
                
                # Detect language by file extension
                ext = os.path.splitext(path)[1].lower()
                if ext == '.cs':
                    metadata['languages'].add('C#')
                    metadata['frameworks'].add('.NET')
                elif ext == '.py':
                    metadata['languages'].add('Python')
                elif ext == '.js':
                    metadata['languages'].add('JavaScript')
                    metadata['frameworks'].add('Node.js')
                elif ext == '.ts':
                    metadata['languages'].add('TypeScript')
                elif ext == '.java':
                    metadata['languages'].add('Java')
                elif ext == '.cpp' or ext == '.cc':
                    metadata['languages'].add('C++')
                elif ext == '.c':
                    metadata['languages'].add('C')
                elif ext == '.go':
                    metadata['languages'].add('Go')
                elif ext == '.rs':
                    metadata['languages'].add('Rust')
        
        # Convert sets to lists for JSON serialization
        metadata['languages'] = list(metadata['languages'])
        metadata['frameworks'] = list(metadata['frameworks'])
        
        return metadata
