# Brewcost

Brewcost is a local desktop app for pricing coffee-shop drinks. It replaces a manual Excel
workflow: keep a running list of ingredients and their costs, then use those ingredients to
figure out what a drink actually costs to make and what it should sell for.

It's built for a single person running it on their own machine. There's no login, no server, and
no internet connection required. Everything is stored in a SQLite database file that lives right
next to the app. It's developed and tested on macOS, but since it's just Python (PySide6) and
SQLite under the hood, it should run the same way on Windows or Linux.

## What it does today

- **Ingredients tab**: add, update, and delete ingredients (name, category, cost per unit,
  unit of measure). This is the only data that's actually saved to the database right now.
- **Calculator tab**: a live scratchpad for building out a drink: pick ingredients, enter how
  much of each goes into a few different size options, and see the total cost update as you go.
  This screen doesn't save anything yet. It resets each time you leave it. Saving recipes is
  planned (see `TODO.md`).

## Tech stack

- **PySide6 (Qt)** for the desktop UI
- **SQLite** for storage, accessed with Python's built-in `sqlite3`
- Plain Python. No web framework, no ORM

## Project layout

```
Brewcost/
  main.py                        # entry point: sets up the database, opens the main window
  database/
    connection.py                # opens brewcost.db, creates tables, small SQL-file loader
    ingredient_repository.py     # everything about the "ingredients" table lives here
    sql/
      schema.sql                 # every CREATE TABLE statement
      ingredients/                # one .sql file per query (insert, select, update, delete)
  ui/
    main_window.py                # app shell / tab switcher
    ingredient_screen.py          # the Ingredients tab
    calculator_screen.py          # the Calculator tab
  requirements.txt
  brewcost.db                     # your local data, not checked into git
```

## How it's structured (the repository pattern)

Each database table gets three things, kept deliberately separate:

1. **Raw SQL**, one query per file, in `database/sql/<table>/`. These files contain nothing but
   SQL.
2. **A repository module**, `database/<table>_repository.py`. This is the only code that knows
   both "which SQL file to run" and "what a row of this table looks like as a Python object." It
   exposes plain functions like `add_x`, `get_all_x`, `update_x`, `delete_x`.
3. **UI screens**, in `ui/`, that call those repository functions and never touch SQL or
   `sqlite3` directly.

The idea is that adding a new table later (recipes, for example) means adding a new SQL folder
and a new repository file. The existing ingredient code doesn't need to change at all.

## Running it locally

```
# macOS/Linux
venv/bin/python3 main.py

# Windows
venv\Scripts\python.exe main.py
```

`brewcost.db` and the tables in it are created automatically the first time it runs, so a fresh
clone starts with an empty database.

## What's next

Planned work is tracked in `TODO.md`.
