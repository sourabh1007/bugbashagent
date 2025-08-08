"""
Centralized Package Versions Configuration

This file contains all package versions used across all language generators.
Update versions here to maintain consistency across the entire codebase.
"""

import os
from typing import Dict, Any


class PackageVersions:
    """Centralized package version management"""
    
    # Language Runtime Versions (from environment variables with defaults)
    LANGUAGE_VERSIONS = {
        'dotnet': os.getenv('DOTNET_VERSION', '8.0'),
        'java': os.getenv('JAVA_VERSION', '17'),
        'node': os.getenv('NODE_VERSION', '18'),
        'python': os.getenv('PYTHON_VERSION', '3.11'),
        'go': os.getenv('GO_VERSION', '1.21'),
        'rust': os.getenv('RUST_VERSION', '1.70'),
    }
    
    # Dynamic package versions that depend on document analyzer output
    _dynamic_packages = {
        'cosmosdb_version': None  # Will be set by document analyzer
    }
    
    # C# / .NET Test Framework Dependencies Only
    CSHARP_TEST_PACKAGES = {
        # Primary testing framework - NUnit (recommended)
        'NUnit': '3.14.0',
        'NUnit3TestAdapter': '4.5.0',
        'Microsoft.NET.Test.Sdk': '17.8.0',
        # Assertion library
        'FluentAssertions': '6.12.0',
        # Mocking framework
        'Moq': '4.20.69',
        # Integration testing
        'Microsoft.AspNetCore.Mvc.Testing': '8.0.0',
    }
    
    # Python Test Framework Dependencies Only
    PYTHON_TEST_PACKAGES = {
        # Primary testing framework - pytest (recommended)
        'pytest': '7.4.3',
        'pytest-mock': '3.12.0',
        'pytest-asyncio': '0.21.1',
        'pytest-cov': '4.1.0',  # Coverage support
        # Alternative testing framework - unittest (built-in, no version needed)
        # Additional test utilities
        'factory-boy': '3.3.0',  # Test data factories
        'freezegun': '1.2.2',    # Time mocking
    }
    
    # JavaScript/Node.js Test Framework Dependencies Only
    JAVASCRIPT_TEST_PACKAGES = {
        # Primary testing framework - Jest (recommended)
        'jest': '^29.7.0',
        '@jest/globals': '^29.7.0',
        # Alternative testing framework - Mocha + Chai
        'mocha': '^10.2.0',
        'chai': '^4.3.10',
        # HTTP testing
        'supertest': '^6.3.3',
        # Test utilities
        'sinon': '^17.0.1',      # Mocking/stubbing
        'nock': '^13.4.0',       # HTTP mocking
        # Development/test support
        'nodemon': '^3.0.1',     # Development server
    }
    
    # Java Test Framework Dependencies Only (Maven)
    JAVA_TEST_PACKAGES = {
        # Primary testing framework - JUnit 5 (recommended)
        'junit.version': '5.10.1',
        'junit-platform.version': '1.10.1',
        # Mocking framework
        'mockito.version': '5.8.0',
        # Assertion library
        'assertj.version': '3.24.2',
        # Spring testing (if using Spring)
        'spring.boot.test.version': '3.2.0',
        # Test containers for integration testing
        'testcontainers.version': '1.19.3',
    }
    
    # Go Test Framework Dependencies Only
    GO_TEST_PACKAGES = {
        # Primary testing framework - built-in testing (no external dependency needed)
        # Additional testing utilities
        'stretchr/testify': 'v1.8.4',      # Assertion library
        'golang/mock': 'v1.6.0',           # Mocking framework
        'DATA-DOG/go-sqlmock': 'v1.5.0',   # SQL mocking
        'onsi/ginkgo/v2': 'v2.13.2',       # BDD testing framework (alternative)
        'onsi/gomega': 'v1.30.0',          # Matcher library for Ginkgo
    }
    
    # Rust Test Framework Dependencies Only (Cargo)
    RUST_TEST_PACKAGES = {
        # Primary testing framework - built-in testing (no external dependency needed)
        # Additional testing utilities
        'tokio-test': {'version': '0.4', 'features': []},    # Async testing
        'mockall': '0.12',                                   # Mocking framework
        'serial_test': '3.0',                               # Sequential test execution
        'proptest': '1.4',                                   # Property-based testing
        'criterion': '0.5',                                  # Benchmarking
    }
    
    @classmethod
    def get_language_version(cls, language: str) -> str:
        """Get the configured version for a specific language"""
        return cls.LANGUAGE_VERSIONS.get(language.lower(), 'latest')
    
    @classmethod
    def get_csharp_test_packages(cls) -> Dict[str, str]:
        """Get all C# test framework package versions"""
        return cls.CSHARP_TEST_PACKAGES.copy()
    
    @classmethod
    def get_python_test_packages(cls) -> Dict[str, str]:
        """Get all Python test framework package versions"""
        return cls.PYTHON_TEST_PACKAGES.copy()
    
    @classmethod
    def get_javascript_test_packages(cls) -> Dict[str, str]:
        """Get all JavaScript test framework package versions"""
        return cls.JAVASCRIPT_TEST_PACKAGES.copy()
    
    @classmethod
    def get_java_test_packages(cls) -> Dict[str, str]:
        """Get all Java test framework package versions"""
        return cls.JAVA_TEST_PACKAGES.copy()
    
    @classmethod
    def get_go_test_packages(cls) -> Dict[str, str]:
        """Get all Go test framework package versions"""
        return cls.GO_TEST_PACKAGES.copy()
    
    @classmethod
    def get_rust_test_packages(cls) -> Dict[str, Any]:
        """Get all Rust test framework package versions"""
        return cls.RUST_TEST_PACKAGES.copy()
    
    @classmethod
    def get_test_packages_for_language(cls, language: str) -> Dict[str, Any]:
        """Get test framework package versions for a specific language"""
        language_lower = language.lower()
        if language_lower in ['csharp', 'c#']:
            return cls.get_csharp_test_packages()
        elif language_lower == 'python':
            return cls.get_python_test_packages()
        elif language_lower in ['javascript', 'js', 'node.js']:
            return cls.get_javascript_test_packages()
        elif language_lower == 'java':
            return cls.get_java_test_packages()
        elif language_lower == 'go':
            return cls.get_go_test_packages()
        elif language_lower == 'rust':
            return cls.get_rust_test_packages()
        else:
            return {}
    
    @classmethod
    def get_primary_test_framework(cls, language: str) -> str:
        """Get the recommended primary test framework for a language"""
        language_lower = language.lower()
        frameworks = {
            'csharp': 'nunit',
            'c#': 'nunit', 
            'python': 'pytest',
            'javascript': 'jest',
            'js': 'jest',
            'node.js': 'jest',
            'java': 'junit5',
            'go': 'testing',  # Built-in Go testing
            'rust': 'testing'  # Built-in Rust testing
        }
        return frameworks.get(language_lower, 'unknown')
    
    @classmethod
    def update_test_package_version(cls, language: str, package_name: str, version: str) -> None:
        """Update a specific test package version (runtime modification)"""
        language_lower = language.lower()
        if language_lower in ['csharp', 'c#'] and hasattr(cls, 'CSHARP_TEST_PACKAGES'):
            cls.CSHARP_TEST_PACKAGES[package_name] = version
        elif language_lower == 'python' and hasattr(cls, 'PYTHON_TEST_PACKAGES'):
            cls.PYTHON_TEST_PACKAGES[package_name] = version
        elif language_lower in ['javascript', 'js', 'node.js'] and hasattr(cls, 'JAVASCRIPT_TEST_PACKAGES'):
            cls.JAVASCRIPT_TEST_PACKAGES[package_name] = version
        elif language_lower == 'java' and hasattr(cls, 'JAVA_TEST_PACKAGES'):
            cls.JAVA_TEST_PACKAGES[package_name] = version
        elif language_lower == 'go' and hasattr(cls, 'GO_TEST_PACKAGES'):
            cls.GO_TEST_PACKAGES[package_name] = version
        elif language_lower == 'rust' and hasattr(cls, 'RUST_TEST_PACKAGES'):
            cls.RUST_TEST_PACKAGES[package_name] = version
    
    @classmethod
    def set_cosmosdb_version_from_analyzer(cls, analyzer_output: Dict[str, Any]) -> None:
        """Set CosmosDB version based on document analyzer output"""
        # Extract CosmosDB version from analyzer output
        cosmosdb_version = None
        
        # Check for CosmosDB version in different possible locations
        if isinstance(analyzer_output, dict):
            # Check direct cosmosdb_version field
            cosmosdb_version = analyzer_output.get('cosmosdb_version')
            
            # Check in projectsetupInfo
            setup_info = analyzer_output.get('projectsetupInfo', {})
            if isinstance(setup_info, dict):
                cosmosdb_version = setup_info.get('cosmosdb_version') or cosmosdb_version
                
                # Check in dependencies array
                dependencies = setup_info.get('dependencies', [])
                if isinstance(dependencies, list):
                    for dep in dependencies:
                        if isinstance(dep, dict):
                            if dep.get('name', '').lower() in ['cosmosdb', 'azure.cosmosdb', 'microsoft.azure.cosmos']:
                                cosmosdb_version = dep.get('version') or cosmosdb_version
                        elif isinstance(dep, str) and 'cosmos' in dep.lower():
                            # Try to extract version from string like "CosmosDB v3.35.4"
                            import re
                            version_match = re.search(r'v?(\d+\.\d+\.\d+)', dep)
                            if version_match:
                                cosmosdb_version = version_match.group(1)
            
            # Check in technology stack or requirements
            tech_stack = analyzer_output.get('technologyStack', [])
            if isinstance(tech_stack, list):
                for tech in tech_stack:
                    if isinstance(tech, str) and 'cosmos' in tech.lower():
                        import re
                        version_match = re.search(r'v?(\d+\.\d+\.\d+)', tech)
                        if version_match:
                            cosmosdb_version = version_match.group(1)
        
        # Set the CosmosDB version
        if cosmosdb_version:
            cls._dynamic_packages['cosmosdb_version'] = cosmosdb_version
            print(f"🌟 CosmosDB version set from analyzer: {cosmosdb_version}")
        else:
            # Use default version if not found in analyzer output
            cls._dynamic_packages['cosmosdb_version'] = '3.35.4'  # Default latest version
            print("⚠️  No CosmosDB version found in analyzer output, using default: 3.35.4")
    
    @classmethod
    def get_cosmosdb_version(cls) -> str:
        """Get the CosmosDB version (either from analyzer or default)"""
        return cls._dynamic_packages.get('cosmosdb_version', '3.35.4')
    
    @classmethod
    def get_test_packages_with_cosmosdb(cls, language: str, analyzer_output: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get test framework packages for a language, including dynamic CosmosDB version if applicable"""
        packages = cls.get_test_packages_for_language(language)
        
        # Update CosmosDB version from analyzer if provided
        if analyzer_output:
            cls.set_cosmosdb_version_from_analyzer(analyzer_output)
        
        # Add CosmosDB packages based on language (for integration testing)
        cosmosdb_version = cls.get_cosmosdb_version()
        language_lower = language.lower()
        
        if language_lower in ['csharp', 'c#']:
            packages['Microsoft.Azure.Cosmos'] = cosmosdb_version
        elif language_lower == 'python':
            packages['azure-cosmos'] = cosmosdb_version
        elif language_lower in ['javascript', 'js', 'node.js']:
            packages['@azure/cosmos'] = f"^{cosmosdb_version}"
        elif language_lower == 'java':
            packages['azure-cosmos.version'] = cosmosdb_version
        elif language_lower == 'go':
            packages['github.com/Azure/azure-sdk-for-go/sdk/data/azcosmos'] = f"v{cosmosdb_version}"
        elif language_lower == 'rust':
            packages['azure_cosmos'] = cosmosdb_version
        
        return packages
    
    @classmethod
    def detect_dependencies_from_scenario(cls, analyzer_output: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        Analyze scenario output and suggest dependencies for each language.
        This method identifies required packages based on the scenario requirements.
        """
        dependencies = {
            'csharp': {},
            'python': {},
            'javascript': {},
            'java': {},
            'go': {},
            'rust': {}
        }
        
        if not isinstance(analyzer_output, dict):
            return dependencies
            
        # Extract scenario information
        scenarios = analyzer_output.get('scenarioList', [])
        setup_info = analyzer_output.get('projectsetupInfo', {})
        technology_stack = analyzer_output.get('technologyStack', [])
        
        # Combine all text for analysis
        analysis_text = ' '.join([
            str(scenarios),
            str(setup_info),
            str(technology_stack),
            analyzer_output.get('description', ''),
            analyzer_output.get('requirements', '')
        ]).lower()
        
        # Web framework detection
        if any(keyword in analysis_text for keyword in ['web', 'api', 'http', 'rest', 'web service', 'endpoint']):
            dependencies['csharp']['Microsoft.AspNetCore.App'] = '8.0.0'
            dependencies['python']['fastapi'] = '0.104.1'
            dependencies['python']['uvicorn'] = '0.24.0' 
            dependencies['javascript']['express'] = '^4.18.2'
            dependencies['java']['spring.boot.version'] = '3.2.0'
            dependencies['go']['gin-gonic/gin'] = 'v1.9.1'
            dependencies['rust']['axum'] = '0.7'
            
        # Database detection
        if any(keyword in analysis_text for keyword in ['database', 'sql', 'db', 'data', 'storage']):
            dependencies['csharp']['Microsoft.EntityFrameworkCore'] = '8.0.0'
            dependencies['python']['sqlalchemy'] = '2.0.23'
            dependencies['javascript']['sequelize'] = '^6.35.0'
            dependencies['java']['spring-data-jpa.version'] = '3.2.0'
            dependencies['go']['gorm.io/gorm'] = 'v1.25.5'
            dependencies['rust']['sqlx'] = {'version': '0.7', 'features': ['runtime-tokio-rustls']}
            
        # PostgreSQL specific
        if 'postgres' in analysis_text or 'postgresql' in analysis_text:
            dependencies['csharp']['Npgsql.EntityFrameworkCore.PostgreSQL'] = '8.0.0'
            dependencies['python']['psycopg2-binary'] = '2.9.9'
            dependencies['javascript']['pg'] = '^8.11.3'
            dependencies['java']['postgresql.version'] = '42.7.1'
            dependencies['go']['gorm.io/driver/postgres'] = 'v1.5.4'
            
        # MongoDB detection
        if 'mongo' in analysis_text:
            dependencies['csharp']['MongoDB.Driver'] = '2.22.0'
            dependencies['python']['pymongo'] = '4.6.0'
            dependencies['javascript']['mongoose'] = '^8.0.3'
            dependencies['java']['mongodb-driver-sync.version'] = '4.11.1'
            dependencies['go']['go.mongodb.org/mongo-driver'] = 'v1.13.1'
            dependencies['rust']['mongodb'] = '2.7'
            
        # CosmosDB detection
        if 'cosmos' in analysis_text:
            cosmosdb_version = cls.get_cosmosdb_version()
            dependencies['csharp']['Microsoft.Azure.Cosmos'] = cosmosdb_version
            dependencies['python']['azure-cosmos'] = cosmosdb_version
            dependencies['javascript']['@azure/cosmos'] = f'^{cosmosdb_version}'
            dependencies['java']['azure-cosmos.version'] = cosmosdb_version
            
        # JSON processing
        if any(keyword in analysis_text for keyword in ['json', 'serialize', 'deserialize']):
            dependencies['csharp']['Newtonsoft.Json'] = '13.0.3'
            dependencies['python']['pydantic'] = '2.5.0'
            dependencies['java']['jackson.version'] = '2.16.0'
            dependencies['rust']['serde_json'] = '1.0'
            
        # HTTP client detection
        if any(keyword in analysis_text for keyword in ['http client', 'api call', 'request', 'client']):
            dependencies['csharp']['RestSharp'] = '110.2.0'
            dependencies['python']['requests'] = '2.31.0'
            dependencies['javascript']['axios'] = '^1.6.2'
            dependencies['java']['httpclient5.version'] = '5.3'
            dependencies['go']['go-resty/resty/v2'] = 'v2.10.0'
            dependencies['rust']['reqwest'] = {'version': '0.11', 'features': ['json']}
            
        # Logging detection
        if any(keyword in analysis_text for keyword in ['log', 'logging', 'trace']):
            dependencies['csharp']['Microsoft.Extensions.Logging'] = '8.0.0'
            dependencies['python']['loguru'] = '0.7.2'
            dependencies['javascript']['winston'] = '^3.11.0'
            dependencies['java']['slf4j.version'] = '2.0.9'
            dependencies['go']['go.uber.org/zap'] = 'v1.26.0'
            dependencies['rust']['tracing'] = '0.1'
            
        # Configuration management
        if any(keyword in analysis_text for keyword in ['config', 'settings', 'environment']):
            dependencies['csharp']['Microsoft.Extensions.Configuration'] = '8.0.0'
            dependencies['python']['python-dotenv'] = '1.0.0'
            dependencies['javascript']['dotenv'] = '^16.3.1'
            dependencies['go']['spf13/viper'] = 'v1.17.0'
            dependencies['rust']['config'] = '0.13'
            
        # Async/concurrency detection
        if any(keyword in analysis_text for keyword in ['async', 'concurrent', 'parallel', 'background']):
            dependencies['python']['asyncio'] = ''  # Built-in, no version
            dependencies['javascript']['async'] = '^3.2.5'
            dependencies['rust']['tokio'] = {'version': '1.35', 'features': ['full']}
            
        return dependencies
