import requests
from secrets import randbelow

# def get_secret_digits(num=SECRET_LEN, min=0, max=digit_max):
def get_secret_digits():
    """
    Get 4 digits for Mastermind.

    1) Try RANDOM.ORG (HTTP API) to get 4 numbers in 0..7, one per line.
    2) If anything goes wrong (no internet, bad response, etc.), use a local fallback.

    Returns:
        (digits, source)
        digits: list of 4 ints, each 0..7
        source: "random.org" or "fallback"
    """
    # 1) Prepare the API endpoint and the parameters it expects.
    url = "https://www.random.org/integers/"
    params = {
        "num": 4,          # how many numbers
        "min": 0,          # minimum value
        "max": 7,          # maximum value
        "col": 1,          # one number per line
        "base": 10,        # decimal numbers
        "format": "plain", # 'plain' = simple text, easy to parse
        "rnd": "new",      # get fresh random numbers
    }

    try:
        # 2) Call the API. Use a short timeout so the game doesn't hang forever.
        resp = requests.get(url, params=params, timeout=3)

        # 3) Basic checks: HTTP must be 200 OK and body must not start with "Error:"
        if resp.status_code != 200:
            raise ValueError("Random.org returned non-200 status")
        body = resp.text.strip()
        if body.startswith("Error:"):
            raise ValueError("Random.org returned an error message")

        # 4) Split into lines and remove any empty lines.
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]

        # We expect exactly 4 numbers
        if len(lines) != 4:
            raise ValueError("Expected 4 lines from Random.org")

        # 5) Convert each line to an int and ensure it is between 0 and 7.
        digits = []
        for ln in lines:
            n = int(ln)  # will raise ValueError if ln isn't a number
            if n < 0 or n > 7:
                raise ValueError("Number out of range 0..7")
            digits.append(n)

        # If everything passed, return the digits from the API.
        return digits, "random.org"

    except Exception:
        # 6) Fallback: if anything fails above, generate 4 digits locally (0..7).
        fallback_digits = [randbelow(8) for _ in range(4)]
        return fallback_digits, "fallback"