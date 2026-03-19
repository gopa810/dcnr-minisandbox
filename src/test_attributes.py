#!/usr/bin/env python3

from dcnr.minisandbox import sandbox_exec

def test_basic_attribute_access():
    """Test basic attribute access"""
    code = """
data = [1, 2, 3, 4, 5]
append_method = data.append
"""
    try:
        result = sandbox_exec(code, {})
        print("✓ Basic attribute access works:", type(result['append_method']))
    except Exception as e:
        print("✗ Basic attribute access failed:", e)

def test_string_methods():
    """Test string method access"""
    code = """
text = "hello world"
upper_text = text.upper()
split_text = text.split()
"""
    try:
        result = sandbox_exec(code, {})
        print("✓ String methods work:", result['upper_text'], result['split_text'])
    except Exception as e:
        print("✗ String methods failed:", e)

def test_list_methods():
    """Test list method access"""
    code = """
data = [1, 2, 3]
data.append(4)
length = len(data)
"""
    try:
        result = sandbox_exec(code, {})
        print("✓ List methods work:", result['data'], "length =", result['length'])
    except Exception as e:
        print("✗ List methods failed:", e)

def test_dangerous_attributes():
    """Test that dangerous attributes are blocked"""
    dangerous_codes = [
        "x = [].__class__",
        "x = [].__dict__", 
        "x = [].__module__",
        "x = len.__code__"
    ]
    
    for code in dangerous_codes:
        try:
            sandbox_exec(code, {})
            print(f"✗ Dangerous attribute should be blocked: {code}")
        except Exception as e:
            print(f"✓ Dangerous attribute blocked: {code} -> {e}")

def test_attribute_assignment():
    """Test attribute assignment"""
    code = """
class SimpleClass:
    def __init__(self):
        self.value = 0

obj = SimpleClass()
obj.value = 42
"""
    try:
        result = sandbox_exec(code, {})
        print("✓ Attribute assignment works:", result['obj'].value)
    except Exception as e:
        print("✗ Attribute assignment failed (expected - no class definitions):", e)

if __name__ == "__main__":
    print("Testing attribute access implementation...")
    test_basic_attribute_access()
    test_string_methods()
    test_list_methods()
    test_dangerous_attributes()
    test_attribute_assignment()
