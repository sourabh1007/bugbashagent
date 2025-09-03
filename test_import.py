#!/usr/bin/env python3
"""Test import script"""

try:
    import main
    print("✅ main.py imports successfully")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
