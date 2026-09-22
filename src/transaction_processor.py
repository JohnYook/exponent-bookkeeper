import constants

class TransactionProcessor:
    merchant_categories = constants.MERCHANT_CATEGORIES

    def __init__(self):
        self.ledger = {}

    def process(self, line):
        # split line by comma
        fields = line.split(',')
        if len(fields) != 7:
            raise ValueError("Invalid line: " + line)

        transaction_id = fields[0]
        sync_batch = int(fields[1])
        date = fields[2]
        account = fields[3].upper()
        merchant = fields[4].upper()
        memo = fields[5].upper()
        amount = float(fields[6])

        self.enter_transaction(
            transaction_id = transaction_id,
            batch = sync_batch,
            date = date,
            account = account,
            merchant = merchant,
            memo = memo,
            amount = amount
        )


    def enter_transaction(self, *, transaction_id, batch, date, account, merchant, memo, amount):
        if transaction_id not in self.ledger or self.ledger[transaction_id]['batch'] < batch:
            transaction_type, type_needs_review = self.determine_type(account, memo, amount)
            category, cat_needs_review = self.get_category(merchant)

            self.ledger[transaction_id]  = {
                'batch': batch,
                'date': date,
                'type': transaction_type,
                'category': category,
                'amount': amount,
                'needs_review': type_needs_review or cat_needs_review 
            }                
        # else ignore?


    def determine_type(self, account, memo, amount):
        # Never returning needs_review = True atm.
        if "PAYMENT" in memo or "TRANSFER" in memo:
            return constants.TransactionType.TRANSFER, False
        elif account == constants.AccountType.CARD and amount < 0:
            return constants.TransactionType.REFUND, False
        elif account == constants.AccountType.BANK and amount < 0:
            return constants.TransactionType.DEPOSIT, False
        else:
            return constants.TransactionType.PURCHASE, False


    def get_category(self, merchant):
        for key, category in self.merchant_categories.items():
            if merchant.startswith(key):
                return category, False
        return constants.Category.UNCATEGORIZED, True


    def write_out_ledger(self):
        with open('ledger.csv', 'w', encoding='utf-8') as file:
            transaction_ids = sorted(self.ledger.keys())

            file.write("transaction_id,date,type,category,amount,needs_review\n")
            for id in transaction_ids:
                entry = self.ledger[id]
                date = entry["date"]
                transaction_type = entry["type"]
                category = entry["category"]
                amount = entry["amount"]
                needs_review = entry["needs_review"]
                file.write(f"{id},{date},{transaction_type},{category},{amount},{needs_review}\n")
