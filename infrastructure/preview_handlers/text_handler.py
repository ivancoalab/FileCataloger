import os
from PySide6.QtWidgets import QTextEdit

from core.interfaces.preview_handler import IPreviewHandler


class TextPreviewHandler(IPreviewHandler):

    SUPPORTED = {".txt", ".log", ".json", ".csv", ".xml", ".py"}

    def can_handle(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.SUPPORTED

    def load(self, file_path: str):
        editor = QTextEdit()
        editor.setReadOnly(True)

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(100000)
                editor.setPlainText(content)
        except Exception as ex:
            editor.setPlainText(f"Failed to load text file\n\n{ex}")

        return editor
