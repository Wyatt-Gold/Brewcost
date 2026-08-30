# Calculator screen: lets the user add ingredients, enter a quantity per fixed drink size, and see the total cost for each size.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import ingredient_repository

INGREDIENT_COLUMN = 0
QUANTITY_COLUMN = 1
SIZE_LABELS = ["12oz", "16oz", "20oz"]

GROUP_BOX_STYLE = (
    "QGroupBox { border: 1px solid palette(mid); border-radius: 4px; margin-top: 10px; }"
    "QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }"
)
TOTAL_LABEL_STYLE = "border-top: 3px solid palette(mid); font-weight: bold; padding: 6px 2px 0 2px;"


class CalculatorScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.ingredient_combo = QComboBox()
        self.add_ingredient_button = QPushButton("Add Ingredient Row")
        self.remove_row_button = QPushButton("Remove Selected Row")

        self.add_ingredient_button.clicked.connect(self._handle_add_ingredient_row)
        self.remove_row_button.clicked.connect(self._handle_remove_row)

        controls = QHBoxLayout()
        controls.addWidget(self.ingredient_combo)
        controls.addWidget(self.add_ingredient_button)
        controls.addWidget(self.remove_row_button)

        # One small table per fixed size, stacked smallest-to-largest. Rows stay in lockstep
        # across tables (same ingredient at the same row index in each) so a row index found
        # in one table is valid in all of them. The total is a label below the table, not a
        # table row, so it stays pinned to the bottom of the box instead of moving as rows
        # are added/removed.
        self.tables = []
        self.total_labels = []
        boxes = QVBoxLayout()
        for size_label in SIZE_LABELS:
            table = QTableWidget(0, 2)
            table.setHorizontalHeaderLabels(["Ingredient", "Quantity"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.itemChanged.connect(self._handle_item_changed)
            self.tables.append(table)

            total_label = QLabel("Total Cost: $0.00")
            total_label.setStyleSheet(TOTAL_LABEL_STYLE)
            self.total_labels.append(total_label)

            box = QGroupBox(size_label)
            box.setStyleSheet(GROUP_BOX_STYLE)
            box_layout = QVBoxLayout()
            box_layout.setContentsMargins(10, 14, 10, 10)
            box_layout.addWidget(table)
            box_layout.addWidget(total_label)
            box.setLayout(box_layout)
            boxes.addWidget(box)

        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addLayout(boxes)
        self.setLayout(layout)

        self.refresh_ingredient_choices()

    # -- ingredient dropdown -------------------------------------------------

    def refresh_ingredient_choices(self):
        # Re-pull the saved ingredient list. Call this whenever this screen becomes visible,
        # since ingredients may have changed on the Ingredient Manager screen.
        self.ingredient_combo.clear()
        for ingredient in ingredient_repository.get_all_ingredients():
            label = f"{ingredient.name} ({ingredient.unit})"
            self.ingredient_combo.addItem(label, ingredient)

    # -- row setup -------------------------------------------------------------

    def _handle_add_ingredient_row(self):
        ingredient = self.ingredient_combo.currentData()
        if ingredient is None:
            QMessageBox.information(self, "No ingredients", "Add ingredients on the Ingredients tab first.")
            return

        for table in self.tables:
            new_row = table.rowCount()
            table.insertRow(new_row)

            name_item = QTableWidgetItem(f"{ingredient.name} ({ingredient.unit})")
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, ingredient)

            table.blockSignals(True)
            table.setItem(new_row, INGREDIENT_COLUMN, name_item)
            table.setItem(new_row, QUANTITY_COLUMN, QTableWidgetItem("0"))
            table.blockSignals(False)

            self._recalculate(table)

    def _handle_remove_row(self):
        row = None
        for table in self.tables:
            selected_rows = table.selectionModel().selectedRows()
            if selected_rows:
                row = selected_rows[0].row()
                break

        if row is None:
            QMessageBox.information(self, "No selection", "Select an ingredient row to remove.")
            return

        for table in self.tables:
            table.removeRow(row)
            self._recalculate(table)

    # -- live totals ------------------------------------------------------------

    def _handle_item_changed(self, item):
        if item.column() == INGREDIENT_COLUMN:
            return
        self._recalculate(item.tableWidget())

    def _recalculate(self, table):
        total_label = self.total_labels[self.tables.index(table)]
        total_cost = 0.0
        for row in range(table.rowCount()):
            name_item = table.item(row, INGREDIENT_COLUMN)
            quantity_item = table.item(row, QUANTITY_COLUMN)
            if name_item is None or quantity_item is None:
                continue
            ingredient = name_item.data(Qt.UserRole)
            quantity = _safe_float(quantity_item.text())
            total_cost += quantity * ingredient.cost_per_unit
        total_label.setText(f"Total Cost: ${total_cost:.2f}")


def _safe_float(text):
    try:
        return float(text)
    except ValueError:
        return 0.0
