from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QTextEdit
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QClipboard

class MainWindow(QMainWindow):
    def __init__(self, w: int = 400, h: int = 300, title="app"):
        super().__init__()
        self.resize(w, h)
        self.setWindowTitle(title)

        # Create central widget with layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        self.layout = QGridLayout(centralWidget)

        #all other essential widgets
        self.outputTextBox = QTextEdit()

        #ui
        self.setupUI()

    def setupUI(self):
        #text box
        self.outputTextBox.setReadOnly(True)
        self.layout.addWidget(self.outputTextBox, 0, 0, 1, 3)

        #buttons
        copybutton = QPushButton("Copy")
        copybutton.clicked.connect(self.copyToClipboard)
        self.layout.addWidget(copybutton, 1, 0)

        clearButton = QPushButton("Clear")
        clearButton.clicked.connect(lambda: self.updateText(""))
        self.layout.addWidget(clearButton, 1, 1)

        quitButton = QPushButton("Quit")
        quitButton.clicked.connect(self.close)  # Properly close the window
        self.layout.addWidget(quitButton, 1, 2)
    
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
