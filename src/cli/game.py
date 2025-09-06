from ..services.random_org import get_secret_digits
from ..engine.scorer import score_guess
from ..services.db import init_db, save_result, get_top5_best_attempts, print_top5_table



def parse_guess_line(raw: str, secret_len: int = 4, digit_min: int = 0, digit_max: int = 7) -> list[int]:
    """
    - Parsing input string
    - Accepts formats like:
      1425
      1,4,2,5
      1 4 2 5
      1      4 2         5
      1,4       2         25
    - Returns secret_len ints in [digit_min..digit_max] or raises ValueError.
    """

    s = raw.strip()

    # 1. String not empty
    if not s:
        raise ValueError("Empty input. Please enter digits.")

    # 2. Any mix of commas/whitespace; explode digit-runs into single digits
    parts = s.replace(",", " ").split()
    digits = []

    # 3. Explore each token into single digits (so '22' => '2','2')
    if len(parts) == 1 and parts[0].isdigit() and len(parts[0]) == secret_len:
        # Compact form like "1425"
        for ch in parts[0]:
            digits.append(int(ch))
    # 4. Check each token is an int
    else:
        for p in parts:
            if not p.isdigit():
                raise ValueError("Invalid token: Use digits and commas/spaces.")
            
            for ch in p:
                digits.append(int(ch))

    # 5. Check the len of input 
    if len(digits) != secret_len:
        raise ValueError(f"Please enter exactly {secret_len} digits.")
    
    # 6. Check each token is match to digit range
    for d in digits:
        if d < digit_min or d > digit_max:
            raise ValueError(f"Digits must be between {digit_min} and {digit_max}.")

    return digits


def start_game_with_lvl(digit_max: int, hints_max: int, attempts: int = 10, secret_len: int = 4, player_name: str = "Player", difficulty_label: str = "normal"):
    '''
    Start the game after picked a difficulty level. The player can then guess numbers and has the following options:
    - Quit the game.
    - View their previous guesses in a history board.
    - Use a hint to reveal one secret number.
    The function also includes these features:
    - Secret numbers are generated (via API or locally).
    - Player guesses are validated for edge cases using the parse_guess_line().
    - Player guesses are collected and tracked in the game history.
    - Game results are saved to a database if the player is qualified.
    After the game ends, new options are available: 
    - View the board 'Top 5 winners'
    - Quit the game
    - Restart the game
    '''

    # Get secret using difficulty
    secret_nums, source = get_secret_digits(num=secret_len, digit_min=0, digit_max=digit_max)
    attempts_left = attempts
    hints_used = 0
    revealed_digits = set()
    history = []

    # Introduction of level settings
    print(f"(Secret generated via {source}. Difficulty: 0–{digit_max}, length={secret_len}, attempts={attempts})")
    # print(f'Secret : {secret_nums}')

    # Commands to select (loop until valid input)
    while attempts_left > 0:

        raw = input("Enter guess (e.g., 1425 or 1,4,2,5). Type 'history', 'hint', or 'quit': ").strip().lower()
    
        # 1. Quit the game
        if raw == "quit":
            print("Goodbye! Game aborted.")
            return
        
        # 2. Check history of previous guess (during the game)
        if raw == "history":
            if not history:
                print("No guesses yet.")
            else:
                for idx, rec in enumerate(history, 1):
                    print(f"#{idx}: {rec['guess']} > Correct Numbers = {rec['CN']}, Correct Locations = {rec['CL']}")
            continue

        # 3. Hints during the game: show the secret numbers > Normal : 2 attempts | Hard : 1 attempt
        if raw == "hint":
            if hints_used >= hints_max:
                print("No hints left for this difficulty.")
                continue
            if attempts_left <= 1:
                print("You need at least 2 attempts left to use a hint.")
                continue 
            # Reveal one digit value (not the position), preferably one not yet revealed
            for val in secret_nums:
                if val not in revealed_digits:
                    print(f"Hint: one of the secret digits is {val} (position not revealed).")
                    revealed_digits.add(val)
                    break
            hints_used += 1
            attempts_left -= 1  # hint costs one attempt
            print(f"Attempts left: {attempts_left}")
            continue

        # 4. Parse and check input numbers 
        try:
            guess = parse_guess_line(raw, secret_len=secret_len, digit_min=0, digit_max=digit_max)
        except ValueError as e:
            print(e)
            continue
            # Loop continues to re-prompt

        
        # 5. Guess Numbers (Logic)
        cn, cl = score_guess(secret_nums, guess)
        # Track guesses in the history board
        history.append({'guess': guess, 'CL' : cl, 'CN' : cn}) # Able to check during the game

        # Results of guess (during the game)
        if cl == 0 and cn == 0:
            print(f">>> Player guesses {guess}, game responds 'all incorrect'")
        else:
            print(f">>> Player guesses {guess}, game responds {cn} correct numbers and {cl} correct locations")
      
        # Win the game
        if cl == secret_len:
            print("\n- Congrats we have a winner!!! -")

            # Guesses taken to win (hints not counted)
            attempts_used = len(history)              
            if attempts_used == 1:
                first_try = 1
            else:
                first_try = 0

            # Save only winners
            save_result(player_name, attempts_used, difficulty_label, "win", first_try)

            # Kitten-shelter joke for first-try
            if first_try:
                print("🎉 First try! Consider donating $1 to a kitten shelter 😺")

            # Offer to show the leaderboard DB (loop until valid input)
            while True:
                show = input(
                    "\nType 'results' to see Top 5 best (fewest attempts), "
                    "'quit' to exit, or just press Enter to continue: "
                ).strip().lower()

                if show == "results":
                    rows = get_top5_best_attempts()
                    print_top5_table(rows)
                    break  # done with this prompt; continue finishing the win flow
                elif show == "quit":
                    print("Goodbye!")
                    return  # end the game function
                elif show == "" or show == "continue":
                    break  # player chose to just continue
                else:
                    print("Invalid option. Please type 'results', 'quit', or press Enter.")
                    # loop continues and asks again

        attempts_left -= 1
        print(f"Attempts left: {attempts_left}")

    # Loss the game
    # Check attempts_left and history elements in the end of the game; and check at the last guess in the history + the number of correct locations. 
    if attempts_left == 0 and (not history or history[-1]['CL'] != secret_len):
        print(f"\nGame Over! The player’s guess was incorrect. The secret numbers are {secret_nums}")


def main(): 
    
    # Data base > Result : Place | Name | Attempts (Top 5) Option in the end of the game
    init_db()  # make sure the DB/table exists

    # Enter your name
    player_name = input("Enter your name: ").strip() or "Player"

    while True:
        # Select Difficulty : Normal(0-7) and Hard(0-9) (loop until valid input)
        choice = input(f"Welcome {player_name}! Choose difficulty (Normal/Hard): \n").strip().lower()
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
