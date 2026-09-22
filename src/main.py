import sys
from transaction_processor import TransactionProcessor

if len(sys.argv) != 2:
    print("Usage: python3 src/main.py <input_file>")
    sys.exit(1)

with open(sys.argv[1]) as input_file:

    transaction_processor = TransactionProcessor()

    for line in input_file:
        if line.startswith("id,sync_batch,date"):
            continue
        transaction_processor.process(line)

    transaction_processor.write_out_ledger()