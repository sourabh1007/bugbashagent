#!/usr/bin/env python3
"""Minimal test of LangSmith integration"""

print("Starting LangSmith test...")

try:
    print("1. Testing basic imports...")
    import os
    from typing import Any, Dict
    print("✅ Basic imports OK")
    
    print("2. Testing config imports...")
    from config_package import LANGCHAIN_API_KEY, LANGCHAIN_PROJECT
    print("✅ Config imports OK")
    
    print("3. Testing LangSmith import...")
    from langsmith import Client
    print("✅ LangSmith Client import OK")
    
    print("4. Testing class definition...")
    class TestLangSmithIntegration:
        def __init__(self):
            self.client = None
            self.project_name = LANGCHAIN_PROJECT
            print(f"✅ Test class initialized with project: {self.project_name}")
    
    print("5. Creating test instance...")
    test = TestLangSmithIntegration()
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
