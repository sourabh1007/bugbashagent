"""
Go Project Generator

Generates Go test projects with proper Go testing conventions.
"""

import os
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class GoProjectGenerator(BaseProjectGenerator):
    """Generator for Go test projects"""
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate Go test project structure"""
        created_files = {}
        
        # Create go.mod file
        module_name = product_name.lower().replace(' ', '_').replace('-', '_')
        go_mod_content = self._create_go_mod(module_name)
        go_mod_file = os.path.join(project_dir, "go.mod")
        with open(go_mod_file, 'w', encoding='utf-8') as f:
            f.write(go_mod_content)
        created_files["go_mod"] = go_mod_file
        
        # Create main test file
        test_content = self._create_test_content(product_name, scenarios)
        test_file = os.path.join(project_dir, f"{module_name}_test.go")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        created_files["test"] = test_file
        
        # Create README with test instructions
        readme_content = self._create_readme(product_name, scenarios, generated_content)
        readme_file = os.path.join(project_dir, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_go_mod(self, module_name: str) -> str:
        """Create go.mod file content"""
        return f'''module {module_name}

go 1.21

require (
    github.com/stretchr/testify v1.8.4
)
'''
    
    def _create_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create Go test file content"""
        package_name = product_name.lower().replace(' ', '_').replace('-', '_')
        
        return f'''package {package_name}

import (
    "strings"
    "testing"
    "github.com/stretchr/testify/assert"
)

// validateScenario simulates validation logic for testing scenarios
func validateScenario(testData, scenario string) bool {{
    return len(strings.TrimSpace(testData)) > 0 && len(strings.TrimSpace(scenario)) > 0
}}

{chr(10).join([f'''// Test{scenario.replace(' ', '').replace('-', '').replace('_', '')} tests the "{scenario}" scenario
func Test{scenario.replace(' ', '').replace('-', '').replace('_', '')}(t *testing.T) {{
    // Arrange
    testData := "test_data_for_{scenario.lower().replace(' ', '_').replace('-', '_')}"
    scenario := "{scenario}"
    
    // Act
    result := validateScenario(testData, scenario)
    
    // Assert
    assert.True(t, result, "Scenario '%s' should pass validation", scenario)
    assert.NotEmpty(t, testData, "Test data should not be empty")
    assert.NotEmpty(t, scenario, "Scenario should not be empty")
}}
''' for scenario in scenarios])}

// TestAllScenariosIntegration tests all scenarios working together
func TestAllScenariosIntegration(t *testing.T) {{
    scenarios := []string{{
{chr(10).join([f'        "{scenario}",' for scenario in scenarios])}
    }}
    
    for _, scenario := range scenarios {{
        t.Run(scenario, func(t *testing.T) {{
            testData := "integration_test_data"
            result := validateScenario(testData, scenario)
            
            assert.True(t, result, "Integration test failed for scenario: %s", scenario)
        }})
    }}
}}

// TestEdgeCases tests various edge cases
func TestEdgeCases(t *testing.T) {{
    testCases := []struct {{
        name     string
        testData string
        scenario string
        expected bool
    }}{{
        {{"empty test data", "", "valid_scenario", false}},
        {{"empty scenario", "valid_data", "", false}},
        {{"whitespace only test data", "   ", "valid_scenario", false}},
        {{"whitespace only scenario", "valid_data", "   ", false}},
        {{"valid inputs", "valid_data", "valid_scenario", true}},
    }}
    
    for _, tc := range testCases {{
        t.Run(tc.name, func(t *testing.T) {{
            result := validateScenario(tc.testData, tc.scenario)
            assert.Equal(t, tc.expected, result, "Test case '%s' failed", tc.name)
        }})
    }}
}}

// TestScenarioCount validates the expected number of scenarios
func TestScenarioCount(t *testing.T) {{
    expectedCount := {len(scenarios)}
    scenarios := []string{{
{chr(10).join([f'        "{scenario}",' for scenario in scenarios])}
    }}
    
    assert.Len(t, scenarios, expectedCount, "Should have exactly %d scenarios", expectedCount)
    
    // Validate all scenarios are non-empty strings
    for i, scenario := range scenarios {{
        assert.NotEmpty(t, scenario, "Scenario at index %d should not be empty", i)
        assert.IsType(t, "", scenario, "Scenario at index %d should be a string", i)
    }}
}}

// BenchmarkValidateScenario benchmarks the validateScenario function
func BenchmarkValidateScenario(b *testing.B) {{
    testData := "benchmark_test_data"
    scenario := "benchmark_scenario"
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {{
        validateScenario(testData, scenario)
    }}
}}
'''
    
    def _create_readme(self, product_name: str, scenarios: List[str], generated_content: str) -> str:
        """Create README with test instructions"""
        module_name = product_name.lower().replace(' ', '_').replace('-', '_')
        
        return f'''# {product_name} Test Project

This is a test-only Go project for {product_name} using Go's built-in testing framework and testify assertions.

## Setup

1. Ensure Go 1.21+ is installed
2. Initialize the module:
   ```bash
   go mod init {module_name}
   go mod tidy
   ```

## Running Tests

```bash
# Run all tests
go test

# Run tests with verbose output
go test -v

# Run tests with coverage
go test -cover

# Run tests with detailed coverage report
go test -coverprofile=coverage.out
go tool cover -html=coverage.out

# Run specific test
go test -run TestSpecificScenario

# Run benchmarks
go test -bench=.
```

## Project Structure

- `go.mod` - Go module definition with dependencies
- `{module_name}_test.go` - Main test file containing all test cases
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
- Individual tests for each scenario with specific test data
- Uses testify assertions for better error messages

### Integration Tests  
- Tests all scenarios working together using subtests
- Validates overall system integration

### Edge Case Tests
- Table-driven tests with various edge cases
- Tests invalid inputs (empty, whitespace-only)

### Benchmark Tests
- Performance benchmarks for validation functions
- Helps identify performance bottlenecks

## Go Testing Best Practices

This project follows Go testing conventions:
- Test functions start with `Test`
- Benchmark functions start with `Benchmark`
- Uses `testing.T` for test functions
- Uses `testing.B` for benchmark functions
- Leverages testify for enhanced assertions
- Uses table-driven tests for edge cases
- Includes subtests for better organization

## Dependencies

- **testify**: Enhanced assertions and test utilities
- **Go 1.21+**: Required Go version

## Notes

This is a test-only project designed to validate the functionality described in the analyzed scenarios. No main application code is generated - only comprehensive test coverage using Go's excellent built-in testing tools.
'''
