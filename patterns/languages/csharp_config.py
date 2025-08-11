"""
C# language configuration
"""

import os
from .base import FrameworkConfig, LanguageConfig


def get_csharp_config() -> LanguageConfig:
    """Get C# language configuration"""
    
    framework = FrameworkConfig(
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
{
    private Dictionary<string, string> validUsers = new Dictionary<string, string>
    {
        {"admin", "password123"},
        {"user", "mypassword"}
    };
    
    public AuthenticationResult AuthenticateUser(string username, string password)
    {
        if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
            throw new ArgumentException("Username and password are required");
        
        if (validUsers.ContainsKey(username) && validUsers[username] == password)
        {
            return new AuthenticationResult 
            { 
                Status = "success", 
                User = username, 
                IsAuthenticated = true 
            };
        }
        
        return new AuthenticationResult 
        { 
            Status = "failed", 
            Message = "Invalid credentials", 
            IsAuthenticated = false 
        };
    }
    
    public bool IsUserValid(string username)
    {
        return validUsers.ContainsKey(username);
    }
}

public class AuthenticationResult
{
    public string Status { get; set; }
    public string User { get; set; }
    public string Message { get; set; }
    public bool IsAuthenticated { get; set; }
}
"""
    )
    
    return LanguageConfig(
        name="csharp",
        display_name="C#",
        file_extensions=[".cs"],
        framework=framework,
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
