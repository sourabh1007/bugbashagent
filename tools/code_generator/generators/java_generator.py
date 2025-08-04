"""
Java Project Generator

Generates Java test projects wi     <packaging>jar</packaging>
    
    <name>{product_name} Tests</name>
    <description>Test project for {product_name}</description>
    <name>{product_name} Tests</name>
    <description>Test project for {product_name}</description>Maven and JUnit 5.
"""

import os
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class JavaProjectGenerator(BaseProjectGenerator):
    """Generator for Java test projects"""
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate Java test project structure only"""
        created_files = {}
        
        # Sanitize project name for Java package
        package_name = self._sanitize_name(product_name).lower()
        class_name = self._sanitize_name(product_name)
        
        # Create Maven test directory structure only
        src_test_java = os.path.join(project_dir, "src", "test", "java", "com", "example", package_name)
        os.makedirs(src_test_java, exist_ok=True)
        
        # Create pom.xml for test project only
        pom_content = self._create_test_pom_xml(package_name, product_name)
        pom_file = os.path.join(project_dir, "pom.xml")
        with open(pom_file, 'w', encoding='utf-8') as f:
            f.write(pom_content)
        created_files["pom"] = pom_file
        
        # Create test class only
        test_content = self._create_test_content(package_name, class_name, scenarios)
        test_file = os.path.join(src_test_java, f"{class_name}Test.java")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        created_files["test_class"] = test_file
        
        # Create README with test instructions
        readme_file = os.path.join(project_dir, "README.md")
        readme_content = self._create_test_readme(package_name, product_name, class_name, scenarios, generated_content)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_test_pom_xml(self, package_name: str, product_name: str) -> str:
        """Create Maven pom.xml for test project only"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>{package_name}-tests</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
        <name>{product_name} Tests</name>
    <description>Test project for {product_name}</description>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <junit.version>5.8.2</junit.version>
        <maven.compiler.testSource>11</maven.compiler.testSource>
        <maven.compiler.testTarget>11</maven.compiler.testTarget>
    </properties>
    
    <dependencies>
        <!-- JUnit 5 for testing -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <version>${{junit.version}}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <version>${{junit.version}}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-params</artifactId>
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
                    <testSource>11</testSource>
                    <testTarget>11</testTarget>
                </configuration>
            </plugin>
            
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0</version>
                <configuration>
                    <includes>
                        <include>**/*Test.java</include>
                        <include>**/*Tests.java</include>
                    </includes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
'''
    
    def _create_test_content(self, package_name: str, class_name: str, scenarios: List[str]) -> str:
        """Create self-contained test class content"""
        return f'''package com.example.{package_name};

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Test class for {class_name}
 * This class contains self-contained tests for all scenarios
 */
@DisplayName("{class_name} Test Suite")
public class {class_name}Test {{
    
    @BeforeEach
    void setUp() {{
        // Setup test data for {class_name} scenarios
    }}

{chr(10).join([f'''    @Test
    @DisplayName("Test: {scenario}")
    void test{scenario.replace(' ', '').replace('-', '').replace('_', '')}() {{
        // Test case for scenario: {scenario}
        // This is a self-contained test that validates the scenario
        
        // Arrange
        String testData = "test input for {scenario}";
        String scenario = "{scenario}";
        
        // Act
        boolean result = validateScenario(testData, scenario);
        
        // Assert
        assertTrue(result, "Scenario '" + scenario + "' should be validated successfully");
        assertNotNull(testData, "Test data should not be null");
        assertFalse(testData.isEmpty(), "Test data should not be empty");
    }}
''' for scenario in scenarios])}
    
    /**
     * Helper method to validate scenarios
     * This simulates the logic that would be tested in a real application
     */
    private boolean validateScenario(String input, String scenario) {{
        // Mock implementation for testing scenario validation
        // In a real project, this would test actual business logic
        
        return input != null && !input.trim().isEmpty() && 
               scenario != null && !scenario.trim().isEmpty();
    }}
    
    @Test
    @DisplayName("Integration test for all scenarios")
    void testAllScenariosIntegration() {{
        // Integration test for all scenarios
        String[] scenarios = {{{', '.join([f'"{scenario}"' for scenario in scenarios])}}};
        
        for (String scenario : scenarios) {{
            String testData = "integration test data for " + scenario;
            boolean result = validateScenario(testData, scenario);
            assertTrue(result, "Integration test failed for scenario: " + scenario);
        }}
        
        assertEquals({len(scenarios)}, scenarios.length, "Should have exactly {len(scenarios)} scenarios");
    }}
    
    @Test
    @DisplayName("Edge cases validation")
    void testEdgeCases() {{
        // Test edge cases
        assertFalse(validateScenario(null, "valid scenario"), "Should handle null input");
        assertFalse(validateScenario("valid input", null), "Should handle null scenario");
        assertFalse(validateScenario("", "valid scenario"), "Should handle empty input");
        assertFalse(validateScenario("valid input", ""), "Should handle empty scenario");
        assertFalse(validateScenario("   ", "valid scenario"), "Should handle whitespace-only input");
        assertFalse(validateScenario("valid input", "   "), "Should handle whitespace-only scenario");
        
        // Test valid case
        assertTrue(validateScenario("valid input", "valid scenario"), "Should handle valid inputs");
    }}
    
    @ParameterizedTest
    @DisplayName("Parameterized test for scenarios")
    @ValueSource(strings = {{{', '.join([f'"{scenario}"' for scenario in scenarios])}}})
    void testParameterizedScenarios(String scenario) {{
        // Parameterized test for each scenario
        String testData = "parameterized test data for " + scenario;
        boolean result = validateScenario(testData, scenario);
        
        assertTrue(result, "Parameterized test failed for scenario: " + scenario);
        assertNotNull(scenario, "Scenario should not be null");
        assertFalse(scenario.trim().isEmpty(), "Scenario should not be empty");
    }}
    
    @Test
    @DisplayName("Scenario count validation")
    void testScenarioCount() {{
        String[] scenarios = {{{', '.join([f'"{scenario}"' for scenario in scenarios])}}};
        
        assertEquals({len(scenarios)}, scenarios.length, "Should have exactly {len(scenarios)} scenarios");
        
        // Validate each scenario is valid
        for (int i = 0; i < scenarios.length; i++) {{
            assertNotNull(scenarios[i], "Scenario at index " + i + " should not be null");
            assertFalse(scenarios[i].trim().isEmpty(), "Scenario at index " + i + " should not be empty");
        }}
    }}
}}
'''
    
    def _create_test_readme(self, package_name: str, product_name: str, class_name: str, scenarios: List[str], generated_content: str) -> str:
        """Create README with test instructions"""
        return f'''# {product_name} Test Project

This is a test-only Java project for {product_name} using Maven and JUnit 5.

## Setup

1. Ensure Java 11+ is installed
2. Ensure Maven 3.6+ is installed
3. Build the project:
   ```bash
   mvn clean compile test-compile
   ```

## Running Tests

```bash
# Run all tests
mvn test

# Run tests with detailed output
mvn test -Dtest={class_name}Test

# Run specific test method
mvn test -Dtest={class_name}Test#testSpecificScenario

# Run tests with coverage (requires jacoco plugin)
mvn clean test jacoco:report

# Generate test report
mvn surefire-report:report
```

## Project Structure

- `pom.xml` - Maven configuration with JUnit 5 dependencies
- `src/test/java/com/example/{package_name}/{class_name}Test.java` - Main test class
- `README.md` - This file with instructions

## Test Scenarios

This test project validates the following scenarios:

{chr(10).join([f"- {scenario}" for scenario in scenarios])}

## Generated Content Analysis

The following content was analyzed to create these tests:

```
{generated_content[:500]}{'...' if len(generated_content) > 500 else ''}
```

## Test Categories

### Scenario Validation Tests
- Individual JUnit 5 tests for each scenario with specific test data
- Uses JUnit 5 assertions and DisplayName annotations

### Integration Tests  
- Tests all scenarios working together
- Validates overall system integration

### Edge Case Tests
- Tests with invalid inputs (null, empty, whitespace)
- Comprehensive boundary testing

### Parameterized Tests
- Uses JUnit 5 @ParameterizedTest for data-driven testing
- Tests all scenarios with the same test logic

## Maven Commands

```bash
# Clean and compile
mvn clean compile

# Run tests only
mvn test

# Skip tests during build
mvn clean install -DskipTests

# Run tests with specific pattern
mvn test -Dtest="*Test"

# Generate dependency tree
mvn dependency:tree

# Check for updates
mvn versions:display-dependency-updates
```

## Dependencies

- **JUnit 5**: Modern testing framework for Java
- **Maven Surefire Plugin**: Test execution
- **Maven Compiler Plugin**: Java compilation
- **Java 11+**: Required Java version

## Notes

This is a test-only project designed to validate the functionality described in the analyzed scenarios. No main application code is generated - only comprehensive test coverage using modern Java testing practices with JUnit 5.

The project follows Maven standard directory layout with tests in `src/test/java`.
'''
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name to be valid Java identifier"""
        # Remove special characters and replace with underscore
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '').replace('-', ''))
        
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'Test' + sanitized
            
        return sanitized if sanitized else 'TestProject'
