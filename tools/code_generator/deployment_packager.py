"""
Deployment and Packaging Tool

Provides capabilities to package generated applications for deployment,
create Docker containers, and generate deployment scripts.
"""

import os
import subprocess
import json
import shutil
import tarfile
import zipfile
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class DeploymentPackager:
    """Tool for packaging and preparing applications for deployment"""
    
    def __init__(self):
        self.package_commands = {
            'csharp': {
                'build_release': ['dotnet', 'build', '--configuration', 'Release'],
                'publish': ['dotnet', 'publish', '--configuration', 'Release', '--output', 'publish'],
                'pack': ['dotnet', 'pack', '--configuration', 'Release'],
                'self_contained': ['dotnet', 'publish', '--configuration', 'Release', '--self-contained', 'true']
            },
            'java': {
                'package': ['mvn', 'package'],
                'install': ['mvn', 'install'],
                'spring_boot_jar': ['mvn', 'spring-boot:build-image'],
                'fat_jar': ['mvn', 'assembly:single']
            },
            'python': {
                'wheel': ['python', 'setup.py', 'bdist_wheel'],
                'source': ['python', 'setup.py', 'sdist'],
                'requirements': ['pip', 'freeze'],
                'executable': ['pyinstaller', '--onefile']
            },
            'javascript': {
                'build': ['npm', 'run', 'build'],
                'pack': ['npm', 'pack'],
                'webpack': ['npx', 'webpack', '--mode=production']
            },
            'go': {
                'build': ['go', 'build', '-ldflags', '-s -w'],
                'build_all': ['go', 'build', '-o', 'dist/'],
                'mod_vendor': ['go', 'mod', 'vendor']
            },
            'rust': {
                'build_release': ['cargo', 'build', '--release'],
                'package': ['cargo', 'package'],
                'install': ['cargo', 'install', '--path', '.']
            }
        }
    
    def create_deployment_package(self, project_dir: str, language: str, 
                                package_type: str = 'standard') -> Dict[str, Any]:
        """Create a deployment package for the application"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"{os.path.basename(project_dir)}_{language}_{timestamp}"
        package_dir = os.path.join(project_dir, "deployment", package_name)
        
        # Create deployment directory
        os.makedirs(package_dir, exist_ok=True)
        
        result = {
            'success': False,
            'package_name': package_name,
            'package_dir': package_dir,
            'files_created': [],
            'size_mb': 0.0,
            'language': language,
            'package_type': package_type,
            'timestamp': timestamp
        }
        
        try:
            # Language-specific packaging
            if language.lower() in ['csharp', 'c#']:
                result.update(self._package_csharp(project_dir, package_dir, package_type))
            elif language.lower() == 'java':
                result.update(self._package_java(project_dir, package_dir, package_type))
            elif language.lower() == 'python':
                result.update(self._package_python(project_dir, package_dir, package_type))
            elif language.lower() in ['javascript', 'js', 'node.js']:
                result.update(self._package_javascript(project_dir, package_dir, package_type))
            elif language.lower() == 'go':
                result.update(self._package_go(project_dir, package_dir, package_type))
            elif language.lower() == 'rust':
                result.update(self._package_rust(project_dir, package_dir, package_type))
            else:
                result['error'] = f"Packaging not supported for language: {language}"
                return result
            
            # Create deployment metadata
            self._create_deployment_metadata(package_dir, result)
            
            # Calculate package size
            result['size_mb'] = self._calculate_directory_size(package_dir)
            
            # Create archive
            archive_path = f"{package_dir}.zip"
            self._create_archive(package_dir, archive_path)
            result['archive_path'] = archive_path
            result['files_created'].append(archive_path)
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _package_csharp(self, project_dir: str, package_dir: str, package_type: str) -> Dict[str, Any]:
        """Package C# application"""
        result = {'files_created': []}
        
        # Build release version
        build_result = subprocess.run(
            ['dotnet', 'build', '--configuration', 'Release'],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        if build_result.returncode != 0:
            raise Exception(f"Build failed: {build_result.stderr}")
        
        if package_type == 'self_contained':
            # Create self-contained deployment
            for runtime in ['win-x64', 'linux-x64', 'osx-x64']:
                runtime_dir = os.path.join(package_dir, runtime)
                subprocess.run([
                    'dotnet', 'publish', '--configuration', 'Release',
                    '--runtime', runtime, '--self-contained', 'true',
                    '--output', runtime_dir
                ], cwd=project_dir, check=True)
                result['files_created'].append(runtime_dir)
        else:
            # Standard publish
            publish_dir = os.path.join(package_dir, 'publish')
            subprocess.run([
                'dotnet', 'publish', '--configuration', 'Release',
                '--output', publish_dir
            ], cwd=project_dir, check=True)
            result['files_created'].append(publish_dir)
        
        # Copy deployment scripts
        self._create_csharp_deployment_scripts(package_dir)
        
        return result
    
    def _package_java(self, project_dir: str, package_dir: str, package_type: str) -> Dict[str, Any]:
        """Package Java application"""
        result = {'files_created': []}
        
        # Build the project
        build_result = subprocess.run(
            ['mvn', 'clean', 'package'],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        if build_result.returncode != 0:
            raise Exception(f"Build failed: {build_result.stderr}")
        
        # Copy JAR files
        target_dir = os.path.join(project_dir, 'target')
        if os.path.exists(target_dir):
            for file in os.listdir(target_dir):
                if file.endswith('.jar'):
                    src = os.path.join(target_dir, file)
                    dst = os.path.join(package_dir, file)
                    shutil.copy2(src, dst)
                    result['files_created'].append(dst)
        
        # Copy dependencies if needed
        if package_type == 'with_dependencies':
            dep_dir = os.path.join(package_dir, 'lib')
            os.makedirs(dep_dir, exist_ok=True)
            subprocess.run([
                'mvn', 'dependency:copy-dependencies',
                f'-DoutputDirectory={dep_dir}'
            ], cwd=project_dir)
            result['files_created'].append(dep_dir)
        
        # Create deployment scripts
        self._create_java_deployment_scripts(package_dir)
        
        return result
    
    def _package_python(self, project_dir: str, package_dir: str, package_type: str) -> Dict[str, Any]:
        """Package Python application"""
        result = {'files_created': []}
        
        # Copy source files
        src_dir = os.path.join(package_dir, 'src')
        shutil.copytree(project_dir, src_dir, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.git', 'venv', '.env'
        ))
        result['files_created'].append(src_dir)
        
        # Create requirements.txt
        req_file = os.path.join(package_dir, 'requirements.txt')
        req_result = subprocess.run(
            ['pip', 'freeze'],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if req_result.returncode == 0:
            with open(req_file, 'w') as f:
                f.write(req_result.stdout)
            result['files_created'].append(req_file)
        
        # Create virtual environment setup script
        self._create_python_deployment_scripts(package_dir)
        
        if package_type == 'executable':
            # Try to create executable with PyInstaller
            try:
                exe_result = subprocess.run([
                    'pyinstaller', '--onefile', '--distpath', package_dir,
                    os.path.join(project_dir, 'main.py')
                ], capture_output=True, text=True)
                if exe_result.returncode == 0:
                    result['executable_created'] = True
            except FileNotFoundError:
                result['note'] = 'PyInstaller not available for executable creation'
        
        return result
    
    def _package_javascript(self, project_dir: str, package_dir: str, package_type: str) -> Dict[str, Any]:
        """Package JavaScript/Node.js application"""
        result = {'files_created': []}
        
        # Copy package.json
        package_json = os.path.join(project_dir, 'package.json')
        if os.path.exists(package_json):
            shutil.copy2(package_json, package_dir)
            result['files_created'].append(os.path.join(package_dir, 'package.json'))
        
        # Run build if available
        if package_type == 'production':
            build_result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            if build_result.returncode == 0:
                # Copy build output
                build_dirs = ['build', 'dist', 'public']
                for build_dir in build_dirs:
                    src_build = os.path.join(project_dir, build_dir)
                    if os.path.exists(src_build):
                        dst_build = os.path.join(package_dir, build_dir)
                        shutil.copytree(src_build, dst_build)
                        result['files_created'].append(dst_build)
                        break
        
        # Copy source files
        src_files = ['index.js', 'server.js', 'app.js', 'main.js']
        for src_file in src_files:
            src_path = os.path.join(project_dir, src_file)
            if os.path.exists(src_path):
                dst_path = os.path.join(package_dir, src_file)
                shutil.copy2(src_path, dst_path)
                result['files_created'].append(dst_path)
        
        # Create deployment scripts
        self._create_javascript_deployment_scripts(package_dir)
        
        return result
    
    def _package_go(self, project_dir: str, package_dir: str, package_type: str) -> Dict[str, Any]:
        """Package Go application"""
        result = {'files_created': []}
        
        # Build for multiple platforms
        platforms = [
            ('windows', 'amd64', '.exe'),
            ('linux', 'amd64', ''),
            ('darwin', 'amd64', '')
        ]
        
        for goos, goarch, ext in platforms:
            binary_name = f"{os.path.basename(project_dir)}_{goos}_{goarch}{ext}"
            binary_path = os.path.join(package_dir, binary_name)
            
            env = os.environ.copy()
            env['GOOS'] = goos
            env['GOARCH'] = goarch
            
            build_result = subprocess.run([
                'go', 'build', '-ldflags', '-s -w',
                '-o', binary_path
            ], cwd=project_dir, env=env, capture_output=True, text=True)
            
            if build_result.returncode == 0:
                result['files_created'].append(binary_path)
        
        # Copy go.mod and go.sum
        for file in ['go.mod', 'go.sum']:
            src = os.path.join(project_dir, file)
            if os.path.exists(src):
                dst = os.path.join(package_dir, file)
                shutil.copy2(src, dst)
                result['files_created'].append(dst)
        
        # Create deployment scripts
        self._create_go_deployment_scripts(package_dir)
        
        return result
    
    def _package_rust(self, project_dir: str, package_dir: str, package_type: str) -> Dict[str, Any]:
        """Package Rust application"""
        result = {'files_created': []}
        
        # Build release version
        build_result = subprocess.run(
            ['cargo', 'build', '--release'],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        if build_result.returncode != 0:
            raise Exception(f"Build failed: {build_result.stderr}")
        
        # Copy binary
        target_dir = os.path.join(project_dir, 'target', 'release')
        if os.path.exists(target_dir):
            for file in os.listdir(target_dir):
                file_path = os.path.join(target_dir, file)
                if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                    dst = os.path.join(package_dir, file)
                    shutil.copy2(file_path, dst)
                    result['files_created'].append(dst)
        
        # Copy Cargo.toml
        cargo_toml = os.path.join(project_dir, 'Cargo.toml')
        if os.path.exists(cargo_toml):
            shutil.copy2(cargo_toml, package_dir)
            result['files_created'].append(os.path.join(package_dir, 'Cargo.toml'))
        
        # Create deployment scripts
        self._create_rust_deployment_scripts(package_dir)
        
        return result
    
    def create_docker_deployment(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Create Docker deployment configuration"""
        docker_dir = os.path.join(project_dir, 'docker')
        os.makedirs(docker_dir, exist_ok=True)
        
        result = {
            'success': False,
            'dockerfile_path': None,
            'docker_compose_path': None,
            'build_script_path': None,
            'language': language
        }
        
        try:
            # Create Dockerfile
            dockerfile_content = self._generate_dockerfile(language)
            dockerfile_path = os.path.join(docker_dir, 'Dockerfile')
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            result['dockerfile_path'] = dockerfile_path
            
            # Create docker-compose.yml
            compose_content = self._generate_docker_compose(language)
            compose_path = os.path.join(docker_dir, 'docker-compose.yml')
            with open(compose_path, 'w') as f:
                f.write(compose_content)
            result['docker_compose_path'] = compose_path
            
            # Create build script
            build_script_content = self._generate_docker_build_script(language)
            build_script_path = os.path.join(docker_dir, 'build.sh')
            with open(build_script_path, 'w') as f:
                f.write(build_script_content)
            os.chmod(build_script_path, 0o755)
            result['build_script_path'] = build_script_path
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _generate_dockerfile(self, language: str) -> str:
        """Generate Dockerfile content based on language"""
        dockerfiles = {
            'csharp': '''FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["*.csproj", "./"]
RUN dotnet restore
COPY . .
RUN dotnet build -c Release -o /app/build

FROM build AS publish
RUN dotnet publish -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "app.dll"]''',
            
            'java': '''FROM openjdk:11-jre-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]''',
            
            'python': '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]''',
            
            'javascript': '''FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8080
CMD ["node", "index.js"]''',
            
            'go': '''FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]''',
            
            'rust': '''FROM rust:1.70 AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/* ./
EXPOSE 8080
CMD ["./app"]'''
        }
        
        return dockerfiles.get(language.lower(), '# Dockerfile template not available for this language')
    
    def _generate_docker_compose(self, language: str) -> str:
        """Generate docker-compose.yml content"""
        app_name = f"app-{language.lower()}"
        
        return f'''version: '3.8'

services:
  {app_name}:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ENV=production
    restart: unless-stopped
    
  # Add additional services as needed
  # database:
  #   image: postgres:13
  #   environment:
  #     POSTGRES_DB: app_db
  #     POSTGRES_USER: app_user
  #     POSTGRES_PASSWORD: app_password
  #   volumes:
  #     - db_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   db_data:
'''
    
    def _generate_docker_build_script(self, language: str) -> str:
        """Generate Docker build script"""
        app_name = f"app-{language.lower()}"
        
        return f'''#!/bin/bash

# Docker build script for {language} application

APP_NAME="{app_name}"
VERSION="latest"
REGISTRY=""  # Set your registry here

echo "Building Docker image for {language} application..."

# Build the image
docker build -t $APP_NAME:$VERSION .

# Tag for registry if specified
if [ ! -z "$REGISTRY" ]; then
    docker tag $APP_NAME:$VERSION $REGISTRY/$APP_NAME:$VERSION
    echo "Tagged image: $REGISTRY/$APP_NAME:$VERSION"
fi

echo "Build completed successfully!"
echo "To run: docker run -p 8080:8080 $APP_NAME:$VERSION"
echo "To run with compose: docker-compose up"

# Optional: Push to registry
# if [ ! -z "$REGISTRY" ]; then
#     echo "Pushing to registry..."
#     docker push $REGISTRY/$APP_NAME:$VERSION
# fi
'''
    
    def _create_deployment_metadata(self, package_dir: str, result: Dict[str, Any]) -> None:
        """Create deployment metadata file"""
        metadata = {
            'package_info': {
                'name': result['package_name'],
                'language': result['language'],
                'package_type': result['package_type'],
                'created_at': result['timestamp'],
                'created_by': 'BugBashAgent Code Generator'
            },
            'deployment_instructions': self._get_deployment_instructions(result['language']),
            'files_included': result['files_created'],
            'system_requirements': self._get_system_requirements(result['language'])
        }
        
        metadata_path = os.path.join(package_dir, 'deployment_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        result['files_created'].append(metadata_path)
    
    def _get_deployment_instructions(self, language: str) -> List[str]:
        """Get deployment instructions for the language"""
        instructions = {
            'csharp': [
                "1. Ensure .NET 8.0 runtime is installed on target system",
                "2. Copy all files to target directory",
                "3. Run: dotnet <AppName>.dll",
                "4. For self-contained: Run the executable directly"
            ],
            'java': [
                "1. Ensure Java 11+ is installed on target system",
                "2. Copy JAR file to target directory",
                "3. Run: java -jar <AppName>.jar",
                "4. For dependencies: Include lib/ directory in classpath"
            ],
            'python': [
                "1. Ensure Python 3.8+ is installed on target system",
                "2. Create virtual environment: python -m venv venv",
                "3. Activate virtual environment",
                "4. Install dependencies: pip install -r requirements.txt",
                "5. Run: python main.py"
            ],
            'javascript': [
                "1. Ensure Node.js 16+ is installed on target system",
                "2. Copy all files to target directory",
                "3. Install dependencies: npm install",
                "4. Run: npm start or node index.js"
            ],
            'go': [
                "1. Copy appropriate binary for target platform",
                "2. Make executable: chmod +x <binary>",
                "3. Run: ./<binary>",
                "4. No additional dependencies required"
            ],
            'rust': [
                "1. Copy binary to target directory",
                "2. Make executable: chmod +x <binary>",
                "3. Run: ./<binary>",
                "4. No additional dependencies required"
            ]
        }
        
        return instructions.get(language.lower(), ["Deployment instructions not available"])
    
    def _get_system_requirements(self, language: str) -> Dict[str, Any]:
        """Get system requirements for the language"""
        requirements = {
            'csharp': {
                'runtime': '.NET 8.0 Runtime',
                'os': 'Windows, Linux, macOS',
                'memory': '512MB minimum',
                'disk': '100MB'
            },
            'java': {
                'runtime': 'Java 11+ JRE',
                'os': 'Windows, Linux, macOS',
                'memory': '512MB minimum',
                'disk': '200MB'
            },
            'python': {
                'runtime': 'Python 3.8+',
                'os': 'Windows, Linux, macOS',
                'memory': '256MB minimum',
                'disk': '100MB'
            },
            'javascript': {
                'runtime': 'Node.js 16+',
                'os': 'Windows, Linux, macOS',
                'memory': '256MB minimum',
                'disk': '100MB'
            },
            'go': {
                'runtime': 'None (static binary)',
                'os': 'Platform-specific binary',
                'memory': '64MB minimum',
                'disk': '20MB'
            },
            'rust': {
                'runtime': 'None (static binary)',
                'os': 'Platform-specific binary',
                'memory': '64MB minimum',
                'disk': '20MB'
            }
        }
        
        return requirements.get(language.lower(), {})
    
    def _calculate_directory_size(self, directory: str) -> float:
        """Calculate directory size in MB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)  # Convert to MB
    
    def _create_archive(self, source_dir: str, archive_path: str) -> None:
        """Create ZIP archive of the deployment package"""
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arc_name)
    
    def _create_csharp_deployment_scripts(self, package_dir: str) -> None:
        """Create C# deployment scripts"""
        # Windows batch script
        bat_content = '''@echo off
echo Starting .NET application...
dotnet publish\\*.dll
pause
'''
        with open(os.path.join(package_dir, 'run.bat'), 'w') as f:
            f.write(bat_content)
        
        # Linux shell script
        sh_content = '''#!/bin/bash
echo "Starting .NET application..."
dotnet publish/*.dll
'''
        sh_path = os.path.join(package_dir, 'run.sh')
        with open(sh_path, 'w') as f:
            f.write(sh_content)
        os.chmod(sh_path, 0o755)
    
    def _create_java_deployment_scripts(self, package_dir: str) -> None:
        """Create Java deployment scripts"""
        # Windows batch script
        bat_content = '''@echo off
echo Starting Java application...
java -jar *.jar
pause
'''
        with open(os.path.join(package_dir, 'run.bat'), 'w') as f:
            f.write(bat_content)
        
        # Linux shell script
        sh_content = '''#!/bin/bash
echo "Starting Java application..."
java -jar *.jar
'''
        sh_path = os.path.join(package_dir, 'run.sh')
        with open(sh_path, 'w') as f:
            f.write(sh_content)
        os.chmod(sh_path, 0o755)
    
    def _create_python_deployment_scripts(self, package_dir: str) -> None:
        """Create Python deployment scripts"""
        # Setup script
        setup_content = '''#!/bin/bash
echo "Setting up Python environment..."
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
echo "Setup complete! Run 'source venv/bin/activate && python src/main.py' to start"
'''
        setup_path = os.path.join(package_dir, 'setup.sh')
        with open(setup_path, 'w') as f:
            f.write(setup_content)
        os.chmod(setup_path, 0o755)
        
        # Run script
        run_content = '''#!/bin/bash
source venv/bin/activate
python src/main.py
'''
        run_path = os.path.join(package_dir, 'run.sh')
        with open(run_path, 'w') as f:
            f.write(run_content)
        os.chmod(run_path, 0o755)
    
    def _create_javascript_deployment_scripts(self, package_dir: str) -> None:
        """Create JavaScript deployment scripts"""
        # Package.json for production
        package_json = {
            "scripts": {
                "start": "node index.js",
                "install": "npm install --production",
                "setup": "npm install"
            }
        }
        
        with open(os.path.join(package_dir, 'package_deployment.json'), 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Setup script
        setup_content = '''#!/bin/bash
echo "Setting up Node.js application..."
npm install --production
echo "Setup complete! Run 'npm start' to start the application"
'''
        setup_path = os.path.join(package_dir, 'setup.sh')
        with open(setup_path, 'w') as f:
            f.write(setup_content)
        os.chmod(setup_path, 0o755)
    
    def _create_go_deployment_scripts(self, package_dir: str) -> None:
        """Create Go deployment scripts"""
        # Run script for different platforms
        platforms = ['windows', 'linux', 'darwin']
        
        for platform in platforms:
            if platform == 'windows':
                script_content = f'''@echo off
echo Starting Go application...
{os.path.basename(package_dir)}_{platform}_amd64.exe
pause
'''
                with open(os.path.join(package_dir, f'run_{platform}.bat'), 'w') as f:
                    f.write(script_content)
            else:
                script_content = f'''#!/bin/bash
echo "Starting Go application..."
./{os.path.basename(package_dir)}_{platform}_amd64
'''
                script_path = os.path.join(package_dir, f'run_{platform}.sh')
                with open(script_path, 'w') as f:
                    f.write(script_content)
                os.chmod(script_path, 0o755)
    
    def _create_rust_deployment_scripts(self, package_dir: str) -> None:
        """Create Rust deployment scripts"""
        # Simple run script
        run_content = '''#!/bin/bash
echo "Starting Rust application..."
./target/release/*
'''
        run_path = os.path.join(package_dir, 'run.sh')
        with open(run_path, 'w') as f:
            f.write(run_content)
        os.chmod(run_path, 0o755)
