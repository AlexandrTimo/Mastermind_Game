from ..services.random_org import get_secret_digits

from ..engine.scorer import score_guess

def parse_guess_line(raw: str) -> list[int]:
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
        raise ValueError("Empty input. Please enter 4 digits (0–7).")

    # Case 1: compact 4 digits (e.g., "1425")
    if s.isdigit() and len(s) == 4:
        nums = [int(ch) for ch in s]
    else:
        # Case 2: any mix of commas/whitespace; explode digit-runs into single digits
        parts = s.replace(",", " ").split()
        digits = []
        for p in parts:
            if not p.isdigit():
                raise ValueError(f"Invalid token: {p!r}. Use digits 0–7 and separators (space/comma).")
            for ch in p:  # explode "22" -> "2","2"
                d = int(ch)
                if not (0 <= d <= 7):
                    raise ValueError("Digits must be between 0 and 7.")
                digits.append(d)
                if len(digits) > 4:
                    raise ValueError("Please enter exactly 4 digits.")
        nums = digits

    # Length check
    if len(nums) != 4:
        raise ValueError(f"Please enter exactly 4 numbers. Got {len(nums)}.")

    # Range check
    for n in nums:
        if not (0 <= n <= 7):
            raise ValueError("Digits must be between 0 and 7.")

    return nums

def enter_numbers() -> list[int]:
    """
    Prompts until a valid 4-digit guess is entered.
    """
    while True:
        raw = input("Enter 4 digits (0–7) e.g. 1425 or 1,4,2,5: ")
        try:
            return parse_guess_line(raw)
        except ValueError as e:
            print(e)
            # loop continues to re-prompt

def main():
    secret_nums, source = get_secret_digits()
    attempts_left = 10
    history = []
    print(f"(Secret generated via {source})")

    while attempts_left > 0:
        guess = enter_numbers()
        cn, cl = score_guess(secret_nums, guess)
        history.append({'guess': guess, 'CL' : cl, 'CN' : cn})

        if cl == 0 and cn == 0:
            print(f"Player guesses {guess}, game responds 'all incorrect'")
        else:
            print(f"Player guesses {guess}, game responds {cn} correct number and {cl} correct location")
            
        if cl == 4:
            print("Congrats we have a winner!!!")
            break

        attempts_left -= 1
        print(f"Attempts left: {attempts_left}")

        if attempts_left == 5:
            print(f"{secret_nums[0]} defently here")

    if attempts_left == 0 and cl != 4:
        print(f"Game Over! The player’s guess was incorrect. The secret numbers are {secret_nums}")
    

if __name__ == "__main__":
    main()