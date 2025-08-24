import pytest
from src.cli.game import parse_guess_line

def test_compact_input_ok():
    assert parse_guess_line("1425") == [1, 4, 2, 5]

def test_mixed_spaces_commas_ok():
    assert parse_guess_line("1,4   2  5") == [1, 4, 2, 5]

def test_explodes_runs_ok():
    # "22" becomes 2 and 2
    assert parse_guess_line("0, 4 22") == [0, 4, 2, 2]

def test_length_error():
    with pytest.raises(ValueError):
        parse_guess_line("1 2 3")   # only 3 digits

def test_range_error_normal_mode():
    # Default digit_max=7, so "8" should fail
    with pytest.raises(ValueError):
        parse_guess_line("1 4 2 8")

def test_hard_mode_allows_9():
    # In Hard (0..9), 9 is allowed
    assert parse_guess_line("1 9 2 5", secret_len=4, digit_min=0, digit_max=9) == [1, 9, 2, 5]
