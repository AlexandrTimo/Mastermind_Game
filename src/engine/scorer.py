from src.services.random_org import get_secret_digits

'''
Game initializes and selects “0 1 3 5”
Player guesses “2 2 4 6”, game responds “all incorrect”
Player guesses “0 2 4 6”, game responds “1 correct number and 1 correct location”
Player guesses “2 2 1 1”, game responds “1 correct number and 0 correct location”
Player guesses “0 1 5 6”, game responds “3 correct numbers and 2 correct location”
'''

def random_nums():

    cl = 0
    cn = 0
    duplicates = set()
    secret_dict = {}
    # add secret numbers to dict "0 1 3 5"
    # secret_dict = {0: 0, 1: 1, 3: 2, 5: 3}
    secret_nums, status = get_secret_digits()

    # Add secret nums to the dictionary
    for el in range(len(secret_nums)):
        secret_dict[secret_nums[el]] = el
    # print(secret_dict)
    
    # Enter list of numbers 
    num_check = enter_numbers()

    # check each item in the list if index or item matched
    for el in range(len(num_check)):
        # collect seperate matches : CL(position) CN(items)
        if num_check[el] in secret_dict and num_check[el] not in duplicates:
            cn += 1
            duplicates.add(num_check[el])
            if secret_dict[num_check[el]] == el:
                cl += 1

    # Return results
    if not cl and not cn:
        return "All incorrect"    

    return f"{cn} correct number and {cl} correct location"

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

print(random_nums())
