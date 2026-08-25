from ui.calculator_screen import CalculatorScreen, _safe_float


def test_safe_float_handles_bad_input():
    assert _safe_float("2.5") == 2.5
    assert _safe_float("") == 0.0
    assert _safe_float("abc") == 0.0


def _add_seeded_ingredient_row(screen, ingredient):
    label = f"{ingredient.name} ({ingredient.unit})"
    screen.ingredient_combo.setCurrentIndex(screen.ingredient_combo.findText(label))
    screen._handle_add_ingredient_row()


def test_recalculate_sums_quantity_times_cost(qapp, temp_db, seeded_ingredient):
    screen = CalculatorScreen()
    _add_seeded_ingredient_row(screen, seeded_ingredient)

    screen.table.item(0, 1).setText("3")

    total_row = screen._total_row_index()
    total_text = screen.table.item(total_row, 1).text()
    assert total_text == f"${3 * seeded_ingredient.cost_per_unit:.2f}"


def test_recalculate_ignores_unparseable_quantity(qapp, temp_db, seeded_ingredient):
    screen = CalculatorScreen()
    _add_seeded_ingredient_row(screen, seeded_ingredient)

    screen.table.item(0, 1).setText("garbage")

    total_row = screen._total_row_index()
    total_text = screen.table.item(total_row, 1).text()
    assert total_text == "$0.00"
