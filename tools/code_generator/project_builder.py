"""
Project Builder Tool

Handles project restoration, dependency downloading, and build operations for different project types.
"""

import os
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ProjectBuilder:
    """Tool for building and restoring projects across different languages/frameworks"""
    
    def __init__(self):
        self.build_commands = {
            'csharp': {
                'restore': ['dotnet', 'restore'],
                'build': ['dotnet', 'build'],
                'test': ['dotnet', 'test'],
                'clean': ['dotnet', 'clean']
            },
            'java': {
                'restore': ['mvn', 'dependency:resolve'],
                'build': ['mvn', 'compile', 'test-compile'],
                'test': ['mvn', 'test'],
                'clean': ['mvn', 'clean']
            },
            'python': {
                'restore': ['pip', 'install', '-r', 'requirements.txt'],
                'build': ['python', '-m', 'py_compile'],
                'test': ['pytest'],
                'clean': ['find', '.', '-name', '*.pyc', '-delete']
            },
            'javascript': {
                'restore': ['npm', 'install'],
                'build': ['npm', 'run', 'build'],
                'test': ['npm', 'test'],
                'clean': ['npm', 'run', 'clean']
            },
            'go': {
                'restore': ['go', 'mod', 'download'],
                'build': ['go', 'build', './...'],
                'test': ['go', 'test', './...'],
                'clean': ['go', 'clean']
            },
            'rust': {
                'restore': ['cargo', 'fetch'],
                'build': ['cargo', 'build'],
                'test': ['cargo', 'test'],
                'clean': ['cargo', 'clean']
            }
        }
    
    def restore_dependencies(self, project_dir: str, language: str) -> Dict[str, any]:
        """Restore/download project dependencies"""
        result = {
            'success': False,
            'output': '',
            'error': '',
            'command': [],
            'language': language,
            'project_dir': project_dir
        }
        
        try:
            commands = self.build_commands.get(language.lower())
            if not commands:
                result['error'] = f"Unsupported language: {language}"
                return result
            
            restore_cmd = commands['restore']
            result['command'] = restore_cmd
            
            # Execute restore command
            process = subprocess.run(
                restore_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            result['return_code'] = process.returncode
            
        except subprocess.TimeoutExpired:
            result['error'] = "Restore command timed out after 5 minutes"
        except FileNotFoundError:
            result['error'] = f"Command not found: {' '.join(restore_cmd)}. Please ensure {language} tools are installed."
        except Exception as e:
            result['error'] = f"Unexpected error during restore: {str(e)}"
        
        return result
    
    def build_project(self, project_dir: str, language: str) -> Dict[str, any]:
        """Build the project"""
        result = {
            'success': False,
            'output': '',
            'error': '',
            'command': [],
            'language': language,
            'project_dir': project_dir
        }
        
        try:
            commands = self.build_commands.get(language.lower())
            if not commands:
                result['error'] = f"Unsupported language: {language}"
                return result
            
            build_cmd = commands['build']
            result['command'] = build_cmd
            
            # Execute build command
            process = subprocess.run(
                build_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            result['return_code'] = process.returncode
            
        except subprocess.TimeoutExpired:
            result['error'] = "Build command timed out after 10 minutes"
        except FileNotFoundError:
            result['error'] = f"Command not found: {' '.join(build_cmd)}. Please ensure {language} tools are installed."
        except Exception as e:
            result['error'] = f"Unexpected error during build: {str(e)}"
        
        return result
    
    def run_tests(self, project_dir: str, language: str) -> Dict[str, any]:
        """Run project tests"""
        result = {
            'success': False,
            'output': '',
            'error': '',
            'command': [],
            'language': language,
            'project_dir': project_dir
        }
        
        try:
            commands = self.build_commands.get(language.lower())
            if not commands:
                result['error'] = f"Unsupported language: {language}"
                return result
            
            test_cmd = commands['test']
            result['command'] = test_cmd
            
            # Execute test command
            process = subprocess.run(
                test_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            result['return_code'] = process.returncode
            
        except subprocess.TimeoutExpired:
            result['error'] = "Test command timed out after 5 minutes"
        except FileNotFoundError:
            result['error'] = f"Command not found: {' '.join(test_cmd)}. Please ensure {language} tools are installed."
        except Exception as e:
            result['error'] = f"Unexpected error during test: {str(e)}"
        
        return result
    
    def full_build_cycle(self, project_dir: str, language: str) -> Dict[str, any]:
        """Execute full build cycle: restore -> build -> test"""
        cycle_result = {
            'success': False,
            'restore': {},
            'build': {},
            'test': {},
            'language': language,
            'project_dir': project_dir,
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Restore dependencies
        print(f"🔄 Restoring dependencies for {language} project...")
        restore_result = self.restore_dependencies(project_dir, language)
        cycle_result['restore'] = restore_result
        
        if not restore_result['success']:
            print(f"❌ Dependency restoration failed: {restore_result['error']}")
            return cycle_result
        
        print(f"✅ Dependencies restored successfully")
        
        # Step 2: Build project
        print(f"🔨 Building {language} project...")
        build_result = self.build_project(project_dir, language)
        cycle_result['build'] = build_result
        
        if not build_result['success']:
            print(f"❌ Build failed: {build_result['error']}")
            return cycle_result
        
        print(f"✅ Project built successfully")
        
        # Step 3: Run tests
        print(f"🧪 Running tests for {language} project...")
        test_result = self.run_tests(project_dir, language)
        cycle_result['test'] = test_result
        
        if not test_result['success']:
            print(f"⚠️ Tests failed or had issues: {test_result['error']}")
            # Don't fail the whole cycle for test failures, as tests might be expected to fail initially
        else:
            print(f"✅ Tests completed successfully")
        
        cycle_result['success'] = restore_result['success'] and build_result['success']
        return cycle_result
    
    def check_tool_availability(self, language: str) -> Dict[str, bool]:
        """Check if required build tools are available for the language"""
        availability = {}
        
        commands = self.build_commands.get(language.lower(), {})
        for operation, cmd in commands.items():
            try:
                # Try to run the command with --version or --help
                tool_name = cmd[0]
                check_process = subprocess.run(
                    [tool_name, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                availability[f"{operation}_tool"] = check_process.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                try:
                    # Fallback to --help for tools that don't support --version
                    check_process = subprocess.run(
                        [tool_name, '--help'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    availability[f"{operation}_tool"] = check_process.returncode == 0
                except:
                    availability[f"{operation}_tool"] = False
        
        return availability
    
    def get_build_info(self, project_dir: str, language: str) -> Dict[str, any]:
        """Get information about the project and its build configuration"""
        info = {
            'language': language,
            'project_dir': project_dir,
            'project_files': [],
            'config_files': [],
            'has_dependencies': False,
            'estimated_build_time': 'Unknown'
        }
        
        # Language-specific project files to look for
        project_file_patterns = {
            'csharp': ['*.csproj', '*.sln'],
            'java': ['pom.xml', 'build.gradle'],
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml'],
            'javascript': ['package.json', 'package-lock.json'],
            'go': ['go.mod', 'go.sum'],
            'rust': ['Cargo.toml', 'Cargo.lock']
        }
        
        patterns = project_file_patterns.get(language.lower(), [])
        for pattern in patterns:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    if pattern.replace('*', '') in file:
                        file_path = os.path.join(root, file)
                        info['project_files'].append(file_path)
                        
                        # Check if it's a config file
                        config_indicators = ['config', 'settings', 'properties']
                        if any(indicator in file.lower() for indicator in config_indicators):
                            info['config_files'].append(file_path)
        
        # Check for dependencies
        dependency_indicators = {
            'csharp': ['PackageReference'],
            'java': ['<dependency>', '<dependencies>'],
            'python': ['==', '>=', '<='],
            'javascript': ['"dependencies"', '"devDependencies"'],
            'go': ['require'],
            'rust': ['[dependencies]']
        }
        
        indicators = dependency_indicators.get(language.lower(), [])
        for project_file in info['project_files']:
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if any(indicator in content for indicator in indicators):
                        info['has_dependencies'] = True
                        break
            except:
                continue
        
        return info
