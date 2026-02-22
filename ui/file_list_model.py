from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

# from core.models.file_metadata import FileMetadata
from core.models.filesystem_item import FileSystemItem


class FileListModel(QAbstractListModel):

    def __init__(self):
        super().__init__()
        # self._files: list[FileMetadata] = []
        self._items: list[FileSystemItem] = []

    def rowCount(self, parent=QModelIndex()):
        # return len(self._files)
        return len(self._items)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self._items[index.row()]

        if role == Qt.DisplayRole:
            prefix = "[DIR] " if item.is_directory else ""
            return f"{prefix}{item.name}"

    # def set_files(self, files: list[FileMetadata]):
    #    self.beginResetModel()
    #    self._files = files
    #    self.endResetModel()

    # def get_file(self, index: QModelIndex) -> FileMetadata:
    #    return self._files[index.row()]

    def set_items(self, items: list[FileSystemItem]):
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def get_item(self, index: QModelIndex) -> FileSystemItem:
        return self._items[index.row()]
