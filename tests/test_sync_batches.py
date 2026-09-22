"""Rule 1: the feed re-syncs.

The same id can arrive in more than one sync_batch, sometimes with a
different memo or amount (pending vs posted). One id, one ledger line,
and the version from the highest sync_batch is the one that survives.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from transaction_processor import TransactionProcessor


def line(
    id="txn_1001",
    batch=1,
    date="2026-08-03",
    account="card",
    merchant="SYSCO PHILA 8827",
    memo="SYSCO PHILA 8827",
    amount="100.00",
):
    return f"{id},{batch},{date},{account},{merchant},{memo},{amount}\n"


class TestResyncedTransactions(unittest.TestCase):
    def test_an_id_seen_twice_produces_one_ledger_line(self):
        processor = TransactionProcessor()
        processor.process(line(id="txn_1020", batch=1, amount="100.00"))
        processor.process(line(id="txn_1020", batch=2, amount="118.40"))

        self.assertEqual(len(processor.ledger), 1)

    def test_the_highest_batch_wins(self):
        processor = TransactionProcessor()
        processor.process(line(id="txn_1020", batch=1, amount="100.00"))
        processor.process(line(id="txn_1020", batch=2, amount="118.40"))

        self.assertEqual(float(processor.ledger["txn_1020"]["amount"]), 118.40)

    def test_the_highest_batch_wins_even_when_it_arrives_first(self):
        processor = TransactionProcessor()
        processor.process(line(id="txn_1020", batch=2, amount="118.40"))
        processor.process(line(id="txn_1020", batch=1, amount="100.00"))

        self.assertEqual(float(processor.ledger["txn_1020"]["amount"]), 118.40)

    def test_a_corrected_memo_is_re_evaluated_not_just_stored(self):
        """A batch-2 memo that makes it a transfer must change the type."""
        processor = TransactionProcessor()
        processor.process(
            line(id="txn_1020", batch=1, merchant="CHASE CARD", memo="PENDING")
        )
        processor.process(
            line(id="txn_1020", batch=2, merchant="CHASE CARD", memo="PAYMENT")
        )

        self.assertEqual(processor.ledger["txn_1020"]["type"], "transfer")

    def test_distinct_ids_are_kept_apart(self):
        processor = TransactionProcessor()
        processor.process(line(id="txn_1020", batch=1))
        processor.process(line(id="txn_1021", batch=1))

        self.assertEqual(len(processor.ledger), 2)
        self.assertEqual(sorted(processor.ledger), ["txn_1020", "txn_1021"])


if __name__ == "__main__":
    unittest.main()
