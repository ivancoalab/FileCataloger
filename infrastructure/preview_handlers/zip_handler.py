import zipfile
import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class ZipPreviewHandler:

    SUPPORTED = {".zip"}

    def can_handle(self, path: str) -> bool:
        return os.path.splitext(path)[1].lower() in self.SUPPORTED

    def load(self, path: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        text = QTextEdit()
        text.setReadOnly(True)

        try:
            with zipfile.ZipFile(path, "r") as z:
                lines = []
                for info in z.infolist():
                    size_kb = info.file_size / 1024
                    lines.append(f"{info.filename}  ({size_kb:.1f} KB)")

                text.setText("\n".join(lines))

        except Exception as ex:
            text.setText(f"[ERROR] Cannot read ZIP:\n{ex}")

        layout.addWidget(text)
        return container
