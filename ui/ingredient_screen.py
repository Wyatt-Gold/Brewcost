# Ingredient screen: lets the user add ingredients to the database, edit them, and delete them.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
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

        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.cost_input = QLineEdit()
        self.unit_input = QLineEdit()

        form = QFormLayout()
        form.addRow("Name", self.name_input)
        form.addRow("Category", self.category_input)
        form.addRow("Cost per Unit", self.cost_input)
        form.addRow("Unit", self.unit_input)

        self.add_button = QPushButton("Add")
        self.update_button = QPushButton("Update Selected")
        self.delete_button = QPushButton("Delete Selected")
        self.clear_button = QPushButton("Clear Form")

        self.add_button.clicked.connect(self._handle_add)
        self.update_button.clicked.connect(self._handle_update)
        self.delete_button.clicked.connect(self._handle_delete)
        self.clear_button.clicked.connect(self._clear_form)

        button_row = QHBoxLayout()
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.update_button)
        button_row.addWidget(self.delete_button)
        button_row.addWidget(self.clear_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(form)
        layout.addLayout(button_row)
        self.setLayout(layout)

        self.refresh()

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
        if not selected_rows:
            return
        row = selected_rows[0].row()
        self._selected_id = self.table.item(row, 0).data(Qt.UserRole)
        self.name_input.setText(self.table.item(row, 0).text())
        self.category_input.setText(self.table.item(row, 1).text())
        self.cost_input.setText(self.table.item(row, 2).text())
        self.unit_input.setText(self.table.item(row, 3).text())

    def _read_form(self):
        name = self.name_input.text().strip()
        category = self.category_input.text().strip()
        unit = self.unit_input.text().strip()
        cost_text = self.cost_input.text().strip()

        if not name or not unit or not cost_text:
            QMessageBox.warning(self, "Missing fields", "Name, cost per unit, and unit are required.")
            return None
        try:
            cost = float(cost_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid cost", "Cost per unit must be a number.")
            return None
        return name, category, cost, unit

    def _handle_add(self):
        values = self._read_form()
        if values is None:
            return
        ingredient_repository.add_ingredient(*values)
        self._clear_form()
        self.refresh()

    def _handle_update(self):
        if self._selected_id is None:
            QMessageBox.information(self, "No selection", "Select a row to update first.")
            return
        values = self._read_form()
        if values is None:
            return
        ingredient_repository.update_ingredient(self._selected_id, *values)
        self._clear_form()
        self.refresh()

    def _handle_delete(self):
        if self._selected_id is None:
            QMessageBox.information(self, "No selection", "Select a row to delete first.")
            return
        ingredient_repository.delete_ingredient(self._selected_id)
        self._clear_form()
        self.refresh()

    def _clear_form(self):
        self._selected_id = None
        self.table.clearSelection()
        self.name_input.clear()
        self.category_input.clear()
        self.cost_input.clear()
        self.unit_input.clear()
