from ..services.random_org import get_secret_digits
from ..engine.scorer import score_guess
from ..services.db import init_db, save_result, get_top5_best_attempts, print_top5_table



def parse_guess_line(raw: str, secret_len: int = 4, digit_min: int = 0, digit_max: int = 7) -> list[int]:
    """
    Accepts formats like:
      1425
      1,4,2,5
      1 4 2 5
      1      4 2         5
      1,4       2         25
    Returns secret_len ints in [digit_min..digit_max] or raises ValueError.
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


def start_game_with_lvl(digit_max: int, hints_max: int, attempts: int = 10, secret_len: int = 4, player_name: str = "Player", difficulty_label: str = "normal",):

    # get secret using difficulty
    secret_nums, source = get_secret_digits(num=secret_len, digit_min=0, digit_max=digit_max)
    attempts_left = attempts
    hints_used = 0
    revealed_digits = set()
    history = []
    print(f"(Secret generated via {source}. Difficulty: 0–{digit_max}, length={secret_len}, attempts={attempts})")
    # print(f'Secret : {secret_nums}')

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
                    print(f"#{idx}: {rec['guess']} > Correct Numbers = {rec['CN']}, Correct Locations = {rec['CL']}")
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
            guess = parse_guess_line(raw, secret_len=secret_len, digit_min=0, digit_max=digit_max)
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

            attempts_used = len(history)              # guesses taken to win (hints not counted)
            if attempts_used == 1:
                first_try = 1
            else:
                first_try = 0

            # Save only winners (you already do this)
            save_result(player_name, attempts_used, difficulty_label, "win", first_try)

            # Kitten-shelter joke for first-try
            if first_try:
                print("🎉 First try! Consider donating $1 to a kitten shelter 😺")

            # Offer to show the leaderboard (loop until valid input)
            while True:
                show = input(
                    "Type 'results' to see Top 5 best (fewest attempts), "
                    "'quit' to exit, or just press Enter to continue: "
                ).strip().lower()

                if show == "results":
                    rows = get_top5_best_attempts()
                    print_top5_table(rows)
                    break  # done with this prompt; continue finishing the win flow
                elif show == "quit":
                    print("Goodbye!")
                    return  # end the game function cleanly
                elif show == "" or show == "continue":
                    break  # player chose to just continue
                else:
                    print("Invalid option. Please type 'results', 'quit', or press Enter.")
                    # loop continues and asks again


        attempts_left -= 1
        print(f"Attempts left: {attempts_left}")

    if attempts_left == 0 and (not history or history[-1]['CL'] != secret_len):
        print(f"Game Over! The player’s guess was incorrect. The secret numbers are {secret_nums}")


def main(): 
    
    # Data base > Result : Place | Name | Attempts (Top 5) Option in the end of the game
    init_db()  # make sure the DB/table exists

    # Enter your name
    player_name = input("Enter your name: ").strip() or "Player"

    while True:
        # Select Difficulty : Normal(0-7) and Hard(0-9)
        choice = input(f"Welcome {player_name}! Choose difficulty (Normal/Hard): ").strip().lower()
        if choice == "hard":
            # Hard: 0–9, 1 hint
            start_game_with_lvl(digit_max=9, hints_max=1, attempts=10, secret_len=4, player_name=player_name, difficulty_label='hard')
            break
        if choice == "normal":
            # Normal: 0–7, 2 hints
            start_game_with_lvl(digit_max=7, hints_max=2, attempts=10, secret_len=4, player_name=player_name, difficulty_label='normal') 
            break
        
        print("Invalid option. Please choose Normal or Hard:")
        
if __name__ == "__main__":
    main()
