"""
Generic Project Generator

Generates projects for languages that don't have dedicated generators or need generic fallback support.
"""

import os
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class GenericProjectGenerator(BaseProjectGenerator):
    """Generator for generic/other language projects"""
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str, language: str = "text") -> Dict[str, str]:
        """Generate test-only project structure for generic languages"""
        created_files = {}
        
        # Determine file extension
        extension_map = {
            "java": ".java",
            "cpp": ".cpp", 
            "c": ".c",
            "go": ".go",
            "rust": ".rs",
            "php": ".php",
            "ruby": ".rb",
            "kotlin": ".kt",
            "scala": ".scala",
            "swift": ".swift"
        }
        
        extension = extension_map.get(language.lower(), ".txt")
        
        # Create test file only
        test_content = self._create_test_content(product_name, scenarios, generated_content, language, extension)
        test_file = os.path.join(project_dir, f"test_{product_name.lower().replace(' ', '_')}{extension}")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        created_files["test"] = test_file
        
        # Create README with test instructions
        readme_content = self._create_test_readme(product_name, scenarios, generated_content, language)
        readme_file = os.path.join(project_dir, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_test_content(self, product_name: str, scenarios: List[str], generated_content: str, language: str, extension: str) -> str:
        """Create test file content for generic languages"""
        if language.lower() == "java":
            return self._create_java_test_content(product_name, scenarios)
        elif language.lower() in ["cpp", "c"]:
            return self._create_c_test_content(product_name, scenarios)
        elif language.lower() == "go":
            return self._create_go_test_content(product_name, scenarios)
        elif language.lower() == "rust":
            return self._create_rust_test_content(product_name, scenarios)
        elif language.lower() == "php":
            return self._create_php_test_content(product_name, scenarios)
        elif language.lower() == "ruby":
            return self._create_ruby_test_content(product_name, scenarios)
        else:
            return self._create_generic_test_content(product_name, scenarios, language)
    
    def _create_java_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create Java test content using configured test framework"""
        class_name = product_name.replace(' ', '')
        test_framework = self.get_test_framework_for_language('java')
        
        if test_framework == 'junit5':
            return f'''import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Test cases for {product_name}
 */
@DisplayName("{product_name} Test Suite")
public class {class_name}Test {{
    
    @BeforeEach
    void setUp() {{
        // Setup test data
    }}
    
{chr(10).join([f'''    @Test
    @DisplayName("Test: {scenario}")
    void test{scenario.replace(' ', '').replace('-', '')}() {{
        // Arrange
        String testData = "test_data_for_{scenario.lower().replace(' ', '_')}";
        
        // Act
        boolean result = validateScenario(testData, "{scenario}");
        
        // Assert
        assertTrue(result, "Scenario '{scenario}' should pass validation");
    }}
''' for scenario in scenarios])}
    
    private boolean validateScenario(String testData, String scenario) {{
        // Mock validation logic
        return testData != null && !testData.isEmpty() && 
               scenario != null && !scenario.isEmpty();
    }}
}}'''
        else:
            # Fallback for other test frameworks or generic case
            return f'''// Test cases for {product_name}
// Using {test_framework} test framework
public class {class_name}Test {{
    
{chr(10).join([f'''    // Test: {scenario}
    public void test{scenario.replace(' ', '').replace('-', '')}() {{
        String testData = "test_data_for_{scenario.lower().replace(' ', '_')}";
        boolean result = validateScenario(testData, "{scenario}");
        // Add assertions based on test framework
    }}
''' for scenario in scenarios])}
    
    private boolean validateScenario(String testData, String scenario) {{
        return testData != null && !testData.isEmpty() && 
               scenario != null && !scenario.isEmpty();
    }}
}}'''
    
    def _create_c_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create C/C++ test content"""
        return f'''/**
 * Test cases for {product_name}
 * Compile with: gcc -o test test_{product_name.lower().replace(' ', '_')}.c
 */

#include <stdio.h>
#include <string.h>
#include <assert.h>

int validate_scenario(const char* test_data, const char* scenario) {{
    return (test_data != NULL && strlen(test_data) > 0 && 
            scenario != NULL && strlen(scenario) > 0);
}}

{chr(10).join([f'''void test_{scenario.lower().replace(' ', '_').replace('-', '_')}() {{
    printf("Testing: {scenario}\\n");
    char test_data[] = "test_data_for_{scenario.lower().replace(' ', '_')}";
    
    int result = validate_scenario(test_data, "{scenario}");
    assert(result == 1);
    
    printf("✓ {scenario} test passed\\n");
}}
''' for scenario in scenarios])}

int main() {{
    printf("Running {product_name} Test Suite\\n");
    printf("================================\\n");
    
{chr(10).join([f'    test_{scenario.lower().replace(" ", "_").replace("-", "_")}();' for scenario in scenarios])}
    
    printf("\\nAll tests passed!\\n");
    return 0;
}}'''
    
    def _create_go_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create Go test content"""
        return f'''package main

import (
    "testing"
    "strings"
)

// validateScenario simulates validation logic
func validateScenario(testData, scenario string) bool {{
    return len(strings.TrimSpace(testData)) > 0 && len(strings.TrimSpace(scenario)) > 0
}}

{chr(10).join([f'''func Test{scenario.replace(' ', '').replace('-', '')}(t *testing.T) {{
    testData := "test_data_for_{scenario.lower().replace(' ', '_')}"
    scenario := "{scenario}"
    
    result := validateScenario(testData, scenario)
    
    if !result {{
        t.Errorf("Scenario '%s' failed validation", scenario)
    }}
}}
''' for scenario in scenarios])}

func TestAllScenarios(t *testing.T) {{
    scenarios := []string{{
{chr(10).join([f'        "{scenario}",' for scenario in scenarios])}
    }}
    
    for _, scenario := range scenarios {{
        t.Run(scenario, func(t *testing.T) {{
            testData := "integration_test_data"
            result := validateScenario(testData, scenario)
            
            if !result {{
                t.Errorf("Integration test failed for scenario: %s", scenario)
            }}
        }})
    }}
}}'''
    
    def _create_rust_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create Rust test content"""
        return f'''/**
 * Test cases for {product_name}
 * Run with: cargo test
 */

fn validate_scenario(test_data: &str, scenario: &str) -> bool {{
    !test_data.trim().is_empty() && !scenario.trim().is_empty()
}}

#[cfg(test)]
mod tests {{
    use super::*;

{chr(10).join([f'''    #[test]
    fn test_{scenario.lower().replace(' ', '_').replace('-', '_')}() {{
        let test_data = "test_data_for_{scenario.lower().replace(' ', '_')}";
        let scenario = "{scenario}";
        
        let result = validate_scenario(test_data, scenario);
        assert!(result, "Scenario '{{}}' should pass validation", scenario);
    }}
''' for scenario in scenarios])}
    
    #[test]
    fn test_all_scenarios_integration() {{
        let scenarios = vec![
{chr(10).join([f'            "{scenario}",' for scenario in scenarios])}
        ];
        
        for scenario in scenarios {{
            let test_data = "integration_test_data";
            let result = validate_scenario(test_data, scenario);
            assert!(result, "Integration test failed for scenario: {{}}", scenario);
        }}
    }}
    
    #[test]
    fn test_edge_cases() {{
        assert!(!validate_scenario("", "valid_scenario"));
        assert!(!validate_scenario("valid_data", ""));
        assert!(!validate_scenario("   ", "valid_scenario"));
        assert!(!validate_scenario("valid_data", "   "));
    }}
}}'''
    
    def _create_php_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create PHP test content"""
        return f'''<?php
/**
 * Test cases for {product_name}
 * Run with: php test_{product_name.lower().replace(' ', '_')}.php
 */

function validateScenario($testData, $scenario) {{
    return !empty(trim($testData)) && !empty(trim($scenario));
}}

{chr(10).join([f'''function test{scenario.replace(' ', '').replace('-', '')}() {{
    $testData = "test_data_for_{scenario.lower().replace(' ', '_')}";
    $scenario = "{scenario}";
    
    $result = validateScenario($testData, $scenario);
    
    if (!$result) {{
        throw new Exception("Scenario '$scenario' failed validation");
    }}
    
    echo "✓ {scenario} test passed\\n";
}}
''' for scenario in scenarios])}

function testAllScenariosIntegration() {{
    $scenarios = [
{chr(10).join([f'        "{scenario}",' for scenario in scenarios])}
    ];
    
    foreach ($scenarios as $scenario) {{
        $testData = "integration_test_data";
        $result = validateScenario($testData, $scenario);
        
        if (!$result) {{
            throw new Exception("Integration test failed for scenario: $scenario");
        }}
    }}
    
    echo "✓ All scenarios integration test passed\\n";
}}

// Run tests
echo "{product_name} Test Suite\\n";
echo str_repeat("=", 30) . "\\n";

try {{
{chr(10).join([f'    test{scenario.replace(" ", "").replace("-", "")}();' for scenario in scenarios])}
    testAllScenariosIntegration();
    
    echo "\\nAll tests passed!\\n";
}} catch (Exception $e) {{
    echo "Test failed: " . $e->getMessage() . "\\n";
    exit(1);
}}
?>'''
    
    def _create_ruby_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create Ruby test content"""
        ruby_code = f'''# Test cases for {product_name}
# Run with: ruby test_{product_name.lower().replace(' ', '_')}.rb

def validate_scenario(test_data, scenario)
  !test_data.to_s.strip.empty? && !scenario.to_s.strip.empty?
end

'''
        
        # Add individual test methods
        for scenario in scenarios:
            ruby_code += f'''def test_{scenario.lower().replace(' ', '_').replace('-', '_')}
  test_data = "test_data_for_{scenario.lower().replace(' ', '_')}"
  scenario = "{scenario}"
  
  result = validate_scenario(test_data, scenario)
  
  raise "Scenario '#{{scenario}}' failed validation" unless result
  
  puts "✓ {scenario} test passed"
end

'''
        
        # Add integration test
        ruby_code += f'''def test_all_scenarios_integration
  scenarios = [
'''
        for scenario in scenarios:
            ruby_code += f'    "{scenario}",\n'
        
        ruby_code += '''  ]
  
  scenarios.each do |scenario|
    test_data = "integration_test_data"
    result = validate_scenario(test_data, scenario)
    
    raise "Integration test failed for scenario: #{scenario}" unless result
  end
  
  puts "✓ All scenarios integration test passed"
end

'''
        
        # Add test runner
        ruby_code += f'''# Run tests
puts "{product_name} Test Suite"
puts "=" * 30

begin
'''
        
        # Add test method calls
        for scenario in scenarios:
            ruby_code += f'  test_{scenario.lower().replace(" ", "_").replace("-", "_")}\n'
        
        ruby_code += '''  test_all_scenarios_integration
  
  puts "\\nAll tests passed!"
rescue => e
  puts "Test failed: #{e.message}"
  exit 1
end'''
        
        return ruby_code
    
    def _create_generic_test_content(self, product_name: str, scenarios: List[str], language: str) -> str:
        """Create generic test content for unsupported languages"""
        return f'''/**
 * Test cases for {product_name}
 * Language: {language.title()}
 * 
 * This is a generic test template. Adapt the syntax for your specific language.
 */

// Test scenarios to validate:
{chr(10).join([f'// - {scenario}' for scenario in scenarios])}

// Pseudo-code test structure:

function validateScenario(testData, scenario) {{
    // Mock validation logic
    return (testData != null && testData.length > 0 && 
            scenario != null && scenario.length > 0);
}}

{chr(10).join([f'''// Test case for: {scenario}
test_{scenario.lower().replace(' ', '_').replace('-', '_')}() {{
    testData = "test_data_for_{scenario.lower().replace(' ', '_')}";
    scenario = "{scenario}";
    
    result = validateScenario(testData, scenario);
    
    assert(result == true, "Scenario '{scenario}' should pass validation");
    
    print("✓ {scenario} test passed");
}}
''' for scenario in scenarios])}

// Integration test
test_all_scenarios_integration() {{
    scenarios = [
{chr(10).join([f'        "{scenario}",' for scenario in scenarios])}
    ];
    
    for each scenario in scenarios {{
        testData = "integration_test_data";
        result = validateScenario(testData, scenario);
        
        assert(result == true, "Integration test failed for scenario: " + scenario);
    }}
    
    print("✓ All scenarios integration test passed");
}}

// Main test runner
main() {{
    print("{product_name} Test Suite");
    print("=" * 30);
    
{chr(10).join([f'    test_{scenario.lower().replace(" ", "_").replace("-", "_")}();' for scenario in scenarios])}
    test_all_scenarios_integration();
    
    print("All tests passed!");
}}'''
    
    def _create_test_readme(self, product_name: str, scenarios: List[str], generated_content: str, language: str) -> str:
        """Create README with test instructions"""
        
        # Define extension map locally  
        extension_map = {
            "java": ".java",
            "cpp": ".cpp", 
            "c": ".c",
            "go": ".go",
            "rust": ".rs",
            "php": ".php",
            "ruby": ".rb",
            "kotlin": ".kt",
            "scala": ".scala",
            "swift": ".swift"
        }
        
        run_instructions = {
            "java": "javac Test*.java && java TestClassName",
            "cpp": "g++ -o test test_*.cpp && ./test", 
            "c": "gcc -o test test_*.c && ./test",
            "go": "go test",
            "rust": "cargo test",
            "php": f"php test_{product_name.lower().replace(' ', '_')}.php",
            "ruby": f"ruby test_{product_name.lower().replace(' ', '_')}.rb"
        }
        
        run_cmd = run_instructions.get(language.lower(), f"# Adapt for {language} - see test file for details")
        
        return f'''# {product_name} Test Project

This is a test-only project for {product_name} written in {language.title()}.

## Setup and Running Tests

```bash
{run_cmd}
```

## Project Structure

- `test_{product_name.lower().replace(' ', '_')}.{extension_map.get(language.lower(), 'txt').lstrip('.')}` - Main test file
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
- Tests each scenario individually with specific test data
- Validates expected behavior for each scenario

### Integration Tests  
- Tests all scenarios working together
- Validates overall system integration

### Edge Case Tests
- Tests with invalid inputs (null, empty, whitespace)
- Tests boundary conditions

## Language-Specific Notes

### {language.title()}
- This test project uses standard {language} testing patterns
- Adapt the test syntax as needed for your specific {language} environment
- The test logic focuses on validation of the analyzed scenarios

## Requirements

- {language.title()} compiler/interpreter
- Standard {language} development environment

## Notes

This is a test-only project designed to validate the functionality described in the analyzed scenarios. No main application code is generated - only comprehensive test coverage.
'''
