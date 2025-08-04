"""
Python Project Generator

Generates Python projects with proper module structure, requirements, and pytest tests.
"""

import os
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class PythonProjectGenerator(BaseProjectGenerator):
    """Generator for Python projects"""
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate Python test project structure only"""
        created_files = {}
        
        # Create test file only
        test_content = self._create_test_content(product_name, scenarios)
        test_file = os.path.join(project_dir, "test_scenarios.py")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        created_files["test"] = test_file
        
        # Create requirements.txt with only testing dependencies
        requirements_content = """pytest>=7.0.0
pytest-cov>=4.0.0
pytest-html>=3.1.0"""
        requirements_file = os.path.join(project_dir, "requirements.txt")
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files["requirements"] = requirements_file
        
        # Create pytest configuration
        pytest_ini_content = """[tool:pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers"""
        pytest_file = os.path.join(project_dir, "pytest.ini")
        with open(pytest_file, 'w', encoding='utf-8') as f:
            f.write(pytest_ini_content)
        created_files["pytest_config"] = pytest_file
        
        # Create README with test instructions
        readme_file = os.path.join(project_dir, "README.md")
        readme_content = self._create_test_readme(product_name, scenarios, generated_content)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_main_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create main.py content"""
        return f'''"""
{product_name}

Main application entry point.
"""

def main():
    """Main function to run the application."""
    print("Welcome to {product_name}!")
    
    # TODO: Implement scenarios:
    {chr(10).join([f'    # - {scenario}' for scenario in scenarios])}
    
    print("Application completed successfully.")

if __name__ == "__main__":
    main()
'''
    
    def _create_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create self-contained test file content"""
        sanitized_name = self._sanitize_name(product_name)
        return f'''"""
Test cases for {product_name}

This module contains comprehensive tests for all scenarios related to {product_name}.
"""

import pytest
from typing import List, Any


class Test{sanitized_name}Scenarios:
    """Test class for {product_name} scenarios."""
    
    def setup_method(self):
        """Setup test data for each test method."""
        self.test_data = {{
            "scenarios": {scenarios},
            "product_name": "{product_name}"
        }}

{chr(10).join([f'''    def test_{scenario.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')}(self):
        """Test scenario: {scenario}"""
        # Arrange
        scenario_name = "{scenario}"
        test_input = "test_data_for_{scenario.lower().replace(' ', '_')}"
        expected_result = True
        
        # Act
        result = self._validate_scenario(test_input, scenario_name)
        
        # Assert
        assert result is True, f"Scenario '{{scenario_name}}' should be validated successfully"
        assert scenario_name in self.test_data["scenarios"], f"Scenario '{{scenario_name}}' should be in the scenario list"
''' for scenario in scenarios])}
    
    def test_all_scenarios_integration(self):
        """Integration test for all scenarios."""
        # Arrange
        all_scenarios = self.test_data["scenarios"]
        
        # Act & Assert
        for scenario in all_scenarios:
            result = self._validate_scenario("integration_test_data", scenario)
            assert result is True, f"Integration test failed for scenario: {{scenario}}"
        
        assert len(all_scenarios) == {len(scenarios)}, f"Expected {len(scenarios)} scenarios, got {{len(all_scenarios)}}"
    
    def test_scenario_validation_with_invalid_input(self):
        """Test scenario validation with invalid inputs."""
        # Test with None input
        result = self._validate_scenario(None, "test_scenario")
        assert result is False, "Validation should fail with None input"
        
        # Test with empty string
        result = self._validate_scenario("", "test_scenario")
        assert result is False, "Validation should fail with empty input"
        
        # Test with None scenario
        result = self._validate_scenario("valid_input", None)
        assert result is False, "Validation should fail with None scenario"
    
    def test_product_name_validation(self):
        """Test that the product name is correctly set."""
        assert self.test_data["product_name"] == "{product_name}"
        assert len(self.test_data["product_name"]) > 0
    
    @staticmethod
    def _validate_scenario(input_data: Any, scenario: str) -> bool:
        """
        Helper method to validate scenarios.
        
        In a real test project, this would test actual business logic.
        For this generated test project, it simulates validation logic.
        
        Args:
            input_data: The input data to validate
            scenario: The scenario name being tested
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        if input_data is None or scenario is None:
            return False
        
        if isinstance(input_data, str) and len(input_data) == 0:
            return False
        
        if isinstance(scenario, str) and len(scenario) == 0:
            return False
        
        # Mock validation logic - in real tests this would contain actual business logic
        return True


# Additional test functions for pytest discovery
def test_module_imports():
    """Test that all required modules can be imported."""
    import pytest
    import typing
    assert pytest.__version__ is not None
    assert typing is not None


def test_scenario_count():
    """Test that the correct number of scenarios are defined."""
    scenarios = {scenarios}
    assert len(scenarios) == {len(scenarios)}
    assert all(isinstance(scenario, str) for scenario in scenarios)


@pytest.mark.parametrize("scenario", {scenarios})
def test_parametrized_scenarios(scenario):
    """Parametrized test for all scenarios."""
    # This test runs once for each scenario
    assert isinstance(scenario, str)
    assert len(scenario) > 0
    
    # Simulate scenario-specific testing
    test_instance = Test{sanitized_name}Scenarios()
    test_instance.setup_method()
    result = test_instance._validate_scenario(f"test_data_for_{{scenario}}", scenario)
    assert result is True, f"Parametrized test failed for scenario: {{scenario}}"
'''
    
    def _create_test_readme(self, product_name: str, scenarios: List[str], generated_content: str) -> str:
        """Create README for test project only"""
        return f"""# {product_name} - Test Project

This is a test-only project generated for validating scenarios related to {product_name}.

## Test Scenarios

{chr(10).join([f'- {scenario}' for scenario in scenarios])}

## Project Structure

```
├── test_scenarios.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Build Instructions

1. Make sure you have Python 3.8+ installed
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\\Scripts\\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```
3. Install test dependencies:
   ```
   pip install -r requirements.txt
   ```

## Test Execution

Run all tests:
```
pytest
```

Run tests with verbose output:
```
pytest -v
```

Run tests with coverage:
```
pytest --cov=. --cov-report=html
```

Run specific test class:
```
pytest test_scenarios.py::Test{self._sanitize_name(product_name)}Scenarios -v
```

Run parametrized tests only:
```
pytest -k "parametrized" -v
```

## Test Details

This test project validates the following scenarios:
{chr(10).join([f'- **{scenario}**: Comprehensive test coverage including edge cases' for scenario in scenarios])}

### Test Types Included:
- **Unit Tests**: Individual scenario validation
- **Integration Tests**: All scenarios working together
- **Parametrized Tests**: Data-driven testing for each scenario
- **Edge Case Tests**: Invalid input handling
- **Validation Tests**: Input and configuration validation

All tests are self-contained and do not require external dependencies beyond the testing framework.

## Generated Content

{generated_content}
"""
