# Qt fixtures for UI tests. Runs headless so no window ever actually appears.

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QWidget


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def qwidget_parent(qapp):
    return QWidget()
