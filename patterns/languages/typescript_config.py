"""
TypeScript language configuration for test project generation.
"""

import os
from .base import FrameworkConfig, LanguageConfig


def get_typescript_config() -> LanguageConfig:
    """Get TypeScript language configuration"""
    
    framework = FrameworkConfig(
        name="Jest",
        version=os.getenv("JEST_VERSION", "29.7.0"),
        dependencies=[
            f"jest@{os.getenv('JEST_VERSION', '29.7.0')}",
            f"@types/jest@{os.getenv('JEST_TYPES_VERSION', '29.5.5')}",
            f"ts-jest@{os.getenv('TS_JEST_VERSION', '29.1.1')}",
            f"typescript@{os.getenv('TYPESCRIPT_VERSION', '5.2.2')}",
            f"@types/node@{os.getenv('NODE_TYPES_VERSION', '20.8.0')}",
            f"ts-node@{os.getenv('TS_NODE_VERSION', '10.9.1')}"
        ],
        test_file_pattern="tests/{product_name}.test.ts",
        test_method_pattern="test('scenario description', ...)",
        example_template="""
interface UserCredentials {
    username: string;
    password: string;
}

interface AuthResult {
    success: boolean;
    token?: string;
    error?: string;
}

class UserAuthenticationService {
    private validUsers: Record<string, string> = {
        'admin': 'password123',
        'user': 'mypassword'
    };
    
    authenticateUser(username: string, password: string): AuthResult {
        if (!username || !password) {
            return { success: false, error: 'Username and password required' };
        }
        
        if (this.validUsers[username] === password) {
            return { success: true, token: `token_${username}_${Date.now()}` };
        }
        
        return { success: false, error: 'Invalid credentials' };
    }
    
    validateToken(token: string): boolean {
        return token.startsWith('token_') && token.length > 10;
    }
}
"""
    )
    
    return LanguageConfig(
        name="typescript",
        display_name="TypeScript",
        file_extensions=[".ts"],
        framework=framework,
        project_structure={
            "source": "src/",
            "tests": "tests/",
            "config": "./",
            "output": "dist/"
        },
        build_file="package.json",
        build_commands=[
            "npm install",
            "npm run build"
        ],
        test_commands=[
            "npm test",
            "npm run test:coverage"
        ],
        imports=[
            "import { describe, test, expect } from '@jest/globals';",
            "import * as fs from 'fs';",
            "import * as path from 'path';"
        ]
    )
