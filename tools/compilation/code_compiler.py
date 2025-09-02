"""
Code Compilation Tool

Provides compilation functionality for different programming languages
to validate generated code and capture compilation errors.
"""

import os
import subprocess
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import re


class CodeCompiler:
    """Tool for compiling generated code and capturing compilation errors"""
    
    def __init__(self):
        self.temp_dirs = []  # Track temporary directories for cleanup
        
        # Language-specific compilation configurations
        self.compilation_configs = {
            'csharp': {
                'file_extension': '.cs',
                'project_file': '.csproj',
                'compile_command': 'dotnet build',
                'test_command': 'dotnet test',
                'required_files': ['*.csproj']
            },
            'c#': {
                'file_extension': '.cs',
                'project_file': '.csproj',
                'compile_command': 'dotnet build',
                'test_command': 'dotnet test',
                'required_files': ['*.csproj']
            },
            'python': {
                'file_extension': '.py',
                'project_file': 'requirements.txt',
                'compile_command': 'python -m py_compile',
                'test_command': 'python -m pytest',
                'required_files': []
            },
            'javascript': {
                'file_extension': '.js',
                'project_file': 'package.json',
                'compile_command': 'node --check',
                'test_command': 'npm test',
                'required_files': []
            },
            'java': {
                'file_extension': '.java',
                'project_file': 'pom.xml',
                'compile_command': 'mvn compile',
                'test_command': 'mvn test',
                'required_files': ['pom.xml']
            },
            'go': {
                'file_extension': '.go',
                'project_file': 'go.mod',
                'compile_command': 'go build',
                'test_command': 'go test',
                'required_files': ['go.mod']
            },
            'rust': {
                'file_extension': '.rs',
                'project_file': 'Cargo.toml',
                'compile_command': 'cargo build',
                'test_command': 'cargo test',
                'required_files': ['Cargo.toml']
            }
        }
    
    def compile_project(self, project_dir: str, language: str) -> Dict[str, Any]:
        """
        Compile the entire project and return compilation results
        
        Args:
            project_dir: Path to the project directory
            language: Programming language
            
        Returns:
            Dictionary containing compilation results, errors, and analysis
        """
        language = language.lower()
        
        if language not in self.compilation_configs:
            return {
                "success": False,
                "error": f"Unsupported language for compilation: {language}",
                "language": language,
                "project_dir": project_dir
            }
        
        config = self.compilation_configs[language]
        
        try:
            # Check if project directory exists
            if not os.path.exists(project_dir):
                return {
                    "success": False,
                    "error": f"Project directory does not exist: {project_dir}",
                    "language": language,
                    "project_dir": project_dir
                }
            
            # Validate required files
            missing_files = self._check_required_files(project_dir, config['required_files'])
            if missing_files:
                return {
                    "success": False,
                    "error": f"Missing required files: {', '.join(missing_files)}",
                    "language": language,
                    "project_dir": project_dir,
                    "missing_files": missing_files
                }
            
            # Perform compilation
            compilation_result = self._execute_compilation(project_dir, config, language)
            
            # Analyze errors if compilation failed
            if not compilation_result["success"]:
                compilation_result["error_analysis"] = self._analyze_compilation_errors(
                    compilation_result.get("stderr", ""), 
                    compilation_result.get("stdout", ""),
                    language
                )
            
            return compilation_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Compilation failed with exception: {str(e)}",
                "language": language,
                "project_dir": project_dir,
                "exception": str(e)
            }
    
    def compile_individual_files(self, file_paths: List[str], language: str) -> Dict[str, Any]:
        """
        Compile individual files (for quick syntax checking)
        
        Args:
            file_paths: List of file paths to compile
            language: Programming language
            
        Returns:
            Dictionary containing compilation results for each file
        """
        language = language.lower()
        
        if language not in self.compilation_configs:
            return {
                "success": False,
                "error": f"Unsupported language for compilation: {language}",
                "language": language
            }
        
        results = {
            "language": language,
            "files_checked": len(file_paths),
            "successful_files": [],
            "failed_files": [],
            "overall_success": True,
            "errors": []
        }
        
        for file_path in file_paths:
            try:
                file_result = self._compile_single_file(file_path, language)
                
                if file_result["success"]:
                    results["successful_files"].append(file_path)
                else:
                    results["failed_files"].append({
                        "file": file_path,
                        "error": file_result.get("error", "Unknown error"),
                        "stderr": file_result.get("stderr", ""),
                        "stdout": file_result.get("stdout", "")
                    })
                    results["overall_success"] = False
                    results["errors"].extend(file_result.get("errors", []))
                    
            except Exception as e:
                results["failed_files"].append({
                    "file": file_path,
                    "error": f"Exception during compilation: {str(e)}",
                    "exception": str(e)
                })
                results["overall_success"] = False
        
        return results
    
    def _check_required_files(self, project_dir: str, required_patterns: List[str]) -> List[str]:
        """Check if required files exist in the project directory"""
        missing_files = []
        
        for pattern in required_patterns:
            # Use glob-like matching
            import glob
            matching_files = glob.glob(os.path.join(project_dir, pattern))
            if not matching_files:
                missing_files.append(pattern)
        
        return missing_files
    
    def _execute_compilation(self, project_dir: str, config: Dict, language: str) -> Dict[str, Any]:
        """Execute the compilation command for the project"""
        compile_command = config['compile_command']
        
        try:
            # Change to project directory and run compilation
            result = subprocess.run(
                compile_command.split(),
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )
            
            success = result.returncode == 0
            
            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": compile_command,
                "project_dir": project_dir,
                "language": language,
                "compilation_time": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Compilation timeout (exceeded 60 seconds)",
                "command": compile_command,
                "project_dir": project_dir,
                "language": language
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Compilation tool not found. Please ensure {language} compiler is installed.",
                "command": compile_command,
                "project_dir": project_dir,
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Compilation failed: {str(e)}",
                "command": compile_command,
                "project_dir": project_dir,
                "language": language,
                "exception": str(e)
            }
    
    def _compile_single_file(self, file_path: str, language: str) -> Dict[str, Any]:
        """Compile a single file for syntax checking"""
        config = self.compilation_configs[language]
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File does not exist: {file_path}",
                "file": file_path
            }
        
        try:
            if language in ['csharp', 'c#']:
                # For C#, we need a project context, so create a minimal temporary project
                return self._compile_csharp_file(file_path)
            elif language == 'python':
                return self._compile_python_file(file_path)
            elif language == 'javascript':
                return self._compile_javascript_file(file_path)
            elif language == 'java':
                return self._compile_java_file(file_path)
            elif language == 'go':
                return self._compile_go_file(file_path)
            elif language == 'rust':
                return self._compile_rust_file(file_path)
            else:
                return {
                    "success": False,
                    "error": f"Single file compilation not implemented for {language}",
                    "file": file_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"File compilation failed: {str(e)}",
                "file": file_path,
                "exception": str(e)
            }
    
    def _compile_csharp_file(self, file_path: str) -> Dict[str, Any]:
        """Compile a single C# file by creating a temporary project"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        try:
            # Copy the file to temp directory
            temp_file = os.path.join(temp_dir, os.path.basename(file_path))
            shutil.copy2(file_path, temp_file)
            
            # Create a minimal .csproj file
            csproj_content = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <OutputType>Library</OutputType>
  </PropertyGroup>
</Project>'''
            
            csproj_path = os.path.join(temp_dir, "TempProject.csproj")
            with open(csproj_path, 'w') as f:
                f.write(csproj_content)
            
            # Compile the project
            result = subprocess.run(
                ['dotnet', 'build'],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": file_path,
                "temp_dir": temp_dir
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def _compile_python_file(self, file_path: str) -> Dict[str, Any]:
        """Compile/check a Python file"""
        try:
            result = subprocess.run(
                ['python', '-m', 'py_compile', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def _compile_javascript_file(self, file_path: str) -> Dict[str, Any]:
        """Check JavaScript file syntax"""
        try:
            result = subprocess.run(
                ['node', '--check', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def _compile_java_file(self, file_path: str) -> Dict[str, Any]:
        """Compile a Java file"""
        try:
            result = subprocess.run(
                ['javac', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def _compile_go_file(self, file_path: str) -> Dict[str, Any]:
        """Check Go file syntax"""
        try:
            # Use go vet for syntax checking
            result = subprocess.run(
                ['go', 'vet', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def _compile_rust_file(self, file_path: str) -> Dict[str, Any]:
        """Check Rust file syntax"""
        try:
            result = subprocess.run(
                ['rustc', '--emit=metadata', '--crate-type=lib', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def _analyze_compilation_errors(self, stderr: str, stdout: str, language: str) -> Dict[str, Any]:
        """Analyze compilation errors and provide structured information"""
        analysis = {
            "total_errors": 0,
            "total_warnings": 0,
            "error_categories": {},
            "detailed_errors": [],
            "suggestions": [],
            "language": language
        }
        
        if language in ['csharp', 'c#']:
            analysis.update(self._analyze_csharp_errors(stderr, stdout))
        elif language == 'python':
            analysis.update(self._analyze_python_errors(stderr, stdout))
        elif language == 'java':
            analysis.update(self._analyze_java_errors(stderr, stdout))
        elif language == 'javascript':
            analysis.update(self._analyze_javascript_errors(stderr, stdout))
        elif language == 'go':
            analysis.update(self._analyze_go_errors(stderr, stdout))
        elif language == 'rust':
            analysis.update(self._analyze_rust_errors(stderr, stdout))
        
        return analysis
    
    def _analyze_csharp_errors(self, stderr: str, stdout: str) -> Dict[str, Any]:
        """Analyze C# compilation errors"""
        errors = []
        warnings = []
        error_categories = {}
        
        # Common C# error patterns
        error_patterns = {
            'CS0103': 'Undefined variable/method',
            'CS0117': 'Type does not contain definition',
            'CS0246': 'Type or namespace not found',
            'CS1002': 'Syntax error',
            'CS1026': 'Syntax error', 
            'CS0029': 'Cannot convert type',
            'CS0161': 'Not all code paths return a value',
            'CS0120': 'Object reference required'
        }
        
        # Parse both stderr and stdout for errors (dotnet outputs to stdout)
        all_output = (stderr + '\n' + stdout).strip()
        lines = all_output.split('\n')
        
        for line in lines:
            if ': error CS' in line:
                errors.append(line.strip())
                # Extract error code
                for code, description in error_patterns.items():
                    if code in line:
                        error_categories[description] = error_categories.get(description, 0) + 1
                        break
                # If no specific pattern matched, categorize generically
                if not any(code in line for code in error_patterns.keys()):
                    error_categories['Other Error'] = error_categories.get('Other Error', 0) + 1
            elif ': warning' in line and ('CS' in line or 'NU' in line or 'NETSDK' in line):
                warnings.append(line.strip())
        
        return {
            "total_errors": len(errors),
            "total_warnings": len(warnings),
            "error_categories": error_categories,
            "detailed_errors": errors,
            "detailed_warnings": warnings
        }
    
    def _analyze_python_errors(self, stderr: str, stdout: str) -> Dict[str, Any]:
        """Analyze Python compilation errors"""
        errors = []
        error_categories = {}
        
        lines = stderr.split('\n')
        for line in lines:
            if line.strip():
                errors.append(line.strip())
                
                # Categorize common Python errors
                if 'SyntaxError' in line:
                    error_categories['Syntax Error'] = error_categories.get('Syntax Error', 0) + 1
                elif 'IndentationError' in line:
                    error_categories['Indentation Error'] = error_categories.get('Indentation Error', 0) + 1
                elif 'NameError' in line:
                    error_categories['Name Error'] = error_categories.get('Name Error', 0) + 1
                elif 'ImportError' in line or 'ModuleNotFoundError' in line:
                    error_categories['Import Error'] = error_categories.get('Import Error', 0) + 1
        
        return {
            "total_errors": len(errors),
            "total_warnings": 0,
            "error_categories": error_categories,
            "detailed_errors": errors
        }
    
    def _analyze_java_errors(self, stderr: str, stdout: str) -> Dict[str, Any]:
        """Analyze Java compilation errors"""
        errors = []
        error_categories = {}
        
        lines = stderr.split('\n')
        for line in lines:
            if line.strip() and ('error:' in line.lower() or '.java:' in line):
                errors.append(line.strip())
                
                # Categorize common Java errors
                if 'cannot find symbol' in line.lower():
                    error_categories['Symbol Not Found'] = error_categories.get('Symbol Not Found', 0) + 1
                elif 'incompatible types' in line.lower():
                    error_categories['Type Mismatch'] = error_categories.get('Type Mismatch', 0) + 1
                elif 'missing return statement' in line.lower():
                    error_categories['Missing Return'] = error_categories.get('Missing Return', 0) + 1
        
        return {
            "total_errors": len(errors),
            "total_warnings": 0,
            "error_categories": error_categories,
            "detailed_errors": errors
        }
    
    def _analyze_javascript_errors(self, stderr: str, stdout: str) -> Dict[str, Any]:
        """Analyze JavaScript syntax errors"""
        errors = []
        error_categories = {}
        
        lines = stderr.split('\n')
        for line in lines:
            if line.strip():
                errors.append(line.strip())
                
                if 'SyntaxError' in line:
                    error_categories['Syntax Error'] = error_categories.get('Syntax Error', 0) + 1
                elif 'ReferenceError' in line:
                    error_categories['Reference Error'] = error_categories.get('Reference Error', 0) + 1
        
        return {
            "total_errors": len(errors),
            "total_warnings": 0,
            "error_categories": error_categories,
            "detailed_errors": errors
        }
    
    def _analyze_go_errors(self, stderr: str, stdout: str) -> Dict[str, Any]:
        """Analyze Go compilation errors"""
        errors = []
        error_categories = {}
        
        lines = stderr.split('\n')
        for line in lines:
            if line.strip():
                errors.append(line.strip())
                
                if 'undefined:' in line:
                    error_categories['Undefined Symbol'] = error_categories.get('Undefined Symbol', 0) + 1
                elif 'syntax error' in line.lower():
                    error_categories['Syntax Error'] = error_categories.get('Syntax Error', 0) + 1
        
        return {
            "total_errors": len(errors),
            "total_warnings": 0,
            "error_categories": error_categories,
            "detailed_errors": errors
        }
    
    def _analyze_rust_errors(self, stderr: str, stdout: str) -> Dict[str, Any]:
        """Analyze Rust compilation errors"""
        errors = []
        error_categories = {}
        
        lines = stderr.split('\n')
        for line in lines:
            if 'error[E' in line:
                errors.append(line.strip())
                
                if 'cannot find' in line.lower():
                    error_categories['Symbol Not Found'] = error_categories.get('Symbol Not Found', 0) + 1
                elif 'mismatched types' in line.lower():
                    error_categories['Type Mismatch'] = error_categories.get('Type Mismatch', 0) + 1
        
        return {
            "total_errors": len(errors),
            "total_warnings": 0,
            "error_categories": error_categories,
            "detailed_errors": errors
        }
    
    def cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Could not clean up temporary directory {temp_dir}: {e}")
        self.temp_dirs.clear()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.cleanup()
