"""
LPC (Local Procedure Call) package for anonymous execution of methods in Python.

This package provides functionality to register callable methods and execute them
by name without direct reference to the implementation.

Example:
    ```python
    from dcnr.lpc import register_proc, exec
    
    # Register a procedure
    def calculate_sum(a, b):
        return a + b
    
    register_proc("math.sum", calculate_sum)
    
    # Execute the procedure anonymously
    result = exec("math.sum", 5, 10)
    print(result)  # 15
    ```
"""
from __future__ import annotations

from typing import Any, Callable
from .registry import get_global_registry


class LPCError(Exception):
    """Base exception for LPC operations."""
    pass


class ProcedureNotFoundError(LPCError):
    """Raised when a procedure is not found in the registry."""
    pass


class ProcedureExecutionError(LPCError):
    """Raised when a procedure execution fails."""
    pass


def register_proc(name: str, method: Callable) -> None:
    """
    Register a callable method for anonymous execution.
    
    Args:
        name: Name identifier for the procedure
        method: Callable object to register
        
    Raises:
        TypeError: If method is not callable
        ValueError: If name is empty or invalid
        
    Example:
        ```python
        def add_numbers(a, b):
            return a + b
        
        register_proc("math.add", add_numbers)
        ```
    """
    registry = get_global_registry()
    try:
        registry.register(name, method)
    except (TypeError, ValueError):
        raise


def exec(method: str, *args, **kwargs) -> Any:
    """
    Execute a registered method by name with provided arguments.
    
    Args:
        method: Name of the registered method to execute
        *args: Positional arguments to pass to the method
        **kwargs: Keyword arguments to pass to the method
        
    Returns:
        The result of the method execution
        
    Raises:
        ProcedureNotFoundError: If the method is not found in the registry
        ProcedureExecutionError: If the method execution fails
        
    Example:
        ```python
        # Assuming "math.add" is registered
        result = exec("math.add", 5, 10)
        print(result)  # 15
        
        # With keyword arguments
        result = exec("string.format", template="{name} is {age}", name="Alice", age=30)
        ```
    """
    if not isinstance(method, str):
        raise TypeError(f"Method name must be a string, got {type(method).__name__}")
    
    registry = get_global_registry()
    
    try:
        procedure = registry.get(method)
    except KeyError:
        raise ProcedureNotFoundError(f"Procedure '{method}' not found in registry")
    
    try:
        return procedure(*args, **kwargs)
    except Exception as exc:
        raise ProcedureExecutionError(
            f"Execution of procedure '{method}' failed: {exc}"
        ) from exc


def unregister_proc(name: str) -> None:
    """
    Remove a procedure from the registry.
    
    Args:
        name: Name of the procedure to remove
        
    Raises:
        ProcedureNotFoundError: If procedure is not found
    """
    registry = get_global_registry()
    try:
        registry.remove(name)
    except KeyError:
        raise ProcedureNotFoundError(f"Procedure '{name}' not found in registry")


def has_proc(name: str) -> bool:
    """
    Check if a procedure is registered.
    
    Args:
        name: Name of the procedure to check
        
    Returns:
        True if procedure exists, False otherwise
    """
    registry = get_global_registry()
    return registry.has(name)


def list_procs() -> list[str]:
    """
    List all registered procedure names.
    
    Returns:
        List of procedure names
    """
    registry = get_global_registry()
    return registry.list_names()


def clear_procs() -> None:
    """Clear all registered procedures."""
    registry = get_global_registry()
    registry.clear()


def get_proc(name: str) -> Callable:
    """
    Get a registered procedure by name.
    
    Args:
        name: Name of the procedure to retrieve
        
    Returns:
        The registered callable
        
    Raises:
        ProcedureNotFoundError: If procedure is not found
    """
    registry = get_global_registry()
    try:
        return registry.get(name)
    except KeyError:
        raise ProcedureNotFoundError(f"Procedure '{name}' not found in registry")


def proc_count() -> int:
    """
    Get the number of registered procedures.
    
    Returns:
        Number of registered procedures
    """
    registry = get_global_registry()
    return registry.size()

def lpc_proc(name: str):
    """
    Decorator to register a function as an LPC procedure.

    Args:
        name: Name to register the procedure under.

    Example:
        @lpc_proc("math.mul")
        def multiply(a, b):
            return a * b
    """
    def decorator(func: Callable) -> Callable:
        register_proc(name, func)
        return func
    return decorator

# Export the main API functions
__all__ = [
    "register_proc",
    "exec", 
    "unregister_proc",
    "has_proc",
    "list_procs", 
    "lpc_proc",
    "clear_procs",
    "get_proc",
    "proc_count",
    "LPCError",
    "ProcedureNotFoundError", 
    "ProcedureExecutionError"
]
