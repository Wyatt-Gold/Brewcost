# SQLite connection + schema setup

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "brewcost.db"
SQL_DIR = Path(__file__).parent / "sql"

# Read a .sql file's text
def load_sql(relative_path):
    return (SQL_DIR / relative_path).read_text()

# Open a connection to the database file, creating it if it doesn't exist yet.
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Run schema.sql to make sure every table exists. Safe to call every startup.
def create_tables():
    connection = get_connection()
    connection.executescript(load_sql("schema.sql"))
    connection.commit()
    connection.close()
