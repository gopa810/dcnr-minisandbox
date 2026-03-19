#!/usr/bin/env python3

import sys
import os

from dcnr.minisandbox import sandbox_exec, get_registry, register_object

from types import SimpleNamespace

def fetch_one():
    return "hello world"

register_object("database.adlib.fetch_one", fetch_one)

def test_string_methods():
    """Test string method calls"""
    code = """
text = app.database.adlib.fetch_one()
upper_text = text.upper()
split_text = text.split()
"""
    try:
        result = sandbox_exec(code, {"app": get_registry()})
        print("✓ String methods work:", result['upper_text'], result['split_text'])
        return True
    except Exception as e:
        print("✗ String methods failed:", e)
        return False

def test_list_methods():
    """Test list method calls"""
    code = """
data = [1, 2, 3]
data.append(4)
length = len(data)
"""
    try:
        result = sandbox_exec(code, {})
        print("✓ List methods work:", result['data'], "length =", result['length'])
        return True
    except Exception as e:
        print("✗ List methods failed:", e)
        return False

def test_basic_attribute():
    """Test basic attribute access (not method calls)"""
    code = """
data = [1, 2, 3]
append_method = data.append
"""
    try:
        result = sandbox_exec(code, {})
        print("✓ Basic attribute access works:", type(result['append_method']))
        return True
    except Exception as e:
        print("✗ Basic attribute access failed:", e)
        return False

if __name__ == "__main__":
    print("Testing attribute access and method calls...")
    success = True
    success &= test_basic_attribute()
    success &= test_string_methods() 
    success &= test_list_methods()
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
