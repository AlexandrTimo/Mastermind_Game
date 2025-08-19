
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
    # add secret numbers to dict "0 1 3 5"
    secret_dict = {0: 0, 1: 1, 3: 2, 5: 3}

    # enter list of numbers 
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



def enter_numbers():
    my_list = []

    while len(my_list) < 4:

        try:
            num = int(input(f"Enter integer {len(my_list) + 1} of 4: "))
            my_list.append(num)
        except ValueError:
            print("Invalid input. Please enter an integer.")
        except 0 > num > 7:
            print("Invalid input. Please enter an integer between 0 and 7")


    return my_list

print(random_nums())
