from abc import ABC, abstractmethod
from typing import List

# from core.models.file_metadata import FileMetadata
from core.models.filesystem_item import FileSystemItem


class IFileService(ABC):

    # @abstractmethod
    # def list_files(self, directory: str) -> List[FileMetadata]:
    #    pass

    @abstractmethod
    def list_directory(self, directory: str) -> List[FileSystemItem]:
        pass
