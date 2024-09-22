from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient

from utils import is_song_completed, get_wpm_record, reset_progress


class LevelMenu(QWidget):
    def __init__(self, parent=None, songs=None):
        super().__init__(parent)
        self.songs = songs
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Выберите песню")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for i, song in enumerate(self.songs):
            button = QPushButton(f"{i+1}. {song['title']}")
            wpm_record = get_wpm_record(song['title'])
            if is_song_completed(song['title']):
                button.setText(f"✓ {i+1}. {song['title']} (Рекорд: {wpm_record} WPM)")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border: none;
                        padding: 10px;
                        font-size: 16px;
                        border-radius: 5px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 10px;
                        font-size: 16px;
                        border-radius: 5px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
            button.clicked.connect(lambda _, idx=i: self.select_song(idx))
            scroll_layout.addWidget(button)

        self.reset_button = QPushButton("Сбросить прогресс")
        self.reset_button.clicked.connect(self.reset_progress)
        scroll_layout.addWidget(self.reset_button)

        scroll_area.setWidget(scroll_content)

        close_button = QPushButton("Закрыть")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_button.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(scroll_area)
        layout.addWidget(close_button)

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

    def select_song(self, index):
        self.parent().set_song(index)
        self.close()

    def reset_progress(self):
        reply = QMessageBox.question(self, 'Сброс прогресса', 
                                     "Вы уверены, что хотите сбросить весь прогресс?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            reset_progress()
            self.init_ui()  # Перерисовываем меню
