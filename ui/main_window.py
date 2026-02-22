import os
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListView,
    QLabel,
    QPushButton,
    QFileDialog,
    QSplitter,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QEvent  # UPDATED IN PHASE 3
from PySide6.QtGui import QFontMetrics  # ADDED IN THIS ITERATION
from PySide6.QtGui import QShortcut, QKeySequence

from application.file_explorer import FileExplorer
from ui.file_list_model import FileListModel
from infrastructure.preview.metadata_widget import MetadataWidget  # ADD IMPORT PHASE 5

from ui.conflict_dialog import ask_conflict_resolution


class MainWindow(QMainWindow):

    def __init__(
        self,
        explorer: FileExplorer,
        file_mover,
        config_manager,
        app_state,
        start_directory,
    ):
        super().__init__()
        self._explorer = explorer
        self._file_mover = file_mover  # ADDED PHASE 6
        self._config = config_manager  # ADDED PHASE 6
        self._preview_manager = None  # ADDED IN PHASE 4
        self._destination_buttons = []
        self._app_state = app_state  # ADDED PHASE 8.2
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self._undo_last_move)

        self.setWindowTitle("File Cataloger")
        self.resize(1000, 600)

        self._model = FileListModel()
        self._init_ui()
        # ADDED PHASE 8.3
        geometry = self._app_state.get_geometry()
        splitter_sizes = self._app_state.get_splitter_sizes()
        if geometry:
            self.restoreGeometry(geometry)
        if splitter_sizes:
            self._splitter.setSizes(splitter_sizes)

        self._load_directory(start_directory)  # ADDED PHASE 8.2

    def set_preview_manager(self, manager):  # ADDED IN PHASE 4
        self._preview_manager = manager

    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # ===== PATH BAR =====
        self._path_label = QLabel("No directory selected")
        self._path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._path_label.setFixedHeight(28)
        self._path_label.setStyleSheet(
            """
            background-color: #2b2b2b;
            color: white;
            padding-left: 8px;
        """
        )
        main_layout.addWidget(self._path_label)

        # ===== SPLITTER =====
        self._splitter = QSplitter(Qt.Horizontal)

        self._list_view = QListView()
        self._list_view.setModel(self._model)
        self._list_view.doubleClicked.connect(self._on_item_double_click)
        self._list_view.selectionModel().currentChanged.connect(
            self._on_current_changed
        )

        # Keyboard navigation  # ADDED IN PHASE 3
        self._list_view.setFocus()
        self._list_view.installEventFilter(self)

        # ===== PREVIEW CONTAINER (FIX PHASE 8.3) =====
        self._preview_container = QWidget()
        self._preview_layout = QVBoxLayout()
        self._preview_layout.setContentsMargins(0, 0, 0, 0)

        # self._preview = QLabel("Preview Area")
        # self._preview.setAlignment(Qt.AlignCenter)
        # self._preview_layout.addWidget(self._preview)

        # Placeholder only (no metadata yet)
        self._content_widget = QLabel("Preview Area")
        self._content_widget.setAlignment(Qt.AlignCenter)
        self._preview_layout.addWidget(self._content_widget)

        self._preview_container.setLayout(self._preview_layout)

        self._splitter.addWidget(self._list_view)
        self._splitter.addWidget(self._preview_container)
        # self._splitter.addWidget(self._preview)

        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setChildrenCollapsible(False)  # ADDED FIX

        # ===== BOTTOM BAR =====
        bottom_bar = QHBoxLayout()
        open_button = QPushButton("Open Folder")
        open_button.clicked.connect(self._open_folder)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self._go_back)

        bottom_bar.addWidget(open_button)
        bottom_bar.addWidget(back_button)

        destination_layout = self._create_destination_panel()  # ADDED PHASE 7

        main_layout.addWidget(self._splitter)
        main_layout.addLayout(bottom_bar)
        main_layout.addLayout(destination_layout)  # ADDED PHASE 7

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def _open_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        if directory:
            self._load_directory(directory)

    def _load_directory(self, directory: str):  # ADDED IN PHASE 3
        self._current_directory = directory  # ADDED PHASE 7
        self._app_state.set_setting("last_directory", directory)  # ADDED PHASE 8.2
        items = self._explorer.open_directory(directory)
        self._model.set_items(items)
        # self._path_label.setText(directory)
        self._set_path_text(directory)  # UPDATED IN THIS ITERATION
        if items:
            self._list_view.setCurrentIndex(self._model.index(0))

    def _set_path_text(self, path: str):  # ADDED IN THIS ITERATION
        metrics = QFontMetrics(self._path_label.font())
        elided = metrics.elidedText(path, Qt.ElideMiddle, self._path_label.width())
        self._path_label.setText(elided)

    def resizeEvent(self, event):  # ADDED IN THIS ITERATION
        current = self._explorer.get_current_directory()
        if current:
            self._set_path_text(current)
        super().resizeEvent(event)

    def _on_item_double_click(self, index):
        item = self._model.get_item(index)

        if item.is_directory:
            # items = self._explorer.open_directory(item.path)
            # self._model.set_items(items)
            self._load_directory(item.path)

    def _on_current_changed(self, current, previous):
        if not current.isValid():
            return
        self._on_item_selected(current)

    def _go_back(self):
        current = self._explorer.get_current_directory()
        if not current:
            return

        parent = os.path.dirname(current)
        if parent and parent != current:
            # items = self._explorer.open_directory(parent)
            # self._model.set_items(items)
            self._load_directory(parent)

    # Keyboard event handling  # ADDED IN PHASE 3
    def eventFilter(self, source, event):
        if source is self._list_view and event.type() == QEvent.KeyPress:
            # HOTKEY DESTINATIONS
            destinations = self._config.get_destinations()
            key = event.key()

            if key == Qt.Key_Return or key == Qt.Key_Enter:
                self._handle_enter()
                return True

            if key == Qt.Key_Backspace:
                self._go_back()
                return True
            # if key == Qt.Key_F6:  # TEMP TEST KEY PHASE 6
            #    test_folder = self._config.get_deleted_folder()
            #    if test_folder:
            #        self._move_current_file(test_folder)
            #    return True
            for dest in destinations:
                if event.text() == dest["hotkey"]:
                    self._move_current_file(dest["path"])
                    return True

            # DELETE KEY → deleted folder
            if key == Qt.Key_Delete:
                deleted = self._config.get_deleted_folder()
                if deleted:
                    self._move_current_file(deleted)
                return True

        return super().eventFilter(source, event)

    def _handle_enter(self):  # ADDED IN PHASE 3
        index = self._list_view.currentIndex()
        if not index.isValid():
            return

        item = self._model.get_item(index)
        if item.is_directory:
            self._load_directory(item.path)

    # def _on_item_selected(self, index):  # ADDED IN PHASE 4
    #    if not self._preview_manager:
    #        return

    #   item = self._model.get_item(index)

    #   if item.is_directory:
    #       return

    #  widget = self._preview_manager.get_preview(item.path)
    #  self._replace_preview_widget(widget)

    def _on_item_selected(self, index):  # UPDATED PHASE 5 FIX
        item = self._model.get_item(index)

        if item.is_directory:
            return

        widget = self._preview_manager.get_preview(item.path)
        self._replace_preview_widget(widget, item.path)

    # def _replace_preview_widget(self, new_widget):  # UPDATED IN THIS ITERATION
    #    index = self._splitter.indexOf(self._preview)
    #    if index == -1:
    #        return

    #    self._preview.setParent(None)
    #    self._preview.deleteLater()

    #    self._splitter.insertWidget(index, new_widget)
    #    self._preview = new_widget

    def _replace_preview_widget(self, new_widget, path: str):
        # Remove old content
        if self._content_widget is not None:
            self._preview_layout.removeWidget(self._content_widget)
            self._content_widget.deleteLater()

        # Remove old metadata if exists
        if hasattr(self, "_metadata_widget") and self._metadata_widget:
            self._preview_layout.removeWidget(self._metadata_widget)
            self._metadata_widget.deleteLater()

        from infrastructure.preview.metadata_widget import MetadataWidget

        # Set new content
        self._content_widget = new_widget
        self._preview_layout.insertWidget(0, self._content_widget)

        # Add metadata below
        self._metadata_widget = MetadataWidget(path)
        self._preview_layout.addWidget(self._metadata_widget)

    def _replace_preview_widget_old(self, new_widget, path: str):  # UPDATED PHASE 5 FIX
        index = self._splitter.indexOf(self._preview)
        if index == -1:
            return

        self._preview.setParent(None)
        self._preview.deleteLater()

        from infrastructure.preview.metadata_widget import MetadataWidget

        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        layout.addWidget(new_widget)
        layout.addWidget(MetadataWidget(path))  # FIXED

        self._splitter.insertWidget(index, container)
        self._preview = container

    def _move_current_file(self, destination_folder):  # ADDED PHASE 6
        index = self._list_view.currentIndex()
        if not index.isValid():
            return
        item = self._model.get_item(index)
        if item.is_directory:
            return
        current_row = index.row()

        source = item.path
        file_name = os.path.basename(source)

        # detect conflict first
        dest_path = os.path.join(destination_folder, file_name)
        policy = None
        if os.path.exists(dest_path):
            policy = ask_conflict_resolution(self, file_name)
            if policy is None:
                return  # user cancelled

        result, data = self._file_mover.move(item.path, destination_folder, policy)

        if result == "success":
            self._refresh_after_move(current_row)
        elif result == "conflict":
            print("[INFO] Conflict detected:", data)
        else:
            print("[ERROR] Move failed:", data)

    def _refresh_after_move(self, previous_row):  # ADDED PHASE 6
        current_dir = self._explorer.get_current_directory()
        items = self._explorer.open_directory(current_dir)
        self._model.set_items(items)

        total = len(items)

        if total == 0:
            return

        if previous_row < total:
            new_row = previous_row
        else:
            new_row = total - 1

        new_index = self._model.index(new_row)
        self._list_view.setCurrentIndex(new_index)
        # self._on_item_selected(new_index)  # ADDED PHASE 7

    def _create_destination_panel(self):  # ADDED PHASE 7
        layout = QHBoxLayout()

        destinations = self._config.get_destinations()

        for dest in destinations:
            button = QPushButton(f"[{dest['hotkey']}] {dest['name']}")
            button.clicked.connect(lambda _, p=dest["path"]: self._move_current_file(p))
            layout.addWidget(button)
            self._destination_buttons.append(button)

        return layout

    def _select_item_by_name(self, name: str):  # UPDATED PHASE 7
        model = self._list_view.model()
        if not model:
            return

        for row in range(model.rowCount()):
            item = model._items[row]  # direct access to model data
            if item.name == name:
                index = model.index(row, 0)
                self._list_view.setCurrentIndex(index)
                # self._on_item_selected(index)
                break

    def _reload_current_directory(self, record=None):
        current_dir = self._current_directory
        self._load_directory(current_dir)
        if record:
            restored_name = os.path.basename(record["from"])
            self._select_item_by_name(restored_name)

    def _undo_last_move(self):
        record = self._file_mover.undo()
        if record:
            self._reload_current_directory(record)
        else:
            print("Nothing to undo or undo failed.")

    def closeEvent(self, event):  # ADDED PHASE 8.3
        geometry = self.saveGeometry()
        splitter_sizes = self._splitter.sizes()

        self._app_state.set_window_state(geometry, splitter_sizes)
        super().closeEvent(event)
