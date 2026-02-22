import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileMetadata:
    name: str
    path: str
    size: int
    modified: datetime

    @staticmethod
    def from_path(path: str) -> "FileMetadata":
        stat = os.stat(path)
        return FileMetadata(
            name=os.path.basename(path),
            path=path,
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
        )
