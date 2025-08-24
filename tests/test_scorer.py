from src.engine.scorer import score_guess

def test_all_incorrect():
    # No overlapping digits at all
    secret = [0, 1, 3, 5]
    guess  = [2, 2, 4, 6]
    cn, cl = score_guess(secret, guess)
    assert cn == 0
    assert cl == 0

def test_one_number_one_location():
    # Digit 0 matches AND is in the same position (index 0)
    secret = [0, 1, 3, 5]
    guess  = [0, 2, 4, 6]
    cn, cl = score_guess(secret, guess)
    assert cn == 1
    assert cl == 1

def test_duplicates_are_handled():
    # Secret has two 1's; guess also has many 1's; overlap should be counted correctly
    secret = [1, 1, 2, 3]
    guess  = [1, 2, 1, 1]
    cn, cl = score_guess(secret, guess)
    assert cn == 3   # two 1's + one 2
    assert cl == 1   # only the first 1 is in the same position
