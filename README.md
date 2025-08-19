Title: Mastermind (Console) — Backend-first Python

What it is
A console Mastermind where the computer selects 4 digits (0–7, duplicates allowed) using random.org. Player has 10 attempts. After each guess, the game prints “X correct numbers; Y correct locations” and keeps history.

How to run

python -m venv .venv && source .venv/bin/activate (Windows: .\.venv\Scripts\activate)

pip install -r requirements.txt

python -m mastermind.cli.game
(or python src/mind.py depending on your entry point)

Optional env vars:

RANDOM_TIMEOUT_MS – HTTP timeout

RANDOM_FALLBACK=1 – force local RNG for offline dev

Testing
Run pytest -q. See tests/ for scenarios incl. duplicates and API failures.

API
Uses random.org integers endpoint with num=4&min=0&max=7&col=1&base=10&format=plain&rnd=new.