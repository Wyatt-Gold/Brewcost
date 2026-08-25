CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

INSERT OR IGNORE INTO categories (name) VALUES ('Syrup'), ('Add-on'), ('Extra');

CREATE TABLE IF NOT EXISTS ingredients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    brand         TEXT NOT NULL,
    category_id   INTEGER NOT NULL REFERENCES categories(id),
    cost_per_unit REAL NOT NULL,
    unit          TEXT NOT NULL
);
