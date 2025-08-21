'''
Game initializes and selects “0 1 3 5”
Player guesses “2 2 4 6”, game responds “all incorrect”
Player guesses “0 2 4 6”, game responds “1 correct number and 1 correct location”
Player guesses “2 2 1 1”, game responds “1 correct number and 0 correct location”
Player guesses “0 1 5 6”, game responds “3 correct numbers and 2 correct location”
'''

def score_guess(secret_nums : list, num_check: list):

    print(f'Secret : {secret_nums}')
    cl = 0
    cn = 0
    # duplicates = set()
    secret_freq = {}
    
    # Count location matches
    for i in range(4):
        if secret_nums[i] == num_check[i]:
            cl += 1

    for el in secret_nums:
        secret_freq[el] = secret_freq.get(el, 0) + 1

    for el in num_check:
        if el in secret_freq:
            if secret_freq.get(el, 0) > 0:
                secret_freq[el] -= 1
                cn += 1

    return (cn, cl)