DEFAULT_EXAMPLE = '''
numbers = [1, 2, 3]
total = 0

for number in numbers:
    total = total + number

print("Total:", total)

count = 3
while count > 0:
    print(count)
    count = count - 1
'''


BROKEN_EXAMPLE = '''
numbers = [1, 2, 3]
total = 0

for number in numbers
    total = total + number

print("Total:", total)

count = 3
while count > 0:
    print(count)
'''