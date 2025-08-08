"""
Compilation Checker Tool

Validates generated code for compilation errors and provides detailed error analysis and fixes.
"""

import os
import subprocess
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class CompilationChecker:
    """Tool for checking and fixing compilation errors in generated code"""
    
    def __init__(self):
        self.compile_commands = {
            'csharp': {
                'command': ['dotnet', 'build', '--verbosity', 'detailed'],
                'error_patterns': [
                    r'error CS(\d+): (.+?) \[(.+?)\]',
                    r'(.+?)\((\d+),(\d+)\): error CS(\d+): (.+)',
                    r'Build FAILED\.'
                ],
                'warning_patterns': [
                    r'warning CS(\d+): (.+?) \[(.+?)\]',
                    r'(.+?)\((\d+),(\d+)\): warning CS(\d+): (.+)'
                ]
            },
            'java': {
                'command': ['mvn', 'compile', '-X'],
                'error_patterns': [
                    r'\[ERROR\] (.+?):(\d+): error: (.+)',
                    r'\[ERROR\] (.+)',
                    r'COMPILATION ERROR'
                ],
                'warning_patterns': [
                    r'\[WARNING\] (.+?):(\d+): warning: (.+)',
                    r'\[WARNING\] (.+)'
                ]
            },
            'python': {
                'command': ['python', '-m', 'py_compile'],
                'error_patterns': [
                    r'File "(.+?)", line (\d+)(.+?)(.+)',
                    r'SyntaxError: (.+)',
                    r'IndentationError: (.+)',
                    r'ImportError: (.+)'
                ],
                'warning_patterns': [
                    r'DeprecationWarning: (.+)',
                    r'FutureWarning: (.+)'
                ]
            },
            'javascript': {
                'command': ['node', '--check'],
                'error_patterns': [
                    r'(.+?):(\d+)(.+?)SyntaxError: (.+)',
                    r'ReferenceError: (.+)',
                    r'TypeError: (.+)'
                ],
                'warning_patterns': [
                    r'Warning: (.+)'
                ]
            },
            'go': {
                'command': ['go', 'build', '-v'],
                'error_patterns': [
                    r'(.+?):(\d+):(\d+): (.+)',
                    r'can\'t load package: (.+)',
                    r'build failed'
                ],
                'warning_patterns': [
                    r'warning: (.+)'
                ]
            },
            'rust': {
                'command': ['cargo', 'check', '--message-format=json'],
                'error_patterns': [
                    r'error\[E(\d+)\]: (.+)',
                    r'error: (.+)',
                    r'could not compile (.+)'
                ],
                'warning_patterns': [
                    r'warning: (.+)'
                ]
            }
        }
    
    def check_compilation(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Check if the project compiles successfully"""
        result = {
            'success': False,
            'language': language,
            'project_dir': project_dir,
            'errors': [],
            'warnings': [],
            'output': '',
            'error_output': '',
            'command': [],
            'timestamp': datetime.now().isoformat(),
            'files_checked': [],
            'error_summary': {
                'total_errors': 0,
                'total_warnings': 0,
                'critical_errors': 0,
                'fixable_errors': 0
            }
        }
        
        try:
            compile_config = self.compile_commands.get(language.lower())
            if not compile_config:
                result['errors'].append({
                    'type': 'unsupported_language',
                    'message': f"Compilation checking not supported for language: {language}",
                    'severity': 'critical'
                })
                return result
            
            # Get list of source files to check
            source_files = self._get_source_files(project_dir, language)
            result['files_checked'] = source_files
            
            if not source_files:
                result['warnings'].append({
                    'type': 'no_source_files',
                    'message': f"No {language} source files found in {project_dir}",
                    'severity': 'medium'
                })
                result['success'] = True  # No files to compile means no errors
                return result
            
            # Execute compilation check
            compile_cmd = compile_config['command']
            
            # Language-specific compilation handling
            if language.lower() == 'python':
                result = self._check_python_files(project_dir, source_files, result)
            elif language.lower() == 'javascript':
                result = self._check_javascript_files(project_dir, source_files, result, compile_cmd)
            else:
                # Use standard compilation command for other languages
                result = self._run_compilation_command(project_dir, compile_cmd, result, compile_config)
            
            # Parse and categorize errors/warnings
            self._parse_compilation_output(result, compile_config)
            
            # Generate error summary
            result['error_summary'] = self._generate_error_summary(result)
            
            result['success'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append({
                'type': 'compilation_check_failed',
                'message': f"Failed to check compilation: {str(e)}",
                'severity': 'critical'
            })
        
        return result
    
    def _get_source_files(self, project_dir: str, language: str) -> List[str]:
        """Get list of source files for the given language"""
        extensions = {
            'csharp': ['.cs'],
            'java': ['.java'],
            'python': ['.py'],
            'javascript': ['.js', '.mjs'],
            'go': ['.go'],
            'rust': ['.rs']
        }
        
        lang_extensions = extensions.get(language.lower(), [])
        source_files = []
        
        for root, dirs, files in os.walk(project_dir):
            # Skip common build/cache directories
            dirs[:] = [d for d in dirs if d not in ['bin', 'obj', 'target', 'node_modules', '__pycache__', '.git']]
            
            for file in files:
                if any(file.endswith(ext) for ext in lang_extensions):
                    source_files.append(os.path.join(root, file))
        
        return source_files
    
    def _check_python_files(self, project_dir: str, source_files: List[str], result: Dict) -> Dict:
        """Check Python files for syntax errors"""
        for file_path in source_files:
            try:
                # Check syntax by compiling
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                try:
                    compile(source_code, file_path, 'exec')
                    result['output'] += f"✅ {file_path}: OK\n"
                except SyntaxError as e:
                    result['errors'].append({
                        'type': 'syntax_error',
                        'file': file_path,
                        'line': e.lineno,
                        'column': e.offset,
                        'message': e.msg,
                        'severity': 'critical',
                        'code': e.text.strip() if e.text else ''
                    })
                except Exception as e:
                    result['errors'].append({
                        'type': 'compilation_error',
                        'file': file_path,
                        'message': str(e),
                        'severity': 'critical'
                    })
                
                # Check for import errors
                self._check_python_imports(file_path, source_code, result)
                
            except Exception as e:
                result['errors'].append({
                    'type': 'file_read_error',
                    'file': file_path,
                    'message': f"Could not read file: {str(e)}",
                    'severity': 'critical'
                })
        
        return result
    
    def _check_javascript_files(self, project_dir: str, source_files: List[str], 
                              result: Dict, compile_cmd: List[str]) -> Dict:
        """Check JavaScript files for syntax errors"""
        for file_path in source_files:
            try:
                # Check syntax using node --check
                process = subprocess.run(
                    [*compile_cmd, file_path],
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if process.returncode == 0:
                    result['output'] += f"✅ {file_path}: OK\n"
                else:
                    # Parse JavaScript errors
                    error_lines = process.stderr.split('\n')
                    for line in error_lines:
                        if line.strip():
                            result['errors'].append({
                                'type': 'syntax_error',
                                'file': file_path,
                                'message': line.strip(),
                                'severity': 'critical'
                            })
                
            except subprocess.TimeoutExpired:
                result['errors'].append({
                    'type': 'timeout_error',
                    'file': file_path,
                    'message': "Compilation check timed out",
                    'severity': 'medium'
                })
            except Exception as e:
                result['errors'].append({
                    'type': 'check_failed',
                    'file': file_path,
                    'message': str(e),
                    'severity': 'critical'
                })
        
        return result
    
    def _run_compilation_command(self, project_dir: str, compile_cmd: List[str], 
                               result: Dict, compile_config: Dict) -> Dict:
        """Run standard compilation command for compiled languages"""
        try:
            process = subprocess.run(
                compile_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            result['command'] = compile_cmd
            result['output'] = process.stdout
            result['error_output'] = process.stderr
            
            if process.returncode != 0:
                # Compilation failed - errors will be parsed later
                pass
            
        except subprocess.TimeoutExpired:
            result['errors'].append({
                'type': 'timeout_error',
                'message': "Compilation timed out after 5 minutes",
                'severity': 'critical'
            })
        except FileNotFoundError:
            result['errors'].append({
                'type': 'tool_not_found',
                'message': f"Compilation tool not found: {compile_cmd[0]}",
                'severity': 'critical'
            })
        except Exception as e:
            result['errors'].append({
                'type': 'compilation_failed',
                'message': f"Compilation failed: {str(e)}",
                'severity': 'critical'
            })
        
        return result
    
    def _check_python_imports(self, file_path: str, source_code: str, result: Dict) -> None:
        """Check Python imports for missing modules"""
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'
        ]
        
        lines = source_code.split('\n')
        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module_name = match.group(1)
                    if not self._is_python_module_available(module_name):
                        result['warnings'].append({
                            'type': 'missing_import',
                            'file': file_path,
                            'line': line_no,
                            'message': f"Module '{module_name}' may not be available",
                            'severity': 'medium',
                            'suggestion': f"Install with: pip install {module_name}"
                        })
    
    def _is_python_module_available(self, module_name: str) -> bool:
        """Check if a Python module is available"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def _parse_compilation_output(self, result: Dict, compile_config: Dict) -> None:
        """Parse compilation output for errors and warnings"""
        output_text = result.get('output', '') + result.get('error_output', '')
        
        error_patterns = compile_config.get('error_patterns', [])
        warning_patterns = compile_config.get('warning_patterns', [])
        
        # Parse errors
        for pattern in error_patterns:
            matches = re.finditer(pattern, output_text, re.MULTILINE)
            for match in matches:
                error_info = {
                    'type': 'compilation_error',
                    'message': match.group(0),
                    'severity': 'critical'
                }
                
                # Try to extract file, line, column info if available
                groups = match.groups()
                if len(groups) >= 2:
                    error_info['details'] = groups
                
                result['errors'].append(error_info)
        
        # Parse warnings
        for pattern in warning_patterns:
            matches = re.finditer(pattern, output_text, re.MULTILINE)
            for match in matches:
                warning_info = {
                    'type': 'compilation_warning',
                    'message': match.group(0),
                    'severity': 'medium'
                }
                
                groups = match.groups()
                if len(groups) >= 2:
                    warning_info['details'] = groups
                
                result['warnings'].append(warning_info)
    
    def _generate_error_summary(self, result: Dict) -> Dict:
        """Generate summary of compilation errors and warnings"""
        errors = result.get('errors', [])
        warnings = result.get('warnings', [])
        
        critical_errors = sum(1 for e in errors if e.get('severity') == 'critical')
        fixable_errors = sum(1 for e in errors if e.get('type') in ['syntax_error', 'missing_import'])
        
        return {
            'total_errors': len(errors),
            'total_warnings': len(warnings),
            'critical_errors': critical_errors,
            'fixable_errors': fixable_errors,
            'error_types': list(set(e.get('type', 'unknown') for e in errors)),
            'warning_types': list(set(w.get('type', 'unknown') for w in warnings))
        }
    
    def suggest_fixes(self, compilation_result: Dict) -> Dict[str, List[str]]:
        """Suggest fixes for common compilation errors"""
        fixes = {
            'critical_fixes': [],
            'recommended_fixes': [],
            'general_suggestions': []
        }
        
        errors = compilation_result.get('errors', [])
        warnings = compilation_result.get('warnings', [])
        
        for error in errors:
            error_type = error.get('type', '')
            message = error.get('message', '')
            
            if error_type == 'syntax_error':
                fixes['critical_fixes'].append(f"Fix syntax error: {message}")
            elif error_type == 'missing_import':
                fixes['recommended_fixes'].append(error.get('suggestion', f"Resolve import: {message}"))
            elif 'undefined' in message.lower() or 'not found' in message.lower():
                fixes['critical_fixes'].append(f"Define missing symbol: {message}")
            elif 'type' in message.lower():
                fixes['recommended_fixes'].append(f"Check type compatibility: {message}")
        
        # General suggestions based on language
        language = compilation_result.get('language', '').lower()
        if language == 'python':
            fixes['general_suggestions'].extend([
                "Ensure all imports are available: pip install -r requirements.txt",
                "Check indentation consistency (use spaces or tabs, not mixed)",
                "Verify Python version compatibility"
            ])
        elif language == 'csharp':
            fixes['general_suggestions'].extend([
                "Run 'dotnet restore' to download packages",
                "Check project target framework compatibility",
                "Ensure all referenced assemblies are available"
            ])
        elif language == 'java':
            fixes['general_suggestions'].extend([
                "Run 'mvn compile' to check compilation",
                "Verify classpath and dependencies",
                "Check Java version compatibility"
            ])
        elif language == 'javascript':
            fixes['general_suggestions'].extend([
                "Run 'npm install' to install dependencies",
                "Check Node.js version compatibility",
                "Verify module paths and imports"
            ])
        
        return fixes
