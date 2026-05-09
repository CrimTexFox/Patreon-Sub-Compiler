# -*- coding: utf-8 -*-
from PySide6.QtCore import QDate, QSize, Qt, Signal
from PySide6.QtGui import QClipboard, QIcon, QAction, QPainter
from PySide6.QtWidgets import (QApplication, 
                               QFrame, QHBoxLayout, 
                               QMainWindow, 
                               QPushButton, 
                               QGridLayout, 
                               QStackedLayout,
                               QWidget, 
                               QTextEdit, 
                               QTabWidget,
                               QDateEdit,
                               QFileDialog,
                               QSizePolicy,
                               QLabel)
import pandas as pd
from gui.ChipSelector import ChipSelector

class FileChipWidget(QWidget):
    removed = Signal(str)

    def __init__(self, text="Select File", parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)

        #main label
        self.label = QLabel(text)
        self.label.setStyleSheet("color: #969696;")
        
        #remove(x) button
        removeBtn = QPushButton("\u2715")
        removeBtn.setFixedSize(18, 18)
        removeBtn.setStyleSheet("QPushButton { border: none; font-weight: bold; }")
        removeBtn.clicked.connect(lambda: self.removed.emit(self.text))

        layout.addWidget(self.label)
        layout.addWidget(removeBtn)

        self.setObjectName("fileChip")
        self.setStyleSheet(
            "#fileChip { background-color: #424242; border-radius: 12px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(30)

    def setText(self, text):
        self.text = text
        self.label.setText(text)

    def paintEvent(self, event):
        from PySide6.QtWidgets import QStyleOption
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(self.style().PrimitiveElement.PE_Widget, opt, p, self)

class FileDialogueWidget(QWidget):
    selected = Signal(str, pd.DataFrame)

    def __init__(self, platform, text="Select File", parent=None):
        super().__init__(parent)
        self.platform = platform

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)

        #main label
        fileButton = QPushButton("Select File")
        fileButton.setStyleSheet("background-color: #404040; color: #969696; border: 1px solid #555555; margin-bottom: 12px; margin-top: 6px; margin-left: 10px;")
        fileButton.clicked.connect(self.selectFile)
        layout.addWidget(fileButton)

        self.setObjectName("fileChip")
        self.setStyleSheet(
            "#fileChip { background-color: #424242; border-radius: 12px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(30)

    def setText(self, text):
        self.text = text
        self.label.setText(text)

    def paintEvent(self, event):
        from PySide6.QtWidgets import QStyleOption
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(self.style().PrimitiveElement.PE_Widget, opt, p, self)

    def selectFile(self) -> None:
        #Emit signal with file name and data table when a file is selected
        print(f"Selecting file for {self.platform}...")
        
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )

        if not filePath:
            raise Exception("No file selected.")

        dataTable = pd.read_csv(filePath)
        fileName = filePath.split("/")[-1]

        self.selected.emit(fileName, dataTable)



class platformWidget(QFrame):
    def __init__(self, platform):
        super().__init__()
        self.platform = platform
        self.platformDataframe = None
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #333333; border: 1px solid #555555; border-radius: 5px;")
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)
        
        self.setupUI()
    

    def setupUI(self):
        #setup overall widget
        self.setStyleSheet("background-color: #262626;")

        #setup label
        platformLabel = QLabel(self.platform.upper())
        platformLabel.setStyleSheet("font-weight: bold; font-size: 20px; color:#969696; margin-bottom: 6px;; margin-top: 6px;margin-left: 10px;")
        self.layout.addWidget(platformLabel, 0, 0, Qt.AlignmentFlag.AlignTop)

        #File Selection box
        fileWidget = QWidget()
        fileLayout = QGridLayout(fileWidget)

        fileLabel = QLabel("File:")
        fileLabel.setStyleSheet("color: #969696; margin-bottom: 12px; margin-top: 6px; margin-left: 10px;")
        fileLayout.addWidget(fileLabel, 1, 0, Qt.AlignmentFlag.AlignTop)

        self.subFileWidget = QWidget()
        self.subFileLayout = QStackedLayout(self.subFileWidget)
        #Empty Button
        self.fileDialogue = FileDialogueWidget(self.platform, "Select File")
        self.fileDialogue.selected.connect(lambda fileName, dataTable: self.selectedFile(fileName, dataTable))

        #Selected File Button
        self.fileChip = FileChipWidget("No file selected")
        self.fileChip.removed.connect(lambda: self.subFileLayout.setCurrentIndex(0))


        self.subFileLayout.addWidget(self.fileDialogue)
        self.subFileLayout.addWidget(self.fileChip)
        self.subFileLayout.setCurrentIndex(0)


        fileLayout.addWidget(self.subFileWidget, 2, 0, Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(fileWidget, 1, 0, Qt.AlignmentFlag.AlignTop)

        # Specific options for each platform
            # includes specifying subscriptiuon name, 
            # choosing how long theybe been subbed, 
            # and how much they've paid total
        self.optionsWidget = QWidget()
        self.optionsLayout = QGridLayout(self.optionsWidget)
        self.optionsLayout.setContentsMargins(0, 0, 0, 0)
        self.optionsLayout.setSpacing(0)

        #Subscription name bar (essentially same as sub platform selection)
        self.tierNameSelector = ChipSelector(["Default"])

        #Subbed Since
        self.tierDateSelector = QDateEdit()
        self.tierDateSelector.setCalendarPopup(True)
        self.tierDateSelector.setDisplayFormat("yyyy-MM-dd")
        self.tierDateSelector.setStyleSheet("""background-color: #404040; 
                                       color: #969696; 
                                       border: 1px solid #555555; 
                                       margin-bottom: 12px; 
                                       margin-top: 6px; 
                                       margin-left: 10px;"""
                                       )
        self.tierDateSelector.setDate(QDate.currentDate())

        #total paid
        totalPaidWidget = QWidget()
        totalPaidLayout = QHBoxLayout(totalPaidWidget)
        totalPaidLabel = QLabel("Total Paid:")
        totalPaidLabel.setStyleSheet("color: #969696; margin-bottom: 12px; margin-top: 6px; margin-left: 10px;")
        totalPaidLayout.addWidget(totalPaidLabel)
        self.totalPaidInput = QTextEdit()
        self.totalPaidInput.setFixedHeight(30)
        self.totalPaidInput.setStyleSheet("""background-color: #404040; 
                                       color: #969696; 
                                       border: 1px solid #555555; 
                                       margin-bottom: 12px; 
                                       margin-top: 6px; 
                                       margin-left: 10px;"""
                                       )
        self.totalPaidInput.setPlaceholderText("$0.00")
        totalPaidLayout.addWidget(self.totalPaidInput)

        self.optionsLayout.addWidget(self.tierNameSelector, 0, 0, Qt.AlignmentFlag.AlignTop)
        self.optionsLayout.addWidget(self.tierDateSelector, 1, 0, Qt.AlignmentFlag.AlignTop)
        self.optionsLayout.addWidget(totalPaidWidget, 1, 1, Qt.AlignmentFlag.AlignTop)

        self.layout.addWidget(self.optionsWidget, 1, 1, Qt.AlignmentFlag.AlignTop)

    def selectedFile(self, fileName, dataTable):
        print(f"Selected file for {self.platform}: {fileName}")
        self.fileChip.setText(fileName)
        self.platformDataframe = dataTable

        self.fileChip.setText(fileName)
        self.subFileLayout.setCurrentIndex(1)
