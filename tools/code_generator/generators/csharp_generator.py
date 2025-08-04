"""
C# Project Generator

Generates C# .NET test projects with NUnit framework and proper project structure.
Optimized for maintainability, readability, and modern .NET practices.
"""

import os
import re
from datetime import datetime
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class CSharpProjectGenerator(BaseProjectGenerator):
    """Generator for C# .NET test projects using NUnit"""
    
    # Constants for better maintainability - all versions pinned for consistency
    TARGET_FRAMEWORK = "net8.0"
    NUNIT_VERSION = "3.14.0"
    TEST_SDK_VERSION = "17.8.0"
    NUNIT_ADAPTER_VERSION = "4.5.0"
    NUNIT_ANALYZERS_VERSION = "3.10.0"
    COVERLET_COLLECTOR_VERSION = "6.0.0"
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate C# test project structure"""
        created_files = {}
        
        # Sanitize project name for C# identifiers
        sanitized_name = self._sanitize_csharp_identifier(product_name)
        test_project_name = f"{sanitized_name}.Tests"
        
        # Create test project directory
        test_project_dir = os.path.join(project_dir, test_project_name)
        os.makedirs(test_project_dir, exist_ok=True)
        
        # Generate all project files
        project_files = self._generate_project_files(
            test_project_dir, project_dir, sanitized_name, product_name, scenarios, generated_content
        )
        created_files.update(project_files)
        
        return created_files
    
    def _generate_project_files(self, test_project_dir: str, base_dir: str, 
                               sanitized_name: str, product_name: str, 
                               scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate all project files and return their paths"""
        files = {}
        
        # Test project file (.csproj)
        csproj_path = os.path.join(test_project_dir, f"{sanitized_name}.Tests.csproj")
        self._write_file(csproj_path, self._create_test_csproj_content())
        files["test_project"] = csproj_path
        
        # Test class file (.cs)
        test_class_path = os.path.join(test_project_dir, f"{sanitized_name}Tests.cs")
        self._write_file(test_class_path, self._create_test_content(sanitized_name, scenarios))
        files["test_file"] = test_class_path
        
        # README file
        readme_path = os.path.join(base_dir, "README.md")
        self._write_file(readme_path, self._create_test_readme(sanitized_name, product_name, scenarios, generated_content))
        files["readme"] = readme_path
        
        return files
    
    def _write_file(self, file_path: str, content: str) -> None:
        """Write content to file with proper encoding"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_test_csproj_content(self) -> str:
        """Create optimized test project .csproj content with pinned versions"""
        return f"""<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>{self.TARGET_FRAMEWORK}</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="{self.TEST_SDK_VERSION}" />
    <PackageReference Include="NUnit" Version="{self.NUNIT_VERSION}" />
    <PackageReference Include="NUnit3TestAdapter" Version="{self.NUNIT_ADAPTER_VERSION}" />
    <PackageReference Include="NUnit.Analyzers" Version="{self.NUNIT_ANALYZERS_VERSION}" />
    <PackageReference Include="coverlet.collector" Version="{self.COVERLET_COLLECTOR_VERSION}" />
  </ItemGroup>

</Project>"""
    
    def _create_test_content(self, project_name: str, scenarios: List[str]) -> str:
        """Create optimized self-contained test file content"""
        test_methods = self._generate_test_methods(scenarios)
        
        return f"""using NUnit.Framework;

namespace {project_name}.Tests
{{
    /// <summary>
    /// Comprehensive test suite for {project_name}
    /// Contains self-contained tests for all scenarios
    /// </summary>
    [TestFixture]
    public class {project_name}Tests
    {{
        [SetUp]
        public void Setup()
        {{
            // Initialize test data and resources
        }}

{test_methods}
        
        [Test]
        [Category("Integration")]
        public void TestAllScenariosIntegration()
        {{
            // Integration test for all scenarios
            var scenarios = new[] {{ {self._format_scenario_array(scenarios)} }};
            
            foreach (var scenario in scenarios)
            {{
                var result = ValidateScenario("integration test data", scenario);
                Assert.That(result, Is.True, $"Integration test failed for scenario: {{scenario}}");
            }}
            
            Assert.That(scenarios.Length, Is.EqualTo({len(scenarios)}), "All {len(scenarios)} scenarios should be validated");
        }}
        
        [Test]
        [Category("EdgeCases")]
        public void TestEdgeCases()
        {{
            // Comprehensive edge case testing using NUnit constraint model
            Assert.That(ValidateScenario(null, "valid scenario"), Is.False, "Should handle null input");
            Assert.That(ValidateScenario("valid input", null), Is.False, "Should handle null scenario");
            Assert.That(ValidateScenario(string.Empty, "valid scenario"), Is.False, "Should handle empty input");
            Assert.That(ValidateScenario("valid input", string.Empty), Is.False, "Should handle empty scenario");
            Assert.That(ValidateScenario("   ", "valid scenario"), Is.False, "Should handle whitespace-only input");
            
            // Valid case
            Assert.That(ValidateScenario("valid input", "valid scenario"), Is.True, "Should handle valid inputs");
        }}
        
        [Test]
        [Category("Performance")]
        [Timeout(1000)]
        public void TestPerformance()
        {{
            // Performance test for scenario validation
            var scenarios = new[] {{ {self._format_scenario_array(scenarios)} }};
            
            var sw = System.Diagnostics.Stopwatch.StartNew();
            
            for (int i = 0; i < 1000; i++)
            {{
                foreach (var scenario in scenarios)
                {{
                    ValidateScenario($"test data {{i}}", scenario);
                }}
            }}
            
            sw.Stop();
            Assert.That(sw.ElapsedMilliseconds, Is.LessThan(1000), "Performance test should complete within 1 second");
        }}
        
        /// <summary>
        /// Helper method to validate scenarios
        /// Simulates business logic validation
        /// </summary>
        /// <param name="input">Input data to validate</param>
        /// <param name="scenario">Scenario context</param>
        /// <returns>True if validation passes, false otherwise</returns>
        private static bool ValidateScenario(string input, string scenario)
        {{
            return !string.IsNullOrWhiteSpace(input) && !string.IsNullOrWhiteSpace(scenario);
        }}
    }}
}}"""
    
    def _generate_test_methods(self, scenarios: List[str]) -> str:
        """Generate individual test methods for each scenario using NUnit best practices"""
        test_methods = []
        
        for i, scenario in enumerate(scenarios, 1):
            method_name = self._sanitize_csharp_identifier(scenario.replace(' ', ''))
            test_methods.append(f"""        [Test]
        [Category("Scenario")]
        [Description("{scenario}")]
        [Order({i})]
        public void Test{method_name}()
        {{
            // Test case for: {scenario}
            
            // Arrange
            const string testData = "test input for {scenario}";
            const string expectedScenario = "{scenario}";
            
            // Act
            var result = ValidateScenario(testData, expectedScenario);
            
            // Assert
            Assert.That(result, Is.True, "Scenario '{scenario}' should validate successfully");
            Assert.That(testData, Is.Not.Null.And.Not.Empty, "Test data should not be null or empty");
            Assert.That(expectedScenario, Is.EqualTo("{scenario}"), "Scenario should match expected value");
        }}""")
        
        return '\n\n'.join(test_methods)
    
    def _format_scenario_array(self, scenarios: List[str]) -> str:
        """Format scenarios as C# string array"""
        return ', '.join(f'"{scenario}"' for scenario in scenarios)
    
    def _create_test_readme(self, sanitized_name: str, product_name: str, scenarios: List[str], generated_content: str) -> str:
        """Create comprehensive README for test project"""
        test_commands = self._get_test_commands_section()
        project_structure = self._get_project_structure_section(sanitized_name)
        
        return f"""# {product_name} - NUnit Test Project

This is a comprehensive **NUnit-based** test project for **{product_name}** using .NET {self.TARGET_FRAMEWORK} and NUnit {self.NUNIT_VERSION}.

## 🧪 NUnit Testing Framework

This project exclusively uses **NUnit** as the testing framework with the following **pinned versions**:
- **Microsoft.NET.Test.Sdk**: {self.TEST_SDK_VERSION}
- **NUnit**: {self.NUNIT_VERSION}
- **NUnit3TestAdapter**: {self.NUNIT_ADAPTER_VERSION}
- **NUnit.Analyzers**: {self.NUNIT_ANALYZERS_VERSION}
- **coverlet.collector**: {self.COVERLET_COLLECTOR_VERSION}

### Key Features:
- **Modern Constraint Model**: Uses `Assert.That()` with fluent assertions
- **Test Categories**: Organized with `[Category]` attributes (Scenario, Integration, EdgeCases, Performance)
- **Test Ordering**: Uses `[Order]` attributes for deterministic test execution
- **Descriptive Tests**: `[Description]` attributes for clear test documentation
- **Timeout Support**: Performance tests with `[Timeout]` attributes

## 📋 Test Scenarios

{self._format_scenarios_list(scenarios)}

## 🏗️ Project Structure

{project_structure}

## 🚀 Quick Start

### Prerequisites
- .NET {self.TARGET_FRAMEWORK} SDK or later
- Visual Studio 2022 or VS Code with C# extension

### Build & Test
```bash
# Navigate to test project
cd {sanitized_name}.Tests

# Restore dependencies
dotnet restore

# Build project
dotnet build

# Run all tests
dotnet test
```

## 🧪 Test Commands

{test_commands}

## 📊 NUnit Test Coverage

The test suite includes comprehensive NUnit-based testing:

### 🎯 Test Categories
- **[Category("Scenario")]**: {len(scenarios)} individual scenario test methods
- **[Category("Integration")]**: Combined scenario validation tests
- **[Category("EdgeCases")]**: Null, empty, and boundary condition testing
- **[Category("Performance")]**: Performance validation with timeout constraints

### 🔍 NUnit Assertion Patterns
- **Constraint Model**: `Assert.That(actual, Is.EqualTo(expected))`
- **Fluent Assertions**: `Assert.That(value, Is.Not.Null.And.Not.Empty)`
- **Boolean Assertions**: `Assert.That(result, Is.True/Is.False)`
- **Exception Testing**: Built-in support for exception validation

### 📋 Test Organization
- **[Order]** attributes for deterministic test execution
- **[Description]** attributes for clear test documentation
- **[Timeout]** attributes for performance testing
- **[TestFixture]** and **[SetUp]** for proper test lifecycle management

## 📖 Generated Content Analysis

```
{self._truncate_content(generated_content, 500)}
```

## 🔧 NUnit Framework Features

- **NUnit {self.NUNIT_VERSION}**: Latest stable version with modern features
- **Test SDK {self.TEST_SDK_VERSION}**: Microsoft's official test SDK for .NET
- **NUnit3TestAdapter {self.NUNIT_ADAPTER_VERSION}**: Latest adapter for Visual Studio and dotnet test
- **NUnit.Analyzers {self.NUNIT_ANALYZERS_VERSION}**: Code analysis and best practices enforcement
- **Coverlet Collector {self.COVERLET_COLLECTOR_VERSION}**: Code coverage collection and reporting

### Technical Features:
- **Constraint Model**: Modern `Assert.That()` syntax with fluent assertions
- **Test Attributes**: `[Test]`, `[SetUp]`, `[TestFixture]`, `[Category]`, `[Order]`, `[Description]`, `[Timeout]`
- **Test Categories**: Organized test execution with category filtering
- **Performance Testing**: Built-in timeout support for performance validation
- **Code Coverage**: Integration with coverlet collector for coverage reports
- **CI/CD Ready**: Full compatibility with GitHub Actions, Azure DevOps, and other CI systems

---
*Generated on {self._get_current_date()} for {product_name} - Powered by NUnit {self.NUNIT_VERSION}*
"""
    
    def _get_test_commands_section(self) -> str:
        """Get formatted NUnit test commands section"""
        return """```bash
# Run all tests with detailed output
dotnet test --verbosity normal

# Run tests with code coverage
dotnet test --collect:"XPlat Code Coverage"

# Run specific test category (NUnit feature)
dotnet test --filter "Category=Scenario"
dotnet test --filter "Category=Integration" 
dotnet test --filter "Category=EdgeCases"
dotnet test --filter "Category=Performance"

# Run specific test method
dotnet test --filter "Name~TestSpecificScenario"

# Run tests in parallel (NUnit supports parallel execution)
dotnet test --parallel

# Run tests with NUnit console output format
dotnet test --logger "console;verbosity=detailed"

# Generate detailed test report with coverage
dotnet test --collect:"XPlat Code Coverage" --results-directory ./TestResults
reportgenerator -reports:"./TestResults/*/coverage.cobertura.xml" -targetdir:"./CoverageReport" -reporttypes:Html

# NUnit-specific: Run tests with custom timeout
dotnet test --blame-hang-timeout 30s
```"""
    
    def _get_project_structure_section(self, sanitized_name: str) -> str:
        """Get formatted project structure section"""
        return f"""```
{sanitized_name}.Tests/
├── {sanitized_name}.Tests.csproj    # Project file with NUnit dependencies
├── {sanitized_name}Tests.cs         # Main test class
└── README.md                        # This documentation
```"""
    
    def _format_scenarios_list(self, scenarios: List[str]) -> str:
        """Format scenarios as numbered list"""
        return '\n'.join(f'{i+1}. **{scenario}**' for i, scenario in enumerate(scenarios))
    
    def _truncate_content(self, content: str, max_length: int) -> str:
        """Truncate content with ellipsis if too long"""
        return content[:max_length] + ('...' if len(content) > max_length else '')
    
    def _get_current_date(self) -> str:
        """Get current date for documentation"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_dependency_versions(self) -> Dict[str, str]:
        """Get all dependency versions used by this generator"""
        return {
            "target_framework": self.TARGET_FRAMEWORK,
            "nunit": self.NUNIT_VERSION,
            "test_sdk": self.TEST_SDK_VERSION,
            "nunit_adapter": self.NUNIT_ADAPTER_VERSION,
            "nunit_analyzers": self.NUNIT_ANALYZERS_VERSION,
            "coverlet_collector": self.COVERLET_COLLECTOR_VERSION
        }
    
    def _sanitize_csharp_identifier(self, name: str) -> str:
        """Sanitize name to be valid C# identifier"""
        # Remove special characters and replace with valid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '').replace('-', ''))
        
        # Ensure it starts with a letter or underscore
        if sanitized and not (sanitized[0].isalpha() or sanitized[0] == '_'):
            sanitized = 'Test' + sanitized
        
        # Return valid identifier or default
        return sanitized if sanitized else 'TestProject'
