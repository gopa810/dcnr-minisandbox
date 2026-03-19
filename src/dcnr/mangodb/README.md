# MangoDatabase Developer Guidelines

MangoDatabase is a lightweight, in-memory database system designed for storing and retrieving objects with hierarchical path-based organization. This document provides comprehensive guidelines for developers using MangoDatabase.

## Overview

MangoDatabase provides:
- **In-memory storage** - Fast access with automatic cleanup
- **Hierarchical organization** - Path-based object organization (like file systems)
- **Type-aware storage** - Store objects with associated type information
- **Time-based tracking** - Automatic timestamp tracking for all objects
- **Flexible querying** - Filter by ID, type, path, and time
- **Automatic limits** - Configurable limits with automatic cleanup
- **Sorting capabilities** - Sort results by ID or timestamp

## Core Concepts

### MangoObject

Every stored item is represented as a `MangoObject`:

```python
@dataclass
class MangoObject:
    object_id: int      # Unique identifier (auto-generated)
    object_type: str    # User-defined type label
    object_data: Any    # The actual data being stored
    object_time: float  # Timestamp when object was created
    path: str          # Hierarchical path location
```

### Path System

Paths work like file system directories:
- Root path: `/`
- Nested paths: `/users`, `/users/active`, `/logs/errors`
- Path normalization handles variations automatically

### Limits and Cleanup

Each path can have storage limits with automatic cleanup:
- Default limit: 10,000 objects per path
- Cleanup strategies: `"drop_oldest"` (default) or `"error"`
- Limits inherit from parent paths

## Basic Usage

### Creating a Database

```python
from dcnr.mangodb import MangoDatabase

db = MangoDatabase()
```

### Adding Objects

```python
# Simple addition
obj = db.add(
    object_type="user",
    object_data={"name": "Alice", "age": 30},
    path="/users"
)
print(f"Created object {obj.object_id} at {obj.path}")

# Add with different types
db.add("log_entry", "User login successful", "/logs/auth")
db.add("config", {"debug": True, "port": 8080}, "/settings")
db.add("temp_data", [1, 2, 3, 4, 5], "/temp")
```

### Selecting Objects

```python
# Select all objects
all_objects = db.select()

# Select by object ID
user = db.select(object_id=1000000)

# Select by type
all_users = db.select(object_type="user")

# Select by path (includes subpaths)
logs = db.select(path="/logs")

# Combined filters
recent_users = db.select(
    object_type="user", 
    path="/users/active"
)

# With sorting and limits
latest_logs = db.select(
    object_type="log_entry",
    path="/logs",
    sort=MangoSorting.SORT_TIME_DESC,
    limit=10
)
```

### Removing Objects

```python
# Remove by ID
db.remove(object_id=1000001)

# Remove by type
deleted_count = db.remove(object_type="temp_data")

# Remove old objects (older than timestamp)
old_time = time.time() - 3600  # 1 hour ago
db.remove(max_time=old_time, path="/logs")

# Remove from specific path
db.remove(path="/temp")
```

## Advanced Usage

### Path-Based Organization

```python
# Organize data hierarchically
db.add("user", {"name": "Alice"}, "/users/active")
db.add("user", {"name": "Bob"}, "/users/inactive") 
db.add("session", {"user_id": 1, "token": "abc123"}, "/sessions/web")
db.add("session", {"user_id": 2, "token": "def456"}, "/sessions/mobile")

# Query entire subtrees
all_users = db.select(path="/users")  # Gets both active and inactive
web_sessions = db.select(path="/sessions/web")
```

### Limit Management

```python
# Set limits for specific paths
db.set_limit("/logs", 1000)        # Keep max 1000 log entries
db.set_limit("/sessions", 100)     # Keep max 100 sessions
db.set_limit("/temp", 10)          # Keep max 10 temp objects

# Limits are inherited by subpaths
db.set_limit("/users", 500)        # Applies to /users/active, /users/inactive, etc.

# Control behavior when limits are exceeded
db.add("log", "New entry", "/logs", on_limit="drop_oldest")  # Default
db.add("critical", "Important", "/logs", on_limit="error")   # Raises exception
```

### Time-Based Operations

```python
import time

# Add objects at different times
db.add("event", "Event 1", "/events")
time.sleep(1)
db.add("event", "Event 2", "/events") 
time.sleep(1)
db.add("event", "Event 3", "/events")

# Sort by time
recent_first = db.select(path="/events", sort=MangoSorting.SORT_TIME_DESC)
oldest_first = db.select(path="/events", sort=MangoSorting.SORT_TIME_ASC)

# Remove old objects
one_hour_ago = time.time() - 3600
db.remove(max_time=one_hour_ago, path="/events")
```

### Sorting Options

```python
from dcnr.mangodb import MangoSorting

# Available sorting options
objects = db.select(sort=MangoSorting.SORT_ID_ASC)     # By ID ascending
objects = db.select(sort=MangoSorting.SORT_ID_DESC)    # By ID descending  
objects = db.select(sort=MangoSorting.SORT_TIME_ASC)   # By time ascending
objects = db.select(sort=MangoSorting.SORT_TIME_DESC)  # By time descending
```

## Common Patterns

### User Session Management

```python
class SessionManager:
    def __init__(self):
        self.db = MangoDatabase()
        # Keep max 1000 sessions, cleanup old ones
        self.db.set_limit("/sessions", 1000)
    
    def create_session(self, user_id, session_data):
        return self.db.add(
            object_type="session",
            object_data={"user_id": user_id, **session_data},
            path="/sessions"
        )
    
    def get_user_sessions(self, user_id):
        sessions = self.db.select(object_type="session", path="/sessions")
        return [s for s in sessions if s.object_data.get("user_id") == user_id]
    
    def cleanup_old_sessions(self, max_age_seconds):
        cutoff_time = time.time() - max_age_seconds
        return self.db.remove(max_time=cutoff_time, path="/sessions")
```

### Logging System

```python
class Logger:
    def __init__(self):
        self.db = MangoDatabase()
        # Different limits for different log levels
        self.db.set_limit("/logs/error", 10000)
        self.db.set_limit("/logs/warn", 5000) 
        self.db.set_limit("/logs/info", 1000)
    
    def log(self, level, message, **kwargs):
        return self.db.add(
            object_type=f"log_{level}",
            object_data={"message": message, **kwargs},
            path=f"/logs/{level}"
        )
    
    def get_recent_errors(self, count=50):
        return self.db.select(
            path="/logs/error",
            sort=MangoSorting.SORT_TIME_DESC,
            limit=count
        )
    
    def search_logs(self, keyword, level=None):
        path = f"/logs/{level}" if level else "/logs"
        logs = self.db.select(path=path)
        return [
            log for log in logs 
            if keyword.lower() in str(log.object_data.get("message", "")).lower()
        ]
```

### Cache Implementation

```python
class Cache:
    def __init__(self, default_ttl=3600):
        self.db = MangoDatabase()
        self.default_ttl = default_ttl
        self.db.set_limit("/cache", 10000)  # Max 10k cached items
    
    def set(self, key, value, ttl=None):
        ttl = ttl or self.default_ttl
        return self.db.add(
            object_type="cache_entry",
            object_data={"key": key, "value": value, "ttl": ttl},
            path="/cache"
        )
    
    def get(self, key):
        entries = self.db.select(object_type="cache_entry", path="/cache")
        for entry in entries:
            if entry.object_data.get("key") == key:
                # Check if expired
                ttl = entry.object_data.get("ttl", self.default_ttl)
                if time.time() - entry.object_time > ttl:
                    self.db.remove(object_id=entry.object_id)
                    return None
                return entry.object_data.get("value")
        return None
    
    def cleanup_expired(self):
        entries = self.db.select(object_type="cache_entry", path="/cache")
        expired_count = 0
        for entry in entries:
            ttl = entry.object_data.get("ttl", self.default_ttl)
            if time.time() - entry.object_time > ttl:
                self.db.remove(object_id=entry.object_id)
                expired_count += 1
        return expired_count
```

## Performance Considerations

### Memory Usage
- MangoDatabase stores all data in memory
- Monitor memory usage for large datasets
- Use limits to prevent unbounded growth
- Regular cleanup of old/expired data

### Query Performance
- Path queries are efficient due to indexing
- ID queries are O(1) lookup
- Type filtering requires iteration
- Large result sets may impact performance

### Best Practices
- Use meaningful object types for efficient filtering
- Organize data hierarchically with logical paths
- Set appropriate limits for each path
- Implement regular cleanup for time-sensitive data
- Consider memory constraints in production

## Error Handling

```python
try:
    # Adding with strict limit
    db.add("data", value, "/limited", on_limit="error")
except ValueError as e:
    print(f"Limit exceeded: {e}")

try:
    # Invalid path
    db.add("data", value, path=123)  # Not a string
except TypeError as e:
    print(f"Invalid path type: {e}")

try:
    # Invalid limit
    db.set_limit("/path", -1)
except ValueError as e:
    print(f"Invalid limit: {e}")
```

## Integration Examples

### With LPC (Local Procedure Call)

```python
from dcnr.lpc import register_proc
from dcnr.mangodb import MangoDatabase

# Create shared database
db = MangoDatabase()

# Register database operations as procedures
register_proc("db.add", lambda obj_type, data, path="/": db.add(obj_type, data, path))
register_proc("db.select", lambda **kwargs: db.select(**kwargs))
register_proc("db.remove", lambda **kwargs: db.remove(**kwargs))

# Use via LPC
from dcnr.lpc import exec
result = exec("db.add", "user", {"name": "Alice"}, "/users")
users = exec("db.select", object_type="user")
```

### With Object Registry

```python
from dcnr.minisandbox import register_object
from dcnr.mangodb import MangoDatabase

# Register database in global registry
db = MangoDatabase()
register_object("app.database", db)
register_object("app.config.db_limits", {
    "users": 10000,
    "sessions": 1000,
    "logs": 50000
})

# Access via registry
from dcnr.minisandbox import get_registry
registry = get_registry()
app_db = registry.app.database
limits = registry.app.config.db_limits

# Apply configuration
for path, limit in limits.items():
    app_db.set_limit(f"/{path}", limit)
```

## Testing

```python
import unittest
from dcnr.mangodb import MangoDatabase

class TestMangoDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MangoDatabase()
    
    def test_add_and_select(self):
        obj = self.db.add("test", {"data": "value"}, "/test")
        self.assertIsNotNone(obj.object_id)
        
        found = self.db.select(object_id=obj.object_id)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].object_data, {"data": "value"})
    
    def test_path_hierarchy(self):
        self.db.add("type1", "data1", "/parent/child1")
        self.db.add("type2", "data2", "/parent/child2") 
        
        parent_objects = self.db.select(path="/parent")
        self.assertEqual(len(parent_objects), 2)
        
        child1_objects = self.db.select(path="/parent/child1")
        self.assertEqual(len(child1_objects), 1)
    
    def test_limits(self):
        self.db.set_limit("/test", 2)
        
        self.db.add("item", "1", "/test")
        self.db.add("item", "2", "/test")
        self.db.add("item", "3", "/test")  # Should trigger cleanup
        
        items = self.db.select(path="/test")
        self.assertEqual(len(items), 2)  # Should have 2 due to limit
```

This comprehensive guide should help developers effectively use MangoDatabase for various in-memory storage needs while following best practices for performance and data organization.
