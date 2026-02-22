import os
from typing import List
from core.interfaces.file_service import IFileService

# from core.models.file_metadata import FileMetadata
from core.models.filesystem_item import FileSystemItem


class LocalFileSystemService(IFileService):

    # def list_files(self, directory: str) -> List[FileSystemItem]:
    def list_directory(self, directory: str) -> List[FileSystemItem]:
        if not os.path.isdir(directory):
            print(f"[WARN] Invalid directory: {directory}")
            return []

        items = []
        for entry in os.scandir(directory):
            try:
                items.append(FileSystemItem.from_path(entry.path))
            except Exception as ex:
                print(f"[ERROR] Failed reading: {entry.path} | {ex}")

        items.sort(key=lambda x: (not x.is_directory, x.name.lower()))
        return items
