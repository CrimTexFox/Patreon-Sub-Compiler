# -*- coding: utf-8 -*-
import json
from collections import Counter
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QDate, QFileInfo, QLocale, QStandardPaths, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter, QPixmap
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from gui.ChipSelector import ChipSelector
from resources import data_path


PLATFORM_CONFIG_PATH = data_path("PlatformColNames.Json")
FILE_ICON_PATH = data_path("icons", "file.png")


class FileChipWidget(QWidget):
    removed = Signal(str)

    def __init__(self, text="Select File", parent=None):
        super().__init__(parent)
        self.text = text
        self._sourcePixmap = QPixmap(str(FILE_ICON_PATH))

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(4)

        self.iconLabel = QLabel()
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.label.setStyleSheet("color: #c8c8c8;")
        self.label.setToolTip(text)

        self.removeBtn = QPushButton("\u2715")
        self.removeBtn.setFixedSize(22, 22)
        self.removeBtn.setStyleSheet(
            "QPushButton { background-color: #262626; color: #ffffff; "
            "border: 1px solid #666666; border-radius: 11px; font-weight: bold; }"
            "QPushButton:hover { background-color: #7a2828; }"
        )
        self.removeBtn.clicked.connect(lambda: self.removed.emit(self.text))

        self.layout.addWidget(self.iconLabel, 0, 0)
        self.layout.addWidget(
            self.removeBtn,
            0,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )
        self.layout.addWidget(self.label, 1, 0)

        self.setObjectName("fileChip")
        self.setStyleSheet(
            "#fileChip { background-color: #383838; border: 1px solid #555555; "
            "border-radius: 8px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setDisplayWidth(90)

    def setText(self, text):
        self.text = text
        self.label.setToolTip(text)
        self._updateFilename()

    def setDisplayWidth(self, width):
        """Keep the file card and icon consistently sized for its platform panel."""
        width = max(72, int(width))
        contentWidth = max(1, width - 16)
        self.setFixedWidth(width)
        self.iconLabel.setFixedSize(contentWidth, contentWidth)
        self.label.setFixedWidth(contentWidth)
        labelHeight = self.label.fontMetrics().height()
        self.label.setFixedHeight(labelHeight)
        self.setFixedHeight(contentWidth + labelHeight + 20)
        if not self._sourcePixmap.isNull():
            self.iconLabel.setPixmap(
                self._sourcePixmap.scaled(
                    contentWidth,
                    contentWidth,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        self._updateFilename()

    def _updateFilename(self):
        availableWidth = max(1, self.label.width())
        metrics = QFontMetrics(self.label.font())
        self.label.setText(
            metrics.elidedText(
                self.text, Qt.TextElideMode.ElideRight, availableWidth
            )
        )

    def paintEvent(self, event):
        from PySide6.QtWidgets import QStyleOption
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(self.style().PrimitiveElement.PE_Widget, opt, p, self)

class FileDialogueWidget(QWidget):
    selected = Signal(str, object)
    selectionFailed = Signal(str)

    def __init__(self, platform, text="Select File", parent=None):
        super().__init__(parent)
        self.platform = platform

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        #main label
        self.fileButton = QPushButton(text)
        self.fileButton.setStyleSheet(
            "QPushButton { background-color: #404040; color: #c8c8c8; "
            "border: 1px solid #555555; border-radius: 4px; padding: 8px 18px; }"
            "QPushButton:hover { border-color: #777777; }"
        )
        self.fileButton.clicked.connect(self.selectFile)
        layout.addWidget(self.fileButton)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(30)

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
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation
            ),
            "CSV Files (*.csv)"
        )

        if not filePath:
            return

        fileName = QFileInfo(filePath).fileName()
        try:
            # Platform exports use different delimiters, so let pandas infer it.
            dataTable = pd.read_csv(filePath, sep=None, engine="python")
        except Exception:
            self.selectionFailed.emit(fileName)
            return

        self.selected.emit(fileName, dataTable)


class CurrencySelectorDialog(QDialog):
    """Compact currency chooser with a visible current selection."""

    currencySelected = Signal(str, str)

    def __init__(self, currencies, currentCode="USD", parent=None):
        super().__init__(parent)
        self.currencies = currencies
        self.setWindowTitle("Currency")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(380, 440)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        headerLayout = QHBoxLayout()
        title = QLabel("Currency")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        closeButton = QPushButton("\u2715")
        closeButton.setFixedSize(26, 26)
        closeButton.clicked.connect(self.reject)
        headerLayout.addWidget(title)
        headerLayout.addStretch(1)
        headerLayout.addWidget(closeButton)

        self.currencyList = QListWidget()
        self.currencyList.setStyleSheet(
            "QListWidget { background-color: #242424; border: 1px solid #555555; }"
            "QListWidget::item { color: #d0d0d0; padding: 7px; }"
            "QListWidget::item:selected { background-color: #218739; color: white; }"
        )

        currentItem = None
        for currency in currencies:
            selectorText = currency["code"] if currency["sharedSymbol"] else currency["symbol"]
            itemText = (
                f"{selectorText}  {currency['name']} ({currency['code']})"
            )
            if currency["code"] == currentCode:
                itemText = f"\u2713  {itemText}"
            item = QListWidgetItem(itemText)
            item.setData(Qt.ItemDataRole.UserRole, currency["code"])
            self.currencyList.addItem(item)
            if currency["code"] == currentCode:
                currentItem = item

        if currentItem is not None:
            self.currencyList.setCurrentItem(currentItem)
            self.currencyList.scrollToItem(currentItem)

        self.currencyList.itemClicked.connect(self._selectCurrency)
        layout.addLayout(headerLayout)
        layout.addWidget(self.currencyList)

        self.setStyleSheet(
            "QDialog { background-color: #303030; border: 1px solid #666666; }"
            "QLabel { color: #ffffff; }"
        )

    def _selectCurrency(self, item):
        currencyCode = item.data(Qt.ItemDataRole.UserRole)
        currency = next(
            value for value in self.currencies if value["code"] == currencyCode
        )
        self.currencySelected.emit(currency["code"], currency["symbol"])
        self.accept()


class TierFilterPanel(QFrame):
    """Filter controls associated with one selected subscription tier."""

    _currencies = None

    def __init__(self, tierName, parent=None):
        super().__init__(parent)
        self.tierName = tierName
        self.currencyCode = "USD"
        self.currencies = self._worldCurrencies()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            "QFrame { background-color: #303030; border: 1px solid #4f4f4f; "
            "border-radius: 4px; } QLabel, QCheckBox { border: none; color: #c8c8c8; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(8)

        tierHeader = QLabel(tierName)
        tierHeader.setStyleSheet("font-weight: bold; color: #ffffff;")
        layout.addWidget(tierHeader)

        controlsLayout = QGridLayout()
        controlsLayout.setContentsMargins(0, 0, 0, 0)
        controlsLayout.setHorizontalSpacing(8)
        controlsLayout.setVerticalSpacing(7)

        self.currentlySubbedCheck = QCheckBox("Currently subbed")
        self.currentlySubbedCheck.setChecked(True)
        controlsLayout.addWidget(self.currentlySubbedCheck, 0, 0, 1, 3)

        self.subbedSinceCheck = QCheckBox("Subbed Since")
        self.subbedSinceInput = QDateEdit()
        self.subbedSinceInput.setCalendarPopup(True)
        self.subbedSinceInput.setDisplayFormat("yyyy-MM-dd")
        self.subbedSinceInput.setDate(QDate.currentDate())
        self.subbedSinceInput.setStyleSheet(
            "QDateEdit { background-color: #f4f4f4; color: #202020; "
            "border: 1px solid #777777; padding: 4px; }"
            "QDateEdit:disabled { background-color: #555555; color: #999999; "
            "border-color: #666666; }"
        )
        self.subbedSinceInput.setEnabled(False)
        self.subbedSinceCheck.toggled.connect(self.subbedSinceInput.setEnabled)
        controlsLayout.addWidget(self.subbedSinceCheck, 1, 0)
        controlsLayout.addWidget(self.subbedSinceInput, 1, 1, 1, 2)

        self.grossPayCheck = QCheckBox("Gross pay")
        self.currencyButton = QPushButton(self._currencySymbol("USD"))
        self.currencyButton.setToolTip("USD")
        self.currencyButton.setFixedWidth(48)
        self.currencyButton.setStyleSheet(
            "QPushButton { background-color: #f4f4f4; color: #202020; "
            "border: 1px solid #777777; padding: 4px; }"
            "QPushButton:disabled { background-color: #555555; color: #999999; "
            "border-color: #666666; }"
        )
        self.currencyButton.setEnabled(False)
        self.currencyButton.clicked.connect(self._showCurrencySelector)

        self.grossPayInput = QDoubleSpinBox()
        self.grossPayInput.setLocale(QLocale.c())
        self.grossPayInput.setDecimals(2)
        self.grossPayInput.setRange(0.00, 999999999.99)
        self.grossPayInput.setValue(0.00)
        self.grossPayInput.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.grossPayInput.setStyleSheet(
            "QDoubleSpinBox { background-color: #f4f4f4; color: #202020; "
            "border: 1px solid #777777; padding: 4px; }"
            "QDoubleSpinBox:disabled { background-color: #555555; color: #999999; "
            "border-color: #666666; }"
        )
        self.grossPayInput.setEnabled(False)
        self.grossPayCheck.toggled.connect(self.currencyButton.setEnabled)
        self.grossPayCheck.toggled.connect(self.grossPayInput.setEnabled)
        controlsLayout.addWidget(self.grossPayCheck, 2, 0)
        controlsLayout.addWidget(self.currencyButton, 2, 1)
        controlsLayout.addWidget(self.grossPayInput, 2, 2)
        controlsLayout.setColumnStretch(2, 1)

        layout.addLayout(controlsLayout)

    def _showCurrencySelector(self):
        selector = CurrencySelectorDialog(
            self.currencies, currentCode=self.currencyCode, parent=self
        )
        selector.currencySelected.connect(self._setCurrency)
        selector.exec()

    def _setCurrency(self, currencyCode, symbol):
        self.currencyCode = currencyCode
        self.currencyButton.setText(symbol)
        self.currencyButton.setToolTip(currencyCode)

    def _currencySymbol(self, currencyCode):
        currency = next(
            (value for value in self.currencies if value["code"] == currencyCode),
            None,
        )
        return currency["symbol"] if currency else currencyCode

    @classmethod
    def _worldCurrencies(cls):
        if cls._currencies is not None:
            return cls._currencies

        currenciesByCode = {}
        locales = QLocale.matchingLocales(
            QLocale.Language.AnyLanguage,
            QLocale.Script.AnyScript,
            QLocale.Country.AnyCountry,
        )
        for locale in locales:
            code = locale.currencySymbol(
                QLocale.CurrencySymbolFormat.CurrencyIsoCode
            ).strip()
            if len(code) != 3 or not code.isalpha() or code == "XXX":
                continue
            symbol = locale.currencySymbol(
                QLocale.CurrencySymbolFormat.CurrencySymbol
            ).strip() or code
            name = locale.currencySymbol(
                QLocale.CurrencySymbolFormat.CurrencyDisplayName
            ).strip() or code
            currency = {"code": code, "symbol": symbol, "name": name}
            if code not in currenciesByCode or locale.language() == QLocale.Language.English:
                currenciesByCode[code] = currency

        # Qt's locale database normally supplies USD; keep a safe UI fallback.
        currenciesByCode.setdefault(
            "USD", {"code": "USD", "symbol": "$", "name": "US Dollar"}
        )
        symbolCounts = Counter(
            currency["symbol"] for currency in currenciesByCode.values()
        )
        cls._currencies = []
        for code in sorted(currenciesByCode):
            currency = currenciesByCode[code]
            currency["sharedSymbol"] = symbolCounts[currency["symbol"]] > 1
            cls._currencies.append(currency)
        return cls._currencies



class platformWidget(QFrame):
    TIER_PANEL_SCROLL_MAX_HEIGHT = 260
    NORMAL_STYLE = (
        "QFrame#platformWidget { background-color: #262626; "
        "border: 1px solid #555555; border-radius: 5px; }"
    )
    INVALID_STYLE = (
        "QFrame#platformWidget { background-color: #6b2020; "
        "border: 1px solid #d05a5a; border-radius: 5px; }"
    )

    def __init__(self, platform):
        super().__init__()
        self.platform = platform
        self.platformDataframe = None
        self.observedTiers = set()
        self.tierPanels = {}
        self.platformConfig = self._loadPlatformConfig(platform)

        self.setObjectName("platformWidget")
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setHorizontalSpacing(18)
        self.setStyleSheet(self.NORMAL_STYLE)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)
        
        self.setupUI()
    

    def setupUI(self):
        # Before a file is loaded, center the platform prompt and file button.
        self.fileAreaWidget = QWidget()
        self.fileAreaLayout = QVBoxLayout(self.fileAreaWidget)
        self.fileAreaLayout.setContentsMargins(0, 0, 0, 0)
        self.fileAreaLayout.setSpacing(6)

        platformDisplayName = self.platformConfig.get("name", self.platform.title())
        self.platformOptionsLabel = QLabel(f"{platformDisplayName} Options")
        self.platformOptionsLabel.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #c8c8c8; "
            "padding-bottom: 4px;"
        )
        self.layout.addWidget(self.platformOptionsLabel, 0, 0, 1, 2)

        self.filePromptLabel = QLabel(f"{platformDisplayName} CSV File")
        self.filePromptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filePromptLabel.setStyleSheet("font-weight: bold; color: #c8c8c8;")

        self.subFileWidget = QWidget()
        self.subFileLayout = QStackedLayout(self.subFileWidget)
        self.subFileLayout.setContentsMargins(0, 0, 0, 0)

        self.fileDialogue = FileDialogueWidget(self.platform, "Select File")
        self.fileDialogue.selected.connect(self.selectedFile)
        self.fileDialogue.selectionFailed.connect(self.invalidFile)

        self.fileChip = FileChipWidget("No file selected")
        self.fileChip.removed.connect(self.clearSelectedFile)

        self.subFileLayout.addWidget(self.fileDialogue)
        self.subFileLayout.addWidget(self.fileChip)
        self.subFileLayout.setCurrentIndex(0)

        self.invalidLabel = QLabel("INVALID FILE")
        self.invalidLabel.setStyleSheet(
            "color: #ffffff; font-weight: bold; padding-top: 4px;"
        )
        self.invalidLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalidLabel.hide()

        self.fileAreaLayout.addWidget(
            self.filePromptLabel, 0, Qt.AlignmentFlag.AlignHCenter
        )
        self.fileAreaLayout.addWidget(
            self.subFileWidget, 0, Qt.AlignmentFlag.AlignHCenter
        )
        self.fileAreaLayout.addWidget(
            self.invalidLabel, 0, Qt.AlignmentFlag.AlignHCenter
        )
        self._positionFileArea(centered=True)

        # The tier submenu appears only after the selected file is validated.
        self.optionsWidget = QWidget()
        self.optionsLayout = QVBoxLayout(self.optionsWidget)
        self.optionsLayout.setContentsMargins(0, 0, 0, 0)
        self.optionsLayout.setSpacing(8)
        self.optionsLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Keep the selector controls in their own fixed section so adding tier
        # panels can never insert space between the label and dropdown.
        self.tierControlsWidget = QWidget()
        self.tierControlsWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        tierControlsLayout = QVBoxLayout(self.tierControlsWidget)
        tierControlsLayout.setContentsMargins(0, 0, 0, 0)
        tierControlsLayout.setSpacing(6)
        tierLabel = QLabel("Subscription Tier")
        tierLabel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        tierLabel.setStyleSheet("font-weight: bold; color: #c8c8c8;")
        self.tierNameSelector = ChipSelector([], placeholderText="All tiers")
        self.tierNameSelector.selectionChanged.connect(self._syncTierPanels)
        tierControlsLayout.addWidget(tierLabel)
        tierControlsLayout.addWidget(self.tierNameSelector)

        # Selected-tier panels live in a separately scrolling lower section.
        self.tierPanelContainer = QWidget()
        self.tierPanelLayout = QVBoxLayout(self.tierPanelContainer)
        self.tierPanelLayout.setContentsMargins(0, 0, 0, 0)
        self.tierPanelLayout.setSpacing(8)
        self.tierPanelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.tierPanelScrollArea = QScrollArea()
        self.tierPanelScrollArea.setWidgetResizable(True)
        self.tierPanelScrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.tierPanelScrollArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.tierPanelScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.tierPanelScrollArea.setWidget(self.tierPanelContainer)
        self.tierPanelScrollArea.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )
        self.tierPanelScrollArea.hide()

        self.optionsLayout.addWidget(self.tierControlsWidget)
        self.optionsLayout.addWidget(self.tierPanelScrollArea)
        self.optionsWidget.hide()

        self.layout.addWidget(self.optionsWidget, 1, 1, 2, 1)
        self.layout.setColumnStretch(1, 1)

    def selectedFile(self, fileName, dataTable):
        tierColumn = self._validatedTierColumn(dataTable)
        if tierColumn is None:
            self.invalidFile(fileName)
            return

        self.platformDataframe = dataTable
        self.observedTiers = {
            str(tier).strip()
            for tier in dataTable[tierColumn].dropna().tolist()
            if str(tier).strip()
        }
        print(
            f"Selected file for {self.platform}: {fileName}; "
            f"observed tiers: {self.observedTiers}"
        )
        self.fileChip.setText(fileName)
        self.subFileLayout.setCurrentIndex(1)
        self.filePromptLabel.hide()
        self.invalidLabel.hide()
        self.setStyleSheet(self.NORMAL_STYLE)
        self._positionFileArea(centered=False)

        self._clearTierPanels()
        self.tierNameSelector.setOptions(
            sorted(self.observedTiers, key=str.casefold), clearSelection=True
        )
        self.optionsWidget.show()

    def invalidFile(self, fileName):
        print(f"Invalid file for {self.platform}: {fileName}")
        self.platformDataframe = None
        self.observedTiers.clear()
        self.subFileLayout.setCurrentIndex(0)
        self.filePromptLabel.show()
        self.invalidLabel.show()
        self.optionsWidget.hide()
        self._positionFileArea(centered=True)
        self.tierNameSelector.setOptions([], clearSelection=True)
        self._clearTierPanels()
        self.setStyleSheet(self.INVALID_STYLE)

    def clearSelectedFile(self, _fileName=None):
        self.platformDataframe = None
        self.observedTiers.clear()
        self.subFileLayout.setCurrentIndex(0)
        self.filePromptLabel.show()
        self.invalidLabel.hide()
        self.optionsWidget.hide()
        self._positionFileArea(centered=True)
        self.tierNameSelector.setOptions([], clearSelection=True)
        self._clearTierPanels()
        self.setStyleSheet(self.NORMAL_STYLE)

    def _validatedTierColumn(self, dataTable):
        if not isinstance(dataTable, pd.DataFrame):
            return None

        normalisedColumns = {
            self._normaliseColumn(column): column for column in dataTable.columns
        }
        requiredKeys = ("nameColName", "tierColName", "dateSubbedColName")
        requiredColumns = [self.platformConfig.get(key, "") for key in requiredKeys]
        if not all(
            self._normaliseColumn(column) in normalisedColumns
            for column in requiredColumns
        ):
            return None

        return normalisedColumns[
            self._normaliseColumn(self.platformConfig["tierColName"])
        ]

    @staticmethod
    def _normaliseColumn(column):
        return str(column).strip().upper().replace(" ", "_")

    @staticmethod
    def _loadPlatformConfig(platform):
        with PLATFORM_CONFIG_PATH.open(encoding="utf-8") as configFile:
            platformConfigs = json.load(configFile)
        if platform not in platformConfigs:
            raise ValueError(f"Unsupported platform: {platform}")
        return platformConfigs[platform]

    def _syncTierPanels(self, selectedTiers):
        selectedSet = set(selectedTiers)
        for tier in list(self.tierPanels):
            if tier not in selectedSet:
                panel = self.tierPanels.pop(tier)
                self.tierPanelLayout.removeWidget(panel)
                panel.setParent(None)
                panel.deleteLater()

        for tier in selectedTiers:
            if tier in self.tierPanels:
                continue
            panel = TierFilterPanel(tier)
            self.tierPanelLayout.addWidget(panel)
            self.tierPanels[tier] = panel

        self._updateTierPanelArea()

    def _clearTierPanels(self):
        for panel in self.tierPanels.values():
            self.tierPanelLayout.removeWidget(panel)
            panel.setParent(None)
            panel.deleteLater()
        self.tierPanels.clear()
        self._updateTierPanelArea()

    def _updateTierPanelArea(self):
        if not self.tierPanels:
            self.tierPanelContainer.setMinimumHeight(0)
            self.tierPanelScrollArea.hide()
            return

        margins = self.tierPanelLayout.contentsMargins()
        panelHeights = [panel.sizeHint().height() for panel in self.tierPanels.values()]
        contentHeight = (
            sum(panelHeights)
            + self.tierPanelLayout.spacing() * (len(panelHeights) - 1)
            + margins.top()
            + margins.bottom()
        )
        self.tierPanelContainer.setMinimumHeight(contentHeight)
        viewportHeight = min(contentHeight, self.TIER_PANEL_SCROLL_MAX_HEIGHT)
        self.tierPanelScrollArea.setFixedHeight(max(1, viewportHeight))
        self.tierPanelScrollArea.show()

    def compileNames(self, applyPlatformHeader=True):
        """Return names matching the selected tiers and their enabled filters."""
        if self.platformDataframe is None:
            return []

        columnMap = {
            self._normaliseColumn(column): column
            for column in self.platformDataframe.columns
        }
        tierColumn = self._columnForConfigKey("tierColName", columnMap)
        nameColumn = self._columnForConfigKey("nameColName", columnMap)
        if tierColumn is None or nameColumn is None:
            return []

        selectedTiers = self.tierNameSelector.selectedItems()
        tiersToCompile = selectedTiers or sorted(self.observedTiers, key=str.casefold)
        compiledNames = []

        for tier in tiersToCompile:
            tierRows = self.platformDataframe[
                self.platformDataframe[tierColumn].astype(str).str.strip() == tier
            ].copy()
            filters = self.tierPanels.get(tier)

            currentlySubbed = (
                filters.currentlySubbedCheck.isChecked() if filters else True
            )
            if currentlySubbed:
                statusColumn = self._columnForConfigKey("subStateName", columnMap)
                activeLabel = self.platformConfig.get("subStateActiveLabel", "").strip()
                if statusColumn is not None and activeLabel:
                    tierRows = tierRows[
                        tierRows[statusColumn].astype(str).str.strip().str.casefold()
                        == activeLabel.casefold()
                    ]

            if filters and filters.subbedSinceCheck.isChecked():
                dateColumn = self._columnForConfigKey("dateSubbedColName", columnMap)
                if dateColumn is not None:
                    selectedDate = pd.Timestamp(
                        filters.subbedSinceInput.date().toPython()
                    )
                    subscriptionDates = pd.to_datetime(
                        tierRows[dateColumn], errors="coerce"
                    )
                    tierRows = tierRows[subscriptionDates.dt.normalize() <= selectedDate]

            if filters and filters.grossPayCheck.isChecked():
                grossColumn = self._columnForConfigKey("grossColName", columnMap)
                if grossColumn is not None:
                    grossValues = pd.to_numeric(
                        tierRows[grossColumn]
                        .astype(str)
                        .str.replace(r"[^0-9.\-]", "", regex=True),
                        errors="coerce",
                    )
                    tierRows = tierRows[
                        grossValues >= filters.grossPayInput.value()
                    ]

            for name in tierRows[nameColumn].dropna():
                cleanName = str(name).strip()
                if not cleanName:
                    continue
                if applyPlatformHeader:
                    header = self.platformConfig.get("header", "").strip()
                    cleanName = f"{header}-{cleanName}" if header else cleanName
                compiledNames.append(cleanName)

        return compiledNames

    def _columnForConfigKey(self, configKey, columnMap):
        configuredColumn = self.platformConfig.get(configKey, "").strip()
        if not configuredColumn:
            return None
        return columnMap.get(self._normaliseColumn(configuredColumn))

    def _positionFileArea(self, centered):
        self.layout.removeWidget(self.fileAreaWidget)
        if centered:
            self.layout.addWidget(
                self.fileAreaWidget,
                1,
                0,
                2,
                2,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            )
        else:
            self.layout.addWidget(
                self.fileAreaWidget,
                1,
                0,
                2,
                1,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fileChip.setDisplayWidth(self.width() * 0.10)
