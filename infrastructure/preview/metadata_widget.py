import os
from PySide6.QtWidgets import QSizePolicy, QWidget, QVBoxLayout, QLabel
from datetime import datetime


class MetadataWidget(QWidget):

    def __init__(self, path: str):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        stats = os.stat(path)

        size_mb = stats.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stats.st_mtime)

        self._path_label = QLabel(f"Path: {path}")
        self._path_label.setWordWrap(True)
        self._path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(QLabel(f"Size: {size_mb:.2f} MB"))
        layout.addWidget(QLabel(f"Modified: {modified}"))
        layout.addWidget(self._path_label)
