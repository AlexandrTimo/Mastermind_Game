# Mastermind (Python · Console)

Backend-focused Mastermind game. Emphasis on clean engine logic, robust input parsing, external randomness with local fallback, and a tiny SQLite leaderboard.

# Requirements

- Python 3.10+

- pip

- Internet optional (used for RANDOM.ORG; game falls back to local secure RNG if offline)

# Setup
from the project root (the folder that contains src/)
- python -m venv .venv

macOS/Linux
- source .venv/bin/activate

Windows (PowerShell)

- .venv\Scripts\Activate.ps1

  
pip install -r requirements.txt

# Run
- python -m src.cli.game

# How to Play

1) Enter your name.
2) Choose difficulty:

- Normal: digits 0–7, 10 attempts, 2 hints
- Hard: digits 0–9, 10 attempts, 1 hint

Guess a 4-digit code. Accepted inputs:

- 1425 · 1,4,2,5 · 1 4 2 5 · mixed spaces/commas (e.g., 1,4 2 5)
- Multi-digit tokens like 22 are exploded → 2 2.

# Feedback per guess:

CN = correct numbers (frequency-based, duplicates handled)

CL = correct locations (exact index matches)

If both are 0 → “all incorrect”

# Commands:

- history → list past guesses with CN/CL
- hint → reveal one digit value (no position), costs 1 attempt
- quit → abort current game

Win when CL == 4. On loss, the secret is revealed.

# Leaderboard (SQLite)

- Stored in mastermind.db (auto-created).
- Only wins are saved.
- Leaderboard shows Top 5 best (fewest attempts):

      Place | Name           | Attempts | Difficulty
          1 | Alice          |    3     | normal
          2 | Bob            |    4     | hard

- After a win you’ll be prompted to type results to display it.
- First-try win prints a fun $1 kitten-shelter nudge 😺.
- To reset the leaderboard, delete mastermind.db.

# Project Structure
    src/
     cli/
       game.py            # entrypoint: I/O loop, difficulty, hints, history, saves results
     engine/
       scorer.py          # pure logic: score_guess(secret, guess) -> (CN, CL)
     services/
       random_org.py      # get_secret_digits(): RANDOM.ORG with secure local fallback
       db.py              # init_db(), save_result(), get_top5_best_attempts(), print_top5_table()

# Design Notes

Pure engine: score_guess is side-effect free
→ CL via index equality; CN via per-digit frequency overlap (correct with duplicates).

- Parser: tolerant of spaces/commas; explodes digit runs; validates exact length and digit range by difficulty.
- RNG: Try RANDOM.ORG once (format=plain, num/min/max). On any issue, fallback to secrets.randbelow with the same shape (length/range).
- DB: Minimal results table; only winners stored; leaderboard sorted by ascending attempts.

# Troubleshooting

- ModuleNotFoundError: No module named 'src'
→ Run from project root: python -m src.cli.game (don’t run files by path).

- No leaderboard rows
→ Win at least once; only wins are saved.

- Reset leaderboard
→ Delete mastermind.db.
