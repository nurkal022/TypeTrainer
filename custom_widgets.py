from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient


class FancyLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(240, 240, 245))
        gradient.setColorAt(1, QColor(220, 220, 235))
        painter.fillRect(self.rect(), gradient)
        super().paintEvent(event)

class KeyboardButton(QLabel):
    def __init__(self, text, parent=None, width=40, height=40):  # Уменьшаем размер кнопок
        super().__init__(text, parent)
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 10, QFont.Weight.Bold))  # Уменьшаем размер шрифта
        self.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: #2c3e50;
            }
        """)

class CustomMessageBox(QWidget):
    def __init__(self, parent=None, song_title="", is_last_song=False, wpm=0):
        super().__init__(parent)
        self.song_title = song_title
        self.is_last_song = is_last_song
        self.wpm = wpm
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Поздравляем!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2ecc71;")

        message = QLabel(f"Вы успешно завершили песню:\n'{self.song_title}'")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setFont(QFont("Arial", 16))
        message.setStyleSheet("color: #34495e;")
        message.setWordWrap(True)

        wpm_label = QLabel(f"Ваша скорость: {self.wpm} WPM")
        wpm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wpm_label.setFont(QFont("Arial", 16))
        wpm_label.setStyleSheet("color: #34495e;")

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f5;
                border-radius: 15px;
                padding: 20px;
                color: #333;
                font-size: 24px;
                border: none;
            }
            QTextEdit QScrollBar {
                width: 0px;
                height: 0px;
            }
        """)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        if not self.is_last_song:
            next_button = QPushButton("Следующая песня")
            next_button.clicked.connect(self.accept)
        else:
            next_button = QPushButton("Завершить")
            next_button.clicked.connect(self.close)
        next_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(next_button)

        layout.addWidget(title)
        layout.addWidget(message)
        layout.addWidget(wpm_label)
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 240))
        gradient.setColorAt(1, QColor(240, 240, 240, 240))

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def accept(self):
        self.parent().next_song()
        self.close()
