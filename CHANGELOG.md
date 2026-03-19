# Changelog

All notable changes to dcnr-minisandbox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-03-28

### Added

- MangoDatabase for in-memory data storage

## [1.0.3] - 2026-03-28

### Added

- New 'lpc' package to enable non-import calls of functions

## [1.0.2] - 2026-03-17

### Changed
- Updated sandbox interpreter to support safe attribute access and method calls
- Enhanced `_eval_call()` method to handle both direct function calls and method calls
- Modified documentation to reflect new attribute access capabilities


## [1.0.1] - 2026-03-17

### Added
- Safe attribute access support for accessing object attributes and methods
- Method call support for built-in types (e.g., `text.upper()`, `data.append()`)
- Attribute validation system that blocks dangerous attribute access (e.g., `__class__`, `__dict__`)
- Attribute assignment support (e.g., `obj.attr = value`)
- Global object registry system with hierarchical namespace support
- `DotDict` class for safe dot-notation access to nested data structures
- `ObjectRegistry` singleton class for centralized object management
- Registry API functions: `register_object()`, `get_registry()`
- Path validation with restrictions on Python keywords and reserved names
- Registry methods: `get_object()`, `has_path()`, `unregister_object()`, `clear()`
- Initial documentation (README.md)
- Changelog documentation



## [1.0.0] - 2026-03-17

### Added
- Initial release of dcnr-minisandbox
- Secure AST-based Python code execution
- Restricted syntax validation with comprehensive safety checks
- Support for basic Python data types (int, float, str, bool, list, tuple, dict, set)
- Arithmetic, comparison, and logical operators
- Control flow statements (if/elif/else, for/while loops)
- Loop control statements (break, continue)
- Built-in functions: abs, min, max, sum, len, range, int, float, str, bool, list, tuple, dict, set, sorted
- Variable assignment and augmented assignment operations
- Tuple and list unpacking support
- Subscript access and slicing operations
- Iteration limits for loops (100,000 iterations maximum)
- Custom exception classes: `SandboxError`, `SandboxSyntaxError`, `SandboxRuntimeError`
- `sandbox_exec()` function as the main API entry point

### Security Features
- Prohibited imports and module access
- Blocked function/class definitions and lambda expressions
- Disabled attribute access to prevent object introspection
- Restricted exception handling mechanisms
- Prevented comprehensions and generator expressions
- Blocked dangerous operations (delete, global/nonlocal, yield, await)
- Safe environment isolation

### Documentation
- Comprehensive API documentation
- Usage examples and best practices
- Security feature explanations
- Error handling guidelines

[Unreleased]: https://github.com/kollath/dcnr-minisandbox/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/kollath/dcnr-minisandbox/releases/tag/v1.0.0
