import pytest

from database import categories_repository, ingredient_repository


def test_seed_categories_are_singular(temp_db):
    categories = categories_repository.get_all_categories()
    assert {c.name for c in categories} == {"Syrup", "Add-on", "Extra"}


def test_add_update_delete_roundtrip(temp_db):
    syrup_id = next(c.id for c in categories_repository.get_all_categories() if c.name == "Syrup")
    ingredient_id = ingredient_repository.add_ingredient("Vanilla Syrup", "Torani", syrup_id, 12.5, "oz")

    ingredients = ingredient_repository.get_all_ingredients()
    assert len(ingredients) == 1
    ingredient = ingredients[0]
    assert ingredient.id == ingredient_id
    assert ingredient.name == "Vanilla Syrup"
    assert ingredient.brand == "Torani"
    assert ingredient.category == "Syrup"
    assert ingredient.cost_per_unit == 12.5
    assert ingredient.unit == "oz"

    ingredient_repository.update_ingredient(ingredient.id, "Vanilla Syrup", "Monin", syrup_id, 13.0, "oz")
    updated = ingredient_repository.get_all_ingredients()[0]
    assert updated.brand == "Monin"
    assert updated.cost_per_unit == 13.0

    ingredient_repository.delete_ingredient(ingredient.id)
    assert ingredient_repository.get_all_ingredients() == []


def test_import_valid_csv(temp_db, tmp_path):
    csv_path = tmp_path / "ingredients.csv"
    csv_path.write_text(
        "name,brand,category,cost_per_unit,unit\n"
        "Vanilla Syrup,Torani,syrup,12.5,oz\n"
        "Whipped Cream,Reddi-wip,Extra,3.0,can\n"
    )

    added, skipped = ingredient_repository.import_ingredients_from_csv(csv_path)

    assert added == 2
    assert skipped == []
    names = {i.name for i in ingredient_repository.get_all_ingredients()}
    assert names == {"Vanilla Syrup", "Whipped Cream"}


def test_import_rejects_missing_column(temp_db, tmp_path):
    csv_path = tmp_path / "ingredients.csv"
    csv_path.write_text("name,brand,category,unit\nVanilla Syrup,Torani,Syrup,oz\n")

    with pytest.raises(ingredient_repository.CSVFormatError):
        ingredient_repository.import_ingredients_from_csv(csv_path)
    assert ingredient_repository.get_all_ingredients() == []


def test_import_rejects_extra_column(temp_db, tmp_path):
    csv_path = tmp_path / "ingredients.csv"
    csv_path.write_text(
        "name,brand,category,cost_per_unit,unit,notes\n"
        "Vanilla Syrup,Torani,Syrup,12.5,oz,tasty\n"
    )

    with pytest.raises(ingredient_repository.CSVFormatError):
        ingredient_repository.import_ingredients_from_csv(csv_path)
    assert ingredient_repository.get_all_ingredients() == []


def test_import_skips_invalid_rows(temp_db, tmp_path):
    csv_path = tmp_path / "ingredients.csv"
    csv_path.write_text(
        "name,brand,category,cost_per_unit,unit\n"
        "Vanilla Syrup,Torani,Syrup,12.5,oz\n"
        "Mystery Item,Torani,NotACategory,4.0,oz\n"
        ",Torani,Syrup,4.0,oz\n"
        "Bad Cost,Torani,Syrup,not-a-number,oz\n"
    )

    added, skipped = ingredient_repository.import_ingredients_from_csv(csv_path)

    assert added == 1
    assert skipped == [
        (3, ["category"]),
        (4, ["name"]),
        (5, ["cost_per_unit"]),
    ]
