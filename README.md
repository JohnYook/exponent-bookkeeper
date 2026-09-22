Exponent Bookkeeper exercise

Reads in a simulated transaction stream csv file and outputs a ledger.

Run with:
./run.sh
(or ./run.sh <input_file>)

Outputs "ledger.csv"

Run tests with:
./test.sh

What I found unclear:
"Money moving between the operator's own accounts is a transfer. Card payments from the bank account, moves to and from savings, both legs. Category Transfer, needs_review = false. Not an expense, not income. The memo will say PAYMENT or TRANSFER."

Does this mean Categories needs to include a "Transfer" category? I chose to interpret it as yes.

Where I used AI:
1. For initial setup, stub TransactionProcessor class, etc. Just to save on some typing.
2. Likewise to create some enums, etc. Copied and pasted merchant list into claude code and asked it to create a dict for it.
3. To create tests. I copied and pasted the business rules and asked it to create tests covering all those cases. If I had more time I would have looked over the test cases much more carefully.
