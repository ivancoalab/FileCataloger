from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget


class IPreviewHandler(ABC):

    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def load(self, file_path: str) -> QWidget:
        pass
