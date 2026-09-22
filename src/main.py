import sys

if len(sys.argv) != 2:
    print("Usage: python3 src/main.py <input_file>")
    sys.exit(1)

with open(sys.argv[1]) as input_file:
    for line in input_file:
        # TODO: add real code to process line by line
        print(line)




