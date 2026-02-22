import os
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from core.interfaces.preview_handler import IPreviewHandler


class ImagePreviewHandler(IPreviewHandler):

    SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

    def can_handle(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.SUPPORTED

    def load(self, file_path: str):
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            label.setText("Failed to load image")
            return label

        label.setPixmap(
            pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        return label
