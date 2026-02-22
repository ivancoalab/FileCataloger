from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
import os


class PdfPreviewHandler:

    SUPPORTED = {".pdf"}

    def can_handle(self, path: str) -> bool:
        return os.path.splitext(path)[1].lower() in self.SUPPORTED

    def load(self, path: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        document = QPdfDocument(container)
        document.load(path)

        view = QPdfView()
        view.setDocument(document)

        layout.addWidget(view)

        container._doc = document
        return container
