"""
Environment Setup Tool

Provides capabilities to set up development and runtime environments,
manage dependencies, and configure development tools.
"""

import os
import subprocess
import platform
import json
import shutil
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class EnvironmentSetup:
    """Tool for setting up development and runtime environments"""
    
    def __init__(self):
        self.system_info = {
            'os': platform.system().lower(),
            'arch': platform.machine().lower(),
            'python_version': platform.python_version(),
            'platform': platform.platform()
        }
    
    def setup_development_environment(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Set up complete development environment for a language"""
        result = {
            'success': False,
            'language': language,
            'project_dir': project_dir,
            'tools_installed': [],
            'environment_configured': [],
            'issues': [],
            'next_steps': []
        }
        
        try:
            if language.lower() in ['csharp', 'c#']:
                result.update(self._setup_csharp_environment(project_dir))
            elif language.lower() == 'java':
                result.update(self._setup_java_environment(project_dir))
            elif language.lower() == 'python':
                result.update(self._setup_python_environment(project_dir))
            elif language.lower() in ['javascript', 'js', 'node.js']:
                result.update(self._setup_javascript_environment(project_dir))
            elif language.lower() == 'go':
                result.update(self._setup_go_environment(project_dir))
            elif language.lower() == 'rust':
                result.update(self._setup_rust_environment(project_dir))
            else:
                result['issues'].append(f"Language {language} not supported")
                return result
            
            # Create development configuration files
            self._create_development_configs(project_dir, language, result)
            
            result['success'] = len(result['issues']) == 0
            
        except Exception as e:
            result['issues'].append(f"Setup failed: {str(e)}")
        
        return result
    
    def _setup_csharp_environment(self, project_dir: str) -> Dict[str, Any]:
        """Set up C# development environment"""
        result = {
            'tools_installed': [],
            'environment_configured': [],
            'issues': [],
            'next_steps': []
        }
        
        # Check for .NET SDK
        dotnet_info = self._check_dotnet_installation()
        if dotnet_info['installed']:
            result['tools_installed'].append(f"✅ .NET SDK {dotnet_info['version']}")
        else:
            result['issues'].append("❌ .NET SDK not found")
            result['next_steps'].append("Install .NET SDK from https://dotnet.microsoft.com/download")
        
        # Create solution and project files if they don't exist
        self._ensure_csharp_project_structure(project_dir, result)
        
        # Set up NuGet configuration
        self._setup_nuget_config(project_dir, result)
        
        # Create development settings
        self._create_csharp_dev_settings(project_dir, result)
        
        return result
    
    def _setup_java_environment(self, project_dir: str) -> Dict[str, Any]:
        """Set up Java development environment"""
        result = {
            'tools_installed': [],
            'environment_configured': [],
            'issues': [],
            'next_steps': []
        }
        
        # Check for Java
        java_info = self._check_java_installation()
        if java_info['installed']:
            result['tools_installed'].append(f"✅ Java {java_info['version']}")
        else:
            result['issues'].append("❌ Java not found")
            result['next_steps'].append("Install Java 11+ from https://adoptium.net/")
        
        # Check for Maven
        maven_info = self._check_maven_installation()
        if maven_info['installed']:
            result['tools_installed'].append(f"✅ Maven {maven_info['version']}")
        else:
            result['issues'].append("❌ Maven not found")
            result['next_steps'].append("Install Maven from https://maven.apache.org/download.cgi")
        
        # Set up project structure
        self._ensure_java_project_structure(project_dir, result)
        
        # Create Maven settings
        self._create_maven_settings(project_dir, result)
        
        return result
    
    def _setup_python_environment(self, project_dir: str) -> Dict[str, Any]:
        """Set up Python development environment"""
        result = {
            'tools_installed': [],
            'environment_configured': [],
            'issues': [],
            'next_steps': []
        }
        
        # Check Python version
        python_info = self._check_python_installation()
        if python_info['installed']:
            result['tools_installed'].append(f"✅ Python {python_info['version']}")
        else:
            result['issues'].append("❌ Python not found")
            result['next_steps'].append("Install Python 3.8+ from https://python.org/downloads")
        
        # Set up virtual environment
        venv_result = self._setup_python_virtual_environment(project_dir)
        if venv_result['success']:
            result['environment_configured'].append("✅ Virtual environment created")
            result['tools_installed'].extend(venv_result['packages_installed'])
        else:
            result['issues'].append(f"❌ Virtual environment setup failed: {venv_result['error']}")
        
        # Create Python development files
        self._create_python_dev_files(project_dir, result)
        
        return result
    
    def _setup_javascript_environment(self, project_dir: str) -> Dict[str, Any]:
        """Set up JavaScript/Node.js development environment"""
        result = {
            'tools_installed': [],
            'environment_configured': [],
            'issues': [],
            'next_steps': []
        }
        
        # Check for Node.js
        node_info = self._check_node_installation()
        if node_info['installed']:
            result['tools_installed'].append(f"✅ Node.js {node_info['version']}")
        else:
            result['issues'].append("❌ Node.js not found")
            result['next_steps'].append("Install Node.js from https://nodejs.org/")
        
        # Check for npm
        npm_info = self._check_npm_installation()
        if npm_info['installed']:
            result['tools_installed'].append(f"✅ npm {npm_info['version']}")
        else:
            result['issues'].append("❌ npm not found")
        
        # Set up package.json if it doesn't exist
        self._ensure_javascript_project_structure(project_dir, result)
        
        # Install development dependencies
        self._setup_javascript_dev_dependencies(project_dir, result)
        
        return result
    
    def _setup_go_environment(self, project_dir: str) -> Dict[str, Any]:
        """Set up Go development environment"""
        result = {
            'tools_installed': [],
            'environment_configured': [],
            'issues': [],
            'next_steps': []
        }
        
        # Check for Go
        go_info = self._check_go_installation()
        if go_info['installed']:
            result['tools_installed'].append(f"✅ Go {go_info['version']}")
        else:
            result['issues'].append("❌ Go not found")
            result['next_steps'].append("Install Go from https://golang.org/dl/")
        
        # Initialize Go module if needed
        self._ensure_go_module(project_dir, result)
        
        # Set up Go development tools
        self._setup_go_dev_tools(project_dir, result)
        
        return result
    
    def _setup_rust_environment(self, project_dir: str) -> Dict[str, Any]:
        """Set up Rust development environment"""
        result = {
            'tools_installed': [],
            'environment_configured': [],
            'issues': [],
            'next_steps': []
        }
        
        # Check for Rust
        rust_info = self._check_rust_installation()
        if rust_info['installed']:
            result['tools_installed'].append(f"✅ Rust {rust_info['version']}")
        else:
            result['issues'].append("❌ Rust not found")
            result['next_steps'].append("Install Rust from https://rustup.rs/")
        
        # Check for Cargo
        cargo_info = self._check_cargo_installation()
        if cargo_info['installed']:
            result['tools_installed'].append(f"✅ Cargo {cargo_info['version']}")
        
        # Initialize Cargo project if needed
        self._ensure_rust_project(project_dir, result)
        
        return result
    
    def _check_dotnet_installation(self) -> Dict[str, Any]:
        """Check if .NET SDK is installed"""
        try:
            result = subprocess.run(['dotnet', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return {
                'installed': result.returncode == 0,
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _check_java_installation(self) -> Dict[str, Any]:
        """Check if Java is installed"""
        try:
            result = subprocess.run(['java', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Parse version from output
                version_line = result.stdout.split('\n')[0]
                return {'installed': True, 'version': version_line}
            return {'installed': False, 'version': None}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _check_maven_installation(self) -> Dict[str, Any]:
        """Check if Maven is installed"""
        try:
            result = subprocess.run(['mvn', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Parse version from output
                version_line = result.stdout.split('\n')[0]
                return {'installed': True, 'version': version_line}
            return {'installed': False, 'version': None}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _check_python_installation(self) -> Dict[str, Any]:
        """Check if Python is installed"""
        try:
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                return {'installed': True, 'version': version}
            return {'installed': False, 'version': None}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _check_node_installation(self) -> Dict[str, Any]:
        """Check if Node.js is installed"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return {
                'installed': result.returncode == 0,
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _check_npm_installation(self) -> Dict[str, Any]:
        """Check if npm is installed"""
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return {
                'installed': result.returncode == 0,
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _check_go_installation(self) -> Dict[str, Any]:
        """Check if Go is installed"""
        try:
            result = subprocess.run(['go', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            return {
                'installed': result.returncode == 0,
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _check_rust_installation(self) -> Dict[str, Any]:
        """Check if Rust is installed"""
        try:
            result = subprocess.run(['rustc', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return {
                'installed': result.returncode == 0,
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _check_cargo_installation(self) -> Dict[str, Any]:
        """Check if Cargo is installed"""
        try:
            result = subprocess.run(['cargo', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return {
                'installed': result.returncode == 0,
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'installed': False, 'version': None}
    
    def _setup_python_virtual_environment(self, project_dir: str) -> Dict[str, Any]:
        """Set up Python virtual environment"""
        venv_dir = os.path.join(project_dir, 'venv')
        
        if os.path.exists(venv_dir):
            return {
                'success': True,
                'message': 'Virtual environment already exists',
                'packages_installed': []
            }
        
        try:
            # Create virtual environment
            subprocess.run(['python', '-m', 'venv', 'venv'], 
                          cwd=project_dir, check=True)
            
            # Activate and install basic packages
            if self.system_info['os'] == 'windows':
                pip_cmd = os.path.join(venv_dir, 'Scripts', 'pip.exe')
            else:
                pip_cmd = os.path.join(venv_dir, 'bin', 'pip')
            
            # Install essential packages
            essential_packages = ['pip', 'setuptools', 'wheel', 'pytest', 'black', 'flake8']
            packages_installed = []
            
            for package in essential_packages:
                try:
                    subprocess.run([pip_cmd, 'install', '--upgrade', package], 
                                  check=True, capture_output=True)
                    packages_installed.append(f"✅ {package}")
                except subprocess.CalledProcessError:
                    packages_installed.append(f"❌ {package} (failed)")
            
            return {
                'success': True,
                'message': 'Virtual environment created successfully',
                'packages_installed': packages_installed
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'packages_installed': []
            }
    
    def _ensure_csharp_project_structure(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Ensure C# project has proper structure"""
        # Look for existing .csproj files
        csproj_files = list(Path(project_dir).glob('*.csproj'))
        
        if not csproj_files:
            # Create a basic test project
            project_name = os.path.basename(project_dir)
            csproj_content = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
    <PackageReference Include="NUnit" Version="4.0.1" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" />
    <PackageReference Include="NUnit.Analyzers" Version="3.9.0" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
  </ItemGroup>
</Project>'''
            
            csproj_path = os.path.join(project_dir, f"{project_name}.csproj")
            with open(csproj_path, 'w') as f:
                f.write(csproj_content)
            
            result['environment_configured'].append("✅ Created .csproj file")
        else:
            result['environment_configured'].append("✅ .csproj file exists")
    
    def _setup_nuget_config(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Set up NuGet configuration"""
        nuget_config = '''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" protocolVersion="3" />
  </packageSources>
  <packageRestore>
    <add key="enabled" value="True" />
    <add key="automatic" value="True" />
  </packageRestore>
</configuration>'''
        
        nuget_path = os.path.join(project_dir, 'nuget.config')
        if not os.path.exists(nuget_path):
            with open(nuget_path, 'w') as f:
                f.write(nuget_config)
            result['environment_configured'].append("✅ Created NuGet configuration")
    
    def _create_csharp_dev_settings(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Create C# development settings"""
        # Create .vscode settings for C# development
        vscode_dir = os.path.join(project_dir, '.vscode')
        os.makedirs(vscode_dir, exist_ok=True)
        
        # Settings.json
        settings = {
            "dotnet.defaultSolution": "disable",
            "omnisharp.enableRoslynAnalyzers": True,
            "omnisharp.enableEditorConfigSupport": True,
            "csharp.semanticHighlighting.enabled": True
        }
        
        with open(os.path.join(vscode_dir, 'settings.json'), 'w') as f:
            json.dump(settings, f, indent=2)
        
        result['environment_configured'].append("✅ Created VS Code settings")
    
    def _ensure_java_project_structure(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Ensure Java project has proper Maven structure"""
        pom_path = os.path.join(project_dir, 'pom.xml')
        
        if not os.path.exists(pom_path):
            project_name = os.path.basename(project_dir)
            pom_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>{project_name.lower()}</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <junit.version>5.9.2</junit.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${{junit.version}}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0</version>
            </plugin>
        </plugins>
    </build>
</project>'''
            
            with open(pom_path, 'w') as f:
                f.write(pom_content)
            
            result['environment_configured'].append("✅ Created pom.xml")
        
        # Create Maven directory structure
        src_main_java = os.path.join(project_dir, 'src', 'main', 'java')
        src_test_java = os.path.join(project_dir, 'src', 'test', 'java')
        
        os.makedirs(src_main_java, exist_ok=True)
        os.makedirs(src_test_java, exist_ok=True)
        
        result['environment_configured'].append("✅ Created Maven directory structure")
    
    def _create_maven_settings(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Create Maven settings"""
        vscode_dir = os.path.join(project_dir, '.vscode')
        os.makedirs(vscode_dir, exist_ok=True)
        
        settings = {
            "java.configuration.updateBuildConfiguration": "automatic",
            "java.compile.nullAnalysis.mode": "automatic",
            "maven.executable.path": "mvn"
        }
        
        with open(os.path.join(vscode_dir, 'settings.json'), 'w') as f:
            json.dump(settings, f, indent=2)
        
        result['environment_configured'].append("✅ Created Maven settings")
    
    def _create_python_dev_files(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Create Python development files"""
        # Create requirements-dev.txt
        dev_requirements = '''# Development dependencies
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
coverage>=7.0.0
pytest-cov>=4.0.0
pre-commit>=3.0.0
'''
        
        dev_req_path = os.path.join(project_dir, 'requirements-dev.txt')
        if not os.path.exists(dev_req_path):
            with open(dev_req_path, 'w') as f:
                f.write(dev_requirements)
            result['environment_configured'].append("✅ Created requirements-dev.txt")
        
        # Create .gitignore
        gitignore_content = '''__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.DS_Store
'''
        
        gitignore_path = os.path.join(project_dir, '.gitignore')
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            result['environment_configured'].append("✅ Created .gitignore")
    
    def _ensure_javascript_project_structure(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Ensure JavaScript project has package.json"""
        package_json_path = os.path.join(project_dir, 'package.json')
        
        if not os.path.exists(package_json_path):
            project_name = os.path.basename(project_dir)
            package_json = {
                "name": project_name.lower().replace(' ', '-'),
                "version": "1.0.0",
                "description": f"Test project for {project_name}",
                "main": "index.js",
                "scripts": {
                    "test": "jest",
                    "start": "node index.js",
                    "dev": "nodemon index.js"
                },
                "devDependencies": {
                    "jest": "^29.5.0",
                    "nodemon": "^3.0.0"
                },
                "engines": {
                    "node": ">=16.0.0"
                }
            }
            
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            
            result['environment_configured'].append("✅ Created package.json")
    
    def _setup_javascript_dev_dependencies(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Install JavaScript development dependencies"""
        package_json_path = os.path.join(project_dir, 'package.json')
        
        if os.path.exists(package_json_path):
            try:
                subprocess.run(['npm', 'install'], 
                              cwd=project_dir, check=True, capture_output=True)
                result['environment_configured'].append("✅ Installed npm dependencies")
            except subprocess.CalledProcessError:
                result['issues'].append("❌ Failed to install npm dependencies")
    
    def _ensure_go_module(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Ensure Go module is initialized"""
        go_mod_path = os.path.join(project_dir, 'go.mod')
        
        if not os.path.exists(go_mod_path):
            project_name = os.path.basename(project_dir)
            try:
                subprocess.run(['go', 'mod', 'init', project_name], 
                              cwd=project_dir, check=True)
                result['environment_configured'].append("✅ Initialized Go module")
            except subprocess.CalledProcessError:
                result['issues'].append("❌ Failed to initialize Go module")
    
    def _setup_go_dev_tools(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Set up Go development tools"""
        # Common Go development tools
        tools = [
            'golang.org/x/tools/cmd/goimports',
            'honnef.co/go/tools/cmd/staticcheck',
            'github.com/go-delve/delve/cmd/dlv'
        ]
        
        for tool in tools:
            try:
                subprocess.run(['go', 'install', tool + '@latest'], 
                              check=True, capture_output=True)
                result['environment_configured'].append(f"✅ Installed {tool.split('/')[-1]}")
            except subprocess.CalledProcessError:
                result['issues'].append(f"❌ Failed to install {tool.split('/')[-1]}")
    
    def _ensure_rust_project(self, project_dir: str, result: Dict[str, Any]) -> None:
        """Ensure Rust project is initialized"""
        cargo_toml_path = os.path.join(project_dir, 'Cargo.toml')
        
        if not os.path.exists(cargo_toml_path):
            project_name = os.path.basename(project_dir)
            try:
                subprocess.run(['cargo', 'init', '--name', project_name, '.'], 
                              cwd=project_dir, check=True)
                result['environment_configured'].append("✅ Initialized Cargo project")
            except subprocess.CalledProcessError:
                result['issues'].append("❌ Failed to initialize Cargo project")
    
    def _create_development_configs(self, project_dir: str, language: str, result: Dict[str, Any]) -> None:
        """Create common development configuration files"""
        # Create .vscode directory and launch.json for debugging
        vscode_dir = os.path.join(project_dir, '.vscode')
        os.makedirs(vscode_dir, exist_ok=True)
        
        launch_config = self._get_launch_config(language)
        if launch_config:
            with open(os.path.join(vscode_dir, 'launch.json'), 'w') as f:
                json.dump(launch_config, f, indent=2)
            result['environment_configured'].append("✅ Created VS Code launch configuration")
        
        # Create tasks.json for build tasks
        tasks_config = self._get_tasks_config(language)
        if tasks_config:
            with open(os.path.join(vscode_dir, 'tasks.json'), 'w') as f:
                json.dump(tasks_config, f, indent=2)
            result['environment_configured'].append("✅ Created VS Code tasks configuration")
    
    def _get_launch_config(self, language: str) -> Optional[Dict[str, Any]]:
        """Get VS Code launch configuration for the language"""
        configs = {
            'csharp': {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": ".NET Core Launch",
                        "type": "coreclr",
                        "request": "launch",
                        "program": "${workspaceFolder}/bin/Debug/net8.0/${workspaceFolderBasename}.dll",
                        "args": [],
                        "cwd": "${workspaceFolder}",
                        "console": "internalConsole",
                        "stopAtEntry": False
                    }
                ]
            },
            'java': {
                "version": "0.2.0",
                "configurations": [
                    {
                        "type": "java",
                        "name": "Launch Java Program",
                        "request": "launch",
                        "mainClass": "",
                        "projectName": "${workspaceFolderBasename}"
                    }
                ]
            },
            'python': {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Python: Current File",
                        "type": "python",
                        "request": "launch",
                        "program": "${file}",
                        "console": "integratedTerminal",
                        "justMyCode": True
                    }
                ]
            },
            'javascript': {
                "version": "0.2.0",
                "configurations": [
                    {
                        "type": "node",
                        "request": "launch",
                        "name": "Launch Program",
                        "skipFiles": ["<node_internals>/**"],
                        "program": "${workspaceFolder}/index.js"
                    }
                ]
            }
        }
        
        return configs.get(language.lower())
    
    def _get_tasks_config(self, language: str) -> Optional[Dict[str, Any]]:
        """Get VS Code tasks configuration for the language"""
        configs = {
            'csharp': {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "build",
                        "command": "dotnet",
                        "type": "process",
                        "args": ["build"],
                        "group": {"kind": "build", "isDefault": True}
                    },
                    {
                        "label": "test",
                        "command": "dotnet",
                        "type": "process",
                        "args": ["test"],
                        "group": "test"
                    }
                ]
            },
            'java': {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "compile",
                        "command": "mvn",
                        "type": "shell",
                        "args": ["compile"],
                        "group": {"kind": "build", "isDefault": True}
                    },
                    {
                        "label": "test",
                        "command": "mvn",
                        "type": "shell",
                        "args": ["test"],
                        "group": "test"
                    }
                ]
            },
            'python': {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "python: run tests",
                        "command": "python",
                        "type": "shell",
                        "args": ["-m", "pytest"],
                        "group": "test"
                    }
                ]
            },
            'javascript': {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "npm: test",
                        "command": "npm",
                        "type": "shell",
                        "args": ["test"],
                        "group": "test"
                    },
                    {
                        "label": "npm: build",
                        "command": "npm",
                        "type": "shell",
                        "args": ["run", "build"],
                        "group": {"kind": "build", "isDefault": True}
                    }
                ]
            }
        }
        
        return configs.get(language.lower())
    
    def create_environment_report(self, setup_result: Dict[str, Any]) -> str:
        """Create a detailed environment setup report"""
        report = f"""# Development Environment Setup Report

## Language: {setup_result['language']}
## Project Directory: {setup_result['project_dir']}
## Setup Status: {'✅ Success' if setup_result['success'] else '❌ Issues Found'}

## System Information
- **Operating System**: {self.system_info['os'].title()}
- **Architecture**: {self.system_info['arch']}
- **Python Version**: {self.system_info['python_version']}
- **Platform**: {self.system_info['platform']}

## Tools Installed
"""
        
        for tool in setup_result.get('tools_installed', []):
            report += f"- {tool}\n"
        
        if not setup_result.get('tools_installed'):
            report += "- No tools information available\n"
        
        report += "\n## Environment Configuration\n"
        
        for config in setup_result.get('environment_configured', []):
            report += f"- {config}\n"
        
        if not setup_result.get('environment_configured'):
            report += "- No configuration changes made\n"
        
        if setup_result.get('issues'):
            report += "\n## Issues Found\n"
            for issue in setup_result['issues']:
                report += f"- {issue}\n"
        
        if setup_result.get('next_steps'):
            report += "\n## Next Steps\n"
            for step in setup_result['next_steps']:
                report += f"1. {step}\n"
        
        if setup_result['success']:
            report += "\n## Ready for Development! 🎉\n"
            report += "Your development environment is set up and ready to use.\n"
        else:
            report += "\n## Action Required ⚠️\n"
            report += "Please address the issues listed above before proceeding with development.\n"
        
        return report
