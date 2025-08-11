"""
Python language configuration
"""

import os
from .base import FrameworkConfig, LanguageConfig


def get_python_config() -> LanguageConfig:
    """Get Python language configuration"""
    
    framework = FrameworkConfig(
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
        self.valid_users = {"admin": "password123", "user": "mypassword"}
    
    def authenticate_user(self, username: str, password: str) -> dict:
        \"\"\"Authenticate user with username and password\"\"\"
        if not username or not password:
            raise ValueError("Username and password are required")
        
        if username in self.valid_users and self.valid_users[username] == password:
            return {"status": "success", "user": username, "authenticated": True}
        else:
            return {"status": "failed", "message": "Invalid credentials", "authenticated": False}
    
    def is_user_valid(self, username: str) -> bool:
        \"\"\"Check if username exists in the system\"\"\"
        return username in self.valid_users

# Example usage
auth_service = UserAuthenticationService()
result = auth_service.authenticate_user("admin", "password123")
print(f"Authentication result: {result}")
"""
    )
    
    return LanguageConfig(
        name="python",
        display_name="Python",
        file_extensions=[".py"],
        framework=framework,
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
