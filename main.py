import sys
import os

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
from application.app_state import AppState  # ADDED PHASE 8
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
    # history = MoveHistory()  # ADDED PHASE 6
    app_state = AppState()  # ADDED PHASE 8
    # ADDED PHASE 8.2
    last_directory = app_state.get_setting("last_directory")
    default_directory = app_state.get_setting("default_directory")

    if last_directory and os.path.exists(last_directory):
        start_directory = last_directory
    elif default_directory and os.path.exists(default_directory):
        start_directory = default_directory
    else:
        start_directory = os.getcwd()

    move_history = MoveHistory(app_state)  # ADDED PHASE 8
    mover = FileMover(move_history)  # ADDED PHASE 6

    # window = MainWindow(explorer)
    # window = MainWindow(explorer, mover, config)  # UPDATED PHASE 6
    window = MainWindow(
        explorer, mover, config, app_state, start_directory
    )  # UPDATED PHASE 8.2
    window.set_preview_manager(preview_manager)  # ADDED IN PHASE 4
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
