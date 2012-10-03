count = 0
f = open('note.py', 'r')
for line in f:
    if not line.lstrip().startswith('#') and line != "\n":
        count += 1

print(count)
