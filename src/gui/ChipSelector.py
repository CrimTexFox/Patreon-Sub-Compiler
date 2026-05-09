# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton,
                               QLayout, QSizePolicy, QMenu)
from PySide6.QtCore import Signal, QRect, QPoint, QSize, Qt
from PySide6.QtGui import QPainter


class FlowLayout(QLayout):
    """Layout that arranges widgets left-to-right, wrapping to the next row when full.
    Based on the Qt FlowLayout example."""

    def __init__(self, parent=None, margin=-1, hSpacing=4, vSpacing=4):
        super().__init__(parent)
        self._items = []
        self._hSpacing = hSpacing
        self._vSpacing = vSpacing
        if margin >= 0:
            self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._doLayout(QRect(0, 0, width, 0), test=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, test=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _doLayout(self, rect, test):
        margins = self.contentsMargins()
        effective = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        x = effective.x()
        y = effective.y()
        rowHeight = 0

        for item in self._items:
            spaceX = self._hSpacing
            spaceY = self._vSpacing
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effective.right() and rowHeight > 0:
                x = effective.x()
                y = y + rowHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                rowHeight = 0
            if not test:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            rowHeight = max(rowHeight, item.sizeHint().height())

        return y + rowHeight - rect.y() + margins.bottom()


class ChipWidget(QWidget):
    """A small tag/chip with a label and an X button to remove it."""
    removed = Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 2, 2)
        layout.setSpacing(4)

        label = QLabel(text)
        removeBtn = QPushButton("\u2715")
        removeBtn.setFixedSize(18, 18)
        removeBtn.setStyleSheet("QPushButton { border: none; font-weight: bold; }")
        removeBtn.clicked.connect(lambda: self.removed.emit(self.text))

        layout.addWidget(label)
        layout.addWidget(removeBtn)

        self.setObjectName("chip")
        self.setStyleSheet(
            "#chip { background-color: #424242; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        from PySide6.QtWidgets import QStyleOption
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(self.style().PrimitiveElement.PE_Widget, opt, p, self)


class ChipSelector(QWidget):
    """A dropdown-style box that shows selected options as chips inside it.
    Clicking the dropdown arrow shows a menu of available options.
    The box grows vertically as more chips are added."""
    selectionChanged = Signal(list)
    itemAdded = Signal(str)
    itemRemoved = Signal(str)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self._allOptions = list(options)
        self._selected = []

        # Main horizontal layout: chip area + dropdown button
        self._outerLayout = QHBoxLayout(self)
        self._outerLayout.setContentsMargins(4, 4, 4, 4)
        self._outerLayout.setSpacing(0)

        # Chip flow area
        self._chipContainer = QWidget()
        self._chipLayout = FlowLayout(self._chipContainer, margin=2, hSpacing=4, vSpacing=4)
        self._outerLayout.addWidget(self._chipContainer, 1)

        # Dropdown arrow label (visual only)
        self._dropLabel = QLabel("\u25BC")
        self._dropLabel.setFixedWidth(24)
        self._dropLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._outerLayout.addWidget(self._dropLabel, 0, Qt.AlignmentFlag.AlignTop)

        # Style the whole widget
        self.setObjectName("chipSelector")
        self.setStyleSheet(
            "#chipSelector { border: 1px solid #292929; border-radius: 3px; background-color: #1f1f1f; }"
        )
        self.setMinimumHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        from PySide6.QtWidgets import QStyleOption
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(self.style().PrimitiveElement.PE_Widget, opt, p, self)

    def mousePressEvent(self, event):
        self._showMenu()

    def _showMenu(self):
        menu = QMenu(self)
        menu.setMinimumWidth(self.width())
        available = [opt for opt in self._allOptions if opt not in self._selected]
        if not available:
            action = menu.addAction("(no options)")
            action.setEnabled(False)
        else:
            for opt in available:
                menu.addAction(opt)
        action = menu.exec(self.mapToGlobal(self.rect().bottomLeft()))
        if action and action.text() in self._allOptions:
            self._selectOption(action.text())

    def _selectOption(self, text):
        self._selected.append(text)
        chip = ChipWidget(text)
        chip.removed.connect(self._removeChip)
        self._chipLayout.addWidget(chip)
        self._updateSize()
        self.itemAdded.emit(text)
        self.selectionChanged.emit(self._selected)

    def _removeChip(self, text):
        chip = self.sender()
        self._chipLayout.removeWidget(chip)
        chip.setParent(None)
        chip.deleteLater()
        self._selected.remove(text)
        self._updateSize()
        self.itemRemoved.emit(text)
        self.selectionChanged.emit(self._selected)

    def _updateSize(self):
        """Recalculate height so the box grows/shrinks with chip count."""
        self._chipContainer.updateGeometry()
        self.updateGeometry()

    def selectedItems(self):
        return list(self._selected)
