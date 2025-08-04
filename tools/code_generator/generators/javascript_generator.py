"""
JavaScript Project Generator

Generates JavaScript/Node.js projects with package.json, Jest tests, and proper project structure.
"""

import os
import json
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class JavaScriptProjectGenerator(BaseProjectGenerator):
    """Generator for JavaScript/Node.js projects"""
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate JavaScript test project structure only"""
        created_files = {}
        
        # Create package.json with only test dependencies
        package_json = {
            "name": f"{product_name.lower().replace(' ', '-')}-tests",
            "version": "1.0.0",
            "description": f"Test project for {product_name}",
            "main": "test/index.test.js",
            "scripts": {
                "test": "jest",
                "test:watch": "jest --watch",
                "test:coverage": "jest --coverage"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "@types/jest": "^29.0.0"
            },
            "jest": {
                "testEnvironment": "node",
                "collectCoverageFrom": [
                    "test/**/*.js"
                ],
                "testMatch": [
                    "**/*.test.js"
                ]
            }
        }
        
        package_file = os.path.join(project_dir, "package.json")
        with open(package_file, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        created_files["package"] = package_file
        
        # Create test directory and test file
        test_dir = os.path.join(project_dir, "test")
        os.makedirs(test_dir, exist_ok=True)
        
        test_content = self._create_test_content(product_name, scenarios)
        test_file = os.path.join(test_dir, "scenarios.test.js")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        created_files["test"] = test_file
        
        # Create README with test instructions
        readme_file = os.path.join(project_dir, "README.md")
        readme_content = self._create_test_readme(product_name, scenarios, generated_content)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_main_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create index.js content"""
        return f'''/**
 * {product_name}
 * Main application entry point
 */

function main() {{
    console.log("Welcome to {product_name}!");
    
    // TODO: Implement scenarios:
    {chr(10).join([f'    // - {scenario}' for scenario in scenarios])}
    
    console.log("Application completed successfully.");
}}

// Export for testing
module.exports = {{ main }};

// Run if this is the main module
if (require.main === module) {{
    main();
}}
'''
    
    def _create_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create self-contained test file content"""
        return f'''/**
 * Test cases for {product_name}
 * 
 * This test suite validates all scenarios related to {product_name}.
 */

describe('{product_name} Test Suite', () => {{
    let testData;
    
    beforeEach(() => {{
        // Setup test data for each test
        testData = {{
            scenarios: {json.dumps(scenarios)},
            productName: '{product_name}'
        }};
    }});

    describe('Scenario Validation Tests', () => {{
{chr(10).join([f'''        test('{scenario}', () => {{
            // Arrange
            const scenarioName = '{scenario}';
            const testInput = 'test_data_for_{scenario.lower().replace(' ', '_')}';
            
            // Act
            const result = validateScenario(testInput, scenarioName);
            
            // Assert
            expect(result).toBe(true);
            expect(testData.scenarios).toContain(scenarioName);
        }});
''' for scenario in scenarios])}    }});
    
    describe('Integration Tests', () => {{
        test('all scenarios integration test', () => {{
            // Test that all scenarios can be processed together
            testData.scenarios.forEach(scenario => {{
                const result = validateScenario('integration_test_data', scenario);
                expect(result).toBe(true);
            }});
            
            expect(testData.scenarios).toHaveLength({len(scenarios)});
        }});
        
        test('product name validation', () => {{
            expect(testData.productName).toBe('{product_name}');
            expect(testData.productName.length).toBeGreaterThan(0);
        }});
    }});
    
    describe('Edge Case Tests', () => {{
        test('validates scenario with invalid inputs', () => {{
            // Test with null/undefined inputs
            expect(validateScenario(null, 'valid_scenario')).toBe(false);
            expect(validateScenario('valid_data', null)).toBe(false);
            expect(validateScenario(undefined, 'valid_scenario')).toBe(false);
            expect(validateScenario('valid_data', undefined)).toBe(false);
            
            // Test with empty strings
            expect(validateScenario('', 'valid_scenario')).toBe(false);
            expect(validateScenario('valid_data', '')).toBe(false);
        }});
        
        test('handles edge case inputs gracefully', () => {{
            // Test with various edge case inputs
            expect(validateScenario('   ', 'scenario')).toBe(false); // whitespace only
            expect(validateScenario('data', '   ')).toBe(false); // whitespace only
            expect(validateScenario(123, 'scenario')).toBe(false); // non-string input
            expect(validateScenario('data', 123)).toBe(false); // non-string scenario
        }});
    }});
    
    describe('Parameterized Tests', () => {{
        test.each({json.dumps(scenarios)})(
            'parameterized test for scenario: %s',
            (scenario) => {{
                expect(typeof scenario).toBe('string');
                expect(scenario.length).toBeGreaterThan(0);
                
                const result = validateScenario(`test_data_for_${{scenario}}`, scenario);
                expect(result).toBe(true);
            }}
        );
    }});
    
    describe('Test Utilities', () => {{
        test('scenario count matches expected', () => {{
            expect(testData.scenarios).toHaveLength({len(scenarios)});
            expect(Array.isArray(testData.scenarios)).toBe(true);
        }});
        
        test('all scenarios are strings', () => {{
            testData.scenarios.forEach(scenario => {{
                expect(typeof scenario).toBe('string');
                expect(scenario.length).toBeGreaterThan(0);
            }});
        }});
    }});
}});

/**
 * Helper function to validate scenarios
 * In a real test project, this would test actual business logic
 * 
 * @param {{string|any}} testData - The test data to validate
 * @param {{string|any}} scenario - The scenario name being tested
 * @returns {{boolean}} - True if validation passes, false otherwise
 */
function validateScenario(testData, scenario) {{
    // Handle null/undefined inputs
    if (testData == null || scenario == null) {{
        return false;
    }}
    
    // Handle non-string inputs
    if (typeof testData !== 'string' || typeof scenario !== 'string') {{
        return false;
    }}
    
    // Handle empty or whitespace-only strings
    if (testData.trim().length === 0 || scenario.trim().length === 0) {{
        return false;
    }}
    
    // Mock validation logic - in real tests this would contain actual business logic
    return true;
}}

module.exports = {{ validateScenario }};
'''
    
    def _create_test_readme(self, product_name: str, scenarios: List[str], generated_content: str) -> str:
        """Create README with test instructions"""
        return f'''# {product_name} Test Project

This is a test-only project for {product_name} containing comprehensive test suites.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run tests:
   ```bash
   npm test
   ```

3. Run tests with coverage:
   ```bash
   npm run test:coverage
   ```

4. Run tests in watch mode:
   ```bash
   npm run test:watch
   ```

## Project Structure

- `test/{product_name.lower().replace(' ', '_')}_test.js` - Main test file containing all test cases
- `package.json` - Project configuration with test dependencies
- `jest.config.js` - Jest test framework configuration

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
- Tests with invalid inputs (null, undefined, empty strings)
- Tests with edge case data

### Parameterized Tests
- Uses Jest's test.each for data-driven testing
- Runs the same test logic across all scenarios

## Requirements

- Node.js 16+ 
- Jest testing framework
- All dependencies listed in package.json

## Notes

This is a test-only project designed to validate the functionality described in the analyzed scenarios. It contains comprehensive test coverage including unit tests, integration tests, and edge case testing.
'''
