# Handles database operations related to ingredient categories.

from dataclasses import dataclass

from database.connection import get_connection, load_sql


@dataclass
class Category:
    id: int
    name: str

    @classmethod
    def from_row(cls, row):
        return cls(id=row["id"], name=row["name"])

# Retrieve all categories from the database as a list of Category objects.
def get_all_categories():
    connection = get_connection()
    sql = load_sql("categories/select_all.sql")
    rows = connection.execute(sql).fetchall()
    connection.close()
    return [Category.from_row(row) for row in rows]
