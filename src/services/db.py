# src/service/db.py
import sqlite3                    # built-in: no install needed
from datetime import datetime     # to store when the game finished

DB_FILE = "mastermind.db"         # SQLite file name on disk


def init_db(db_path: str = DB_FILE) -> None:
    """
    Make sure the results table exists.
    Call this once when the app starts.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create a simple results table if it doesn't exist yet.
    # We store a bit more than we print (name, attempts, difficulty, result, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            attempts INTEGER NOT NULL,
            difficulty TEXT NOT NULL,     -- 'normal' or 'hard'
            result TEXT NOT NULL,         -- 'win' or 'loss'
            first_try_win INTEGER NOT NULL DEFAULT 0,  -- 1 if win in 1 attempt
            created_at TEXT NOT NULL      -- ISO timestamp
        );
    """)

    conn.commit()
    conn.close()


def save_result(
    name: str,
    attempts: int,
    difficulty: str,     # 'normal' or 'hard'
    result: str,         # 'win' or 'loss'
    first_try_win: int = 0,
    db_path: str = DB_FILE
) -> None:
    """
    Insert one finished game into the results table.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

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
            datetime.utcnow().isoformat(timespec="seconds"),
        )
    )

    conn.commit()
    conn.close()


def get_top5_best_attempts(db_path: str = DB_FILE):
    """
    Return the Top 5 winners who used the FEWEST attempts.
    (We only include rows where result='win'.)
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT name, attempts, difficulty
        FROM results
        WHERE result = 'win'
        ORDER BY attempts ASC, created_at ASC   -- fewest attempts first
        LIMIT 5;
        """
    )
    rows = cur.fetchall()

    conn.close()
    return rows


def print_top5_table(rows) -> None:
    """
    Print:
    Place | Name | Attempts | Difficulty
    (If no winners yet, say so.)
    """
    print("Place | Name           | Attempts | Difficulty")
    print("----------------------------------------------")
    if not rows:
        print("(no winning results yet)")
        return

    for i, (name, attempts, difficulty) in enumerate(rows, start=1):
        print(f"{i:>5} | {name:<14} | {attempts:^8} | {difficulty}")
        