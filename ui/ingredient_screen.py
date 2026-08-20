# Ingredient screen: lets the user add ingredients to the database, edit them, and delete them.

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import ingredient_repository

COLUMNS = ["Name", "Category", "Cost per Unit", "Unit"]

# Opacity of the dimming overlay shown behind the add/update popup.
SHADE_OPACITY = "rgba(0, 0, 0, 90)"


class IngredientFormDialog(QDialog):
    # Modal popup for adding or updating a single ingredient. Stays centered
    # on, and locked to, whatever window it was opened from.
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self._anchor = parent.window()
        self._anchor.installEventFilter(self)

        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.cost_input = QLineEdit()
        self.unit_input = QLineEdit()

        self.name_input.textChanged.connect(self._update_confirm_enabled)
        self.cost_input.textChanged.connect(self._update_confirm_enabled)
        self.unit_input.textChanged.connect(self._update_confirm_enabled)

        form = QFormLayout()
        form.addRow("Name", self.name_input)
        form.addRow("Category", self.category_input)
        form.addRow("Cost per Unit", self.cost_input)
        form.addRow("Unit", self.unit_input)

        self.confirm_button = QPushButton("Add")
        self.cancel_button = QPushButton("Cancel")
        self.confirm_button.clicked.connect(self._handle_confirm)
        self.cancel_button.clicked.connect(self.reject)
        self.values = None

        button_row = QHBoxLayout()
        button_row.addWidget(self.confirm_button)
        button_row.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(button_row)
        self.setLayout(layout)

    def set_mode(self, mode, name="", category="", cost="", unit=""):
        self.mode = mode
        self.setWindowTitle("Update Ingredient" if mode == "update" else "Add Ingredient")
        self.confirm_button.setText("Update" if mode == "update" else "Add")
        self.name_input.setText(name)
        self.category_input.setText(category)
        self.cost_input.setText(cost)
        self.unit_input.setText(unit)
        self._update_confirm_enabled()

    def _handle_confirm(self):
        name = self.name_input.text().strip()
        category = self.category_input.text().strip()
        unit = self.unit_input.text().strip()
        cost_text = self.cost_input.text().strip()

        if not name or not unit or not cost_text:
            QMessageBox.warning(self, "Missing fields", "Name, cost per unit, and unit are required.")
            return
        try:
            cost = float(cost_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid cost", "Cost per unit must be a number.")
            return

        self.values = (name, category, cost, unit)
        self.accept()

    def _update_confirm_enabled(self):
        ready = bool(
            self.name_input.text().strip()
            and self.cost_input.text().strip()
            and self.unit_input.text().strip()
        )
        self.confirm_button.setEnabled(ready)

    def showEvent(self, event):
        super().showEvent(event)
        self._recenter()

    def eventFilter(self, watched, event):
        if watched is self._anchor and event.type() in (QEvent.Move, QEvent.Resize):
            self._recenter()
        return super().eventFilter(watched, event)

    def _recenter(self):
        anchor_geometry = self._anchor.frameGeometry()
        center = anchor_geometry.center()
        self.adjustSize()
        self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)

    def closeEvent(self, event):
        self._anchor.removeEventFilter(self)
        super().closeEvent(event)


class IngredientScreen(QWidget):
    def __init__(self):
        super().__init__()
        self._selected_id = None

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_row_selected)

        self.add_open_button = QPushButton("Add Ingredient")
        self.update_open_button = QPushButton("Update Selected")
        self.delete_button = QPushButton("Delete Selected")

        self.add_open_button.clicked.connect(self._open_add_form)
        self.update_open_button.clicked.connect(self._open_update_form)
        self.delete_button.clicked.connect(self._handle_delete)

        self.update_open_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        button_row = QHBoxLayout()
        button_row.addWidget(self.add_open_button)
        button_row.addWidget(self.update_open_button)
        button_row.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_row)
        self.setLayout(layout)

        # Dimming overlay shown behind the popup dialog. Parented to this
        # screen so it only shades the ingredients tab, not the whole app.
        self.shade = QWidget(self)
        self.shade.setStyleSheet(f"background-color: {SHADE_OPACITY};")
        self.shade.hide()

        self.refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.shade.setGeometry(self.rect())

    def refresh(self):
        ingredients = ingredient_repository.get_all_ingredients()
        self.table.setRowCount(len(ingredients))
        for row, ingredient in enumerate(ingredients):
            self.table.setItem(row, 0, QTableWidgetItem(ingredient.name))
            self.table.setItem(row, 1, QTableWidgetItem(ingredient.category or ""))
            self.table.setItem(row, 2, QTableWidgetItem(f"{ingredient.cost_per_unit:.4f}"))
            self.table.setItem(row, 3, QTableWidgetItem(ingredient.unit))
            self.table.item(row, 0).setData(Qt.UserRole, ingredient.id)

    def _on_row_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        has_selection = bool(selected_rows)
        self.update_open_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        if not has_selection:
            self._selected_id = None
            return
        row = selected_rows[0].row()
        self._selected_id = self.table.item(row, 0).data(Qt.UserRole)

    def _open_add_form(self):
        dialog = IngredientFormDialog(self)
        dialog.set_mode("add")
        self._run_dialog(dialog)

    def _open_update_form(self):
        if self._selected_id is None:
            return
        row = self.table.selectionModel().selectedRows()[0].row()
        dialog = IngredientFormDialog(self)
        dialog.set_mode(
            "update",
            name=self.table.item(row, 0).text(),
            category=self.table.item(row, 1).text(),
            cost=self.table.item(row, 2).text(),
            unit=self.table.item(row, 3).text(),
        )
        self._run_dialog(dialog)

    def _run_dialog(self, dialog):
        self.shade.raise_()
        self.shade.show()
        try:
            if dialog.exec() == QDialog.Accepted and dialog.values is not None:
                if dialog.mode == "add":
                    ingredient_repository.add_ingredient(*dialog.values)
                else:
                    ingredient_repository.update_ingredient(self._selected_id, *dialog.values)
                self.refresh()
        finally:
            self.shade.hide()
            self.table.clearSelection()
            self._selected_id = None

    def _handle_delete(self):
        if self._selected_id is None:
            QMessageBox.information(self, "No selection", "Select a row to delete first.")
            return
        ingredient_repository.delete_ingredient(self._selected_id)
        self.refresh()
        self.table.clearSelection()
        self._selected_id = None
