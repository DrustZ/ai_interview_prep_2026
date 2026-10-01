"""Simple four-level Cloud Storage solution (CodeSignal style)."""

from typing import Dict, List, Tuple


class CloudStorage:
    def __init__(self) -> None:
        # name -> (size, owner)
        self.files: Dict[str, Tuple[int, str]] = {}
        self.capacity: Dict[str, int] = {}
        self.used: Dict[str, int] = {}

    def execute(self, query: List[str]) -> str:
        operation = query[0]

        if operation == "ADD_FILE":
            return self.add_file(query[1], int(query[2]))
        if operation == "COPY_FILE":
            return self.copy_file(query[1], query[2])
        if operation == "GET_FILE_SIZE":
            return self.get_file_size(query[1])
        if operation == "FIND_FILE":
            return self.find_file(query[1], query[2])
        if operation == "ADD_USER":
            return self.add_user(query[1], int(query[2]))
        if operation == "ADD_FILE_BY":
            return self.add_file_by(query[1], query[2], int(query[3]))
        if operation == "UPDATE_CAPACITY":
            return self.update_capacity(query[1], int(query[2]))
        if operation == "COMPRESS_FILE":
            return self.compress_file(query[1], query[2])
        if operation == "DECOMPRESS_FILE":
            return self.decompress_file(query[1], query[2])

        raise ValueError(f"unknown operation: {operation}")

    # ------------------------------------------------------------------
    # Level 1
    # ------------------------------------------------------------------

    def add_file(self, name: str, size: int) -> str:
        if name in self.files:
            return "false"
        self.files[name] = (size, "admin")
        return "true"

    def copy_file(self, source: str, destination: str) -> str:
        if source not in self.files or destination in self.files:
            return "false"

        size, owner = self.files[source]
        if owner != "admin" and self._remaining(owner) < size:
            return "false"

        self.files[destination] = (size, owner)
        if owner != "admin":
            self.used[owner] += size
        return "true"

    def get_file_size(self, name: str) -> str:
        return str(self.files[name][0]) if name in self.files else ""

    # ------------------------------------------------------------------
    # Level 2
    # ------------------------------------------------------------------

    def find_file(self, prefix: str, suffix: str) -> str:
        matches = [
            (name, size)
            for name, (size, _) in self.files.items()
            if name.startswith(prefix) and name.endswith(suffix)
        ]
        matches.sort(key=lambda item: (-item[1], item[0]))
        return ", ".join(f"{name}({size})" for name, size in matches)

    # ------------------------------------------------------------------
    # Level 3
    # ------------------------------------------------------------------

    def add_user(self, user_id: str, capacity: int) -> str:
        if user_id == "admin" or user_id in self.capacity:
            return "false"
        self.capacity[user_id] = capacity
        self.used[user_id] = 0
        return "true"

    def add_file_by(self, user_id: str, name: str, size: int) -> str:
        if (
            user_id not in self.capacity
            or name in self.files
            or self._remaining(user_id) < size
        ):
            return ""

        self.files[name] = (size, user_id)
        self.used[user_id] += size
        return str(self._remaining(user_id))

    def update_capacity(self, user_id: str, new_capacity: int) -> str:
        if user_id not in self.capacity:
            return ""

        self.capacity[user_id] = new_capacity
        owned_files = [
            (name, size)
            for name, (size, owner) in self.files.items()
            if owner == user_id
        ]
        owned_files.sort(key=lambda item: (-item[1], item[0]))

        deleted = 0
        for name, size in owned_files:
            if self.used[user_id] <= new_capacity:
                break
            del self.files[name]
            self.used[user_id] -= size
            deleted += 1

        return str(deleted)

    # ------------------------------------------------------------------
    # Level 4
    # ------------------------------------------------------------------

    def compress_file(self, user_id: str, name: str) -> str:
        compressed_name = name + ".COMPRESSED"
        if (
            user_id not in self.capacity
            or name not in self.files
            or name.endswith(".COMPRESSED")
            or compressed_name in self.files
        ):
            return ""

        size, owner = self.files[name]
        if owner != user_id:
            return ""

        compressed_size = size // 2
        del self.files[name]
        self.files[compressed_name] = (compressed_size, owner)
        self.used[user_id] -= size - compressed_size
        return str(self._remaining(user_id))

    def decompress_file(self, user_id: str, name: str) -> str:
        suffix = ".COMPRESSED"
        if (
            user_id not in self.capacity
            or name not in self.files
            or not name.endswith(suffix)
        ):
            return ""

        compressed_size, owner = self.files[name]
        original_name = name[: -len(suffix)]
        original_size = compressed_size * 2
        extra_space = original_size - compressed_size

        if (
            owner != user_id
            or original_name in self.files
            or self._remaining(user_id) < extra_space
        ):
            return ""

        del self.files[name]
        self.files[original_name] = (original_size, owner)
        self.used[user_id] += extra_space
        return str(self._remaining(user_id))

    def _remaining(self, user_id: str) -> int:
        return self.capacity[user_id] - self.used[user_id]


def solution(queries: List[List[str]]) -> List[str]:
    storage = CloudStorage()
    return [storage.execute(query) for query in queries]
