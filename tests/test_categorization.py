"""Rule 3: category comes from the merchant list.

Match when the merchant field *starts with* a name on the list, ignoring
case. Store numbers and other junk on the end are normal. A merchant that
is not on the list is Uncategorized and needs_review = true.
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
    memo="",
    amount="100.00",
):
    memo = memo or merchant
    return f"{id},{batch},{date},{account},{merchant},{memo},{amount}\n"


def categorize(merchant):
    """Run one transaction through and return its ledger entry."""
    processor = TransactionProcessor()
    processor.process(line(merchant=merchant))
    return processor.ledger["txn_1001"]


class TestMerchantMatching(unittest.TestCase):
    def test_an_exact_merchant_name_matches(self):
        self.assertEqual(categorize("ECOLAB")["category"], "Cleaning & supplies")

    def test_a_trailing_store_number_still_matches(self):
        self.assertEqual(categorize("US FOODS 2201")["category"], "Food & beverage")

    def test_trailing_junk_still_matches(self):
        self.assertEqual(
            categorize("HOME DEPOT #4102")["category"], "Repairs & maintenance"
        )

    def test_matching_ignores_case(self):
        self.assertEqual(categorize("sysco phila 8827")["category"], "Food & beverage")

    def test_mixed_case_matches(self):
        self.assertEqual(categorize("Restaurant Depot 77")["category"], "Food & beverage")

    def test_a_matched_merchant_is_not_flagged(self):
        self.assertFalse(categorize("GUSTO PAYROLL")["needs_review"])

    def test_the_name_must_be_a_prefix_not_just_present(self):
        """`SYSCO` appearing later in the string is not a match."""
        entry = categorize("PHILA SYSCO SUPPLY")
        self.assertEqual(entry["category"], "Uncategorized")

    def test_an_unknown_merchant_is_uncategorized(self):
        self.assertEqual(categorize("AMZN MKTP US*2K4X9")["category"], "Uncategorized")

    def test_an_unknown_merchant_is_flagged_for_review(self):
        self.assertTrue(categorize("AMZN MKTP US*2K4X9")["needs_review"])


class TestEveryMerchantOnTheList(unittest.TestCase):
    """One row per line of the merchant table."""

    CASES = [
        ("SYSCO PHILA 8827", "Food & beverage"),
        ("US FOODS 2201", "Food & beverage"),
        ("RESTAURANT DEPOT 118", "Food & beverage"),
        ("METRO GAS & ELECTRIC", "Utilities"),
        ("CITY WATER DEPT", "Utilities"),
        ("COMCAST BUSINESS 55", "Utilities"),
        ("HOME DEPOT #4102", "Repairs & maintenance"),
        ("ECOLAB 9931", "Cleaning & supplies"),
        ("WEBSTAURANT STORE", "Smallwares & supplies"),
        ("GUSTO", "Payroll"),
        ("INDEED", "Hiring"),
        ("7SHIFTS", "Software"),
        ("MAINLINE PROPERTIES", "Rent"),
        ("TOAST PAYOUT", "Card sales"),
        ("DOORDASH PAYOUT", "Delivery sales"),
        ("UBER EATS PAYOUT", "Delivery sales"),
    ]

    def test_each_merchant_maps_to_its_category(self):
        for merchant, expected in self.CASES:
            with self.subTest(merchant=merchant):
                self.assertEqual(categorize(merchant)["category"], expected)


if __name__ == "__main__":
    unittest.main()
