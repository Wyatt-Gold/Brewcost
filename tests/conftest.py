# Shared fixtures for tests that need a real (throwaway) SQLite database.

import tempfile
from pathlib import Path

import pytest

import database.connection as connection


@pytest.fixture
def temp_db():
    original_db_path = connection.DB_PATH
    with tempfile.TemporaryDirectory() as tmpdir:
        connection.DB_PATH = Path(tmpdir) / "test.db"
        connection.create_tables()
        try:
            yield
        finally:
            connection.DB_PATH = original_db_path


@pytest.fixture
def seeded_ingredient(temp_db):
    from database import categories_repository, ingredient_repository

    syrup_id = next(c.id for c in categories_repository.get_all_categories() if c.name == "Syrup")
    ingredient_id = ingredient_repository.add_ingredient("Vanilla Syrup", "Torani", syrup_id, 12.5, "oz")
    return next(i for i in ingredient_repository.get_all_ingredients() if i.id == ingredient_id)
