# Self-check for the ingredients/categories join. Run directly: python3 -m database.test_ingredient_repository

import sqlite3
import tempfile
from pathlib import Path

import database.connection as connection


def demo():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_db_path = connection.DB_PATH
        connection.DB_PATH = Path(tmpdir) / "test.db"
        try:
            connection.create_tables()

            from database import categories_repository, ingredient_repository

            categories = categories_repository.get_all_categories()
            assert {c.name for c in categories} == {"Syrup", "Add-on", "Extra"}

            syrup_id = next(c.id for c in categories if c.name == "Syrup")
            ingredient_repository.add_ingredient("Vanilla Syrup", "Torani", syrup_id, 12.5, "oz")

            ingredients = ingredient_repository.get_all_ingredients()
            assert len(ingredients) == 1
            ingredient = ingredients[0]
            assert ingredient.name == "Vanilla Syrup"
            assert ingredient.brand == "Torani"
            assert ingredient.category == "Syrup"
            assert ingredient.cost_per_unit == 12.5
            assert ingredient.unit == "oz"

            ingredient_repository.update_ingredient(
                ingredient.id, "Vanilla Syrup", "Monin", syrup_id, 13.0, "oz"
            )
            updated = ingredient_repository.get_all_ingredients()[0]
            assert updated.brand == "Monin"
            assert updated.cost_per_unit == 13.0

            ingredient_repository.delete_ingredient(ingredient.id)
            assert ingredient_repository.get_all_ingredients() == []

            print("OK")
        finally:
            connection.DB_PATH = original_db_path


if __name__ == "__main__":
    demo()
