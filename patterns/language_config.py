"""
Language-specific configuration for test project generation.
This file contains configurable environment properties and library versions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import os


@dataclass
class FrameworkConfig:
    """Configuration for a specific testing framework"""
    name: str
    version: str
    dependencies: List[str]
    test_file_pattern: str
    test_method_pattern: str
    example_template: str


@dataclass
class LanguageConfig:
    """Configuration for a specific programming language"""
    name: str
    display_name: str
    file_extensions: List[str]
    framework: FrameworkConfig
    project_structure: Dict[str, str]
    build_file: str
    build_commands: List[str]
    test_commands: List[str]
    imports: List[str]


class LanguageConfigManager:
    """Manages language-specific configurations"""
    
    def __init__(self):
        self._configs = self._initialize_configs()
    
    def _initialize_configs(self) -> Dict[str, LanguageConfig]:
        """Initialize all language configurations"""
        configs = {}
        
        # C# Configuration
        csharp_framework = FrameworkConfig(
            name="NUnit",
            version=os.getenv("NUNIT_VERSION", "4.0.1"),
            dependencies=[
                f"NUnit@{os.getenv('NUNIT_VERSION', '4.0.1')}",
                f"NUnit3TestAdapter@{os.getenv('NUNIT_ADAPTER_VERSION', '4.5.0')}",
                f"Microsoft.NET.Test.Sdk@{os.getenv('DOTNET_TEST_SDK_VERSION', '17.8.0')}"
            ],
            test_file_pattern="Tests/{product_name}Tests.cs",
            test_method_pattern="Test_ScenarioMethod",
            example_template="""
public class UserAuthenticationService
{{
    private Dictionary<string, string> validUsers = new Dictionary<string, string>
    {{
        {{"admin", "password123"}},
        {{"user", "mypassword"}}
    }};
    
    public AuthenticationResult AuthenticateUser(string username, string password)
    {{
        if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
            throw new ArgumentException("Username and password are required");
        
        if (validUsers.ContainsKey(username) && validUsers[username] == password)
        {{
            return new AuthenticationResult 
            {{ 
                Status = "success", 
                User = username, 
                IsAuthenticated = true 
            }};
        }}
        
        return new AuthenticationResult 
        {{ 
            Status = "failed", 
            Message = "Invalid credentials", 
            IsAuthenticated = false 
        }};
    }}
    
    public bool IsUserValid(string username)
    {{
        return validUsers.ContainsKey(username);
    }}
}}

public class AuthenticationResult
{{
    public string Status {{ get; set; }}
    public string User {{ get; set; }}
    public string Message {{ get; set; }}
    public bool IsAuthenticated {{ get; set; }}
}}
"""
        )
        
        configs['csharp'] = LanguageConfig(
            name="csharp",
            display_name="C#",
            file_extensions=[".cs"],
            framework=csharp_framework,
            project_structure={
                "source": "src/",
                "tests": "Tests/",
                "config": "./"
            },
            build_file="{product_name}.csproj",
            build_commands=["dotnet restore", "dotnet build"],
            test_commands=["dotnet test"],
            imports=["using System;", "using NUnit.Framework;"]
        )
        
        # Java Configuration
        java_framework = FrameworkConfig(
            name="JUnit",
            version=os.getenv("JUNIT_VERSION", "5.10.0"),
            dependencies=[
                f"org.junit.jupiter:junit-jupiter-api:{os.getenv('JUNIT_VERSION', '5.10.0')}",
                f"org.junit.jupiter:junit-jupiter-engine:{os.getenv('JUNIT_VERSION', '5.10.0')}",
                f"org.junit.platform:junit-platform-runner:{os.getenv('JUNIT_PLATFORM_VERSION', '1.10.0')}"
            ],
            test_file_pattern="src/test/java/{product_name}Tests.java",
            test_method_pattern="testScenarioMethod",
            example_template="""
public class UserAuthenticationService {{
    private Map<String, String> validUsers;
    
    public UserAuthenticationService() {{
        validUsers = new HashMap<>();
        validUsers.put("admin", "password123");
        validUsers.put("user", "mypassword");
    }}
    
    public AuthenticationResult authenticateUser(String username, String password) {{
        if (username == null || username.isEmpty() || password == null || password.isEmpty()) {{
            throw new IllegalArgumentException("Username and password are required");
        }}
        
        if (validUsers.containsKey(username) && validUsers.get(username).equals(password)) {{
            return new AuthenticationResult("success", username, true, null);
        }}
        
        return new AuthenticationResult("failed", null, false, "Invalid credentials");
    }}
    
    public boolean isUserValid(String username) {{
        return validUsers.containsKey(username);
    }}
}}

class AuthenticationResult {{
    private String status;
    private String user;
    private boolean authenticated;
    private String message;
    
    public AuthenticationResult(String status, String user, boolean authenticated, String message) {{
        this.status = status;
        this.user = user;
        this.authenticated = authenticated;
        this.message = message;
    }}
    
    // Getters and setters omitted for brevity
    public String getStatus() {{ return status; }}
    public boolean isAuthenticated() {{ return authenticated; }}
}}
"""
        )
        
        configs['java'] = LanguageConfig(
            name="java",
            display_name="Java",
            file_extensions=[".java"],
            framework=java_framework,
            project_structure={
                "source": "src/main/java/",
                "tests": "src/test/java/",
                "config": "./"
            },
            build_file="pom.xml",
            build_commands=["mvn clean compile", "mvn test-compile"],
            test_commands=["mvn test"],
            imports=["import org.junit.jupiter.api.*;", "import static org.junit.jupiter.api.Assertions.*;"]
        )
        
        # Python Configuration
        python_framework = FrameworkConfig(
            name="pytest",
            version=os.getenv("PYTEST_VERSION", "7.4.0"),
            dependencies=[
                f"pytest=={os.getenv('PYTEST_VERSION', '7.4.0')}",
                f"pytest-cov=={os.getenv('PYTEST_COV_VERSION', '4.1.0')}",
                f"pytest-mock=={os.getenv('PYTEST_MOCK_VERSION', '3.11.1')}"
            ],
            test_file_pattern="tests/test_{product_name}.py",
            test_method_pattern="test_scenario_method",
            example_template="""
class UserAuthenticationService:
    def __init__(self):
        self.valid_users = {{"admin": "password123", "user": "mypassword"}}
    
    def authenticate_user(self, username: str, password: str) -> dict:
        \"\"\"Authenticate user with username and password\"\"\"
        if not username or not password:
            raise ValueError("Username and password are required")
        
        if username in self.valid_users and self.valid_users[username] == password:
            return {{"status": "success", "user": username, "authenticated": True}}
        else:
            return {{"status": "failed", "message": "Invalid credentials", "authenticated": False}}
    
    def is_user_valid(self, username: str) -> bool:
        \"\"\"Check if username exists in the system\"\"\"
        return username in self.valid_users

# Example usage
auth_service = UserAuthenticationService()
result = auth_service.authenticate_user("admin", "password123")
print(f"Authentication result: {{result}}")
"""
        )
        
        configs['python'] = LanguageConfig(
            name="python",
            display_name="Python",
            file_extensions=[".py"],
            framework=python_framework,
            project_structure={
                "source": "src/",
                "tests": "tests/",
                "config": "./"
            },
            build_file="requirements.txt",
            build_commands=["pip install -r requirements.txt"],
            test_commands=["pytest -v"],
            imports=["import pytest", "import unittest"]
        )
        
        # JavaScript Configuration
        js_framework = FrameworkConfig(
            name="Jest",
            version=os.getenv("JEST_VERSION", "29.7.0"),
            dependencies=[
                f"jest@{os.getenv('JEST_VERSION', '29.7.0')}",
                f"@types/jest@{os.getenv('JEST_TYPES_VERSION', '29.5.5')}",
                f"ts-jest@{os.getenv('TS_JEST_VERSION', '29.1.1')}"
            ],
            test_file_pattern="tests/{product_name}.test.js",
            test_method_pattern="test('scenario description', ...)",
            example_template="""
class UserAuthenticationService {{
    constructor() {{
        this.validUsers = {{
            'admin': 'password123',
            'user': 'mypassword'
        }};
    }}
    
    authenticateUser(username, password) {{
        if (!username || !password) {{
            throw new Error('Username and password are required');
        }}
        
        if (this.validUsers[username] && this.validUsers[username] === password) {{
            return {{
                status: 'success',
                user: username,
                authenticated: true
            }};
        }}
        
        return {{
            status: 'failed',
            message: 'Invalid credentials',
            authenticated: false
        }};
    }}
    
    isUserValid(username) {{
        return username in this.validUsers;
    }}
}}

// Example usage
const authService = new UserAuthenticationService();
const result = authService.authenticateUser('admin', 'password123');
console.log('Authentication result:', result);

module.exports = UserAuthenticationService;
"""
        )
        
        configs['javascript'] = LanguageConfig(
            name="javascript",
            display_name="JavaScript",
            file_extensions=[".js", ".ts"],
            framework=js_framework,
            project_structure={
                "source": "src/",
                "tests": "tests/",
                "config": "./"
            },
            build_file="package.json",
            build_commands=["npm install", "npm run build"],
            test_commands=["npm test"],
            imports=["// Jest configuration in package.json"]
        )
        
        # Go Configuration
        go_framework = FrameworkConfig(
            name="testing",
            version=os.getenv("GO_VERSION", "1.21"),
            dependencies=[],  # Built-in testing package
            test_file_pattern="{product_name}_test.go",
            test_method_pattern="TestScenarioMethod",
            example_template="""
func TestUserLoginWithValidCredentials(t *testing.T) {{
    // Arrange
    username := "testuser"
    password := "validpassword"
    expectedResult := true
    
    // Act
    actualResult := simulateLogin(username, password)
    
    // Assert
    if actualResult != expectedResult {{
        t.Errorf("Expected %v, got %v", expectedResult, actualResult)
    }}
}}

func simulateLogin(username, password string) bool {{
    return len(username) > 0 && len(password) > 0
}}
"""
        )
        
        configs['go'] = LanguageConfig(
            name="go",
            display_name="Go",
            file_extensions=[".go"],
            framework=go_framework,
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
        
        # Rust Configuration
        rust_framework = FrameworkConfig(
            name="built-in",
            version=os.getenv("RUST_VERSION", "1.70"),
            dependencies=[],  # Built-in testing framework
            test_file_pattern="src/{product_name}_tests.rs",
            test_method_pattern="test_scenario_method",
            example_template="""
#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_user_login_with_valid_credentials() {{
        // Arrange
        let username = "testuser";
        let password = "validpassword";
        let expected_result = true;
        
        // Act
        let actual_result = simulate_login(username, password);
        
        // Assert
        assert_eq!(actual_result, expected_result, "Login should succeed with valid credentials");
    }}
}}

fn simulate_login(username: &str, password: &str) -> bool {{
    !username.is_empty() && !password.is_empty()
}}
"""
        )
        
        configs['rust'] = LanguageConfig(
            name="rust",
            display_name="Rust",
            file_extensions=[".rs"],
            framework=rust_framework,
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
        
        # Add aliases
        configs['c#'] = configs['csharp']
        configs['node.js'] = configs['javascript']
        configs['js'] = configs['javascript']
        
        return configs
    
    def get_config(self, language: str) -> Optional[LanguageConfig]:
        """Get configuration for a specific language"""
        return self._configs.get(language.lower())
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(set(self._configs.keys()) - {'c#', 'node.js', 'js'})  # Remove aliases
    
    def get_all_language_aliases(self) -> List[str]:
        """Get all language names including aliases"""
        return list(self._configs.keys())
