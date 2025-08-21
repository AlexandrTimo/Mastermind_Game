import requests
import os                # lets us read environment variables (e.g., to force fallback)
import time              # used for small sleeps between retries
from secrets import randbelow  # secure random numbers for fallback



def get_secret_digits(
    num: int = 4,                 # how many digits to fetch (e.g., 4)
    digit_min: int = 0,           # smallest allowed digit (inclusive)
    digit_max: int = 7,           # largest allowed digit (inclusive) — set to 9 for Hard mode
    timeout: float = 3.0,         # seconds to wait for the HTTP request before giving up
    retries: int = 2,             # how many times to retry if the request fails
    force_fallback: bool = False  # if True, skip the API and use local RNG (useful for offline/tests
    ):
    """
    Fetch `num` digits from RANDOM.ORG within [digit_min, digit_max].
    If anything goes wrong, return digits from a local secure fallback.

    Returns a tuple: (digits, source)
      - digits: list[int] with length == num, each between digit_min and digit_max
      - source: "random.org" or "fallback"
    """

    # If caller asks us to force fallback, or environment variable is set,
    # skip the network entirely and just return locally generated digits.
    if force_fallback or os.environ.get("RANDOM_FALLBACK") == "1":
        return _fallback_digits(num, digit_min, digit_max), "fallback"

    # RANDOM.ORG endpoint that returns integers in plain text (one per line)
    url = "https://www.random.org/integers/"

    # Query parameters the API expects
    params = {
        "num": num,               # number of integers to return
        "min": digit_min,         # minimum value (inclusive)
        "max": digit_max,         # maximum value (inclusive)
        "col": 1,                 # one number per line
        "base": 10,               # decimal numbers
        "format": "plain",        # plain text response (easy to parse)
        "rnd": "new",             # request fresh randomness
    }

    # Good practice: identify your app politely to the service
    headers = {"User-Agent": "Mastermind/0.1 (+your-github-or-email)"}

    # Try the request a few times in case of temporary network hiccups
    for attempt in range(retries + 1):  # e.g., 0,1,2 when retries=2
        try:
            # Make the HTTP GET request with a timeout so the game won't hang
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)

            # If the HTTP status code is not 200 OK, treat as failure
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}")

            # Grab the text body and strip leading/trailing whitespace/newlines
            body = resp.text.strip()

            # RANDOM.ORG sometimes returns a body starting with "Error:" when unhappy
            if body.startswith("Error:"):
                raise RuntimeError("Random.org returned an error body")

            # Split into lines, trimming each, and ignore any empty lines
            lines = [ln.strip() for ln in body.splitlines() if ln.strip() != ""]

            # We expect exactly `num` lines (one integer per line)
            if len(lines) != num:
                raise RuntimeError(f"Expected {num} lines, got {len(lines)}")

            # Convert each line to an int
            digits = [int(ln) for ln in lines]

            # Validate the range: every digit should be within [digit_min, digit_max]
            if any(d < digit_min or d > digit_max for d in digits):
                raise RuntimeError("Digit out of expected range")

            # If we reached this point, everything is valid → return API digits
            return digits, "random.org"

        except Exception:
            # If this wasn't our last try, sleep a tiny bit and retry
            if attempt < retries:
                # Simple backoff: 0.25s, 0.5s, ...
                time.sleep(0.25 * (attempt + 1))
            else:
                # We've used all retries; we'll fall back below
                break

    # If all attempts failed, generate digits locally using secure RNG
    return _fallback_digits(num, digit_min, digit_max), "fallback"


def _fallback_digits(num: int, digit_min: int, digit_max: int):
    """
    Generate `num` secure random digits locally within [digit_min, digit_max].
    Uses `secrets.randbelow`, which is cryptographically strong and unbiased.
    """
    span = digit_max - digit_min + 1                   # number of possible values
    return [digit_min + randbelow(span) for _ in range(num)]  # map 0..span-1 into the desired range


# def get_secret_digits():
#     """
#     Get 4 digits for Mastermind.

#     1) Try RANDOM.ORG (HTTP API) to get 4 numbers in 0..7, one per line.
#     2) If anything goes wrong (no internet, bad response, etc.), use a local fallback.

#     Returns:
#         (digits, source)
#         digits: list of 4 ints, each 0..7
#         source: "random.org" or "fallback"
#     """
#     # 1) Prepare the API endpoint and the parameters it expects.
#     url = "https://www.random.org/integers/"
#     params = {
#         "num": 4,          # how many numbers
#         "min": 0,          # minimum value
#         "max": 7,          # maximum value
#         "col": 1,          # one number per line
#         "base": 10,        # decimal numbers
#         "format": "plain", # 'plain' = simple text, easy to parse
#         "rnd": "new",      # get fresh random numbers
#     }

#     try:
#         # 2) Call the API. Use a short timeout so the game doesn't hang forever.
#         resp = requests.get(url, params=params, timeout=3)

#         # 3) Basic checks: HTTP must be 200 OK and body must not start with "Error:"
#         if resp.status_code != 200:
#             raise ValueError("Random.org returned non-200 status")
#         body = resp.text.strip()
#         if body.startswith("Error:"):
#             raise ValueError("Random.org returned an error message")

#         # 4) Split into lines and remove any empty lines.
#         lines = [ln.strip() for ln in body.splitlines() if ln.strip()]

#         # We expect exactly 4 numbers
#         if len(lines) != 4:
#             raise ValueError("Expected 4 lines from Random.org")

#         # 5) Convert each line to an int and ensure it is between 0 and 7.
#         digits = []
#         for ln in lines:
#             n = int(ln)  # will raise ValueError if ln isn't a number
#             if n < 0 or n > 7:
#                 raise ValueError("Number out of range 0..7")
#             digits.append(n)

#         # If everything passed, return the digits from the API.
#         return digits, "random.org"

#     except Exception:
#         # 6) Fallback: if anything fails above, generate 4 digits locally (0..7).
#         fallback_digits = [randbelow(8) for _ in range(4)]
#         return fallback_digits, "fallback"