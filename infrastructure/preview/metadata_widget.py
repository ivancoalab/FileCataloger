import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from datetime import datetime


class MetadataWidget(QWidget):

    def __init__(self, path: str):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        stats = os.stat(path)

        size_mb = stats.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stats.st_mtime)

        layout.addWidget(QLabel(f"Size: {size_mb:.2f} MB"))
        layout.addWidget(QLabel(f"Modified: {modified}"))
        layout.addWidget(QLabel(f"Path: {path}"))
