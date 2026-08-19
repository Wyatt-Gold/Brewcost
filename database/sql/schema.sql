CREATE TABLE IF NOT EXISTS ingredients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    category      TEXT,
    cost_per_unit REAL NOT NULL,
    unit          TEXT NOT NULL
);
