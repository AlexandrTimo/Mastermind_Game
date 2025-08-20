'''
Game initializes and selects “0 1 3 5”
Player guesses “2 2 4 6”, game responds “all incorrect”
Player guesses “0 2 4 6”, game responds “1 correct number and 1 correct location”
Player guesses “2 2 1 1”, game responds “1 correct number and 0 correct location”
Player guesses “0 1 5 6”, game responds “3 correct numbers and 2 correct location”
'''

def score_guess(secret_nums, num_check):

    cl = 0
    cn = 0
    duplicates = set()
    secret_dict = {}

    # Add secret nums to the dictionary
    for el in range(len(secret_nums)):
        secret_dict[secret_nums[el]] = el
    
    # check each item in the list if index or item matched
    for el in range(len(num_check)):
        # collect seperate matches : CL(position) CN(items)
        if num_check[el] in secret_dict and num_check[el] not in duplicates:
            cn += 1
            duplicates.add(num_check[el])
            if secret_dict[num_check[el]] == el:
                cl += 1

    return cl, cn