#!/usr/bin/env python3
"""
Bug Bash Agent - Demo Script
Professional UI demonstration with Bug Bash branding and terminology
"""

import os
import sys
import subprocess
import time

def main():
    """Run the Bug Bash Agent demo"""
    print("🔍 Bug Bash Agent - Professional Demo")
    print("=" * 50)
    print()
    print("🎯 Product: Your intelligent assistant for smarter bug bashes")
    print("📋 Features:")
    print("  • AI-powered documentation analysis")
    print("  • Automated test scenario generation")
    print("  • Real-time bug bash execution")
    print("  • Comprehensive testing reports")
    print()
    print("🚀 Starting enhanced UI...")
    
    # Check if streamlit is available
    try:
        import streamlit
        print("✅ Streamlit found")
    except ImportError:
        print("❌ Streamlit not found. Please install with: pip install streamlit")
        return
    
    # Check if we're in the right directory
    if not os.path.exists("streamlit_app.py"):
        print("❌ streamlit_app.py not found. Please run from the BugBashAgent directory.")
        return
    
    print("✅ All dependencies ready")
    print()
    print("🌟 Opening Bug Bash Agent Professional UI...")
    print("📱 The UI will open in your default browser")
    print("🔄 Real-time monitoring and professional styling enabled")
    print()
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.headless", "false",
            "--server.enableCORS", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error running demo: {str(e)}")

if __name__ == "__main__":
    main()
