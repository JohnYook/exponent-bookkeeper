import constants

class TransactionProcessor:
    merchant_categories = constants.MERCHANT_CATEGORIES

    def __init__(self):
        self.transaction_ids = set()
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

        enter_transaction(
            id = transaction_id,
            batch = sync_batch,
            date = date,
            account = account,
            merchant = merchant,
            memo = memo,
            amount = amount
        )

    def enter_transaction(id:, batch:, date:, account:, merchant:, memo:, amount:):
        if id not in self.ledger or self.ledger[id]['batch'] < batch:
            transaction_type, type_needs_review = determine_type(account = account, memo = memo, amount = amount)
            category, cat_needs_review = get_category(merchant)

            self.ledger[id]  = {
                'batch': batch,
                'date': date,
                'type': transaction_type,
                'category': category,
                'amount': amount,
                'needs_review': type_needs_review or cat_needs_review 
            }                
        # else ignore?


    def determine_type(account:, memo:, amount:):
        # Never returning needs_review = True atm.
        if "PAYMENT" in memo or "TRANSFER" in memo:
            return constants.TransactionType(TRANSFER), False
        elif account == constants.AccountType(CARD) && amount < 0:
            return constants.TransactionType(REFUND), False
        elif account == constants.AccountType(BANK) && amount < 0:
            return constants.TransactionType(DEPOSIT), False
        else:
            return constant.TransactionType(PURCHASE), False


    def get_category(merchant):
        for key, category in self.merchant_categories.items():
            if merchant.startswith(key):
                return category, False
        return constants.Category(UNCATEGORIZED), True


    def write_out_ledger(self):
        with open('ledger.csv', 'w', encoding='utf-8') as file:
            transaction_ids = self.ledger.keys()
            transaction_ids.sort()

            file.write("transaction_id,date,type,category,amount,needs_review\n")
            for id in transaction_ids:
                entry = self.ledger[id]
                date = entry["date"]
                transaction_type = entry["type"]
                category = entry["category"]
                amount = entry["amount"]
                needs_review = entry["needs_review"]
                file.write(f"{id},{date},{transaction_type},{category},{amount},{needs_review}\n")
