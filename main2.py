import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                             QGraphicsDropShadowEffect, QHBoxLayout, QPushButton, QMessageBox, 
                             QScrollArea, QTextEdit, QGraphicsOpacityEffect, QScrollArea, QProgressBar)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter

from song_lyrics import SONGS
from progress import save_progress, is_song_completed, get_wpm_record, reset_progress
import time

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

class TypingTrainer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Luxury Typing Trainer")
        self.setGeometry(100, 100, 1000, 800)
        
        self.songs = SONGS
        self.current_song = 0
        self.lines = self.songs[self.current_song]["lyrics"].split('\n')
        self.current_line = 0
        self.current_char = 0
        self.current_incorrect = False  # Add this line
        
        self.fade_animation = None
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.update_fade_animation)
        
        self.total_chars = sum(len(line) for line in self.lines)
        self.chars_typed = 0
        
        self.start_time = None
        self.wpm = 0
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        title_label = QLabel("Luxury Typing Trainer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Helvetica", 36, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FF4500;")  # Bright orange color
        
        self.level_label = QLabel(f"Song: {self.songs[self.current_song]['title']}")
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_label.setFont(QFont("Helvetica", 24))
        self.level_label.setStyleSheet("color: #1E90FF;")  # Bright blue color
        
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
            }
        """)
        self.text_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.text_edit)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        main_layout.addWidget(title_label)
        main_layout.addWidget(self.level_label)
        main_layout.addWidget(scroll_area)
        
        # Add virtual keyboard
        keyboard_layout = QVBoxLayout()
        keyboard_layout.setSpacing(5)  # Уменьшаем расстояние между рядами
        
        rows = [
            ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
            ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
            ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
            ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
            ["Ctrl", "Win", "Alt", "Space", "Alt", "Fn", "Ctrl"]
        ]
        
        self.key_buttons = {}
        
        for row in rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(2)  # Уменьшаем расстояние между кнопками
            for char in row:
                if char in ["Backspace", "Tab", "Caps", "Enter", "Shift", "Ctrl", "Win", "Alt", "Fn"]:
                    button = KeyboardButton(char, width=60, height=40)  # Увеличиваем ширину для специальных клавиш
                elif char == "Space":
                    button = KeyboardButton(char, width=200, height=40)  # Делаем пробел широким
                else:
                    button = KeyboardButton(char)
                self.key_buttons[char] = button
                row_layout.addWidget(button)
            keyboard_layout.addLayout(row_layout)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
                height: 20px;  # Уменьшаем высоту прогресс-бара
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(keyboard_layout)
        
        # Set stretch factors to give more space to the text area
        main_layout.setStretchFactor(self.text_edit, 3)
        main_layout.setStretchFactor(keyboard_layout, 1)
        
        # Set a luxurious color scheme
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 250))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(44, 62, 80))
        self.setPalette(palette)
        
        self.update_text_display()
        
        # Add a blinking cursor effect
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.blink_cursor)
        self.cursor_timer.start(500)
        
        # Add opacity animation
        effect = QGraphicsOpacityEffect(self.text_edit)
        self.text_edit.setGraphicsEffect(effect)
        
        # Add menu button
        menu_button = QPushButton("Меню песен")
        menu_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        menu_button.clicked.connect(self.show_level_menu)

        main_layout.addWidget(menu_button)
        
    def reset_level(self):
        self.lines = self.songs[self.current_song]["lyrics"].split('\n')
        self.current_line = 0
        self.current_char = 0
        self.current_incorrect = False
        self.level_label.setText(f"Song: {self.songs[self.current_song]['title']}")
        self.total_chars = sum(len(line) for line in self.lines)
        self.chars_typed = 0
        self.update_progress()
        self.update_text_display()
        self.start_time = None
        self.wpm = 0
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif self.current_line < len(self.lines):
            if self.start_time is None:
                self.start_time = time.time()
            
            current_text = self.lines[self.current_line]
            if self.current_char < len(current_text):
                if event.key() == Qt.Key.Key_Space:
                    typed_char = " "
                else:
                    typed_char = event.text()
                
                if typed_char:
                    self.process_typed_char(typed_char)
                    self.highlight_pressed_key(typed_char)


    def process_typed_char(self, typed_char):
        if self.current_line < len(self.lines):
            current_text = self.lines[self.current_line]
            if self.current_char < len(current_text):
                expected_char = current_text[self.current_char]
                if typed_char == expected_char:
                    self.current_char += 1
                    self.chars_typed += 1
                    self.current_incorrect = False
                    self.update_text_display()
                    self.update_progress()
                    self.animate_correct()
                    
                    if self.current_char == len(current_text):
                        self.current_line += 1
                        self.current_char = 0
                        if self.current_line == len(self.lines):
                            self.level_completed()
                        else:
                            self.start_fade_animation()
                else:
                    self.current_incorrect = True
                    self.highlight_current_char(QColor(231, 76, 60))
                    self.animate_incorrect()
    
    def update_text_display(self):
        if self.current_line < len(self.lines):
            displayed_text = '<div style="text-align: center;">'
            
            # Добавляем две предыдущие строки (если есть)
            for i in range(2):
                if self.current_line > i:
                    displayed_text += f'<p style="color: #AAAAAA; margin: 5px 0; font-size: 18px;">{self.lines[self.current_line-i-1]}</p>'
            
            # Текущая строка
            current_text = self.lines[self.current_line]
            displayed_text += '<p style="font-size: 32px; font-weight: bold; margin: 15px 0;">'
            for i, char in enumerate(current_text):
                if i < self.current_char:
                    displayed_text += f'<font color="#27ae60">{char}</font>'  # Зеленый для правильных
                elif i == self.current_char:
                    if self.current_incorrect:
                        displayed_text += f'<span style="background-color: #e74c3c;">{char}</span>'
                    else:
                        displayed_text += f'<span style="background-color: #3498db;">{char}</span>'
                else:
                    displayed_text += char
            displayed_text += '</p>'
            
            # Добавляем две следующие строки (если есть)
            for i in range(2):
                if self.current_line + i + 1 < len(self.lines):
                    displayed_text += f'<p style="color: #AAAAAA; margin: 5px 0; font-size: 18px;">{self.lines[self.current_line+i+1]}</p>'
            
            displayed_text += '</div>'
            
            self.text_edit.setHtml(displayed_text)
            self.text_edit.ensureCursorVisible()
        
    def highlight_current_char(self, color):
        self.update_text_display()
        
    def blink_cursor(self):
        displayed_text = self.text_edit.toHtml()
        if 'background-color: yellow;' in displayed_text:
            displayed_text = displayed_text.replace('background-color: yellow;', '')
        else:
            displayed_text = displayed_text.replace('id="cursor"', 'id="cursor" style="background-color: yellow;"')
        self.text_edit.setHtml(displayed_text)
        
    def animate_correct(self):
        animation = QPropertyAnimation(self.text_edit, b"pos")
        animation.setDuration(150)  # Увеличиваем длительность до 150 мс
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # Используем более плавную кривую
        start_pos = self.text_edit.pos()
        animation.setKeyValueAt(0, start_pos)
        animation.setKeyValueAt(0.5, start_pos + QPoint(0, 3))  # Уменьшаем амплитуду до 3 пикселей
        animation.setKeyValueAt(1, start_pos)
        animation.start()
        
    def animate_incorrect(self):
        animation = QPropertyAnimation(self.text_edit, b"pos")
        animation.setDuration(100)  # Увеличиваем длительность до 100 мс
        animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        start_pos = self.text_edit.pos()
        animation.setKeyValueAt(0, start_pos)
        animation.setKeyValueAt(0.25, start_pos + QPoint(-3, 0))  # Уменьшаем амплитуду до 3 пикселей
        animation.setKeyValueAt(0.75, start_pos + QPoint(3, 0))
        animation.setKeyValueAt(1, start_pos)
        animation.start()
        
    def highlight_pressed_key(self, char):
        if char == " ":
            char = "Space"
        elif char.isalpha():
            char = char.upper()
        
        if char in self.key_buttons:
            button = self.key_buttons[char]
            button.setStyleSheet("""
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 10px;
            """)
            QTimer.singleShot(200, lambda: button.setStyleSheet("""
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 10px;
                color: #2c3e50;
            """))
        
    def level_completed(self):
        if self.start_time is not None:
            end_time = time.time()
            elapsed_time = end_time - self.start_time
            words = sum(len(line.split()) for line in self.lines)
            self.wpm = int((words / elapsed_time) * 60)
        else:
            self.wpm = 0
        
        is_last_song = self.current_song == len(self.songs) - 1
        save_progress(self.songs[self.current_song]["title"], self.wpm)
        custom_box = CustomMessageBox(self, self.songs[self.current_song]["title"], is_last_song, self.wpm)
        custom_box.move(self.geometry().center() - custom_box.rect().center())
        custom_box.show()
        
        self.start_time = None

    def show_level_menu(self):
        level_menu = LevelMenu(self, self.songs)
        level_menu.move(self.geometry().center() - level_menu.rect().center())
        level_menu.show()

    def set_song(self, index):
        self.current_song = index
        self.reset_level()
    
    def next_song(self):
        if self.current_song < len(self.songs) - 1:
            self.current_song += 1
            self.reset_level()
        else:
            QMessageBox.information(self, "Поздравляем!", "Вы прошли все песни!")
            self.close()
    
    def start_fade_animation(self):
        self.fade_animation = QPropertyAnimation(self.text_edit.graphicsEffect(), b"opacity")
        self.fade_animation.setDuration(800)  # Увеличиваем длительность анимации до 800 мс
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)  # Используем более плавную кривую
        self.fade_animation.start()
        self.fade_timer.start(400)  # Запускаем таймер на половине анимации

    def update_fade_animation(self):
        self.fade_timer.stop()
        self.update_text_display()
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def update_progress(self):
        progress = (self.chars_typed / self.total_chars) * 100
        self.progress_bar.setValue(int(progress))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    trainer = TypingTrainer()
    trainer.show()
    sys.exit(app.exec())
    