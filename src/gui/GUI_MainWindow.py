# -*- coding: utf-8 -*-
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QClipboard, QIcon, QAction
from PySide6.QtWidgets import (QApplication, 
                               QMainWindow, 
                               QPushButton, 
                               QGridLayout, 
                               QWidget, 
                               QTextEdit, 
                               QTabWidget,
                               QLabel)
from gui.ChipSelector import ChipSelector

class MainWindow(QMainWindow):
    def __init__(self, w: int = 800, h: int = 600, title="app"):
        super().__init__()
        self.resize(w, h)
        self.setWindowTitle(title)

        # Create central widget with layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        self.layout = QGridLayout(centralWidget)

        #all other essential widgets (predefined for later)
        self.outputTextBox = QTextEdit()
        self.tabs = QTabWidget()

        #ui
        self.setupUI()

    
    def setupUI(self):
        #create window menu/toolbar
        self.setupMenu()

        #setup tabs
        self.tabs.addTab(self.setupInput(),QIcon("data/icons/inputHeader.png"), "General")
        self.tabs.addTab(self.setupOutput(),QIcon("data/icons/outputHeader.png"), "Output")

        #add tab to central layout
        self.layout.addWidget(self.tabs, 0, 0, 1, 1)

    def setupMenu(self):
        toolbar = self.menuBar()
        fileMenu = toolbar.addMenu("&File")

        actionQuit = QAction("Quit", self)
        actionQuit.triggered.connect(self.close)
        fileMenu.addAction(actionQuit)

        actionClear = QAction("Clear", self)
        actionClear.triggered.connect(self.clearEvent)
        fileMenu.addAction(actionClear)

    def setupInput(self):
        inputWidget = QWidget()
        inputLayout = QGridLayout(inputWidget)

        #website selector field
        websiteSelectWidget = QWidget()
        websiteSelectLayout = QGridLayout(websiteSelectWidget)

        primaryLabel = QLabel("Platforms")
        self.websiteSelect = ChipSelector(["Patreon", "Substar", "Ko-fi"])
        websiteSelectLayout.addWidget(primaryLabel, 0, 0)
        websiteSelectLayout.addWidget(self.websiteSelect, 1, 0)
        inputLayout.addWidget(websiteSelectWidget, 0, 0, Qt.AlignmentFlag.AlignTop)


        return inputWidget

    def setupOutput(self):
        outputWidget = QWidget()
        outputLayout = QGridLayout(outputWidget)

        #text box
        self.outputTextBox.setReadOnly(True)
        outputLayout.addWidget(self.outputTextBox, 0, 0, 1, 3)

        #buttons
        copybutton = QPushButton("Copy")
        copybutton.clicked.connect(self.copyToClipboard)
        outputLayout.addWidget(copybutton, 1, 0)

        clearButton = QPushButton("Clear")
        clearButton.clicked.connect(lambda: self.updateText(""))
        outputLayout.addWidget(clearButton, 1, 1)

        quitButton = QPushButton("Quit")
        quitButton.clicked.connect(self.close)  # Properly close the window
        outputLayout.addWidget(quitButton, 1, 2)

        return outputWidget
    
    #main window helpers
    def clearEvent(self):
        """Custom event to clear all input and output fields"""
        self.updateText("")

    #Output Helpers
    def updateText(self, newText : str = ""):
        self.outputTextBox.setText(newText)

    def copyToClipboard(self):
        text = self.outputTextBox.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        print(f"Copied to clipboard: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    
    @classmethod
    def runApp(cls, dataList=None):
        """Class method to create and run the application with optional data"""
        app = QApplication([])
        window = cls()
        if dataList:
            window.updateText("\n".join(dataList))
        window.show()
        app.exec()