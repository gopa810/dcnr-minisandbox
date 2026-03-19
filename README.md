# DCNR Minisandbox

A secure, lightweight Python sandbox interpreter that allows safe execution of untrusted Python code with strict limitations, plus a global object registry and LPC (Local Procedure Call) system for application data management and anonymous method execution.

## Features

- **Secure AST-based execution** - Uses Python's AST parser to validate and execute code without using `eval()` or `exec()`
- **Restricted syntax** - Only allows a safe subset of Python constructs
- **Built-in safety limits** - Prevents infinite loops with iteration limits
- **Customizable environment** - Pre-populate variables and control available functions
- **Comprehensive error handling** - Clear error messages for syntax and runtime violations
- **Global object registry** - Hierarchical storage and access system for application objects and data
- **LPC (Local Procedure Call)** - Anonymous execution of registered methods by name

## Installation

```bash
pip install dcnr-minisandbox
```

## Components

This package provides three main components:

1. **Sandbox Interpreter** (`sandbox_exec`) - Secure execution of Python code with AST validation
2. **Object Registry** (`get_registry`, `register_object`) - Global hierarchical storage for application objects
3. **LPC (Local Procedure Call)** (`register_proc`, `exec`) - Anonymous execution of registered methods

## Quick Start

### Sandbox Execution

```python
from dcnr.minisandbox import sandbox_exec

# Simple calculation
code = """
x = 10
y = 20
result = x + y * 2
"""

variables = {}
result = sandbox_exec(code, variables)
print(result)  # {'x': 10, 'y': 20, 'result': 50}

# Pre-populate with variables
initial_vars = {'data': [1, 2, 3, 4, 5]}
code = """
total = sum(data)
average = total / len(data)
"""

result = sandbox_exec(code, initial_vars)
print(result)  # {'data': [1, 2, 3, 4, 5], 'total': 15, 'average': 3.0}

# Using attribute access and method calls
code = """
text = "hello world"
upper_text = text.upper()
words = text.split()
data = [1, 2, 3]
data.append(4)
"""

result = sandbox_exec(code, {})
print(result)  # {'text': 'hello world', 'upper_text': 'HELLO WORLD', 'words': ['hello', 'world'], 'data': [1, 2, 3, 4]}
```

### Global Object Registry

```python
from dcnr.minisandbox import register_object, get_registry

# Register functions and data
def fetchone():
    return {"id": 1, "name": "Alice"}

register_object("database.prod.fetchone", fetchone)
register_object("database.prod.version", "1.0")
register_object("config.debug", True)

# Access through registry
registry = get_registry()
print(registry.database.prod.fetchone())  # {'id': 1, 'name': 'Alice'}
print(registry.database.prod.version)     # '1.0'
print(registry.config.debug)              # True
```

### LPC (Local Procedure Call)

```python
from dcnr.lpc import register_proc, exec

# Register procedures
def calculate_sum(a, b):
    return a + b

def format_message(name, age):
    return f"{name} is {age} years old"

register_proc("math.sum", calculate_sum)
register_proc("string.format", format_message)

# Execute procedures anonymously
result = exec("math.sum", 10, 5)
print(result)  # 15

message = exec("string.format", "Alice", 30)
print(message)  # "Alice is 30 years old"

# Using decorator syntax
from dcnr.lpc import lpc_proc

@lpc_proc("math.multiply")
def multiply(x, y):
    return x * y

result = exec("math.multiply", 4, 7)
print(result)  # 28
```

## Allowed Features

### Data Types
- Numbers: `int`, `float`
- Strings: `str`
- Collections: `list`, `tuple`, `dict`, `set`
- Booleans: `bool`

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `not in`, `is`, `is not`
- Logical: `and`, `or`, `not`

### Control Flow
- Conditional statements: `if`, `elif`, `else`
- Loops: `for`, `while` (with iteration limits)
- Loop control: `break`, `continue`

### Built-in Functions
- Math: `abs()`, `min()`, `max()`, `sum()`
- Type conversion: `int()`, `float()`, `str()`, `bool()`
- Collections: `len()`, `range()`, `list()`, `tuple()`, `dict()`, `set()`, `sorted()`

### Variable Operations
- Assignment: `x = value`
- Augmented assignment: `x += 1`, `x -= 1`, etc.
- Tuple/list unpacking: `a, b = (1, 2)`
- Subscript access: `data[0]`, `data[1:3]`
- Attribute access: `obj.attr`, `obj.method()`

## Prohibited Features

For security reasons, the following are **not allowed**:

- **Imports**: No `import` or `from ... import` statements
- **Function definitions**: No `def`, `lambda`, or `class` definitions
- **Dangerous attribute access**: No access to `__class__`, `__dict__`, `__module__`, etc.
- **Exception handling**: No `try`, `except`, `finally`, `raise`
- **File I/O**: No file operations or system calls
- **Advanced features**: No comprehensions, generators, decorators, or async code

## Global Object Registry

The registry provides a hierarchical namespace for storing and accessing application objects, functions, and configuration data.

### Registry Features

- **Dot-notation access** - Navigate the registry like `registry.database.prod.version`
- **Safe path validation** - Prevents conflicts with Python keywords and reserved names
- **Singleton pattern** - Single global registry instance across your application
- **Type safety** - Automatic wrapping of nested dictionaries for consistent access

### Registry API

```python
from dcnr.minisandbox import get_registry, register_object

# Get the global registry instance
registry = get_registry()

# Register objects at various paths
register_object("app.config.debug", True)
register_object("app.database.host", "localhost")
register_object("app.database.port", 5432)

# Alternative: use registry methods directly
registry.register_object("services.auth.enabled", True)

# Access registered objects
print(registry.app.config.debug)      # True
print(registry.app.database.host)     # 'localhost'
print(registry.services.auth.enabled) # True

# Check if path exists
if registry.has_path("app.config.debug"):
    print("Debug mode is configured")

# Get object programmatically
db_host = registry.get_object("app.database.host")

# Remove objects
registry.unregister_object("app.config.debug")

# Clear entire registry
registry.clear()
```

### Path Restrictions

For safety and consistency, certain path components are not allowed:

```python
# ❌ These will raise ValueError:
register_object("app.items.test", 1)      # 'items' is reserved (dict method)
register_object("app.__class__.x", 1)     # Names starting with '_' not allowed
register_object("app.for.x", 1)          # 'for' is a Python keyword
register_object("app..x", 1)             # Empty components not allowed
```

## LPC (Local Procedure Call)

The LPC package provides anonymous execution of registered callable methods, enabling dynamic procedure dispatch without direct references to the implementation.

### LPC Features

- **Anonymous execution** - Call procedures by name without importing or referencing them directly
- **Dynamic registration** - Register procedures at runtime from any part of your application
- **Decorator support** - Use `@lpc_proc` decorator for clean registration syntax
- **Type safety** - Validates that registered objects are callable
- **Error handling** - Clear exceptions for missing procedures or execution failures
- **Procedure management** - List, check, and remove registered procedures

### Core API

#### Registration Functions

```python
from dcnr.lpc import register_proc, lpc_proc

# Function registration
def add_numbers(a, b):
    return a + b

register_proc("math.add", add_numbers)

# Decorator registration
@lpc_proc("math.subtract")
def subtract_numbers(a, b):
    return a - b

# Lambda registration
register_proc("math.square", lambda x: x ** 2)
```

#### Execution Function

```python
from dcnr.lpc import exec

# Execute registered procedures
result1 = exec("math.add", 10, 5)        # 15
result2 = exec("math.subtract", 10, 5)   # 5
result3 = exec("math.square", 4)         # 16

# With keyword arguments
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

register_proc("utils.greet", greet)
message = exec("utils.greet", "Alice", greeting="Hi")  # "Hi, Alice!"
```

#### Management Functions

```python
from dcnr.lpc import has_proc, list_procs, proc_count, unregister_proc, clear_procs

# Check if procedure exists
if has_proc("math.add"):
    print("Math add procedure is available")

# List all registered procedures
procedures = list_procs()
print("Available procedures:", procedures)

# Get procedure count
count = proc_count()
print(f"Total procedures: {count}")

# Remove specific procedure
unregister_proc("math.add")

# Clear all procedures
clear_procs()
```

### Advanced Usage

#### Procedure Pipelines

```python
from dcnr.lpc import register_proc, exec

# Register data processing pipeline
register_proc("data.load", lambda: [1, 2, 3, 4, 5])
register_proc("data.filter_even", lambda data: [x for x in data if x % 2 == 0])
register_proc("data.sum", lambda data: sum(data))

# Execute pipeline
raw_data = exec("data.load")
filtered_data = exec("data.filter_even", raw_data)
result = exec("data.sum", filtered_data)
print(result)  # 6 (2 + 4)
```

#### Conditional Procedure Execution

```python
from dcnr.lpc import exec, has_proc

def safe_exec(proc_name, *args, **kwargs):
    if has_proc(proc_name):
        return exec(proc_name, *args, **kwargs)
    else:
        print(f"Procedure '{proc_name}' not available")
        return None

# Safe execution
result = safe_exec("math.add", 1, 2)  # Works if registered
result = safe_exec("missing.proc", 1, 2)  # Prints warning, returns None
```

#### Dynamic Procedure Loading

```python
from dcnr.lpc import register_proc, exec

# Dynamic loading based on configuration
config = {
    "processors": ["data.clean", "data.transform", "data.validate"]
}

def clean_data(data):
    return [x for x in data if x is not None]

def transform_data(data):
    return [x * 2 for x in data]

def validate_data(data):
    return all(isinstance(x, (int, float)) for x in data)

# Register based on configuration
processors = {
    "data.clean": clean_data,
    "data.transform": transform_data,
    "data.validate": validate_data
}

for proc_name in config["processors"]:
    if proc_name in processors:
        register_proc(proc_name, processors[proc_name])

# Execute processing chain
data = [1, None, 3, 4.5]
for proc_name in config["processors"]:
    data = exec(proc_name, data)
print(data)  # [2, 6, 9.0] (cleaned, transformed, validated)
```

### Error Handling

The LPC package provides specific exception types for different error scenarios:

```python
from dcnr.lpc import exec, register_proc
from dcnr.lpc import ProcedureNotFoundError, ProcedureExecutionError, LPCError

# Handle procedure not found
try:
    result = exec("nonexistent.procedure", 1, 2, 3)
except ProcedureNotFoundError as e:
    print(f"Procedure not found: {e}")

# Handle execution errors
def risky_procedure(x):
    if x < 0:
        raise ValueError("Negative values not allowed")
    return x * 2

register_proc("math.risky", risky_procedure)

try:
    result = exec("math.risky", -5)
except ProcedureExecutionError as e:
    print(f"Procedure execution failed: {e}")
    # Original exception available via e.__cause__

# Handle registration errors
try:
    register_proc("invalid.proc", "not_a_function")
except TypeError as e:
    print(f"Registration failed: {e}")

# Catch all LPC errors
try:
    result = exec("some.procedure", arg1, arg2)
except LPCError as e:
    print(f"LPC error occurred: {e}")
```

### Best Practices

#### Naming Conventions

Use hierarchical naming for better organization:

```python
# Good naming patterns
register_proc("auth.login", login_user)
register_proc("auth.logout", logout_user)
register_proc("data.users.create", create_user)
register_proc("data.users.update", update_user)
register_proc("utils.validation.email", validate_email)
register_proc("utils.formatting.currency", format_currency)
```

#### Error-Safe Execution

```python
from dcnr.lpc import exec, has_proc, ProcedureNotFoundError

def safe_procedure_call(proc_name, *args, default=None, **kwargs):
    """Execute procedure with fallback to default value."""
    try:
        if has_proc(proc_name):
            return exec(proc_name, *args, **kwargs)
        else:
            print(f"Warning: Procedure '{proc_name}' not registered")
            return default
    except Exception as e:
        print(f"Error executing '{proc_name}': {e}")
        return default

# Usage
result = safe_procedure_call("math.divide", 10, 2, default=0)
```

#### Procedure Documentation

```python
from dcnr.lpc import register_proc, list_procs

def documented_procedure(x, y):
    """
    Add two numbers together.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        Sum of x and y
    """
    return x + y

register_proc("math.add", documented_procedure)

# Access documentation
from dcnr.lpc import get_proc
proc = get_proc("math.add")
print(proc.__doc__)  # Prints the docstring
```

## Error Handling

### Sandbox Errors

The sandbox raises specific exceptions for different types of violations:

```python
from dcnr.minisandbox import sandbox_exec, SandboxSyntaxError, SandboxRuntimeError

try:
    # This will raise SandboxSyntaxError
    sandbox_exec("import os", {})
except SandboxSyntaxError as e:
    print(f"Syntax violation: {e}")

try:
    # This will raise SandboxRuntimeError  
    sandbox_exec("unknown_variable", {})
except SandboxRuntimeError as e:
    print(f"Runtime error: {e}")
```

### Registry Errors

The registry raises standard Python exceptions for invalid operations:

```python
from dcnr.minisandbox import register_object, get_registry

try:
    # Invalid path component
    register_object("app.for.test", 1)  # 'for' is a Python keyword
except ValueError as e:
    print(f"Invalid path: {e}")

try:
    # Path not found
    registry = get_registry()
    value = registry.get_object("nonexistent.path")
except KeyError as e:
    print(f"Path not found: {e}")
```

## Safety Features

### Iteration Limits
Loops are automatically limited to 100,000 iterations to prevent infinite loops:

```python
# This will raise SandboxRuntimeError after 100,000 iterations
code = """
i = 0
while True:
    i += 1
"""
```

### Memory Safety
Only safe data types and operations are allowed. No access to system resources or dangerous built-ins.

## Use Cases

### Sandbox Execution
- **Educational platforms** - Safe execution of student code
- **Code challenges** - Running untrusted submissions
- **Configuration scripts** - Controlled execution of user-defined logic
- **Expression evaluation** - Safe calculation of mathematical expressions
- **Templating** - Dynamic value computation in templates

### Object Registry
- **Application configuration** - Centralized storage of settings and parameters
- **Service registration** - Registry for application services and dependencies
- **Plugin systems** - Dynamic registration and discovery of plugins
- **Feature flags** - Hierarchical feature toggle management
- **Resource management** - Centralized access to database connections, APIs, etc.

### LPC (Local Procedure Call)
- **Plugin architectures** - Dynamic loading and execution of plugin methods
- **Microservices** - Anonymous procedure calls between service components
- **Workflow engines** - Step-by-step execution of named procedures in workflows
- **API routing** - Map request paths to procedure implementations
- **Command pattern** - Decouple command invocation from implementation
- **Data processing pipelines** - Chain procedures for data transformation
- **Event handling** - Register and execute event handlers by name
- **Configuration-driven execution** - Execute procedures based on configuration files

## Limitations

- No custom function definitions
- No module imports or external libraries
- Limited to basic Python constructs
- No file system or network access
- Fixed iteration limits for loops

## Development

To contribute to dcnr-minisandbox:

1. Clone the repository
2. Install development dependencies
3. Run tests with your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Peter Kollath (peter.kollath@gopal.home.sk)

## Links

- Homepage: https://dcnr-utilities.com/minisandbox
- PyPI: https://pypi.org/project/dcnr-minisandbox/
