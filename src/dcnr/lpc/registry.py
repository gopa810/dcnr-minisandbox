"""
Registry module for the LPC (Local Procedure Call) package.

This module provides the internal registry functionality for storing
and managing callable procedures.
"""
from __future__ import annotations

from typing import Any, Callable


class ProcedureRegistry:
    """
    Internal registry for storing and managing callable procedures.
    
    This class handles the storage, retrieval, and validation of
    registered procedures for the LPC system.
    """
    
    def __init__(self):
        self._procedures: dict[str, Callable] = {}
    
    def register(self, name: str, method: Callable) -> None:
        """
        Register a callable method in the registry.
        
        Args:
            name: Name identifier for the procedure
            method: Callable object to register
            
        Raises:
            TypeError: If method is not callable
            ValueError: If name is empty or invalid
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, got {type(name).__name__}")
        
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        
        if not callable(method):
            raise TypeError(f"Method must be callable, got {type(method).__name__}")
        
        self._procedures[name] = method
    
    def get(self, name: str) -> Callable:
        """
        Retrieve a procedure from the registry.
        
        Args:
            name: Name of the procedure to retrieve
            
        Returns:
            The registered callable
            
        Raises:
            KeyError: If procedure is not found
        """
        if name not in self._procedures:
            raise KeyError(f"Procedure '{name}' not found in registry")
        
        return self._procedures[name]
    
    def has(self, name: str) -> bool:
        """
        Check if a procedure exists in the registry.
        
        Args:
            name: Name of the procedure to check
            
        Returns:
            True if procedure exists, False otherwise
        """
        return name in self._procedures
    
    def remove(self, name: str) -> None:
        """
        Remove a procedure from the registry.
        
        Args:
            name: Name of the procedure to remove
            
        Raises:
            KeyError: If procedure is not found
        """
        if name not in self._procedures:
            raise KeyError(f"Procedure '{name}' not found in registry")
        
        del self._procedures[name]
    
    def list_names(self) -> list[str]:
        """
        List all registered procedure names.
        
        Returns:
            List of procedure names
        """
        return list(self._procedures.keys())
    
    def clear(self) -> None:
        """Clear all registered procedures."""
        self._procedures.clear()
    
    def size(self) -> int:
        """
        Get the number of registered procedures.
        
        Returns:
            Number of registered procedures
        """
        return len(self._procedures)


# Global registry instance
_global_registry = ProcedureRegistry()


def get_global_registry() -> ProcedureRegistry:
    """
    Get the global procedure registry instance.
    
    Returns:
        The global ProcedureRegistry instance
    """
    return _global_registry
