#!/usr/bin/env python3
"""
LangSmith Integration Setup and Verification
"""

import subprocess
import sys
import os

def install_langsmith():
    """Install LangSmith package"""
    print("📦 Installing LangSmith...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "langsmith"], 
                              capture_output=True, text=True, check=True)
        print("✅ LangSmith installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install LangSmith: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def verify_installation():
    """Verify LangSmith installation"""
    print("🔍 Verifying LangSmith installation...")
    try:
        import langsmith
        print("✅ LangSmith can be imported successfully")
        print(f"📦 LangSmith version: {langsmith.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Cannot import LangSmith: {e}")
        return False

def test_integration():
    """Test LangSmith integration functionality"""
    print("🧪 Testing LangSmith Integration...")
    
    try:
        from .langsmith_integration import LangSmithIntegration, get_langsmith_dashboard_url
        
        # Check if LangSmith is configured
        integration = LangSmithIntegration()
        if integration.enabled:
            print("✅ LangSmith is properly configured")
            print(f"📊 Project: {integration.project_name}")
            print(f"🔗 Dashboard: {get_langsmith_dashboard_url()}")
            return True
        else:
            print("⚠️ LangSmith is not configured")
            print("Set LANGCHAIN_API_KEY in your .env file to enable tracing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LangSmith integration: {e}")
        return False

def main():
    """Main setup and verification process"""
    print("🤖 BugBashAgent LangSmith Integration Setup")
    print("=" * 50)
    
    # Step 1: Install LangSmith
    if not install_langsmith():
        return 1
    
    # Step 2: Verify installation
    if not verify_installation():
        return 1
    
    # Step 3: Test integration
    configured = test_integration()
    
    print("\n🎯 Setup Summary:")
    print("✅ LangSmith package installed")
    print("✅ BugBashAgent integration code added")
    if configured:
        print("✅ LangSmith monitoring configured")
        print("🔗 Dashboard: https://smith.langchain.com/projects")
    else:
        print("⚠️ LangSmith monitoring not configured (optional)")
    
    print("\n🚀 Ready to run BugBashAgent with LangSmith!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
