from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class MangoObject:
    object_id: int
    object_type: str
    object_data: Any
    object_time: float
    path: str

class MangoSorting:
    SORT_ID_ASC = "id_asc"
    SORT_ID_DESC = "id_desc"
    SORT_TIME_ASC = "time_asc"
    SORT_TIME_DESC = "time_desc"

class MangoDatabase:
    def __init__(self) -> None:
        self._next_id: int = 1_000_000
        self._objects: dict[int, MangoObject] = {}
        self._path_index: dict[str, list[int]] = {"/": []}
        self._limits: dict[str, int] = {}

    # ---------- public API ----------

    def add(
        self,
        object_type: Optional[str] = None,
        object_data: Any = None,
        path: Optional[str] = None,
        on_limit: Optional[str] = None
    ) -> MangoObject:
        norm_path = self._normalize_path(path)
        object_type = "" if object_type is None else str(object_type)

        self._ensure_path_exists(norm_path)
        self._check_add_allowed(norm_path, on_limit=on_limit)

        obj = MangoObject(
            object_id=self._next_id,
            object_type=object_type,
            object_data=object_data,
            object_time=time.time(),
            path=norm_path,
        )
        self._next_id += 1

        self._objects[obj.object_id] = obj
        self._path_index[norm_path].append(obj.object_id)
        return obj

    def remove(
        self,
        object_id: Optional[int] = None,
        object_type: Optional[str] = None,
        max_time: Optional[float] = None,
        path: Optional[str] = None,
    ) -> int:
        selected = self.select(
            object_id=object_id,
            object_type=object_type,
            path=path,
        )

        to_remove: list[MangoObject] = []
        for obj in selected:
            if max_time is not None and obj.object_time > max_time:
                continue
            to_remove.append(obj)

        for obj in to_remove:
            self._objects.pop(obj.object_id, None)
            ids = self._path_index.get(obj.path)
            if ids is not None:
                try:
                    ids.remove(obj.object_id)
                except ValueError:
                    pass

        return len(to_remove)

    def select(
        self,
        object_id: Optional[int] = None,
        object_type: Optional[str] = None,
        path: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[MangoObject]:
        if object_id is not None:
            obj = self._objects.get(object_id)
            if obj is None:
                return []
            if object_type is not None and obj.object_type != object_type:
                return []
            if path is not None and not self._is_under_path(obj.path, self._normalize_path(path)):
                return []
            return [obj]

        if path is not None:
            norm_path = self._normalize_path(path)
            candidate_ids = []
            for p, ids in self._path_index.items():
                if self._is_under_path(p, norm_path):
                    candidate_ids.extend(ids)
            candidates = (self._objects[i] for i in candidate_ids if i in self._objects)
        else:
            candidates = self._objects.values()

        result: list[MangoObject] = []
        for obj in candidates:
            if object_type is not None and obj.object_type != object_type:
                continue
            result.append(obj)

        if sort is not None:
            if sort == MangoSorting.SORT_ID_ASC:
                result.sort(key=lambda x: x.object_id)
            elif sort == MangoSorting.SORT_ID_DESC:
                result.sort(key=lambda x: x.object_id, reverse=True)
            elif sort == MangoSorting.SORT_TIME_ASC:
                result.sort(key=lambda x: x.object_time)
            elif sort == MangoSorting.SORT_TIME_DESC:
                result.sort(key=lambda x: x.object_time, reverse=True)

        if limit is not None and len(result) >= limit:
            result = result[:limit]

        return result

    def set_limit(self, path: str, limit: int) -> None:
        if limit < 0:
            raise ValueError("limit must be >= 0")
        norm_path = self._normalize_path(path)
        self._ensure_path_exists(norm_path)
        self._limits[norm_path] = limit

    # ---------- internal helpers ----------

    def _normalize_path(self, path: Optional[str]) -> str:
        if path is None or path == "":
            return "/"
        if not isinstance(path, str):
            raise TypeError("path must be a string or None")

        parts = [p for p in path.strip("/").split("/") if p]
        return "/" + "/".join(parts) if parts else "/"

    def _ensure_path_exists(self, path: str) -> None:
        for p in self._ancestor_chain(path):
            self._path_index.setdefault(p, [])

    def _ancestor_chain(self, path: str) -> list[str]:
        if path == "/":
            return ["/"]
        parts = path.strip("/").split("/")
        result = ["/"]
        current = ""
        for part in parts:
            current += "/" + part
            result.append(current)
        return result


    def _effective_limit(self, path: str) -> int:
        for p in reversed(self._ancestor_chain(path)):
            if p in self._limits:
                return self._limits[p]
        return 10_000

    def _check_add_allowed(self, path: str, on_limit: Optional[str] = None) -> None:
        if on_limit is None:
            on_limit = "drop_oldest"
        limit = self._effective_limit(path)
        if limit is None:
            return

        current_count = len(self._path_index.get(path, []))
        if current_count >= limit:
            if on_limit == "error":
                raise ValueError(
                    f"Path limit exceeded for {path!r}: limit={limit}, current={current_count}"
                )
            elif on_limit == "drop_oldest":
                to_remove = self._path_index.get(path, [])[:current_count - limit + 1]
                for obj_id in to_remove:
                    self.remove(object_id=obj_id)

    def _is_under_path(self, candidate: str, root: str) -> bool:
        if root == "/":
            return True
        return candidate == root or candidate.startswith(root + "/")
    