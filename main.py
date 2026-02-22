import sys
from PySide6.QtWidgets import QApplication

from infrastructure.filesystem_service import LocalFileSystemService

from application.file_explorer import FileExplorer
from application.preview_manager import PreviewManager

from infrastructure.preview_handlers.image_handler import ImagePreviewHandler
from infrastructure.preview_handlers.text_handler import TextPreviewHandler
from infrastructure.preview_handlers.hex_handler import HexPreviewHandler

from infrastructure.config_manager import ConfigManager  # ADDED PHASE 6
from application.move_history import MoveHistory  # ADDED PHASE 6
from application.file_mover import FileMover  # ADDED PHASE 6

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    file_service = LocalFileSystemService()
    explorer = FileExplorer(file_service)

    preview_manager = PreviewManager(
        [
            ImagePreviewHandler(),
            TextPreviewHandler(),
            HexPreviewHandler(),  # fallback last
        ]
    )

    config = ConfigManager()  # ADDED PHASE 6
    history = MoveHistory()  # ADDED PHASE 6
    mover = FileMover(history)  # ADDED PHASE 6

    # window = MainWindow(explorer)
    window = MainWindow(explorer, mover, config)  # UPDATED PHASE 6
    window.set_preview_manager(preview_manager)  # ADDED IN PHASE 4
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
