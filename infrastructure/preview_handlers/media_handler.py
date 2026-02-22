from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl
import os


class MediaPreviewHandler:

    SUPPORTED_VIDEO = {".mp4", ".mkv", ".avi", ".mov"}
    SUPPORTED_AUDIO = {".mp3", ".wav", ".ogg", ".flac"}

    def can_handle(self, path: str) -> bool:
        ext = os.path.splitext(path)[1].lower()
        return ext in self.SUPPORTED_VIDEO or ext in self.SUPPORTED_AUDIO

    def load(self, path: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        player = QMediaPlayer()
        audio = QAudioOutput()
        player.setAudioOutput(audio)

        ext = os.path.splitext(path)[1].lower()

        if ext in self.SUPPORTED_VIDEO:
            video_widget = QVideoWidget()
            player.setVideoOutput(video_widget)
            layout.addWidget(video_widget)

        play_button = QPushButton("Play / Pause")
        play_button.clicked.connect(lambda: self._toggle(player))
        layout.addWidget(play_button)

        player.setSource(QUrl.fromLocalFile(path))

        container._player = player
        container._audio = audio

        return container

    def _toggle(self, player):
        if player.playbackState() == QMediaPlayer.PlayingState:
            player.pause()
        else:
            player.play()
