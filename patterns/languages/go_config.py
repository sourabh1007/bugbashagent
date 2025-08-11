"""
Go language configuration
"""

import os
from .base import FrameworkConfig, LanguageConfig


def get_go_config() -> LanguageConfig:
    """Get Go language configuration"""
    
    framework = FrameworkConfig(
        name="testing",
        version=os.getenv("GO_VERSION", "1.21"),
        dependencies=[],  # Built-in testing package
        test_file_pattern="{product_name}_test.go",
        test_method_pattern="TestScenarioMethod",
        example_template="""
func TestUserLoginWithValidCredentials(t *testing.T) {
    // Arrange
    username := "testuser"
    password := "validpassword"
    expectedResult := true
    
    // Act
    actualResult := simulateLogin(username, password)
    
    // Assert
    if actualResult != expectedResult {
        t.Errorf("Expected %v, got %v", expectedResult, actualResult)
    }
}

func simulateLogin(username, password string) bool {
    return len(username) > 0 && len(password) > 0
}
"""
    )
    
    return LanguageConfig(
        name="go",
        display_name="Go",
        file_extensions=[".go"],
        framework=framework,
        project_structure={
            "source": "./",
            "tests": "./",
            "config": "./"
        },
        build_file="go.mod",
        build_commands=["go mod tidy", "go build"],
        test_commands=["go test -v"],
        imports=["import \"testing\""]
    )
