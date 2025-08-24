# src/service/db.py
import sqlite3                    # built-in: no install needed
from datetime import datetime     # to store when the game finished

DB_FILE = "mastermind.db"         # SQLite file name on disk


def init_db(db_path: str = DB_FILE) -> None:
    """
    Make sure the results table exists.
    Call this once when the app starts.
    """
    # Open a connection to the DB file (creates file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    # Create a cursor to run SQL commands
    cur = conn.cursor()

    # Create a simple results table if it doesn't exist yet.
    # We store a bit more than we print (name, attempts, difficulty, result, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            attempts INTEGER NOT NULL,
            difficulty TEXT NOT NULL,     -- 'normal' or 'hard'
            result TEXT NOT NULL,         -- 'win'
            first_try_win INTEGER NOT NULL DEFAULT 0,  -- 1 if win in 1 attempt
            created_at TEXT NOT NULL      -- ISO timestamp
        );
    """)

    # Save schema changes to disk and close connection
    conn.commit()
    conn.close()


def save_result(
    name: str,
    attempts: int,
    difficulty: str,     # 'normal' or 'hard'
    result: str,         # 'win' (we only save wins)
    first_try_win: int = 0,
    db_path: str = DB_FILE
) -> None:
    """
    Insert one finished game into the results table.
    Call this right after a win.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Using parameter placeholders (?) protects against SQL injection
    # and avoids manual string formatting.
    cur.execute(
        """
        INSERT INTO results (name, attempts, difficulty, result, first_try_win, created_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            name,
            attempts,
            difficulty,
            result,
            first_try_win,
            # ISO 8601 timestamp like '2025-08-23T11:05:00'
            datetime.utcnow().isoformat(timespec="seconds"),
        )
    )

    conn.commit()
    conn.close()


def get_top5_best_attempts(db_path: str = DB_FILE):
    """
    Return the Top 5 winners who used the best attempts.
    - Only rows where result='win' are included.
    - Sorted by attempts ASC (best at top), then created_at ASC (stable ties).
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT name, attempts, difficulty
        FROM results
        WHERE result = 'win'
        ORDER BY attempts ASC, created_at ASC   -- best attempts first
        LIMIT 5;
        """
    )
    rows = cur.fetchall() # rows is a list of tuples: [(name, attempts, difficulty), ...]

    conn.close()
    return rows


def print_top5_table(rows) -> None:
    """
    Print:
    Place | Name | Attempts | Difficulty
    (If no winners yet, say so.)
    Formatting tips used below:
        {i:>5}   -> right-align in width 5
        {name:<14} -> left-align in width 14
        {attempts:^8} -> center in width 8
    """
    print("Place | Name           | Attempts | Difficulty")
    print("----------------------------------------------")
    if not rows:
        print("(no winning results yet)")
        return

    # Enumerate gives us the 1-based "Place" number
    for i, row in enumerate(rows, start=1):
        # Row is a tuple like: ("Alice", 3, "normal")
        # Access by index to keep it super clear:
        name = row[0]
        attempts = row[1]
        difficulty = row[2]
        print(f"{i:>5} | {name:<14} | {attempts:^8} | {difficulty}")
