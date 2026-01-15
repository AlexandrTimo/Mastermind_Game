from typing import List, Tuple

'''
Game initializes and selects “0 1 3 5”
Player guesses “2 2 4 6”, game responds “all incorrect”
Player guesses “0 2 4 6”, game responds “1 correct number and 1 correct location”
Player guesses “2 2 1 1”, game responds “1 correct number and 0 correct location”
Player guesses “0 1 5 6”, game responds “3 correct numbers and 2 correct location”
'''


def score_guess(secret_nums: List, guess_nums: List) -> Tuple:

    # print(f'Secret : {secret_nums}')
    cl = 0
    cn = 0
    secret_freq = {}
    
    # Count location matches
    for i in range(4):
        if secret_nums[i] == guess_nums[i]:
            cl += 1

    # Travers secret_nums count duplictes and store them in the dict > 2234
    for el in secret_nums:
        secret_freq[el] = secret_freq.get(el, 0) + 1 # {2: 2, 3: 1, 4: 1}

    # Travers num_check and decrese dict values
    for el in guess_nums: # > 2234
        if el in secret_freq:
            if secret_freq.get(el, 0) > 0: # {2: 0, 3: 0, 4: 0}
                secret_freq[el] -= 1
                cn += 1

    return (cn, cl)
