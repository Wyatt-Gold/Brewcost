# Calculator screen: lets the user add ingredients and sizes, enter quantities, and see the total cost for each size.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import ingredient_repository

INGREDIENT_COLUMN = 0
TOTAL_ROW_LABEL = "Total Cost"


class CalculatorScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.ingredient_combo = QComboBox()
        self.add_ingredient_button = QPushButton("Add Ingredient Row")
        self.add_size_button = QPushButton("Add Size Column")
        self.remove_row_button = QPushButton("Remove Selected Row")

        self.add_ingredient_button.clicked.connect(self._handle_add_ingredient_row)
        self.add_size_button.clicked.connect(self._handle_add_size_column)
        self.remove_row_button.clicked.connect(self._handle_remove_row)

        controls = QHBoxLayout()
        controls.addWidget(self.ingredient_combo)
        controls.addWidget(self.add_ingredient_button)
        controls.addWidget(self.add_size_button)
        controls.addWidget(self.remove_row_button)

        self.table = QTableWidget(1, 2)
        self.table.setHorizontalHeaderLabels(["Ingredient", "Size 1"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._set_total_row_label()
        self.table.itemChanged.connect(self._handle_item_changed)

        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.refresh_ingredient_choices()

    # -- ingredient dropdown -------------------------------------------------

    def refresh_ingredient_choices(self):
        """Re-pull the saved ingredient list. Call this whenever this screen becomes visible,
        since ingredients may have changed on the Ingredient Manager screen."""
        self.ingredient_combo.clear()
        for ingredient in ingredient_repository.get_all_ingredients():
            label = f"{ingredient.name} ({ingredient.unit})"
            self.ingredient_combo.addItem(label, ingredient)

    # -- row/column setup -----------------------------------------------------

    def _total_row_index(self):
        return self.table.rowCount() - 1

    def _set_total_row_label(self):
        row = self._total_row_index()
        item = QTableWidgetItem(TOTAL_ROW_LABEL)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, INGREDIENT_COLUMN, item)

    def _handle_add_ingredient_row(self):
        ingredient = self.ingredient_combo.currentData()
        if ingredient is None:
            QMessageBox.information(self, "No ingredients", "Add ingredients on the Ingredients tab first.")
            return

        total_row = self._total_row_index()
        self.table.insertRow(total_row)
        new_row = total_row

        name_item = QTableWidgetItem(f"{ingredient.name} ({ingredient.unit})")
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        name_item.setData(Qt.UserRole, ingredient)

        self.table.blockSignals(True)
        self.table.setItem(new_row, INGREDIENT_COLUMN, name_item)
        for col in range(1, self.table.columnCount()):
            self.table.setItem(new_row, col, QTableWidgetItem("0"))
        self.table.blockSignals(False)

        self._recalculate()

    def _handle_remove_row(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No selection", "Select an ingredient row to remove.")
            return
        row = selected_rows[0].row()
        if row == self._total_row_index():
            QMessageBox.information(self, "Can't remove", "That's the totals row.")
            return
        self.table.removeRow(row)
        self._recalculate()

    def _handle_add_size_column(self):
        label, ok = QInputDialog.getText(self, "Add Size Column", "Size label (e.g. 16oz):")
        if not ok or not label.strip():
            return

        col = self.table.columnCount()
        self.table.insertColumn(col)
        self.table.setHorizontalHeaderItem(col, QTableWidgetItem(label.strip()))

        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            if row == self._total_row_index():
                continue
            self.table.setItem(row, col, QTableWidgetItem("0"))
        self.table.blockSignals(False)

        self._recalculate()

    # -- live totals ------------------------------------------------------------

    def _handle_item_changed(self, item):
        if item.row() == self._total_row_index():
            return
        if item.column() == INGREDIENT_COLUMN:
            return
        self._recalculate()

    def _recalculate(self):
        total_row = self._total_row_index()
        self.table.blockSignals(True)
        for col in range(1, self.table.columnCount()):
            total_cost = 0.0
            for row in range(total_row):
                name_item = self.table.item(row, INGREDIENT_COLUMN)
                quantity_item = self.table.item(row, col)
                if name_item is None or quantity_item is None:
                    continue
                ingredient = name_item.data(Qt.UserRole)
                quantity = _safe_float(quantity_item.text())
                total_cost += quantity * ingredient.cost_per_unit
            self.table.setItem(total_row, col, QTableWidgetItem(f"${total_cost:.2f}"))
        self.table.blockSignals(False)


def _safe_float(text):
    try:
        return float(text)
    except ValueError:
        return 0.0
