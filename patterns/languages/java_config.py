"""
Java language configuration
"""

import os
from .base import FrameworkConfig, LanguageConfig


def get_java_config() -> LanguageConfig:
    """Get Java language configuration"""
    
    framework = FrameworkConfig(
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
public class UserAuthenticationService {
    private Map<String, String> validUsers;
    
    public UserAuthenticationService() {
        validUsers = new HashMap<>();
        validUsers.put("admin", "password123");
        validUsers.put("user", "mypassword");
    }
    
    public AuthenticationResult authenticateUser(String username, String password) {
        if (username == null || username.isEmpty() || password == null || password.isEmpty()) {
            throw new IllegalArgumentException("Username and password are required");
        }
        
        if (validUsers.containsKey(username) && validUsers.get(username).equals(password)) {
            return new AuthenticationResult("success", username, true, null);
        }
        
        return new AuthenticationResult("failed", null, false, "Invalid credentials");
    }
    
    public boolean isUserValid(String username) {
        return validUsers.containsKey(username);
    }
}

class AuthenticationResult {
    private String status;
    private String user;
    private boolean authenticated;
    private String message;
    
    public AuthenticationResult(String status, String user, boolean authenticated, String message) {
        this.status = status;
        this.user = user;
        this.authenticated = authenticated;
        this.message = message;
    }
    
    // Getters and setters omitted for brevity
    public String getStatus() { return status; }
    public boolean isAuthenticated() { return authenticated; }
}
"""
    )
    
    return LanguageConfig(
        name="java",
        display_name="Java",
        file_extensions=[".java"],
        framework=framework,
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
