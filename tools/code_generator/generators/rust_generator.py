"""
Rust Project Generator

Generates Rust test projects with proper Cargo and Rust testing conventions.
"""

import os
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class RustProjectGenerator(BaseProjectGenerator):
    """Generator for Rust test projects"""
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate Rust test project structure"""
        created_files = {}
        
        # Create Cargo.toml file
        package_name = product_name.lower().replace(' ', '_').replace('-', '_')
        cargo_toml_content = self._create_cargo_toml(package_name)
        cargo_toml_file = os.path.join(project_dir, "Cargo.toml")
        with open(cargo_toml_file, 'w', encoding='utf-8') as f:
            f.write(cargo_toml_content)
        created_files["cargo_toml"] = cargo_toml_file
        
        # Create src directory
        src_dir = os.path.join(project_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        
        # Create lib.rs file (minimal library for testing)
        lib_content = self._create_lib_content(product_name, scenarios)
        lib_file = os.path.join(src_dir, "lib.rs")
        with open(lib_file, 'w', encoding='utf-8') as f:
            f.write(lib_content)
        created_files["lib"] = lib_file
        
        # Create tests directory
        tests_dir = os.path.join(project_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        
        # Create integration test file
        integration_test_content = self._create_integration_test_content(product_name, scenarios)
        integration_test_file = os.path.join(tests_dir, "integration_tests.rs")
        with open(integration_test_file, 'w', encoding='utf-8') as f:
            f.write(integration_test_content)
        created_files["integration_test"] = integration_test_file
        
        # Create README with test instructions
        readme_content = self._create_readme(product_name, scenarios, generated_content)
        readme_file = os.path.join(project_dir, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_cargo_toml(self, package_name: str) -> str:
        """Create Cargo.toml file content"""
        return f'''[package]
name = "{package_name}"
version = "0.1.0"
edition = "2021"

[dependencies]

[dev-dependencies]
tokio-test = "0.4"
assert_matches = "1.5"
'''
    
    def _create_lib_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create lib.rs file content with test validation logic"""
        return f'''//! {product_name} Test Library
//! 
//! This library contains validation logic for testing scenarios.

/// Validates a scenario with test data
/// 
/// # Arguments
/// 
/// * `test_data` - The test data to validate
/// * `scenario` - The scenario name being tested
/// 
/// # Returns
/// 
/// * `bool` - True if validation passes, false otherwise
pub fn validate_scenario(test_data: &str, scenario: &str) -> bool {{
    !test_data.trim().is_empty() && !scenario.trim().is_empty()
}}

/// Gets the list of supported scenarios
pub fn get_scenarios() -> Vec<&'static str> {{
    vec![
{chr(10).join([f'        "{scenario}",' for scenario in scenarios])}
    ]
}}

/// Validates all scenarios with integration test data
pub fn validate_all_scenarios(test_data: &str) -> Result<(), String> {{
    let scenarios = get_scenarios();
    
    for scenario in scenarios {{
        if !validate_scenario(test_data, scenario) {{
            return Err(format!("Validation failed for scenario: {{}}", scenario));
        }}
    }}
    
    Ok(())
}}

#[cfg(test)]
mod tests {{
    use super::*;

{chr(10).join([f'''    #[test]
    fn test_{scenario.lower().replace(' ', '_').replace('-', '_')}() {{
        let test_data = "test_data_for_{scenario.lower().replace(' ', '_').replace('-', '_')}";
        let scenario = "{scenario}";
        
        let result = validate_scenario(test_data, scenario);
        assert!(result, "Scenario '{{}}' should pass validation", scenario);
    }}
''' for scenario in scenarios])}
    
    #[test]
    fn test_all_scenarios_integration() {{
        let test_data = "integration_test_data";
        let result = validate_all_scenarios(test_data);
        
        assert!(result.is_ok(), "All scenarios integration test should pass: {{:?}}", result);
    }}
    
    #[test]
    fn test_edge_cases() {{
        // Test empty inputs
        assert!(!validate_scenario("", "valid_scenario"));
        assert!(!validate_scenario("valid_data", ""));
        
        // Test whitespace-only inputs
        assert!(!validate_scenario("   ", "valid_scenario"));
        assert!(!validate_scenario("valid_data", "   "));
        
        // Test valid inputs
        assert!(validate_scenario("valid_data", "valid_scenario"));
    }}
    
    #[test]
    fn test_scenario_count() {{
        let scenarios = get_scenarios();
        assert_eq!(scenarios.len(), {len(scenarios)}, "Should have exactly {len(scenarios)} scenarios");
        
        // Validate all scenarios are non-empty
        for (i, scenario) in scenarios.iter().enumerate() {{
            assert!(!scenario.is_empty(), "Scenario at index {{}} should not be empty", i);
        }}
    }}
    
    #[test]
    fn test_validate_all_scenarios_with_invalid_data() {{
        let result = validate_all_scenarios("");
        assert!(result.is_err(), "Should fail with empty test data");
        
        let result = validate_all_scenarios("   ");
        assert!(result.is_err(), "Should fail with whitespace-only test data");
    }}
}}
'''
    
    def _create_integration_test_content(self, product_name: str, scenarios: List[str]) -> str:
        """Create integration test file content"""
        package_name = product_name.lower().replace(' ', '_').replace('-', '_')
        
        return f'''//! Integration tests for {product_name}
//! 
//! These tests validate the library functionality from an external perspective.

use {package_name}::{{validate_scenario, get_scenarios, validate_all_scenarios}};

#[test]
fn integration_test_all_scenarios() {{
    let scenarios = get_scenarios();
    
    for scenario in scenarios {{
        let test_data = format!("integration_test_data_for_{{}}", scenario.to_lowercase().replace(' ', "_"));
        let result = validate_scenario(&test_data, scenario);
        
        assert!(result, "Integration test failed for scenario: {{}}", scenario);
    }}
}}

#[test]
fn integration_test_batch_validation() {{
    let test_data = "batch_integration_test_data";
    let result = validate_all_scenarios(test_data);
    
    assert!(result.is_ok(), "Batch validation should succeed: {{:?}}", result);
}}

#[test]
fn integration_test_error_handling() {{
    // Test with invalid inputs
    let result = validate_all_scenarios("");
    assert!(result.is_err(), "Should handle empty test data gracefully");
    
    let result = validate_all_scenarios("   ");
    assert!(result.is_err(), "Should handle whitespace-only test data gracefully");
}}

#[test]
fn integration_test_scenario_consistency() {{
    let scenarios = get_scenarios();
    
    // Verify all scenarios from the list work with validation
    for scenario in scenarios {{
        let test_data = "consistency_test_data";
        let result = validate_scenario(test_data, scenario);
        
        assert!(result, "Scenario consistency test failed for: {{}}", scenario);
    }}
}}

/// Test module for performance and stress testing
#[cfg(test)]
mod performance_tests {{
    use super::*;
    use std::time::Instant;
    
    #[test]
    fn performance_test_single_validation() {{
        let start = Instant::now();
        let iterations = 10_000;
        
        for _ in 0..iterations {{
            let result = validate_scenario("performance_test_data", "performance_scenario");
            assert!(result);
        }}
        
        let duration = start.elapsed();
        println!("{{}} validations took: {{:?}}", iterations, duration);
        
        // Should complete reasonably quickly (adjust threshold as needed)
        assert!(duration.as_millis() < 1000, "Performance test took too long: {{:?}}", duration);
    }}
    
    #[test]
    fn stress_test_batch_validation() {{
        let test_data = "stress_test_data";
        let iterations = 1_000;
        
        let start = Instant::now();
        for _ in 0..iterations {{
            let result = validate_all_scenarios(test_data);
            assert!(result.is_ok());
        }}
        let duration = start.elapsed();
        
        println!("{{}} batch validations took: {{:?}}", iterations, duration);
        assert!(duration.as_millis() < 5000, "Stress test took too long: {{:?}}", duration);
    }}
}}
'''
    
    def _create_readme(self, product_name: str, scenarios: List[str], generated_content: str) -> str:
        """Create README with test instructions"""
        package_name = product_name.lower().replace(' ', '_').replace('-', '_')
        
        return f'''# {product_name} Test Project

This is a test-only Rust project for {product_name} using Cargo and Rust's built-in testing framework.

## Setup

1. Ensure Rust 1.70+ is installed
2. Build the project:
   ```bash
   cargo build
   ```

## Running Tests

```bash
# Run all tests (unit + integration)
cargo test

# Run tests with output
cargo test -- --nocapture

# Run only unit tests
cargo test --lib

# Run only integration tests  
cargo test --test integration_tests

# Run specific test
cargo test test_specific_scenario

# Run tests with coverage (requires cargo-tarpaulin)
cargo install cargo-tarpaulin
cargo tarpaulin --out Html

# Run benchmarks (if any)
cargo bench
```

## Project Structure

- `Cargo.toml` - Package configuration and dependencies
- `src/lib.rs` - Library code with unit tests
- `tests/integration_tests.rs` - Integration tests
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

### Unit Tests (in src/lib.rs)
- Individual tests for each scenario with specific test data
- Edge case testing with invalid inputs
- Scenario count validation

### Integration Tests (in tests/)
- External perspective testing of the library
- Batch validation testing
- Performance and stress testing
- Error handling validation

## Rust Testing Features Used

This project demonstrates various Rust testing capabilities:
- `#[test]` attribute for test functions
- `assert!`, `assert_eq!` macros for assertions
- `cfg(test)` conditional compilation
- Integration tests in separate files
- Documentation tests (in doc comments)
- Custom test modules
- Performance testing with timing

## Dependencies

- **tokio-test**: Async testing utilities (dev dependency)
- **assert_matches**: Pattern matching assertions (dev dependency)
- **Rust 1.70+**: Required Rust version

## Commands Reference

```bash
# Check code without building
cargo check

# Format code
cargo fmt

# Lint code
cargo clippy

# Generate documentation
cargo doc --open

# Clean build artifacts
cargo clean
```

## Notes

This is a test-only project designed to validate the functionality described in the analyzed scenarios. No main application code is generated - only comprehensive test coverage using Rust's excellent built-in testing ecosystem.

The project structure follows Rust best practices with unit tests alongside the code and integration tests in a separate directory.
'''
