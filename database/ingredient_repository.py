# Handles database operations related to ingredients.

import csv
from dataclasses import dataclass

from database import categories_repository
from database.connection import get_connection, load_sql

REQUIRED_COLUMNS = {"name", "brand", "category", "cost_per_unit", "unit"}


class CSVFormatError(Exception):
    pass


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

# Import ingredients from a CSV file. Rejects the whole file if its header
# row doesn't match REQUIRED_COLUMNS exactly (missing or extra columns).
# Otherwise adds every valid row and returns (added_count, skipped), where
# skipped is a list of (row_number, [bad_column_names]) for rows that were
# left out due to missing/invalid data.
def import_ingredients_from_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        headers = {(h or "").strip().lower() for h in reader.fieldnames or []}
        if headers != REQUIRED_COLUMNS:
            missing = REQUIRED_COLUMNS - headers
            extra = headers - REQUIRED_COLUMNS
            parts = []
            if missing:
                parts.append(f"missing columns: {', '.join(sorted(missing))}")
            if extra:
                parts.append(f"unexpected columns: {', '.join(sorted(extra))}")
            raise CSVFormatError("; ".join(parts))

        categories_by_name = {c.name.lower(): c.id for c in categories_repository.get_all_categories()}

        added = 0
        skipped = []
        for row_number, row in enumerate(reader, start=2):
            row = {key.strip().lower(): (value or "").strip() for key, value in row.items()}
            bad_columns = []

            if not row["name"]:
                bad_columns.append("name")
            if not row["brand"]:
                bad_columns.append("brand")
            if not row["unit"]:
                bad_columns.append("unit")

            category_id = categories_by_name.get(row["category"].lower())
            if category_id is None:
                bad_columns.append("category")

            try:
                cost = float(row["cost_per_unit"])
                if cost < 0.01:
                    bad_columns.append("cost_per_unit")
            except ValueError:
                bad_columns.append("cost_per_unit")

            if bad_columns:
                skipped.append((row_number, bad_columns))
                continue

            add_ingredient(row["name"], row["brand"], category_id, cost, row["unit"])
            added += 1

        return added, skipped
