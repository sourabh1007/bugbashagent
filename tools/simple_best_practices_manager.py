"""
Simple language-specific best practices manager.
"""

import os


class SimpleBestPracticesManager:
    """Simple manager for language-specific best practices."""
    
    def __init__(self):
        self.base_path = "prompts/code_generator/language_best_practices"
        self._language_file_mapping = {
            'c#': 'csharp_best_practices.prompty',
            'csharp': 'csharp_best_practices.prompty',
            '.net': 'csharp_best_practices.prompty',
            'python': 'python_best_practices.prompty',
            'javascript': 'javascript_best_practices.prompty',
            'typescript': 'javascript_best_practices.prompty',
            'js': 'javascript_best_practices.prompty',
            'ts': 'javascript_best_practices.prompty',
            'java': 'java_best_practices.prompty',
            'go': 'go_best_practices.prompty',
            'golang': 'go_best_practices.prompty',
            'rust': 'rust_best_practices.prompty'
        }
    
    def get_language_best_practices(self, language: str, testing_framework: str = "standard") -> str:
        """Get language-specific best practices from prompty files."""
        language_key = language.lower().strip()
        
        # Get the appropriate prompty file
        prompty_file = self._language_file_mapping.get(language_key)
        if not prompty_file:
            return self._get_generic_best_practices(language, testing_framework)
        
        try:
            # Read the prompty file content directly
            prompty_path = f"{self.base_path}/{prompty_file}"
            
            # Check if file exists
            if not os.path.exists(prompty_path):
                return self._get_generic_best_practices(language, testing_framework)
            
            # Read the file content
            with open(prompty_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the content after the YAML front matter
            parts = content.split('---')
            if len(parts) >= 3:
                # Get the template content (after the second ---)
                template_content = '---'.join(parts[2:]).strip()
                
                # Replace the testing_framework placeholder
                template_content = template_content.replace('{{testing_framework}}', testing_framework)
                
                return template_content
            else:
                return self._get_generic_best_practices(language, testing_framework)
            
        except Exception as e:
            print(f"Warning: Could not load best practices for {language}: {e}")
            return self._get_generic_best_practices(language, testing_framework)
    
    def _get_generic_best_practices(self, language: str, testing_framework: str) -> str:
        """Fallback generic best practices for unsupported languages."""
        return f"""**{language} Best Practices:**
1. Follow language-specific syntax and conventions
2. Handle errors and exceptions appropriately
3. Use proper imports and dependencies
4. Initialize variables before use
5. Follow naming conventions
6. Use appropriate data types and structures
7. Handle memory management (if applicable)
8. Implement proper testing patterns
9. Use version control best practices
10. Include proper documentation

**Testing Framework Guidelines:**
Use {testing_framework} with proper test structure, assertions, and lifecycle management.
"""
