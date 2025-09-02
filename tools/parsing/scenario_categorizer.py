"""
Scenario Categorizer Tool

Categorizes test scenarios into different files based on their type and complexity.
"""

import os
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime


class ScenarioCategorizer:
    """Tool for categorizing and organizing test scenarios into separate files"""
    
    def __init__(self):
        self.scenario_categories = {
            'basic': {
                'keywords': ['basic', 'simple', 'standard', 'default', 'core', 'fundamental', 'primary'],
                'description': 'Basic functionality and core features',
                'file_suffix': 'BasicTests'
            },
            'integration': {
                'keywords': ['integration', 'end-to-end', 'e2e', 'workflow', 'complete', 'full', 'system'],
                'description': 'Integration and end-to-end testing scenarios',
                'file_suffix': 'IntegrationTests'
            },
            'edge_cases': {
                'keywords': ['edge', 'boundary', 'limit', 'extreme', 'corner', 'invalid', 'error', 'exception'],
                'description': 'Edge cases and boundary testing',
                'file_suffix': 'EdgeCaseTests'
            },
            'performance': {
                'keywords': ['performance', 'load', 'stress', 'speed', 'benchmark', 'timeout', 'memory', 'cpu'],
                'description': 'Performance and load testing scenarios',
                'file_suffix': 'PerformanceTests'
            },
            'security': {
                'keywords': ['security', 'auth', 'permission', 'access', 'vulnerability', 'injection', 'xss'],
                'description': 'Security testing scenarios',
                'file_suffix': 'SecurityTests'
            },
            'api': {
                'keywords': ['api', 'rest', 'http', 'endpoint', 'request', 'response', 'json', 'xml'],
                'description': 'API testing scenarios',
                'file_suffix': 'ApiTests'
            },
            'ui': {
                'keywords': ['ui', 'interface', 'user', 'click', 'button', 'form', 'page', 'browser'],
                'description': 'User interface testing scenarios',
                'file_suffix': 'UiTests'
            },
            'data': {
                'keywords': ['data', 'database', 'sql', 'crud', 'storage', 'persistence', 'migration'],
                'description': 'Data and database testing scenarios',
                'file_suffix': 'DataTests'
            }
        }
    
    def categorize_scenarios(self, scenarios: List[str]) -> Dict[str, List[str]]:
        """Categorize scenarios based on their content and keywords"""
        categorized = {category: [] for category in self.scenario_categories.keys()}
        uncategorized = []
        
        for scenario in scenarios:
            scenario_lower = scenario.lower()
            matched_category = None
            max_matches = 0
            
            # Find the category with the most keyword matches
            for category, config in self.scenario_categories.items():
                matches = sum(1 for keyword in config['keywords'] if keyword in scenario_lower)
                if matches > max_matches:
                    max_matches = matches
                    matched_category = category
            
            # If we found a good match (at least one keyword), categorize it
            if max_matches > 0:
                categorized[matched_category].append(scenario)
            else:
                uncategorized.append(scenario)
        
        # Put uncategorized scenarios in 'basic' by default
        if uncategorized:
            categorized['basic'].extend(uncategorized)
        
        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}
        
        return categorized
    
    def generate_test_file_content(self, category: str, scenarios: List[str], language: str, 
                                   product_name: str, namespace: str = None) -> str:
        """Generate test file content for a specific category"""
        category_config = self.scenario_categories.get(category, {})
        file_suffix = category_config.get('file_suffix', 'Tests')
        description = category_config.get('description', 'Test scenarios')
        
        if language.lower() in ['csharp', 'c#']:
            return self._generate_csharp_test_content(category, scenarios, product_name, file_suffix, description, namespace)
        elif language.lower() == 'java':
            return self._generate_java_test_content(category, scenarios, product_name, file_suffix, description)
        elif language.lower() == 'python':
            return self._generate_python_test_content(category, scenarios, product_name, file_suffix, description)
        elif language.lower() in ['javascript', 'js', 'node.js']:
            return self._generate_javascript_test_content(category, scenarios, product_name, file_suffix, description)
        elif language.lower() == 'go':
            return self._generate_go_test_content(category, scenarios, product_name, file_suffix, description)
        elif language.lower() == 'rust':
            return self._generate_rust_test_content(category, scenarios, product_name, file_suffix, description)
        else:
            return self._generate_generic_test_content(category, scenarios, product_name, file_suffix, description)
    
    def _generate_csharp_test_content(self, category: str, scenarios: List[str], product_name: str, 
                                      file_suffix: str, description: str, namespace: str = None) -> str:
        """Generate C# NUnit test content"""
        # Ensure class name matches file name exactly
        safe_product_name = product_name.replace(' ', '').replace('-', '')
        class_name = f"{safe_product_name}{file_suffix}"
        test_namespace = namespace or f"{safe_product_name}.Tests"
        
        content = f"""using NUnit.Framework;
using System;
using System.Threading.Tasks;

namespace {test_namespace}
{{
    /// <summary>
    /// {description}
    /// Category: {category.title()}
    /// Class name: {class_name} (matches file name)
    /// </summary>
    [TestFixture]
    [Category("{category.title()}")]
    public class {class_name}
    {{
        [SetUp]
        public void SetUp()
        {{
            // Initialize test data and setup before each test
            Console.WriteLine($"Setting up {{GetType().Name}} test");
        }}

        [TearDown]
        public void TearDown()
        {{
            // Clean up after each test
            Console.WriteLine($"Cleaning up {{GetType().Name}} test");
        }}

"""

        # Generate test methods for each scenario
        for i, scenario in enumerate(scenarios, 1):
            method_name = self._sanitize_method_name(scenario)
            test_timeout = 30000 if category == 'performance' else 10000
            
            content += f"""        [Test]
        [Category("{category.title()}")]
        [Description("{scenario}")]
        [Timeout({test_timeout})]
        public void Test{method_name}()
        {{
            // Arrange
            Console.WriteLine("Testing: {scenario}");
            
            // Act
            var result = ExecuteScenario("{scenario}");
            
            // Assert
            Assert.That(result, Is.Not.Null, "Scenario should return a valid result");
            Assert.That(result.Success, Is.True, "Scenario should execute successfully");
            
            Console.WriteLine($"Scenario completed successfully: {scenario}");
        }}

"""

            # Add async version for integration and performance tests
            if category in ['integration', 'performance']:
                content += f"""        [Test]
        [Category("{category.title()}")]
        [Description("{scenario} - Async Version")]
        [Timeout({test_timeout * 2})]
        public async Task Test{method_name}Async()
        {{
            // Arrange
            Console.WriteLine("Testing (Async): {scenario}");
            
            // Act
            var result = await ExecuteScenarioAsync("{scenario}");
            
            // Assert
            Assert.That(result, Is.Not.Null, "Async scenario should return a valid result");
            Assert.That(result.Success, Is.True, "Async scenario should execute successfully");
            
            Console.WriteLine($"Async scenario completed successfully: {scenario}");
        }}

"""

        # Add helper methods
        content += f"""        private ScenarioResult ExecuteScenario(string scenarioName)
        {{
            try
            {{
                // Simulate scenario execution
                Console.WriteLine($"Executing scenario: {{scenarioName}}");
                
                // Add your actual test logic here
                // This is a placeholder that simulates successful execution
                System.Threading.Thread.Sleep(100); // Simulate some work
                
                return new ScenarioResult {{ Success = true, Message = "Scenario executed successfully" }};
            }}
            catch (Exception ex)
            {{
                return new ScenarioResult {{ Success = false, Message = ex.Message }};
            }}
        }}

        private async Task<ScenarioResult> ExecuteScenarioAsync(string scenarioName)
        {{
            try
            {{
                // Simulate async scenario execution
                Console.WriteLine($"Executing async scenario: {{scenarioName}}");
                
                // Add your actual async test logic here
                await Task.Delay(100); // Simulate some async work
                
                return new ScenarioResult {{ Success = true, Message = "Async scenario executed successfully" }};
            }}
            catch (Exception ex)
            {{
                return new ScenarioResult {{ Success = false, Message = ex.Message }};
            }}
        }}
    }}

    public class ScenarioResult
    {{
        public bool Success {{ get; set; }}
        public string Message {{ get; set; }}
    }}
}}"""

        return content
    
    def _generate_python_test_content(self, category: str, scenarios: List[str], product_name: str, 
                                      file_suffix: str, description: str) -> str:
        """Generate Python pytest test content"""
        content = f'''"""
{description}
Category: {category.title()}
"""

import pytest
import asyncio
import time
from typing import Dict, Any


class Test{product_name.replace(' ', '').replace('-', '')}{file_suffix}:
    """
    {description}
    """
    
    def setup_method(self, method):
        """Setup before each test method"""
        print(f"Setting up {{method.__name__}}")
    
    def teardown_method(self, method):
        """Cleanup after each test method"""
        print(f"Cleaning up {{method.__name__}}")

'''

        # Generate test methods for each scenario
        for scenario in scenarios:
            method_name = self._sanitize_method_name(scenario, 'python')
            timeout = 30 if category == 'performance' else 10
            
            content += f'''    @pytest.mark.{category}
    @pytest.mark.timeout({timeout})
    def test_{method_name}(self):
        """Test: {scenario}"""
        print(f"Testing: {scenario}")
        
        # Arrange
        scenario_name = "{scenario}"
        
        # Act
        result = self._execute_scenario(scenario_name)
        
        # Assert
        assert result is not None, "Scenario should return a valid result"
        assert result.get('success', False), "Scenario should execute successfully"
        
        print(f"Scenario completed successfully: {scenario}")

'''

            # Add async version for integration and performance tests
            if category in ['integration', 'performance']:
                content += f'''    @pytest.mark.{category}
    @pytest.mark.asyncio
    @pytest.mark.timeout({timeout * 2})
    async def test_{method_name}_async(self):
        """Test (Async): {scenario}"""
        print(f"Testing (Async): {scenario}")
        
        # Arrange
        scenario_name = "{scenario}"
        
        # Act
        result = await self._execute_scenario_async(scenario_name)
        
        # Assert
        assert result is not None, "Async scenario should return a valid result"
        assert result.get('success', False), "Async scenario should execute successfully"
        
        print(f"Async scenario completed successfully: {scenario}")

'''

        # Add helper methods
        content += '''    def _execute_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Execute a test scenario"""
        try:
            print(f"Executing scenario: {scenario_name}")
            
            # Add your actual test logic here
            # This is a placeholder that simulates successful execution
            time.sleep(0.1)  # Simulate some work
            
            return {"success": True, "message": "Scenario executed successfully"}
        except Exception as ex:
            return {"success": False, "message": str(ex)}
    
    async def _execute_scenario_async(self, scenario_name: str) -> Dict[str, Any]:
        """Execute a test scenario asynchronously"""
        try:
            print(f"Executing async scenario: {scenario_name}")
            
            # Add your actual async test logic here
            await asyncio.sleep(0.1)  # Simulate some async work
            
            return {"success": True, "message": "Async scenario executed successfully"}
        except Exception as ex:
            return {"success": False, "message": str(ex)}
'''

        return content
    
    def _generate_java_test_content(self, category: str, scenarios: List[str], product_name: str, 
                                    file_suffix: str, description: str) -> str:
        """Generate Java JUnit test content"""
        # Ensure class name matches file name exactly
        safe_product_name = product_name.replace(' ', '').replace('-', '')
        class_name = f"{safe_product_name}{file_suffix}"
        package_name = f"com.{product_name.lower().replace(' ', '').replace('-', '')}.tests"
        
        content = f'''package {package_name};

import org.junit.jupiter.api.*;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

/**
 * {description}
 * Category: {category.title()}
 * Class name: {class_name} (matches file name)
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@Tag("{category}")
public class {class_name} {{

    @BeforeEach
    void setUp() {{
        System.out.println("Setting up " + getClass().getSimpleName() + " test");
    }}

    @AfterEach
    void tearDown() {{
        System.out.println("Cleaning up " + getClass().getSimpleName() + " test");
    }}

'''

        # Generate test methods for each scenario
        for scenario in scenarios:
            method_name = self._sanitize_method_name(scenario, 'java')
            timeout = 30 if category == 'performance' else 10
            
            content += f'''    @Test
    @Tag("{category}")
    @DisplayName("{scenario}")
    @Timeout(value = {timeout}, unit = TimeUnit.SECONDS)
    void test{method_name}() {{
        System.out.println("Testing: {scenario}");
        
        // Arrange
        String scenarioName = "{scenario}";
        
        // Act
        ScenarioResult result = executeScenario(scenarioName);
        
        // Assert
        Assertions.assertNotNull(result, "Scenario should return a valid result");
        Assertions.assertTrue(result.isSuccess(), "Scenario should execute successfully");
        
        System.out.println("Scenario completed successfully: " + scenarioName);
    }}

'''

        # Add helper methods and inner class
        content += f'''    private ScenarioResult executeScenario(String scenarioName) {{
        try {{
            System.out.println("Executing scenario: " + scenarioName);
            
            // Add your actual test logic here
            // This is a placeholder that simulates successful execution
            Thread.sleep(100); // Simulate some work
            
            return new ScenarioResult(true, "Scenario executed successfully");
        }} catch (Exception ex) {{
            return new ScenarioResult(false, ex.getMessage());
        }}
    }}

    public static class ScenarioResult {{
        private final boolean success;
        private final String message;

        public ScenarioResult(boolean success, String message) {{
            this.success = success;
            this.message = message;
        }}

        public boolean isSuccess() {{
            return success;
        }}

        public String getMessage() {{
            return message;
        }}
    }}
}}'''

        return content
    
    def _generate_javascript_test_content(self, category: str, scenarios: List[str], product_name: str, 
                                          file_suffix: str, description: str) -> str:
        """Generate JavaScript Jest test content"""
        content = f'''/**
 * {description}
 * Category: {category.title()}
 */

describe('{product_name} - {file_suffix}', () => {{
    beforeEach(() => {{
        console.log('Setting up test');
    }});

    afterEach(() => {{
        console.log('Cleaning up test');
    }});

'''

        # Generate test cases for each scenario
        for scenario in scenarios:
            timeout = 30000 if category == 'performance' else 10000
            
            content += f'''    test('{scenario}', async () => {{
        console.log('Testing: {scenario}');
        
        // Arrange
        const scenarioName = '{scenario}';
        
        // Act
        const result = await executeScenario(scenarioName);
        
        // Assert
        expect(result).toBeDefined();
        expect(result.success).toBe(true);
        
        console.log('Scenario completed successfully:', scenarioName);
    }}, {timeout});

'''

        # Add helper functions
        content += '''});

/**
 * Execute a test scenario
 * @param {string} scenarioName - Name of the scenario to execute
 * @returns {Promise<{success: boolean, message: string}>}
 */
async function executeScenario(scenarioName) {
    try {
        console.log('Executing scenario:', scenarioName);
        
        // Add your actual test logic here
        // This is a placeholder that simulates successful execution
        await new Promise(resolve => setTimeout(resolve, 100)); // Simulate some async work
        
        return { success: true, message: 'Scenario executed successfully' };
    } catch (error) {
        return { success: false, message: error.message };
    }
}
'''

        return content
    
    def _generate_go_test_content(self, category: str, scenarios: List[str], product_name: str, 
                                  file_suffix: str, description: str) -> str:
        """Generate Go test content"""
        package_name = product_name.lower().replace(' ', '').replace('-', '')
        
        content = f'''package {package_name}

import (
    "fmt"
    "testing"
    "time"
)

// {description}
// Category: {category.title()}

'''

        # Generate test functions for each scenario
        for scenario in scenarios:
            func_name = self._sanitize_method_name(scenario, 'go')
            
            content += f'''func Test{func_name}(t *testing.T) {{
    fmt.Printf("Testing: {scenario}\\n")
    
    // Arrange
    scenarioName := "{scenario}"
    
    // Act
    result := executeScenario(scenarioName)
    
    // Assert
    if result == nil {{
        t.Error("Scenario should return a valid result")
        return
    }}
    
    if !result.Success {{
        t.Errorf("Scenario should execute successfully: %s", result.Message)
        return
    }}
    
    fmt.Printf("Scenario completed successfully: %s\\n", scenarioName)
}}

'''

        # Add helper types and functions
        content += '''type ScenarioResult struct {
    Success bool
    Message string
}

func executeScenario(scenarioName string) *ScenarioResult {
    fmt.Printf("Executing scenario: %s\\n", scenarioName)
    
    // Add your actual test logic here
    // This is a placeholder that simulates successful execution
    time.Sleep(100 * time.Millisecond) // Simulate some work
    
    return &ScenarioResult{
        Success: true,
        Message: "Scenario executed successfully",
    }
}
'''

        return content
    
    def _generate_rust_test_content(self, category: str, scenarios: List[str], product_name: str, 
                                    file_suffix: str, description: str) -> str:
        """Generate Rust test content"""
        content = f'''//! {description}
//! Category: {category.title()}

use std::{{thread, time}};

#[derive(Debug)]
pub struct ScenarioResult {{
    pub success: bool,
    pub message: String,
}}

'''

        # Generate test functions for each scenario
        for scenario in scenarios:
            func_name = self._sanitize_method_name(scenario, 'rust')
            
            content += f'''#[test]
fn test_{func_name}() {{
    println!("Testing: {scenario}");
    
    // Arrange
    let scenario_name = "{scenario}";
    
    // Act
    let result = execute_scenario(scenario_name);
    
    // Assert
    assert!(result.success, "Scenario should execute successfully: {{}}", result.message);
    
    println!("Scenario completed successfully: {{}}", scenario_name);
}}

'''

        # Add helper function
        content += '''fn execute_scenario(scenario_name: &str) -> ScenarioResult {
    println!("Executing scenario: {}", scenario_name);
    
    // Add your actual test logic here
    // This is a placeholder that simulates successful execution
    thread::sleep(time::Duration::from_millis(100)); // Simulate some work
    
    ScenarioResult {
        success: true,
        message: "Scenario executed successfully".to_string(),
    }
}
'''

        return content
    
    def _generate_generic_test_content(self, category: str, scenarios: List[str], product_name: str, 
                                       file_suffix: str, description: str) -> str:
        """Generate generic test content for unsupported languages"""
        content = f'''/*
 * {description}
 * Category: {category.title()}
 * Product: {product_name}
 */

Test Scenarios for {category.title()}:

'''
        
        for i, scenario in enumerate(scenarios, 1):
            content += f'''{i}. {scenario}
   - Description: Test scenario for {scenario}
   - Expected: Successful execution
   - Category: {category}

'''
        
        return content
    
    def _sanitize_method_name(self, scenario: str, language: str = 'csharp') -> str:
        """Sanitize scenario text to create valid method names"""
        # Remove special characters and replace with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', scenario)
        
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Ensure it starts with a letter (for languages that require it)
        if language.lower() in ['csharp', 'c#', 'java']:
            if sanitized and not sanitized[0].isalpha():
                sanitized = 'Test_' + sanitized
            # Capitalize first letter for C# and Java
            if sanitized:
                sanitized = sanitized[0].upper() + sanitized[1:]
        
        # Handle empty or very short names
        if not sanitized or len(sanitized) < 3:
            sanitized = 'TestScenario'
        
        return sanitized
    
    def create_categorized_test_files(self, project_dir: str, scenarios: List[str], language: str, 
                                      product_name: str, namespace: str = None) -> Dict[str, str]:
        """Create categorized test files for all scenarios"""
        categorized_scenarios = self.categorize_scenarios(scenarios)
        created_files = {}
        
        # Ensure safe product name for file and class naming
        safe_product_name = product_name.replace(' ', '').replace('-', '')
        
        for category, category_scenarios in categorized_scenarios.items():
            if not category_scenarios:
                continue
            
            # Generate file content
            content = self.generate_test_file_content(
                category, category_scenarios, language, product_name, namespace
            )
            
            # Determine file extension and path
            file_extensions = {
                'csharp': '.cs',
                'c#': '.cs',
                'java': '.java',
                'python': '.py',
                'javascript': '.test.js',
                'js': '.test.js',
                'node.js': '.test.js',
                'go': '_test.go',
                'rust': '.rs'
            }
            
            extension = file_extensions.get(language.lower(), '.txt')
            category_config = self.scenario_categories.get(category, {})
            file_suffix = category_config.get('file_suffix', 'Tests')
            
            # Create appropriate directory structure
            if language.lower() in ['csharp', 'c#']:
                test_dir = os.path.join(project_dir, 'Tests')
            elif language.lower() == 'java':
                test_dir = os.path.join(project_dir, 'src', 'test', 'java')
            elif language.lower() == 'python':
                test_dir = os.path.join(project_dir, 'tests')
            else:
                test_dir = os.path.join(project_dir, 'tests')
            
            os.makedirs(test_dir, exist_ok=True)
            
            # Create file - ensure filename matches class name exactly
            filename = f"{safe_product_name}{file_suffix}{extension}"
            file_path = os.path.join(test_dir, filename)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                created_files[f"{category}_tests"] = file_path
                print(f"✅ Created {category} test file: {filename} (class: {safe_product_name}{file_suffix})")
                
            except Exception as e:
                print(f"❌ Failed to create {category} test file: {str(e)}")
        
        return created_files
    
    def get_categorization_summary(self, scenarios: List[str]) -> Dict[str, Any]:
        """Get a summary of how scenarios would be categorized"""
        categorized = self.categorize_scenarios(scenarios)
        
        summary = {
            'total_scenarios': len(scenarios),
            'categories_found': len(categorized),
            'categorization': {},
            'distribution': {}
        }
        
        for category, category_scenarios in categorized.items():
            config = self.scenario_categories.get(category, {})
            summary['categorization'][category] = {
                'count': len(category_scenarios),
                'scenarios': category_scenarios,
                'description': config.get('description', ''),
                'file_suffix': config.get('file_suffix', '')
            }
            summary['distribution'][category] = len(category_scenarios)
        
        return summary
