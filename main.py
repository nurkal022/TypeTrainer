import sys
from PyQt6.QtWidgets import QApplication
from typing_trainer import TypingTrainer

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    trainer = TypingTrainer()
    trainer.show()
    sys.exit(app.exec())