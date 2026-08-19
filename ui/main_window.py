# App shell: a window with tabs switching between the Ingredients and Calculator screens

from PySide6.QtWidgets import QMainWindow, QTabWidget

from ui.calculator_screen import CalculatorScreen
from ui.ingredient_screen import IngredientScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brewcost")
        self.resize(900, 600)

        self.ingredient_screen = IngredientScreen()
        self.calculator_screen = CalculatorScreen()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.ingredient_screen, "Ingredients")
        self.tabs.addTab(self.calculator_screen, "Calculator")
        self.tabs.currentChanged.connect(self._handle_tab_changed)

        self.setCentralWidget(self.tabs)

    def _handle_tab_changed(self, index):
        if self.tabs.widget(index) is self.calculator_screen:
            self.calculator_screen.refresh_ingredient_choices()
