from typing import List
from core.interfaces.file_service import IFileService

# from core.models.file_metadata import FileMetadata
from core.models.filesystem_item import FileSystemItem


class FileExplorer:

    def __init__(self, file_service: IFileService):
        self._file_service = file_service
        self._current_directory: str | None = None

    # def get_files(self, directory: str) -> List[FileMetadata]:
    #    return self._file_service.list_files(directory)

    def open_directory(self, directory: str) -> List[FileSystemItem]:
        self._current_directory = directory
        return self._file_service.list_directory(directory)

    def get_current_directory(self) -> str | None:
        return self._current_directory
