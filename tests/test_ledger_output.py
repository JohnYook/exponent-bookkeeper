"""The shape of the ledger we hand back.

Column order, formatting and row order all have to match the sample in
expected_first_15.csv, so these assert on the written file rather than on
the in-memory dict.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from transaction_processor import TransactionProcessor

HEADER = "transaction_id,date,type,category,amount,needs_review"


def write_and_read(processor):
    """write_out_ledger() writes ./ledger.csv, so run it somewhere disposable."""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            processor.write_out_ledger()
            return Path(tmp, "ledger.csv").read_text(encoding="utf-8").splitlines()
        finally:
            os.chdir(cwd)


def line(id, batch=1, date="2026-08-03", account="card", merchant="SYSCO PHILA", memo="SYSCO PHILA", amount="100.00"):
    return f"{id},{batch},{date},{account},{merchant},{memo},{amount}\n"


class TestLedgerFormat(unittest.TestCase):
    def test_the_header_row(self):
        processor = TransactionProcessor()
        processor.process(line("txn_1001"))

        self.assertEqual(write_and_read(processor)[0], HEADER)

    def test_amounts_keep_two_decimal_places(self):
        """-6120.30 must not be written as -6120.3."""
        processor = TransactionProcessor()
        processor.process(
            line("txn_1004", account="bank", merchant="TOAST PAYOUT",
                 memo="TOAST INC DAILY PAYOUT", amount="-6120.30")
        )

        self.assertIn("-6120.30", write_and_read(processor)[1])

    def test_needs_review_is_lowercase(self):
        processor = TransactionProcessor()
        processor.process(line("txn_1006", merchant="AMZN MKTP", memo="AMAZON", amount="84.12"))

        self.assertTrue(write_and_read(processor)[1].endswith(",true"))

    def test_needs_review_false_is_lowercase_too(self):
        processor = TransactionProcessor()
        processor.process(line("txn_1001"))

        self.assertTrue(write_and_read(processor)[1].endswith(",false"))

    def test_rows_come_out_in_transaction_id_order(self):
        processor = TransactionProcessor()
        for id in ["txn_1003", "txn_1001", "txn_1002"]:
            processor.process(line(id))

        ids = [row.split(",")[0] for row in write_and_read(processor)[1:]]
        self.assertEqual(ids, ["txn_1001", "txn_1002", "txn_1003"])


class TestAgainstTheProvidedSample(unittest.TestCase):
    """End to end: the real feed against the 15 rows we were given."""

    def setUp(self):
        self.transactions = REPO_ROOT / "transactions.csv"
        self.expected = REPO_ROOT / "expected_first_15.csv"
        if not (self.transactions.exists() and self.expected.exists()):
            self.skipTest("sample files not present")

    def test_first_fifteen_rows_match(self):
        processor = TransactionProcessor()
        with open(self.transactions, encoding="utf-8") as handle:
            for row in handle:
                if row.startswith("id,sync_batch,date"):
                    continue
                processor.process(row)

        actual = write_and_read(processor)[:16]
        expected = self.expected.read_text(encoding="utf-8").splitlines()[:16]

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
