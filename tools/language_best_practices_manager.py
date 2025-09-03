"""
Simple language-specific best practices manager.
"""

import os


class LanguageBestPracticesManager:
    """Simple manager for language-specific best practices."""
    
    def __init__(self):
        self.base_path = "prompts/code_generator/language_best_practices"
        self.compilation_checklist_base_path = "prompts/code_generator/language_compilation_checklists"
        self.product_specific_base_path = "prompts/code_generator/product_specific"
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
        self._product_file_mapping = {
            # Legacy fallback files for products without language-specific guidance
            # Note: Cosmos DB now uses language-specific files in _product_language_mapping
        }
        self._product_language_mapping = {
            'cosmos db': {
                'c#': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'csharp': 'cosmos_db/csharp_cosmos_guidance.prompty',
                '.net': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'python': 'cosmos_db/python_cosmos_guidance.prompty',
                'javascript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'typescript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'js': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'ts': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'java': 'cosmos_db/java_cosmos_guidance.prompty',
                'go': 'cosmos_db/go_cosmos_guidance.prompty',
                'golang': 'cosmos_db/go_cosmos_guidance.prompty',
                'rust': 'cosmos_db/rust_cosmos_guidance.prompty'
            },
            'cosmosdb': {
                'c#': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'csharp': 'cosmos_db/csharp_cosmos_guidance.prompty',
                '.net': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'python': 'cosmos_db/python_cosmos_guidance.prompty',
                'javascript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'typescript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'js': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'ts': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'java': 'cosmos_db/java_cosmos_guidance.prompty',
                'go': 'cosmos_db/go_cosmos_guidance.prompty',
                'golang': 'cosmos_db/go_cosmos_guidance.prompty',
                'rust': 'cosmos_db/rust_cosmos_guidance.prompty'
            },
            'cosmos': {
                'c#': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'csharp': 'cosmos_db/csharp_cosmos_guidance.prompty',
                '.net': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'python': 'cosmos_db/python_cosmos_guidance.prompty',
                'javascript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'typescript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'js': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'ts': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'java': 'cosmos_db/java_cosmos_guidance.prompty',
                'go': 'cosmos_db/go_cosmos_guidance.prompty',
                'golang': 'cosmos_db/go_cosmos_guidance.prompty',
                'rust': 'cosmos_db/rust_cosmos_guidance.prompty'
            },
            'azure cosmos db': {
                'c#': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'csharp': 'cosmos_db/csharp_cosmos_guidance.prompty',
                '.net': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'python': 'cosmos_db/python_cosmos_guidance.prompty',
                'javascript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'typescript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'js': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'ts': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'java': 'cosmos_db/java_cosmos_guidance.prompty',
                'go': 'cosmos_db/go_cosmos_guidance.prompty',
                'golang': 'cosmos_db/go_cosmos_guidance.prompty',
                'rust': 'cosmos_db/rust_cosmos_guidance.prompty'
            },
            'azure cosmosdb': {
                'c#': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'csharp': 'cosmos_db/csharp_cosmos_guidance.prompty',
                '.net': 'cosmos_db/csharp_cosmos_guidance.prompty',
                'python': 'cosmos_db/python_cosmos_guidance.prompty',
                'javascript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'typescript': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'js': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'ts': 'cosmos_db/javascript_cosmos_guidance.prompty',
                'java': 'cosmos_db/java_cosmos_guidance.prompty',
                'go': 'cosmos_db/go_cosmos_guidance.prompty',
                'golang': 'cosmos_db/go_cosmos_guidance.prompty',
                'rust': 'cosmos_db/rust_cosmos_guidance.prompty'
            }
        }
        self._compilation_checklist_file_mapping = {
            'c#': 'csharp_compilation_checklist.prompty',
            'csharp': 'csharp_compilation_checklist.prompty',
            '.net': 'csharp_compilation_checklist.prompty',
            'python': 'python_compilation_checklist.prompty',
            'javascript': 'javascript_compilation_checklist.prompty',
            'typescript': 'javascript_compilation_checklist.prompty',
            'js': 'javascript_compilation_checklist.prompty',
            'ts': 'javascript_compilation_checklist.prompty',
            'java': 'java_compilation_checklist.prompty',
            'go': 'go_compilation_checklist.prompty',
            'golang': 'go_compilation_checklist.prompty',
            'rust': 'rust_compilation_checklist.prompty'
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
    
    def _normalize_product_name(self, product_name: str) -> str:
        """Normalize product name to match mapping keys."""
        name = product_name.lower().strip()
        
        # Handle Cosmos DB variations
        if 'cosmos' in name and 'db' in name:
            return 'cosmos db'
        if 'cosmosdb' in name:
            return 'cosmos db'
            
        # Add other product normalizations here as needed
        # e.g., if 'storage' in name: return 'azure storage'
        
        return name
    
    def get_product_specific_guidance(self, product_name: str, language: str = "", version: str = "") -> str:
        """Get product-specific guidance from language-specific prompty files."""
        # Normalize product name to match mapping keys
        product_key = self._normalize_product_name(product_name)
        language_key = language.lower().strip() if language else ""
        
        # First try to get language-specific product guidance
        if language_key and product_key in self._product_language_mapping:
            language_mapping = self._product_language_mapping[product_key]
            prompty_file = language_mapping.get(language_key)
            
            if prompty_file:
                try:
                    # Read the language-specific prompty file
                    prompty_path = f"{self.product_specific_base_path}/{prompty_file}"
                    
                    # Check if file exists
                    if os.path.exists(prompty_path):
                        # Read the file content
                        with open(prompty_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract the content after the YAML front matter
                        parts = content.split('---')
                        if len(parts) >= 3:
                            # Get the template content (after the second ---)
                            template_content = '---'.join(parts[2:]).strip()
                            
                            # Replace placeholders if provided
                            if language:
                                template_content = template_content.replace('{{language}}', language)
                            if version:
                                template_content = template_content.replace('{{version}}', version)
                            
                            return template_content
                
                except Exception as e:
                    print(f"Warning: Could not load language-specific product guidance for {product_name} + {language}: {e}")
        
        # Fallback to generic product guidance (for backward compatibility)
        prompty_file = self._product_file_mapping.get(product_key)
        if prompty_file:
            try:
                # Read the prompty file content directly
                prompty_path = f"{self.product_specific_base_path}/{prompty_file}"
                
                # Check if file exists
                if not os.path.exists(prompty_path):
                    return self._get_generic_product_guidance(product_name)
                
                # Read the file content
                with open(prompty_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract the content after the YAML front matter
                parts = content.split('---')
                if len(parts) >= 3:
                    # Get the template content (after the second ---)
                    template_content = '---'.join(parts[2:]).strip()
                    
                    # Replace placeholders if provided
                    if language:
                        template_content = template_content.replace('{{language}}', language)
                    if version:
                        template_content = template_content.replace('{{version}}', version)
                    
                    return template_content
                else:
                    return self._get_generic_product_guidance(product_name)
                
            except Exception as e:
                print(f"Warning: Could not load product guidance for {product_name}: {e}")
        
        # Final fallback to generic guidance
        return self._get_generic_product_guidance(product_name)
    
    def _get_generic_product_guidance(self, product_name: str) -> str:
        """Fallback generic product guidance for unsupported products."""
        return f"""**{product_name} SDK Guidance:**
- Verify all methods and classes exist in the official {product_name} documentation
- Use appropriate SDK initialization patterns
- Handle product-specific exceptions and error codes
- Follow recommended authentication and connection patterns
- Use proper async/sync patterns as required by the SDK
- Include all necessary dependencies and imports
- Test common CRUD operations and error scenarios
- Follow product-specific best practices and conventions
"""
    
    def get_language_compilation_checklist(self, language: str) -> str:
        """Get language-specific compilation checklist from prompty file."""
        language_key = language.lower().strip()
        
        # Get the appropriate compilation checklist prompty file
        prompty_file = self._compilation_checklist_file_mapping.get(language_key)
        if not prompty_file:
            return self._get_generic_compilation_checklist(language)
        
        try:
            # Read the prompty file content directly
            prompty_path = f"{self.compilation_checklist_base_path}/{prompty_file}"
            
            # Check if file exists
            if not os.path.exists(prompty_path):
                return self._get_generic_compilation_checklist(language)
            
            # Read the file content
            with open(prompty_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the content after the YAML front matter
            parts = content.split('---')
            if len(parts) >= 3:
                # Get the template content (after the second ---)
                template_content = '---'.join(parts[2:]).strip()
                
                # Replace the language placeholder if needed
                template_content = template_content.replace('{{language}}', language)
                
                return template_content
            else:
                return self._get_generic_compilation_checklist(language)
            
        except Exception as e:
            print(f"Warning: Could not load compilation checklist for {language}: {e}")
            return self._get_generic_compilation_checklist(language)
    
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
    
    def _get_generic_compilation_checklist(self, language: str) -> str:
        """Fallback generic compilation checklist for unsupported languages."""
        return f"""**{language} Compilation Checklist:**
✅ **{language}**: Proper syntax, imports, error handling, type safety, and language-specific conventions
"""
