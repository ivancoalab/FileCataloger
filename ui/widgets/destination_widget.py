from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QPropertyAnimation
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QTimer


class DestinationWidget(QWidget):

    clicked = Signal(str)  # emit path

    def __init__(self, name: str, path: str, hotkey: str | None = None, parent=None):
        super().__init__(parent)

        self._name = name
        self._path = path
        self._hotkey = hotkey

        self.setFixedSize(150, 40)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(
            """
        QWidget {
            background-color: #3a3a3a;
            border-radius: 6px;
        }
        QWidget:hover {
            background-color: #505050;
        }
        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(0)

        self._label = QLabel(name)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("color: white;")

        layout.addWidget(self._label)

        if hotkey:
            self._hotkey_label = QLabel(f"[{hotkey}]")
            self._hotkey_label.setAlignment(Qt.AlignCenter)
            self._hotkey_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")
            layout.addWidget(self._hotkey_label)

        self.setLayout(layout)

        self.setToolTip(path)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._blink()
            self.clicked.emit(self._path)

    # def _blink(self):
    #     anim = QPropertyAnimation(self, b"windowOpacity")
    #     anim.setDuration(2000)
    #     anim.setStartValue(1)
    #     anim.setKeyValueAt(0.5, 0.4)
    #     anim.setEndValue(1)
    #     anim.start()
    #     self._animation = anim  # evitar garbage collection

    def _blink(self):
        # Cambiar temporalmente el color de fondo
        self.setStyleSheet(
            """
        QWidget {
            background-color: #00aa55;
            border-radius: 6px;
        }
        """
        )
        QTimer.singleShot(1500, self._restore_style)

    def _restore_style(self):
        self.setStyleSheet(
            """
        QWidget {
            background-color: #3a3a3a;
            border-radius: 6px;
        }
        QWidget:hover {
            background-color: #505050;
        }
        """
        )
