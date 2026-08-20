# Entry point: creates the app, sets up the database, opens the main window.

import sys

from PySide6.QtWidgets import QApplication

from database import connection
from ui.main_window import MainWindow


def main():
    connection.create_tables()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
