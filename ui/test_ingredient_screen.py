# Self-check for the ingredient form's validation/currency-formatting logic.
# Run directly: QT_QPA_PLATFORM=offscreen python3 -m ui.test_ingredient_screen

from PySide6.QtCore import QEvent
from PySide6.QtGui import QFocusEvent
from PySide6.QtWidgets import QApplication, QWidget

from ui.ingredient_screen import INVALID_BORDER, VALID_BORDER, IngredientFormDialog


def demo():
    QApplication.instance() or QApplication([])
    focus_in = lambda: QFocusEvent(QEvent.FocusIn)
    focus_out = lambda: QFocusEvent(QEvent.FocusOut)

    parent = QWidget()
    dialog = IngredientFormDialog(parent)

    # Add mode: blank form starts untouched (no border color), button disabled.
    dialog.set_mode("add")
    assert dialog.name_input.styleSheet() == ""
    assert not dialog.confirm_button.isEnabled()

    # Typing marks the field touched and colors it.
    dialog.name_input.setText("Vanilla Syrup")
    assert dialog.name_input.styleSheet() == VALID_BORDER

    # Cost validity is based on the parsed dollar amount, not raw text (a $-prefixed value
    # from a previous blur must still parse correctly).
    dialog.cost_input.setText("abc")
    assert dialog.cost_input.styleSheet() == INVALID_BORDER
    dialog.cost_input.setText("0")
    assert dialog.cost_input.styleSheet() == INVALID_BORDER
    dialog.cost_input.setText("1.5")
    assert dialog.cost_input.styleSheet() == VALID_BORDER

    # Name field respects the 100-character cap.
    assert dialog.name_input.maxLength() == 100

    # All four fields valid -> button enabled.
    dialog.brand_input.setText("Torani")
    dialog.unit_input.setText("oz")
    assert dialog.confirm_button.isEnabled()

    # Losing focus reformats to "$X.XX", including whole numbers, leading zeros, and a
    # bare leading decimal point.
    for typed, expected in [("1", "$1.00"), ("0.5", "$0.50"), ("000.5", "$0.50"), (".5", "$0.50")]:
        dialog.cost_input.setText(typed)
        dialog.cost_input.focusOutEvent(focus_out())
        assert dialog.cost_input.text() == expected, (typed, dialog.cost_input.text())

    # Regaining focus strips the "$" back off so the raw number is editable.
    dialog.cost_input.focusInEvent(focus_in())
    assert dialog.cost_input.text() == "0.50"

    # Update mode: pre-filled fields (already "$"-formatted) start touched/green immediately.
    dialog.set_mode("update", name="Oat Milk", brand="Chobani", category_id=None, cost="$4.00", unit="oz")
    assert dialog.name_input.styleSheet() == VALID_BORDER
    assert dialog.cost_input.styleSheet() == VALID_BORDER

    print("OK")


if __name__ == "__main__":
    demo()
