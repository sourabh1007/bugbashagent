"""
JavaScript/Node.js language configuration
"""

import os
from .base import FrameworkConfig, LanguageConfig


def get_javascript_config() -> LanguageConfig:
    """Get JavaScript language configuration"""
    
    framework = FrameworkConfig(
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
class UserAuthenticationService {
    constructor() {
        this.validUsers = {
            'admin': 'password123',
            'user': 'mypassword'
        };
    }
    
    authenticateUser(username, password) {
        if (!username || !password) {
            throw new Error('Username and password are required');
        }
        
        if (this.validUsers[username] && this.validUsers[username] === password) {
            return {
                status: 'success',
                user: username,
                authenticated: true
            };
        }
        
        return {
            status: 'failed',
            message: 'Invalid credentials',
            authenticated: false
        };
    }
    
    isUserValid(username) {
        return username in this.validUsers;
    }
}

// Example usage
const authService = new UserAuthenticationService();
const result = authService.authenticateUser('admin', 'password123');
console.log('Authentication result:', result);

module.exports = UserAuthenticationService;
"""
    )
    
    return LanguageConfig(
        name="javascript",
        display_name="JavaScript",
        file_extensions=[".js", ".ts"],
        framework=framework,
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
