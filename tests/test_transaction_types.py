"""Rules 2 and 4-7: how a transaction gets its type.

  2. Positive is money leaving the operator, negative is money coming in,
     on both accounts.
  4. Money moving between the operator own accounts is a transfer, both
     legs. Category Transfer, needs_review = false.
  5. A negative on the card that is not a card payment is a refund, and
     keeps the category the purchase would have had.
  6. A negative on the bank that is not a transfer is a deposit.
  7. Everything else is a purchase.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from transaction_processor import TransactionProcessor


def entry_for(account, merchant, memo, amount, id="txn_1001"):
    processor = TransactionProcessor()
    processor.process(
        f"{id},1,2026-08-03,{account},{merchant},{memo},{amount}\n"
    )
    return processor.ledger[id]


class TestAmountSign(unittest.TestCase):
    """Rule 2: same convention on both accounts."""

    def test_money_leaving_stays_positive(self):
        entry = entry_for("card", "SYSCO PHILA 8827", "SYSCO PHILA 8827", "1842.17")
        self.assertEqual(float(entry["amount"]), 1842.17)

    def test_money_arriving_stays_negative(self):
        entry = entry_for("bank", "TOAST PAYOUT", "TOAST INC DAILY PAYOUT", "-6120.30")
        self.assertEqual(float(entry["amount"]), -6120.30)


class TestTransfers(unittest.TestCase):
    """Rule 4: both legs of an internal move."""

    def test_card_payment_leaving_the_bank_account_is_a_transfer(self):
        entry = entry_for("bank", "CHASE CARD", "CHASE CARD PAYMENT", "3500.00")
        self.assertEqual(entry["type"], "transfer")

    def test_the_card_leg_of_that_payment_is_also_a_transfer(self):
        """Negative on the card, but a payment -- so not a refund."""
        entry = entry_for("card", "CHASE CARD", "PAYMENT THANK YOU", "-3500.00")
        self.assertEqual(entry["type"], "transfer")

    def test_a_move_to_savings_is_a_transfer(self):
        entry = entry_for("bank", "SAVINGS", "TRANSFER TO SAVINGS", "5000.00")
        self.assertEqual(entry["type"], "transfer")

    def test_a_move_from_savings_is_a_transfer_not_a_deposit(self):
        entry = entry_for("bank", "SAVINGS", "TRANSFER FROM SAVINGS", "-5000.00")
        self.assertEqual(entry["type"], "transfer")

    def test_a_transfer_is_categorized_as_transfer(self):
        entry = entry_for("bank", "CHASE CARD", "CHASE CARD PAYMENT", "3500.00")
        self.assertEqual(entry["category"], "Transfer")

    def test_a_transfer_is_never_flagged_for_review(self):
        """Even though the merchant is not on the list."""
        entry = entry_for("bank", "CHASE CARD", "CHASE CARD PAYMENT", "3500.00")
        self.assertFalse(entry["needs_review"])


class TestRefunds(unittest.TestCase):
    """Rule 5: negative on the card, not a payment."""

    def test_a_negative_on_the_card_is_a_refund(self):
        entry = entry_for("card", "US FOODS 2201", "US FOODS 2201", "-412.75")
        self.assertEqual(entry["type"], "refund")

    def test_a_refund_keeps_the_category_the_purchase_would_get(self):
        entry = entry_for("card", "US FOODS 2201", "US FOODS 2201", "-412.75")
        self.assertEqual(entry["category"], "Food & beverage")

    def test_a_refund_is_not_a_deposit(self):
        entry = entry_for("card", "US FOODS 2201", "US FOODS 2201", "-412.75")
        self.assertNotEqual(entry["type"], "deposit")


class TestDeposits(unittest.TestCase):
    """Rule 6: negative on the bank, not a transfer."""

    def test_a_sales_payout_is_a_deposit(self):
        entry = entry_for("bank", "TOAST PAYOUT", "TOAST INC DAILY PAYOUT", "-6120.30")
        self.assertEqual(entry["type"], "deposit")

    def test_a_delivery_payout_is_a_deposit(self):
        entry = entry_for("bank", "DOORDASH PAYOUT", "DOORDASH INC PAYOUT", "-2210.45")
        self.assertEqual(entry["type"], "deposit")

    def test_a_deposit_keeps_its_merchant_category(self):
        entry = entry_for("bank", "TOAST PAYOUT", "TOAST INC DAILY PAYOUT", "-6120.30")
        self.assertEqual(entry["category"], "Card sales")


class TestPurchases(unittest.TestCase):
    """Rule 7: everything else."""

    def test_a_positive_card_charge_is_a_purchase(self):
        entry = entry_for("card", "SYSCO PHILA 8827", "SYSCO PHILA 8827", "1842.17")
        self.assertEqual(entry["type"], "purchase")

    def test_a_positive_bank_debit_is_a_purchase(self):
        entry = entry_for("bank", "MAINLINE PROPERTIES", "RENT AUG", "8500.00")
        self.assertEqual(entry["type"], "purchase")

    def test_an_autopay_memo_is_not_a_transfer(self):
        """AUTOPAY contains PAY but is not PAYMENT."""
        entry = entry_for(
            "bank", "METRO GAS & ELECTRIC", "AUTOPAY METRO GAS & ELECTRIC", "1288.40"
        )
        self.assertEqual(entry["type"], "purchase")
        self.assertEqual(entry["category"], "Utilities")

    def test_an_unknown_merchant_is_still_a_purchase(self):
        entry = entry_for("card", "AMZN MKTP US*2K4X9", "AMAZON MARKETPLACE", "84.12")
        self.assertEqual(entry["type"], "purchase")
        self.assertEqual(entry["category"], "Uncategorized")
        self.assertTrue(entry["needs_review"])


if __name__ == "__main__":
    unittest.main()
