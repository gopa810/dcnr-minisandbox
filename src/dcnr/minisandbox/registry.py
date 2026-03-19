"""
Implementation of global registry for application data, objects and methods

Example:

```python
def fetchone():
    return {"id": 1, "name": "Alice"}

register_object("database.prod.fetchone", fetchone)
register_object("database.prod.version", "1.0")

registry = get_registry()

print(registry.database.prod.fetchone())
print(registry.database.prod.version)
```

Not allowed:

```python
register_object("database.items.test", 1)
# ValueError: Invalid path component 'items': reserved name is not allowed

register_object("database.__class__.x", 1)
# ValueError: Invalid path component '__class__': reserved name is not allowed

register_object("database.for.x", 1)
# ValueError: Invalid path component 'for': Python keyword is not allowed
```



"""
from __future__ import annotations

import keyword
from typing import Any, Iterable


class DotDict(dict):
    """
    Dict with safe dot-notation access.

    Example:
        root = DotDict()
        root["database"] = DotDict()
        root.database.adlib = DotDict()
        root.database.adlib.fetchone = lambda: 123

        print(root.database.adlib.fetchone())   # 123
    """

    # Names that should not be allowed as path components because they would
    # clash with dict methods / internals / Python special attributes.
    _RESERVED_NAMES = {
        # dict API
        "clear", "copy", "fromkeys", "get", "items", "keys", "pop",
        "popitem", "setdefault", "update", "values",
        # object / Python internals
        "__class__", "__dict__", "__doc__", "__module__", "__weakref__",
        "__getattr__", "__getattribute__", "__setattr__", "__delattr__",
        "__init__", "__new__", "__reduce__", "__reduce_ex__", "__sizeof__",
        "__str__", "__repr__", "__format__", "__subclasshook__",
    }

    def __getattr__(self, name: str) -> Any:
        try:
            value = self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict._from_mapping(value)
            self[name] = value
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        self._validate_component(name)
        self[name] = self._wrap_value(value)

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setitem__(self, key: str, value: Any) -> None:
        self._validate_component(key)
        super().__setitem__(key, self._wrap_value(value))

    @classmethod
    def _from_mapping(cls, mapping: dict[str, Any]) -> "DotDict":
        result = cls()
        for k, v in mapping.items():
            result[k] = v
        return result

    @classmethod
    def _wrap_value(cls, value: Any) -> Any:
        if isinstance(value, dict) and not isinstance(value, DotDict):
            return cls._from_mapping(value)
        return value

    @classmethod
    def _validate_component(cls, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError(f"Path component must be str, got {type(name).__name__}")

        if not name:
            raise ValueError("Path component must not be empty")

        if not name.isidentifier():
            raise ValueError(
                f"Invalid path component {name!r}: must be a valid Python identifier"
            )

        if keyword.iskeyword(name):
            raise ValueError(
                f"Invalid path component {name!r}: Python keyword is not allowed"
            )

        if name.startswith("_"):
            raise ValueError(
                f"Invalid path component {name!r}: names starting with '_' are not allowed"
            )

        if name in cls._RESERVED_NAMES:
            raise ValueError(
                f"Invalid path component {name!r}: reserved name is not allowed"
            )


class ObjectRegistry:
    """
    Singleton registry that stores objects in a nested DotDict and supports:

        register_object("database.adlib.fetchone", func)

    Then access:

        registry.database.adlib.fetchone()
    """

    _instance: ObjectRegistry | None = None

    def __new__(cls) -> "ObjectRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._root = DotDict()
        return cls._instance

    @property
    def root(self) -> DotDict:
        return self._root

    def clear(self) -> None:
        self._root.clear()

    def register_object(self, path: str, obj: Any) -> None:
        components = self._parse_path(path)
        node = self._root

        for component in components[:-1]:
            existing = node.get(component)
            if existing is None:
                child = DotDict()
                node[component] = child
                node = child
            else:
                if not isinstance(existing, DotDict):
                    raise ValueError(
                        f"Cannot create subpath under {component!r}: "
                        f"path segment already contains non-container object "
                        f"of type {type(existing).__name__}"
                    )
                node = existing

        leaf = components[-1]
        node[leaf] = obj

    def get_object(self, path: str) -> Any:
        components = self._parse_path(path)
        node: Any = self._root

        for component in components:
            if not isinstance(node, DotDict):
                raise KeyError(
                    f"Path {path!r} is invalid: segment {component!r} "
                    f"is under non-container object"
                )
            try:
                node = node[component]
            except KeyError as exc:
                raise KeyError(f"Path not found: {path!r}") from exc

        return node

    def has_path(self, path: str) -> bool:
        try:
            self.get_object(path)
            return True
        except KeyError:
            return False

    def unregister_object(self, path: str) -> None:
        components = self._parse_path(path)
        node = self._root

        for component in components[:-1]:
            value = node.get(component)
            if not isinstance(value, DotDict):
                raise KeyError(f"Path not found: {path!r}")
            node = value

        leaf = components[-1]
        if leaf not in node:
            raise KeyError(f"Path not found: {path!r}")
        del node[leaf]

    def _parse_path(self, path: str) -> list[str]:
        if not isinstance(path, str):
            raise TypeError(f"path must be str, got {type(path).__name__}")

        if not path:
            raise ValueError("path must not be empty")

        path = path.strip('.')

        if path.startswith(".") or path.endswith(".") or ".." in path:
            raise ValueError(f"Invalid path {path!r}")

        components = path.split(".")
        for component in components:
            DotDict._validate_component(component)

        return components

    def __getattr__(self, name: str) -> Any:
        return getattr(self._root, name)


def get_registry() -> ObjectRegistry:
    return ObjectRegistry()


def register_object(path: str, obj: Any) -> None:
    get_registry().register_object(path, obj)