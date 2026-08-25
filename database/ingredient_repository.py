# Handles database operations related to ingredients.

from dataclasses import dataclass

from database.connection import get_connection, load_sql


@dataclass
class Ingredient:
    id: int
    name: str
    brand: str
    category_id: int
    category: str
    cost_per_unit: float
    unit: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            name=row["name"],
            brand=row["brand"],
            category_id=row["category_id"],
            category=row["category"],
            cost_per_unit=row["cost_per_unit"],
            unit=row["unit"],
        )

# Add a new ingredient to the database and return its ID.
def add_ingredient(name, brand, category_id, cost_per_unit, unit):
    connection = get_connection()
    sql = load_sql("ingredients/insert.sql")
    cursor = connection.execute(sql, (name, brand, category_id, cost_per_unit, unit))
    connection.commit()
    new_id = cursor.lastrowid
    connection.close()
    return new_id

# Retrieve all ingredients from the database as a list of Ingredient objects.
def get_all_ingredients():
    connection = get_connection()
    sql = load_sql("ingredients/select_all.sql")
    rows = connection.execute(sql).fetchall()
    connection.close()
    return [Ingredient.from_row(row) for row in rows]

# Update an existing ingredient's details in the database.
def update_ingredient(ingredient_id, name, brand, category_id, cost_per_unit, unit):
    connection = get_connection()
    sql = load_sql("ingredients/update.sql")
    connection.execute(sql, (name, brand, category_id, cost_per_unit, unit, ingredient_id))
    connection.commit()
    connection.close()

# Delete an ingredient from the database by its ID.
def delete_ingredient(ingredient_id):
    connection = get_connection()
    sql = load_sql("ingredients/delete.sql")
    connection.execute(sql, (ingredient_id,))
    connection.commit()
    connection.close()
