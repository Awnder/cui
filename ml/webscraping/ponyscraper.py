import re

file = 'tv_my_little_pony_season1.txt'

unique_people = []

with open(file, 'r') as f:
    text = f.read()
    # print(text)

    # Find all the names in the text
    names = re.findall(r'[A-Z][a-z]+:', text)
    
    names = [n.replace(':','') for n in names]

    print(set(names))