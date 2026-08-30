# Small reusable UI widgets shared across screens.

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton

# Muted, fully opaque tints rather than saturated alert colors.
COLORS = {
    "success": "#a5d6a7",
    "error": "#ef9a9a",
    "warning": "#ffe082",
}

GROW_DURATION_MS = 220


class Toast(QFrame):
    # Centered message overlay that grows into place and stays until the
    # user dismisses it with the close button. Construct it and forget it.
    def __init__(self, parent, header, body, kind):
        super().__init__(parent)
        color = COLORS[kind]
        self.setStyleSheet(
            f"""
            QFrame {{ background-color: {color}; border-radius: 10px; }}
            QLabel {{ color: #212121; background: transparent; }}
            QPushButton {{
                color: #212121; background: transparent; border: none;
                font-weight: bold; font-size: 20px;
            }}
            """
        )

        header_label = QLabel(header)
        header_label.setWordWrap(True)
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        body_label = QLabel(body)
        body_label.setWordWrap(True)
        body_label.setStyleSheet("font-size: 12px;")

        close_button = QPushButton("✕")
        close_button.setFixedSize(26, 26)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.deleteLater)

        # Grid so the close button shares the header's row (top-right corner)
        # instead of reserving a whole row of its own above the text.
        layout = QGridLayout(self)
        layout.setContentsMargins(16, 10, 10, 16)
        layout.setHorizontalSpacing(8)
        layout.addWidget(header_label, 0, 0)
        layout.addWidget(close_button, 0, 1, Qt.AlignTop | Qt.AlignRight)
        layout.addWidget(body_label, 1, 0, 1, 2)

        self.setMaximumWidth(int(parent.width() * 0.8))
        self.adjustSize()
        self._animate_in()

    def _animate_in(self):
        parent_rect = self.parent().rect()
        target_rect = QRect(0, 0, self.width(), self.height())
        target_rect.moveCenter(parent_rect.center())

        # Stack below any other toasts already showing, instead of overlapping.
        others = [w for w in self.parent().findChildren(Toast) if w is not self and w.isVisible()]
        if others:
            target_rect.moveTop(target_rect.top() + sum(w.height() + 12 for w in others))

        start_rect = QRect(target_rect)
        start_rect.setWidth(max(1, int(target_rect.width() * 0.3)))
        start_rect.setHeight(max(1, int(target_rect.height() * 0.3)))
        start_rect.moveCenter(target_rect.center())

        self.setGeometry(start_rect)
        self.show()
        self.raise_()

        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(GROW_DURATION_MS)
        self._animation.setStartValue(start_rect)
        self._animation.setEndValue(target_rect)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.start()
