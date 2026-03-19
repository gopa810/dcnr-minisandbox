#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dcnr.lpc import register_proc, exec, has_proc, list_procs, clear_procs, proc_count
from dcnr.lpc import ProcedureNotFoundError, ProcedureExecutionError

def test_basic_lpc():
    """Test basic LPC functionality"""
    print("Testing basic LPC functionality...")
    
    # Clear any existing procedures
    clear_procs()
    
    # Define test procedures
    def add_numbers(a, b):
        return a + b
    
    def format_string(template, **kwargs):
        return template.format(**kwargs)
    
    def multiply_list(data, factor):
        return [x * factor for x in data]
    
    # Register procedures
    register_proc("math.add", add_numbers)
    register_proc("string.format", format_string)
    register_proc("data.multiply", multiply_list)
    
    # Test procedure count
    assert proc_count() == 3, f"Expected 3 procedures, got {proc_count()}"
    
    # Test procedure existence
    assert has_proc("math.add"), "math.add should be registered"
    assert has_proc("string.format"), "string.format should be registered"
    assert not has_proc("nonexistent"), "nonexistent should not be registered"
    
    # Test procedure listing
    procs = list_procs()
    print(f"Registered procedures: {procs}")
    assert "math.add" in procs, "math.add should be in procedure list"
    assert "string.format" in procs, "string.format should be in procedure list"
    assert "data.multiply" in procs, "data.multiply should be in procedure list"
    
    # Test procedure execution
    result1 = exec("math.add", 5, 10)
    print(f"math.add(5, 10) = {result1}")
    assert result1 == 15, f"Expected 15, got {result1}"
    
    result2 = exec("string.format", "Hello, {name}!", name="World")
    print(f"string.format result = {result2}")
    assert result2 == "Hello, World!", f"Expected 'Hello, World!', got {result2}"
    
    result3 = exec("data.multiply", [1, 2, 3], 2)
    print(f"data.multiply([1, 2, 3], 2) = {result3}")
    assert result3 == [2, 4, 6], f"Expected [2, 4, 6], got {result3}"
    
    print("✓ Basic LPC functionality works!")
    return True

def test_error_handling():
    """Test LPC error handling"""
    print("\nTesting LPC error handling...")
    
    # Test procedure not found
    try:
        exec("nonexistent.proc", 1, 2, 3)
        assert False, "Should have raised ProcedureNotFoundError"
    except ProcedureNotFoundError as e:
        print(f"✓ Correctly caught ProcedureNotFoundError: {e}")
    
    # Register a procedure that raises an exception
    def failing_proc():
        raise ValueError("This procedure always fails")
    
    register_proc("test.fail", failing_proc)
    
    # Test procedure execution error
    try:
        exec("test.fail")
        assert False, "Should have raised ProcedureExecutionError"
    except ProcedureExecutionError as e:
        print(f"✓ Correctly caught ProcedureExecutionError: {e}")
    
    # Test invalid registration
    try:
        register_proc("test.invalid", "not_a_callable")
        assert False, "Should have raised TypeError"
    except TypeError as e:
        print(f"✓ Correctly caught TypeError for non-callable: {e}")
    
    # Test empty name registration
    try:
        register_proc("", lambda: None)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Correctly caught ValueError for empty name: {e}")
    
    print("✓ Error handling works correctly!")
    return True

def test_procedure_management():
    """Test procedure management functions"""
    print("\nTesting procedure management...")
    
    clear_procs()
    
    # Register some procedures
    register_proc("test1", lambda: "result1")
    register_proc("test2", lambda: "result2")
    register_proc("test3", lambda: "result3")
    
    assert proc_count() == 3, f"Expected 3 procedures, got {proc_count()}"
    
    # Test unregistration
    from dcnr.lpc import unregister_proc
    unregister_proc("test2")
    
    assert proc_count() == 2, f"Expected 2 procedures after removal, got {proc_count()}"
    assert not has_proc("test2"), "test2 should be removed"
    assert has_proc("test1"), "test1 should still exist"
    assert has_proc("test3"), "test3 should still exist"
    
    # Test getting procedure directly
    from dcnr.lpc import get_proc
    proc = get_proc("test1")
    result = proc()
    assert result == "result1", f"Expected 'result1', got {result}"
    
    # Test clear all
    clear_procs()
    assert proc_count() == 0, f"Expected 0 procedures after clear, got {proc_count()}"
    
    print("✓ Procedure management works correctly!")
    return True

def test_integration_example():
    """Test a realistic integration example"""
    print("\nTesting realistic integration example...")
    
    clear_procs()
    
    # Register a set of data processing procedures
    def load_data():
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    def filter_even(data):
        return [x for x in data if x % 2 == 0]
    
    def calculate_stats(data):
        return {
            'count': len(data),
            'sum': sum(data),
            'average': sum(data) / len(data) if data else 0,
            'min': min(data) if data else None,
            'max': max(data) if data else None
        }
    
    def format_report(stats):
        return f"Data Analysis Report:\n" \
               f"Count: {stats['count']}\n" \
               f"Sum: {stats['sum']}\n" \
               f"Average: {stats['average']:.2f}\n" \
               f"Range: {stats['min']} - {stats['max']}"
    
    # Register the procedures
    register_proc("data.load", load_data)
    register_proc("data.filter.even", filter_even)
    register_proc("analysis.stats", calculate_stats)
    register_proc("report.format", format_report)
    
    # Execute a data processing pipeline
    raw_data = exec("data.load")
    even_data = exec("data.filter.even", raw_data)
    stats = exec("analysis.stats", even_data)
    report = exec("report.format", stats)
    
    print("Data processing pipeline result:")
    print(report)
    
    # Verify results
    expected_even = [2, 4, 6, 8, 10]
    assert even_data == expected_even, f"Expected {expected_even}, got {even_data}"
    assert stats['count'] == 5, f"Expected count 5, got {stats['count']}"
    assert stats['sum'] == 30, f"Expected sum 30, got {stats['sum']}"
    assert stats['average'] == 6.0, f"Expected average 6.0, got {stats['average']}"
    
    print("✓ Integration example works perfectly!")
    return True

if __name__ == "__main__":
    print("Testing LPC (Local Procedure Call) package...")
    success = True
    
    try:
        success &= test_basic_lpc()
        success &= test_error_handling()
        success &= test_procedure_management()
        success &= test_integration_example()
        
        if success:
            print("\n🎉 All LPC tests passed!")
        else:
            print("\n❌ Some LPC tests failed!")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)
