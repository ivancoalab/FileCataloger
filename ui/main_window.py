import os
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QListView,
    QLabel,
    QPushButton,
    QFileDialog,
    QSplitter,
    QSizePolicy,
    QApplication,
    QLineEdit,
)
from PySide6.QtCore import Qt, QEvent  # UPDATED IN PHASE 3
from PySide6.QtGui import QFontMetrics  # ADDED IN THIS ITERATION
from PySide6.QtGui import QShortcut, QKeySequence


from application.file_explorer import FileExplorer
from ui.file_list_model import FileListModel
from ui.widgets.destination_widget import DestinationWidget
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
        preview_manager,
    ):
        super().__init__()
        self._explorer = explorer
        self._file_mover = file_mover  # ADDED PHASE 6
        self._config = config_manager  # ADDED PHASE 6
        # self._preview_manager = None  # ADDED IN PHASE 4
        self._preview_manager = preview_manager  # ADDED IN PHASE 4
        self._destination_buttons = []
        self._app_state = app_state  # ADDED PHASE 8.2
        # self._hotkey_map = {}
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
        # ===== CENTRAL CONTAINER =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(5, 5, 5, 5)
        central_widget.setLayout(self._main_layout)

        # ===== TOOLBAR (TOP) =====
        self._create_toolbar()

        # ===== DESTINATIONS CONTAINER (Single Row Scrollable) =====
        self._destinations_scroll = QScrollArea()
        self._destinations_scroll.setWidgetResizable(True)
        self._destinations_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._destinations_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._destinations_scroll.setFixedHeight(70)

        self._destinations_widget = QWidget()
        self._destinations_layout = QHBoxLayout()
        self._destinations_layout.setContentsMargins(5, 5, 5, 5)
        self._destinations_layout.setSpacing(8)

        self._destinations_widget.setLayout(self._destinations_layout)
        self._destinations_scroll.setWidget(self._destinations_widget)

        self._main_layout.addWidget(self._destinations_scroll)

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
        self._main_layout.addWidget(self._path_label)

        # ===== SPLITTER =====
        self._splitter = QSplitter(Qt.Horizontal)

        # ===== LEFT PANEL (List + Stats Line) =====
        self._left_panel = QWidget()
        self._left_layout = QVBoxLayout()
        self._left_layout.setContentsMargins(0, 0, 0, 0)

        self._list_view = QListView()
        self._list_view.setModel(self._model)
        self._list_view.doubleClicked.connect(self._on_item_double_click)
        self._list_view.selectionModel().currentChanged.connect(
            self._on_current_changed
        )

        self._list_view.setFocus()
        # self._list_view.installEventFilter(self)
        # self.installEventFilter(self)
        QApplication.instance().installEventFilter(self)

        self._folder_stats_label = QLabel("0 files | 0 MB")
        self._folder_stats_label.setFixedHeight(22)
        self._folder_stats_label.setStyleSheet(
            "background-color: #1e1e1e; color: #cccccc; padding-left: 5px;"
        )

        self._left_layout.addWidget(self._list_view)
        self._left_layout.addWidget(self._folder_stats_label)
        self._left_panel.setLayout(self._left_layout)

        # ===== PREVIEW CONTAINER (unchanged logic) =====
        self._preview_container = QWidget()
        self._preview_layout = QVBoxLayout()
        self._preview_layout.setContentsMargins(0, 0, 0, 0)

        self._content_widget = QLabel("Preview Area")
        self._content_widget.setAlignment(Qt.AlignCenter)
        self._preview_layout.addWidget(self._content_widget)

        self._preview_container.setLayout(self._preview_layout)

        # ===== ADD TO SPLITTER =====
        self._splitter.addWidget(self._left_panel)
        self._splitter.addWidget(self._preview_container)

        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setChildrenCollapsible(False)

        self._main_layout.addWidget(self._splitter)

        # ===== STATUS BAR =====
        self.statusBar().showMessage("Ready")

        # ===== POPULATE DESTINATIONS (temporary buttons for now) =====
        self._populate_destinations()

    def _create_toolbar(self):
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)

        self._open_action = toolbar.addAction("Open Folder")
        self._back_action = toolbar.addAction("Back")
        toolbar.addSeparator()
        self._toggle_mode_action = toolbar.addAction("Text Mode")

        self._open_action.triggered.connect(self._open_folder)
        self._back_action.triggered.connect(self._go_back)
        self._toggle_mode_action.triggered.connect(self._toggle_view_mode)

    def _populate_destinations(self):
        self._destination_widgets = {}
        # self._hotkey_map.clear()
        # Limpiar layout
        while self._destinations_layout.count():
            item = self._destinations_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        destinations = self._config.get_destinations()
        if not isinstance(destinations, list):
            return
        for dest in destinations:
            name = dest.get("name", "Unnamed")
            path = dest.get("path")
            hotkey = dest.get("hotkey")
            # buttonlabel = str(f"[{hotkey}] {name}")
            widget = DestinationWidget(name, path, hotkey)
            widget.clicked.connect(lambda p=path: self._activate_destination_by_path(p))
            self._destination_widgets[path] = widget
            self._destinations_layout.addWidget(widget)
            # widget = DestinationWidget(name, path, hotkey)
            # widget.clicked.connect(self._handle_destination_click)
            # self._destinations_layout.addWidget(widget)
            # if hotkey:
            #     self._register_hotkey(hotkey, widget)

        self._destinations_layout.addStretch()

    def _activate_destination_by_path(self, path: str):
        widget = self._destination_widgets.get(path)
        if widget:
            widget._blink()
        self._move_current_file(path)

    # def _register_hotkey(self, hotkey: str, widget):
    #     if hotkey in self._hotkey_map:
    #         print(f"Hotkey duplicada: {hotkey}")
    #         return
    #     shortcut = QShortcut(QKeySequence(hotkey), self)
    #     shortcut.activated.connect(lambda w=widget: self._activate_destination(w))
    #     self._hotkey_map[hotkey] = widget

    # def _activate_destination(self, widget):
    #     # Activar blink visual
    #     widget._blink()
    #     # Emitir como si fuera click real
    #     self._handle_destination_click(widget._path)

    def _handle_destination_click(self, path: str):
        print("Destino seleccionado:", path)

    def _toggle_view_mode(self):
        self.statusBar().showMessage("Toggle view mode (not implemented yet)")

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
        if event.type() == QEvent.KeyPress:
            # Evitar interferir si en futuro agregas QLineEdit
            if isinstance(QApplication.focusWidget(), QLineEdit):
                return super().eventFilter(source, event)
            destinations = self._config.get_destinations()
            key = event.key()
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self._handle_enter()
                return True
            if key == Qt.Key_Backspace:
                self._go_back()
                return True
            if key == Qt.Key_Delete:
                deleted = self._config.get_deleted_folder()
                if deleted:
                    self._move_current_file(deleted)
                return True
            # HOTKEY DESTINATIONS
            char = event.text()
            if char:
                for dest in destinations:
                    hotkey = dest.get("hotkey")
                    if hotkey and char == hotkey:
                        self._activate_destination_by_path(dest["path"])
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

    # def _create_destination_panel(self):  # ADDED PHASE 7
    #    layout = QHBoxLayout()

    #    destinations = self._config.get_destinations()

    #    for dest in destinations:
    #        button = QPushButton(f"[{dest['hotkey']}] {dest['name']}")
    #        button.clicked.connect(lambda _, p=dest["path"]: self._move_current_file(p))
    #        layout.addWidget(button)
    #        self._destination_buttons.append(button)

    #    return layout

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
