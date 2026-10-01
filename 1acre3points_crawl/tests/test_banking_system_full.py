import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "practice"
    / "anthropic"
    / "banking_system_full.py"
)
SPEC = importlib.util.spec_from_file_location("banking_system_full", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
BankingSystem = MODULE.BankingSystem
ONE_DAY_MS = MODULE.ONE_DAY_MS


class BankingSystemTests(unittest.TestCase):
    def test_level_1_is_atomic(self):
        bank = BankingSystem()
        self.assertTrue(bank.create_account(1, "A"))
        self.assertFalse(bank.create_account(2, "A"))
        self.assertTrue(bank.create_account(3, "B"))
        self.assertEqual(bank.deposit(4, "A", 100), 100)
        self.assertIsNone(bank.deposit(5, "missing", 10))
        self.assertIsNone(bank.transfer(6, "A", "A", 10))
        self.assertIsNone(bank.transfer(7, "A", "B", 101))
        self.assertEqual(bank.transfer(8, "A", "B", 40), 60)
        self.assertEqual(bank.deposit(9, "B", 1), 41)

    def test_top_spenders_tie_break_and_failed_operations(self):
        bank = BankingSystem()
        for timestamp, account_id in enumerate(("C", "A", "B"), 1):
            bank.create_account(timestamp, account_id)
        bank.deposit(4, "A", 100)
        bank.deposit(5, "B", 100)
        bank.deposit(6, "C", 100)
        bank.transfer(7, "A", "C", 40)
        bank.transfer(8, "B", "C", 40)
        bank.transfer(9, "C", "A", 10)
        bank.transfer(10, "C", "A", 1000)  # failure does not count
        self.assertEqual(
            bank.top_spenders(11, 10),
            ["A(40)", "B(40)", "C(10)"],
        )

    def test_cashback_boundary_idempotence_and_id_sequence(self):
        bank = BankingSystem()
        bank.create_account(1, "A")
        bank.create_account(2, "B")
        bank.deposit(3, "A", 1000)
        self.assertIsNone(bank.pay(4, "B", 1))  # failed pay uses no ID
        payment = bank.pay(5, "A", 501)
        self.assertEqual(payment, "payment1")
        self.assertEqual(bank.get_payment_status(6, "A", payment), "IN_PROGRESS")
        self.assertEqual(
            bank.get_payment_status(5 + ONE_DAY_MS, "A", payment),
            "CASHBACK_RECEIVED",
        )
        # The 10-unit cashback is posted once even when status is read again.
        self.assertEqual(
            bank.get_payment_status(5 + ONE_DAY_MS + 1, "A", payment),
            "CASHBACK_RECEIVED",
        )
        self.assertEqual(bank.deposit(5 + ONE_DAY_MS + 2, "A", 1), 510)

    def test_cashback_is_processed_before_operation_at_same_timestamp(self):
        bank = BankingSystem()
        bank.create_account(1, "A")
        bank.deposit(2, "A", 100)
        payment = bank.pay(3, "A", 100)  # cashback = 2
        due = 3 + ONE_DAY_MS
        self.assertEqual(bank.deposit(due, "A", 5), 7)
        self.assertEqual(
            bank.get_payment_status(due + 1, "A", payment),
            "CASHBACK_RECEIVED",
        )

    def test_merge_moves_balance_spending_payments_and_future_cashback(self):
        bank = BankingSystem()
        bank.create_account(1, "A")
        bank.create_account(2, "B")
        bank.deposit(3, "A", 200)
        bank.deposit(4, "B", 300)
        payment = bank.pay(5, "B", 101)  # B=199, cashback 2 later
        self.assertTrue(bank.merge_accounts(6, "A", "B"))
        self.assertIsNone(bank.get_payment_status(7, "B", payment))
        self.assertEqual(bank.get_payment_status(8, "A", payment), "IN_PROGRESS")
        due = 5 + ONE_DAY_MS
        self.assertEqual(
            bank.get_payment_status(due, "A", payment),
            "CASHBACK_RECEIVED",
        )
        self.assertEqual(bank.deposit(due + 1, "A", 1), 402)
        self.assertEqual(bank.top_spenders(due + 2, 2), ["A(101)"])

    def test_merge_history_and_recreated_id_have_separate_lifetimes(self):
        bank = BankingSystem()
        bank.create_account(1, "A")
        bank.create_account(2, "B")
        bank.deposit(3, "A", 100)
        bank.deposit(4, "B", 50)
        bank.transfer(5, "A", "B", 20)  # A=80, B=70
        self.assertEqual(bank.get_balance(6, "B", 4), 50)
        self.assertEqual(bank.get_balance(7, "B", 5), 70)
        self.assertTrue(bank.merge_accounts(8, "A", "B"))  # A=150
        self.assertEqual(bank.get_balance(9, "A", 7), 80)
        self.assertEqual(bank.get_balance(10, "A", 8), 150)
        self.assertEqual(bank.get_balance(11, "B", 7), 70)
        self.assertIsNone(bank.get_balance(12, "B", 8))
        self.assertTrue(bank.create_account(13, "B"))
        self.assertEqual(bank.get_balance(14, "B", 14), 0)
        self.assertEqual(bank.get_balance(15, "B", 7), 70)

    def test_invalid_merge_has_no_side_effect(self):
        bank = BankingSystem()
        bank.create_account(1, "A")
        bank.deposit(2, "A", 10)
        self.assertFalse(bank.merge_accounts(3, "A", "A"))
        self.assertFalse(bank.merge_accounts(4, "A", "missing"))
        self.assertEqual(bank.deposit(5, "A", 1), 11)


if __name__ == "__main__":
    unittest.main()
