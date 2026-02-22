from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ImagePreviewHandler:

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")
        )

    def load(self, file_path: str):
        return ScalableImageLabel(file_path)


class ScalableImageLabel(QLabel):

    def __init__(self, file_path):
        super().__init__()
        self._pixmap = QPixmap(file_path)

        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(0, 0)  # FIX
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # FIX

    def resizeEvent(self, event):
        if not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled)
        super().resizeEvent(event)
