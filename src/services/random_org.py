import requests
from requests import exceptions as req_exc
from secrets import randbelow
from typing import List, Tuple


def get_secret_digits(num: int = 4, digit_min: int = 0, digit_max: int = 7) -> Tuple[List[int], str]:
    """
    Try RANDOM.ORG once to get `num` integers in [digit_min..digit_max].
    If anything fails, fall back to local secure random.
    Returns: (digits, source) where source is "random.org" or "fallback".
    """
    url = "https://www.random.org/integers/"
    params = {
        "num": num,         # how many numbers we want
        "min": digit_min,   # smallest allowed digit (inclusive)
        "max": digit_max,   # largest allowed digit (inclusive)
        "col": 1,           # one number per line
        "base": 10,         # decimal numbers
        "format": "plain",  # plain text response
        "rnd": "new",       # fresh randomness
    }
    headers = {"User-Agent": "Mastermind/0.1 (+contact-or-repo)"}

    # helper: print reason, prompt Enter, then produce fallback digits
    def _fallback_with_prompt(reason_msg: str) -> Tuple[List[int], str]:
        if reason_msg:
            print(reason_msg)
        try:
            input("Press Enter to launch local generator — fallback...\n")
        except EOFError:
            pass  # non-interactive env (tests/CI)
        print("Running game locally — fallback version.")
        span = digit_max - digit_min + 1
        fallback_digits = []
        for _ in range(num):
            # randbelow(span) returns 0..(span-1). Shift by digit_min to match our range.
            fallback_digits.append(digit_min + randbelow(span))
        return fallback_digits, "fallback"

    # Basic parameter sanity (prevents bad span in fallback)
    if num <= 0 or digit_min > digit_max:
        return _fallback_with_prompt("Bad parameters to RNG (num must be >= 1 and min <= max).")

    try:
        # 1) Make the HTTP request. Short timeout so the game doesn't hang.
        resp = requests.get(url, params=params, headers=headers, timeout=3)

        # 2) Must be HTTP 200 OK.
        if resp.status_code != 200:
            raise ValueError(f"URL incorrect or has bad response (HTTP {resp.status_code}).")

        # 3) Get the response text and remove spaces at the ends.
        body = resp.text.strip()

        # 4) RANDOM.ORG sends error messages starting with "Error:"
        if body.startswith("Error:"):
            first_line = body.splitlines()[0]
            raise ValueError(f"Random.org error body: {first_line}")

        # 5) Split into lines and keep only non-empty lines (some responses have a blank at the end).
        raw_lines = body.splitlines()
        lines = []
        for line in raw_lines:
            cleaned = line.strip()
            if cleaned != "":
                lines.append(cleaned)

        # 6) We expect exactly `num` lines.
        if len(lines) != num:
            raise ValueError("Wrong number of lines in response")

        # 7) Convert each line to an int and check the range.
        digits = []
        for item in lines:
            # Convert text like "5" to int 5
            try:
                value = int(item)
            except ValueError:
                raise ValueError("Non-numeric value in response")

            # Make sure it is inside our chosen range
            if value < digit_min or value > digit_max:
                raise ValueError("Value out of allowed range")

            digits.append(value)

        # 8) Everything looks good → use the API digits.
        return digits, "random.org"

    except req_exc.RequestException as e:
        # 9) Covers DNS errors, timeouts, connection errors > secure local fallback.
        return _fallback_with_prompt(f"URL incorrect or has bad response: {e}")
        
    except Exception as e:
        # Any other parsing/validation error
        return _fallback_with_prompt(str(e))
