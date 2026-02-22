import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileSystemItem:
    name: str
    path: str
    is_directory: bool
    size: int
    modified: datetime

    @staticmethod
    def from_path(path: str) -> "FileSystemItem":
        stat = os.stat(path)
        return FileSystemItem(
            name=os.path.basename(path),
            path=path,
            is_directory=os.path.isdir(path),
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
        )
