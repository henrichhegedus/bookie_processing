import itertools

permutations = itertools.product(range(2), repeat=3)

combinations = list()
for i in permutations:
    print(i)


