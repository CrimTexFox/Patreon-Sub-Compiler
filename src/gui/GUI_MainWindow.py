# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import QSize

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setFixedSize(QSize(400,300))

        button = QPushButton("Press Me")
        self.setCentralWidget(button)

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()

    app.exec()