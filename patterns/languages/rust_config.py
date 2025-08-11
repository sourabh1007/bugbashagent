"""
Rust language configuration
"""

import os
from .base import FrameworkConfig, LanguageConfig


def get_rust_config() -> LanguageConfig:
    """Get Rust language configuration"""
    
    framework = FrameworkConfig(
        name="built-in",
        version=os.getenv("RUST_VERSION", "1.70"),
        dependencies=[],  # Built-in testing framework
        test_file_pattern="src/{product_name}_tests.rs",
        test_method_pattern="test_scenario_method",
        example_template="""
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_user_login_with_valid_credentials() {
        // Arrange
        let username = "testuser";
        let password = "validpassword";
        let expected_result = true;
        
        // Act
        let actual_result = simulate_login(username, password);
        
        // Assert
        assert_eq!(actual_result, expected_result, "Login should succeed with valid credentials");
    }
}

fn simulate_login(username: &str, password: &str) -> bool {
    !username.is_empty() && !password.is_empty()
}
"""
    )
    
    return LanguageConfig(
        name="rust",
        display_name="Rust",
        file_extensions=[".rs"],
        framework=framework,
        project_structure={
            "source": "src/",
            "tests": "tests/",
            "config": "./"
        },
        build_file="Cargo.toml",
        build_commands=["cargo build"],
        test_commands=["cargo test"],
        imports=["// Built-in testing framework"]
    )
