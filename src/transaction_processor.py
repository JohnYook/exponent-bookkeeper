import constants

class TransactionProcessor:
    merchant_categories = constants.MERCHANT_CATEGORIES

    def __init__(self):
        self.transaction_ids = set()
        self.ledger = []

    def process(self, line):
        # split line by comma
        fields = line.split(',')
        if len(fields) != 7:
            raise ValueError("Invalid line: " + line)

        transaction_id = fields[0].upper()
        sync_batch = fields[1]
        date = fields[2]
        account = fields[3].upper()
        merchant = fields[4].upper()
        memo = fields[5].upper()
        amount = float(fields[6])

        # TODO: add real code to process line by line
        self.ledger.append({
            'transaction_id': transaction_id,
            'sync_batch': sync_batch,
            'date': date,
            'account': account,
            'merchant': merchant,
            'memo': memo,
            'amount': amount
        })

    def get_ledger(self):
        return self.ledger