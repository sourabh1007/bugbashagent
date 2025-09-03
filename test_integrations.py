#!/usr/bin/env python3
"""Test individual imports"""

print("Testing individual imports...")

try:
    from integrations.azure_openai import get_azure_openai_client
    print("✅ Azure OpenAI import: OK")
except Exception as e:
    print(f"❌ Azure OpenAI import error: {e}")

try:
    from integrations.langsmith import trace_agent_execution
    print("✅ LangSmith import: OK") 
except Exception as e:
    print(f"❌ LangSmith import error: {e}")

try:
    from integrations import get_azure_openai_client, setup_langsmith
    print("✅ Main integrations import: OK")
except Exception as e:
    print(f"❌ Main integrations import error: {e}")

print("Import test complete.")
