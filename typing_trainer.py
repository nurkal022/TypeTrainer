from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, 
                             QHBoxLayout, QPushButton, QMessageBox, 
                             QScrollArea, QTextEdit, QProgressBar,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette

from custom_widgets import FancyLabel, KeyboardButton, CustomMessageBox
from level_menu import LevelMenu
from utils import SONGS, save_progress, is_song_completed, get_wpm_record, reset_progress
import time
import win32api
import win32con

    

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
        self.current_incorrect = False
        
        self.fade_animation = None
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.update_fade_animation)
        
        self.total_chars = sum(len(line) for line in self.lines)
        self.chars_typed = 0
        
        self.start_time = None
        self.wpm = 0
        
        self.current_layout = self.get_system_layout()
        self.keyboard_layout = None
        self.key_buttons = {}
        
        # Создаем таймер для проверки раскладки
        self.layout_check_timer = QTimer(self)
        self.layout_check_timer.timeout.connect(self.check_and_update_layout)
        self.layout_check_timer.start(100)  # Проверяем каждые 100 мс
        
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
        
        # Добавляем progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Инициализируем клавиатуру
        self.keyboard_layout = QVBoxLayout()
        main_layout.addLayout(self.keyboard_layout)
        self.create_keyboard()
        
        # Set stretch factors to give more space to the text area
        main_layout.setStretchFactor(self.text_edit, 3)
        main_layout.setStretchFactor(self.keyboard_layout, 1)
        
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

    def create_keyboard(self):
        # Очищаем существующую клавиатуру
        if self.keyboard_layout:
            for i in reversed(range(self.keyboard_layout.count())): 
                item = self.keyboard_layout.itemAt(i)
                if item.widget():
                    item.widget().setParent(None)
                elif item.layout():
                    self.clear_layout(item.layout())
        
        layouts = {
            'en': [
                ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
                ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
                ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
                ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
                ["Ctrl", "Win", "Alt", "Space", "Alt", "Fn", "Ctrl"]
            ],
            'ru': [
                ["Ё", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
                ["Tab", "Й", "Ц", "У", "К", "Е", "Н", "Г", "Ш", "Щ", "З", "Х", "Ъ", "\\"],
                ["Caps", "Ф", "Ы", "В", "А", "П", "Р", "О", "Л", "Д", "Ж", "Э", "Enter"],
                ["Shift", "Я", "Ч", "С", "М", "И", "Т", "Ь", "Б", "Ю", ".", "Shift"],
                ["Ctrl", "Win", "Alt", "Space", "Alt", "Fn", "Ctrl"]
            ],
            'kk': [
                ["(", ")", "\"", "Ә", "І", "Ң", "Ғ", "Ү", "Ұ", "Қ", "Ө", "Һ", ")", "Backspace"],
                ["Tab", "Й", "Ц", "У", "К", "Е", "Н", "Г", "Ш", "Щ", "З", "Х", "Ъ", "\\"],
                ["Caps", "Ф", "Ы", "В", "А", "П", "Р", "О", "Л", "Д", "Ж", "Э", "Enter"],
                ["Shift", "Я", "Ч", "С", "М", "И", "Т", "Ь", "Б", "Ю", "№", "Shift"],
                ["Ctrl", "Win", "Alt", "Space", "Alt", "Fn", "Ctrl"]
            ]
        }
        
        self.key_buttons = {}
        
        for row in layouts[self.current_layout]:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(1)  # Минимальный зазор между кнопками
            for char in row:
                if char in ["Backspace", "Tab", "Caps", "Enter", "Shift", "Ctrl", "Win", "Alt", "Fn"]:
                    button = KeyboardButton(char, width=60, height=40)
                elif char == "Space":
                    button = KeyboardButton(char, width=200, height=40)
                else:
                    button = KeyboardButton(char)
                self.key_buttons[char] = button
                row_layout.addWidget(button)
            self.keyboard_layout.addLayout(row_layout)
    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.clear_layout(item.layout())
    
    def get_system_layout(self):
        layout_id = win32api.GetKeyboardLayout() & 0xFFFF
        if layout_id == 0x0409:  # английский (США)
            return 'en'
        elif layout_id == 0x0419:  # русский
            return 'ru'
        elif layout_id == 0x043F:  # казахский
            return 'kk'
        else:
            return 'en'  # По умолчанию английский

    def check_and_update_layout(self):
        new_layout = self.get_system_layout()
        if new_layout != self.current_layout:
            self.current_layout = new_layout
            self.create_keyboard()