from PySide6.QtWidgets import QWidget

from core.interfaces.preview_handler import IPreviewHandler

from infrastructure.preview_handlers.image_handler import ImagePreviewHandler
from infrastructure.preview_handlers.text_handler import TextPreviewHandler
from infrastructure.preview_handlers.hex_handler import HexPreviewHandler
from infrastructure.preview_handlers.media_handler import MediaPreviewHandler
from infrastructure.preview_handlers.pdf_handler import PdfPreviewHandler
from infrastructure.preview_handlers.zip_handler import (
    ZipPreviewHandler,
)  # ADDED PHASE 5 ZIP


class PreviewManager:

    def __init__(self, handlers: list[IPreviewHandler]):
        # self._handlers = handlers
        self._handlers = [
            ImagePreviewHandler(),
            TextPreviewHandler(),
            PdfPreviewHandler(),  # ADDED PHASE 5
            MediaPreviewHandler(),  # ADDED PHASE 5
            ZipPreviewHandler(),  # ADDED PHASE 5 ZIP
            HexPreviewHandler(),
        ]

    def get_preview(self, file_path: str) -> QWidget:
        for handler in self._handlers:
            try:
                if handler.can_handle(file_path):
                    return handler.load(file_path)
            except Exception as ex:
                print(f"[ERROR] Preview handler failed: {ex}")

        print("[WARN] No handler found, returning empty widget")
        return QWidget()
