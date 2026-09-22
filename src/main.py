import sys
from transaction_processor import TransactionProcessor

if len(sys.argv) != 2:
    print("Usage: python3 src/main.py <input_file>")
    sys.exit(1)

with open(sys.argv[1]) as input_file:

    transaction_processor = TransactionProcessor()

    for line in input_file:
        # TODO: add real code to process line by line
        transaction_processor.process(line)

    print(transaction_processor.get_ledger())