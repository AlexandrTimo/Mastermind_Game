from ..services.random_org import get_secret_digits
from ..engine.scorer import score_guess


def parse_guess_line(raw: str, secret_len: int = 4, digit_min: int = 0, digit_max: int = 7) -> list[int]:
    """
    Accepts formats like:
      1425
      1,4,2,5
      1 4 2 5
      1      4 2         5
      1,4       2         25
    Returns a list of 4 ints in [0,7] or raises ValueError.
    """

    s = raw.strip()
    if not s:
        raise ValueError("Empty input. Please enter digits.")

    # Any mix of commas/whitespace; explode digit-runs into single digits
    parts = s.replace(",", " ").split()
    digits = []

    # Explode each token into single digits (so '22' => '2','2')
    if len(parts) == 1 and parts[0].isdigit() and len(parts[0]) == secret_len:
        # compact form like "1425"
        digits = [int(ch) for ch in parts[0]]
    else:
        for p in parts:
            if not p.isdigit():
                raise ValueError("Invalid token: Use digits and commas/spaces.")
            
            for ch in p:
                digits.append(int(ch))

    if len(digits) != secret_len:
        raise ValueError(f"Please enter exactly {secret_len} digits.")
    

    for d in digits:
        if d < digit_min or d > digit_max:
            raise ValueError(f"Digits must be between {digit_min} and {digit_max}.")

    return digits


def start_game_with_lvl(digit_max: int, hints_max: int, attempts: int = 10, secret_len: int = 4):

    # 0..digit_max inclusive
    DIGIT_MIN = 0

    # get secret using difficulty
    secret_nums, source = get_secret_digits(secret_len, DIGIT_MIN, digit_max)
    attempts_left = attempts
    hints_used = 0
    revealed_digits = set()
    history = []
    print(f"(Secret generated via {source}. Difficulty: 0–{digit_max}, length={secret_len}, attempts={attempts})")

    while attempts_left > 0:

        raw = input("Enter guess (e.g., 1425 or 1,4,2,5). Type 'history', 'hint', or 'quit': ").strip().lower()
        # commands
        if raw == "quit":
            print("Goodbye! Game aborted.")
            return
        
        # Check history of previous guess during the game
        if raw == "history":
            if not history:
                print("No guesses yet.")
            else:
                for idx, rec in enumerate(history, 1):
                    print(f"#{idx}: {rec['guess']} > CN={rec['CN']}, CL={rec['CL']}")
            continue

        # Hints during the game: secret numbers > Normal : 2 attempts | 1 attempt
        if raw == "hint":
            if hints_used >= hints_max:
                print("No hints left for this difficulty.")
                continue
            if attempts_left <= 1:
                print("You need at least 2 attempts left to use a hint.")
                continue
            # reveal one digit value (not the position), preferably one not yet revealed
            for val in secret_nums:
                if val not in revealed_digits:
                    print(f"Hint: one of the secret digits is {val} (position not revealed).")
                    revealed_digits.add(val)
                    break
            hints_used += 1
            attempts_left -= 1  # hint costs one attempt
            print(f"Attempts left: {attempts_left}")
            continue

        # otherwise, treat as a guess
        try:
            guess = parse_guess_line(raw, secret_len=secret_len, digit_min=DIGIT_MIN, digit_max=digit_max)
            # guess = parse_guess_line(raw)
        except ValueError as e:
            print(e)
            continue
            # loop continues to re-prompt

        cn, cl = score_guess(secret_nums, guess)
        history.append({'guess': guess, 'CL' : cl, 'CN' : cn}) # Able to check during the game

        if cl == 0 and cn == 0:
            print(f"Player guesses {guess}, game responds 'all incorrect'")
        else:
            print(f"Player guesses {guess}, game responds {cn} correct numbers and {cl} correct locations")
            
        if cl == secret_len:
            print("Congrats we have a winner!!!")
            break

        attempts_left -= 1
        print(f"Attempts left: {attempts_left}")

    if attempts_left == 0 and (not history or history[-1]['CL'] != secret_len):
        print(f"Game Over! The player’s guess was incorrect. The secret numbers are {secret_nums}")


def main():
    
    
    # Data base > Result : Name | Attempts
    # Joke : For the winner > Donate 1$ to kitten shelter

    # Enter your name
    player_name = input("Enter your name: ").strip() or "Player"
    # Select Difficulty : Normal(0-7) and Hard(0-9)
    choice = input(f"Welcome {player_name}! Choose difficulty (Normal/Hard): ").strip().lower()
    SECRET_LEN = 4

    if choice == "hard":
        # Hard: 0–9, 1 hint, you can keep attempts=10 or tweak
        start_game_with_lvl(digit_max=9, hints_max=1, attempts=10, secret_len=SECRET_LEN)
    else:
        # Normal: 0–7, 2 hints
        start_game_with_lvl(digit_max=7, hints_max=2, attempts=10, secret_len=SECRET_LEN)   
        
if __name__ == "__main__":
    main()