from PySide6.QtCore import QEvent
from PySide6.QtGui import QFocusEvent

from ui.ingredient_screen import DEFAULT_CATEGORY, INVALID_BORDER, VALID_BORDER, IngredientFormDialog


def _focus_event(kind):
    return QFocusEvent(kind)


def test_add_mode_starts_untouched_and_defaults_to_syrup(qwidget_parent, temp_db):
    dialog = IngredientFormDialog(qwidget_parent)
    dialog.set_mode("add")
    assert dialog.name_input.styleSheet() == ""
    assert not dialog.confirm_button.isEnabled()
    assert dialog.category_input.currentText() == DEFAULT_CATEGORY


def test_touching_a_field_colors_it_by_validity(qwidget_parent, temp_db):
    dialog = IngredientFormDialog(qwidget_parent)
    dialog.set_mode("add")

    dialog.name_input.setText("Vanilla Syrup")
    assert dialog.name_input.styleSheet() == VALID_BORDER

    dialog.cost_input.setText("abc")
    assert dialog.cost_input.styleSheet() == INVALID_BORDER
    dialog.cost_input.setText("0")
    assert dialog.cost_input.styleSheet() == INVALID_BORDER
    dialog.cost_input.setText("1.5")
    assert dialog.cost_input.styleSheet() == VALID_BORDER


def test_confirm_button_enables_once_all_fields_valid(qwidget_parent, temp_db):
    dialog = IngredientFormDialog(qwidget_parent)
    dialog.set_mode("add")

    dialog.name_input.setText("Vanilla Syrup")
    dialog.cost_input.setText("1.5")
    assert not dialog.confirm_button.isEnabled()

    dialog.brand_input.setText("Torani")
    dialog.unit_input.setText("oz")
    assert dialog.confirm_button.isEnabled()


def test_name_field_caps_at_100_characters(qwidget_parent, temp_db):
    dialog = IngredientFormDialog(qwidget_parent)
    assert dialog.name_input.maxLength() == 100


def test_cost_reformats_to_dollars_on_focus_out(qwidget_parent, temp_db):
    dialog = IngredientFormDialog(qwidget_parent)
    dialog.set_mode("add")

    for typed, expected in [("1", "$1.00"), ("0.5", "$0.50"), ("000.5", "$0.50"), (".5", "$0.50")]:
        dialog.cost_input.setText(typed)
        dialog.cost_input.focusOutEvent(_focus_event(QEvent.FocusOut))
        assert dialog.cost_input.text() == expected, (typed, dialog.cost_input.text())

    dialog.cost_input.focusInEvent(_focus_event(QEvent.FocusIn))
    assert dialog.cost_input.text() == "0.50"


def test_update_mode_starts_prefilled_and_touched(qwidget_parent, temp_db, seeded_ingredient):
    dialog = IngredientFormDialog(qwidget_parent)
    dialog.set_mode(
        "update",
        name=seeded_ingredient.name,
        brand=seeded_ingredient.brand,
        category_id=seeded_ingredient.category_id,
        cost=f"${seeded_ingredient.cost_per_unit:.2f}",
        unit=seeded_ingredient.unit,
    )
    assert dialog.name_input.styleSheet() == VALID_BORDER
    assert dialog.cost_input.styleSheet() == VALID_BORDER
    assert dialog.category_input.currentData() == seeded_ingredient.category_id
