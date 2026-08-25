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
