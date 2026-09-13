# -*- coding: utf-8 -*-
import json

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QApplication, 
                               QCheckBox,
                               QFrame,
                               QMainWindow, 
                               QPushButton, 
                               QGridLayout, QScrollArea, 
                               QHBoxLayout,
                               QVBoxLayout,
                               QWidget, 
                               QTextEdit, 
                               QTabWidget,
                               QLabel,
                               QStackedLayout,
                               QSizePolicy)
from gui.ChipSelector import ChipSelector
from gui.PlatformWidget import PLATFORM_CONFIG_PATH, platformWidget
from resources import data_path

class MainWindow(QMainWindow):
    H1LABEL_STYLE = "font-weight: bold; font-size: 18px; color:#969696; margin-bottom: 6px;"
    def __init__(self, w: int = 800, h: int = 600, title="Patreon Sub Compiler"):
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

        #non GUI
        self.platformDict = {}

        #ui
        self.setupUI()

    
    def setupUI(self):
        #create window menu/toolbar
        self.setupMenu()

        #setup tabs
        self.tabs.addTab(self.setupInput(),QIcon(str(data_path("icons", "inputHeader.png"))), "General")
        self.tabs.addTab(self.setupOutput(),QIcon(str(data_path("icons", "outputHeader.png"))), "Output")

        #add tab to central layout
        self.layout.addWidget(self.tabs, 0, 0, 1, 1)

        # This action bar stays outside the tab's scroll area so it is always visible.
        self.actionBar = QFrame()
        self.actionBar.setObjectName("actionBar")
        self.actionBar.setStyleSheet(
            "QFrame#actionBar { background-color: #292929; "
            "border: 1px solid #444444; border-radius: 5px; }"
        )
        self.actionBar.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.actionBarStack = QStackedLayout(self.actionBar)
        self.actionBarStack.setContentsMargins(0, 0, 0, 0)

        self.inputActionWidget = QWidget()
        self.actionLayout = QGridLayout(self.inputActionWidget)
        self.actionLayout.setContentsMargins(12, 5, 12, 5)
        self.actionLayout.setHorizontalSpacing(10)

        self.prefixOptionWidget = QWidget()
        prefixOptionLayout = QHBoxLayout(self.prefixOptionWidget)
        prefixOptionLayout.setContentsMargins(0, 0, 0, 0)
        prefixOptionLayout.setSpacing(6)
        self.applyHeaderCheck = QCheckBox()
        self.applyHeaderCheck.setChecked(True)
        applyHeaderLabel = QLabel("Apply platform acronym to compiled names")
        applyHeaderLabel.setWordWrap(True)
        prefixOptionLayout.addWidget(self.applyHeaderCheck)
        prefixOptionLayout.addWidget(applyHeaderLabel, 1)

        self.compileButton = QPushButton("Compile")
        self.compileButton.setMinimumHeight(42)
        self.compileButton.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.compileButton.clicked.connect(self.compileEvent)

        self.clearInputsButton = QPushButton("clear")
        self.clearInputsButton.setMinimumHeight(42)
        self.clearInputsButton.clicked.connect(self.clearEvent)

        self.actionLayout.addWidget(self.prefixOptionWidget, 0, 0)
        self.actionLayout.addWidget(self.compileButton, 0, 1)
        self.actionLayout.addWidget(self.clearInputsButton, 0, 2)

        self.outputActionWidget = QWidget()
        outputActionLayout = QGridLayout(self.outputActionWidget)
        outputActionLayout.setContentsMargins(12, 5, 12, 5)
        outputActionLayout.setHorizontalSpacing(10)

        self.outputCopyButton = QPushButton("Copy")
        self.outputCopyButton.setMinimumHeight(42)
        self.outputCopyButton.clicked.connect(self.copyToClipboard)
        self.outputClearButton = QPushButton("Clear")
        self.outputClearButton.setMinimumHeight(42)
        self.outputClearButton.clicked.connect(lambda: self.updateText(""))
        self.outputQuitButton = QPushButton("Quit")
        self.outputQuitButton.setMinimumHeight(42)
        self.outputQuitButton.clicked.connect(self.close)

        outputActionLayout.addWidget(self.outputCopyButton, 0, 0)
        outputActionLayout.addWidget(self.outputClearButton, 0, 1)
        outputActionLayout.addWidget(self.outputQuitButton, 0, 2)
        outputActionLayout.setColumnStretch(0, 1)
        outputActionLayout.setColumnStretch(1, 1)
        outputActionLayout.setColumnStretch(2, 1)

        self.actionBarStack.addWidget(self.inputActionWidget)
        self.actionBarStack.addWidget(self.outputActionWidget)
        self.tabs.currentChanged.connect(self._updateActionBarPage)
        self._updateActionBarPage(self.tabs.currentIndex())
        self.layout.addWidget(self.actionBar, 1, 0, 1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 0)
        self._sizeActionBarHeight()

        self.compilingOverlay = QLabel("Compiling in progress", self.tabs)
        self.compilingOverlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compilingOverlay.setStyleSheet(
            "background-color: #d97706; color: white; border: 2px solid #f59e0b; "
            "border-radius: 8px; font-size: 24px; font-weight: bold;"
        )
        self.compilingOverlay.hide()

    def setupMenu(self):
        toolbar = self.menuBar()
        self.fileMenu = toolbar.addMenu("&File")

        self.actionQuit = QAction("Quit", self)
        self.actionQuit.triggered.connect(self.close)
        self.fileMenu.addAction(self.actionQuit)

        self.actionClear = QAction("Clear", self)
        self.actionClear.triggered.connect(self.clearEvent)
        self.fileMenu.addAction(self.actionClear)

        # Preserve the menu and its actions for later, but keep it out of the UI.
        toolbar.hide()

    def setupInput(self):
        scrollArea = QScrollArea()
        inputWidget = QWidget()
        inputLayout = QGridLayout(inputWidget)
        scrollArea.setWidget(inputWidget)
        scrollArea.setWidgetResizable(True)

        #website selector field
        websiteSelectWidget = QWidget()
        websiteSelectLayout = QGridLayout(websiteSelectWidget)

        with PLATFORM_CONFIG_PATH.open(encoding="utf-8") as configFile:
            platformConfigs = json.load(configFile)
        platformEntries = [
            (platformKey, platformConfig["name"])
            for platformKey, platformConfig in platformConfigs.items()
            if platformKey != "default"
        ]
        platformNames = [displayName for _, displayName in platformEntries]
        self.platformNameToKey = {
            displayName: platformKey
            for platformKey, displayName in platformEntries
        }

        #platform selector
        primaryLabel = QLabel("Platforms")
        primaryLabel.setStyleSheet(self.H1LABEL_STYLE)
        self.websiteSelect = ChipSelector(platformNames)
        self.websiteSelect.itemAdded.connect(self.addPlatformWidget)
        self.websiteSelect.itemRemoved.connect(self.removePlatformWidget)
        websiteSelectLayout.addWidget(primaryLabel, 0, 0)
        websiteSelectLayout.addWidget(self.websiteSelect, 1, 0)
        inputLayout.addWidget(websiteSelectWidget, 0, 0, Qt.AlignmentFlag.AlignTop)

        #platform input area
        platformStorageWidget = QWidget()
        self.platformStorageLayout = QVBoxLayout(platformStorageWidget)
        self.platformStorageLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.platformStorageLayout.setSpacing(10)
        self.platformStorageLayout.setContentsMargins(10, 10, 10, 10)
        secondaryLabel = QLabel("Platform Details")
        secondaryLabel.setStyleSheet(self.H1LABEL_STYLE)
        self.platformStorageLayout.addWidget(secondaryLabel)

        # Preload every supported platform once. Selecting a platform only
        # changes its visibility; deselecting it clears and hides the same widget.
        for platformKey, _displayName in platformEntries:
            widget = platformWidget(platformKey)
            widget.hide()
            self.platformStorageLayout.addWidget(widget)
            self.platformDict[platformKey] = widget

        inputLayout.addWidget(platformStorageWidget, 1, 0, Qt.AlignmentFlag.AlignTop)
        inputLayout.setRowStretch(1, 1)

        return scrollArea

    def setupOutput(self):
        outputWidget = QWidget()
        outputLayout = QGridLayout(outputWidget)

        #text box
        self.outputTextBox.setReadOnly(True)
        outputLayout.addWidget(self.outputTextBox, 0, 0)

        return outputWidget
    
    #main window helpers
    def clearEvent(self):
        """Restore input defaults and remove every selected platform file."""
        for widget in self.platformDict.values():
            widget.clearSelectedFile()
        self.applyHeaderCheck.setChecked(True)
        self.updateText("")

    def compileEvent(self):
        """Show progress feedback, then compile on the next event-loop cycle."""
        if self.compilingOverlay.isVisible():
            return
        self.updateText("")
        self._positionCompilingOverlay()
        self.compilingOverlay.show()
        self.compilingOverlay.raise_()
        self.compileButton.setEnabled(False)
        QApplication.processEvents()
        QTimer.singleShot(0, self._finishCompilation)

    def _finishCompilation(self):
        try:
            compiledNames = []
            applyHeader = self.applyHeaderCheck.isChecked()
            for widget in self.platformDict.values():
                compiledNames.extend(widget.compileNames(applyHeader))
            self.updateText("\n".join(compiledNames))
        except Exception as error:
            self.updateText(f"Compilation failed: {error}")
        finally:
            self.compilingOverlay.hide()
            self.compileButton.setEnabled(True)
            self.tabs.setCurrentIndex(1)

    def _positionCompilingOverlay(self):
        availableWidth = max(1, self.tabs.width() - 24)
        overlayWidth = min(max(280, int(self.tabs.width() * 0.68)), availableWidth)
        overlayHeight = min(120, max(1, self.tabs.height() - 24))
        xPosition = (self.tabs.width() - overlayWidth) // 2
        yPosition = (self.tabs.height() - overlayHeight) // 2
        self.compilingOverlay.setGeometry(
            xPosition, yPosition, overlayWidth, overlayHeight
        )

    def _updateActionBarPage(self, tabIndex):
        self.actionBarStack.setCurrentIndex(0 if tabIndex == 0 else 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "compilingOverlay"):
            self._positionCompilingOverlay()
        if hasattr(self, "actionBar"):
            self._sizeActionBarHeight()
            QTimer.singleShot(0, self._sizeActionBarControls)

    def _sizeActionBarHeight(self):
        availableHeight = self.centralWidget().height()
        targetHeight = max(54, (availableHeight + 19) // 20)
        self.actionBar.setFixedHeight(targetHeight)

    def _sizeActionBarControls(self):
        margins = self.actionLayout.contentsMargins()
        spacing = self.actionLayout.horizontalSpacing() * 2
        frameWidth = self.actionBar.frameWidth() * 2
        contentWidth = max(
            1,
            self.actionBar.width()
            - margins.left()
            - margins.right()
            - spacing
            - frameWidth,
        )
        prefixWidth = int(contentWidth * 0.30)
        compileWidth = int(contentWidth * 0.60)
        clearWidth = contentWidth - prefixWidth - compileWidth
        self.prefixOptionWidget.setFixedWidth(prefixWidth)
        self.compileButton.setFixedWidth(compileWidth)
        self.clearInputsButton.setFixedWidth(clearWidth)
    
    #Input Helpers
    def addPlatformWidget(self, platformName):
        """Reveal the platform widget that was preloaded during startup."""
        platformKey = self.platformNameToKey.get(platformName, platformName)
        widget = self.platformDict.get(platformKey)
        if widget is not None:
            widget.show()

    def removePlatformWidget(self, platformName):
        """Reset and hide a platform widget without destroying it."""
        platformKey = self.platformNameToKey.get(platformName, platformName)
        widget = self.platformDict.get(platformKey)
        if widget is not None:
            widget.clearSelectedFile()
            widget.hide()

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
