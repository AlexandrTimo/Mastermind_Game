list1 = ["bob", "steve", "jessica", "karl", "alex"]
list_spaces = [" ", ",", ".", "!", "?", "-"]

for word in list1:
    counter = 0 
    if word not in list_spaces:
        for ch in word:
            counter += 1
            
    print(f"The word {word} has {counter} characters")