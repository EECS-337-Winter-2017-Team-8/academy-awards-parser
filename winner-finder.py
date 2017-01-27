print("Hello World")

with open("goldenglobes.tab") as f:
    for line in f:
        if ("RT @goldenglobes" in line):
            print(line)


