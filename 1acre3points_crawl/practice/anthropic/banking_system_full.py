"""Complete four-level Banking System solution.

The implementation follows the locally saved CodeSignal-style specification:

Level 1: create_account, deposit, transfer
Level 2: top_spenders
Level 3: pay, get_payment_status, delayed 2% cashback
Level 4: merge_accounts, historical get_balance

All public timestamps are expected to be increasing.  Python APIs return None
for failed integer/string operations.  A Java wrapper can translate None to -1.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


ONE_DAY_MS = 86_400_000


@dataclass(frozen=True)
class Transaction:
    """Immutable audit entry; balance snapshots remain separate."""

    timestamp: int
    sequence: int
    account_id: str
    kind: str
    delta: int
    balance_after: int
    counterparty: Optional[str] = None
    reference: Optional[str] = None


@dataclass
class Account:
    """One lifetime of an account ID.

    An ID may have multiple lifetimes because a merged-away ID may be created
    again later.  Keeping objects rather than only strings prevents a new
    account from inheriting the old account's payments or balance history.
    """

    uid: int
    account_id: str
    created_at: int
    balance: int = 0
    outgoing: int = 0
    ended_at: Optional[int] = None
    balance_history: List[Tuple[int, int]] = field(default_factory=list)
    transactions: List[Transaction] = field(default_factory=list)
    payment_ids: Set[str] = field(default_factory=set)


@dataclass
class Payment:
    payment_id: str
    amount: int
    created_at: int
    cashback_at: int
    cashback_amount: int
    owner: Account
    cashback_received: bool = False


class BankingSystem:
    """Single-threaded in-memory implementation of all four levels."""

    IN_PROGRESS = "IN_PROGRESS"
    CASHBACK_RECEIVED = "CASHBACK_RECEIVED"

    def __init__(self) -> None:
        self._active: Dict[str, Account] = {}
        self._lifetimes: Dict[str, List[Account]] = {}
        self._payments: Dict[str, Payment] = {}
        self._cashbacks: List[Tuple[int, int, str]] = []

        self._account_counter = 0
        self._payment_counter = 0
        self._transaction_counter = 0
        self._last_timestamp = -1

    # ------------------------------------------------------------------
    # Level 1
    # ------------------------------------------------------------------

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._advance(timestamp)
        if account_id in self._active:
            return False

        self._account_counter += 1
        account = Account(
            uid=self._account_counter,
            account_id=account_id,
            created_at=timestamp,
            balance_history=[(timestamp, 0)],
        )
        self._active[account_id] = account
        self._lifetimes.setdefault(account_id, []).append(account)
        self._append_transaction(account, timestamp, "CREATE", 0)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> Optional[int]:
        self._advance(timestamp)
        account = self._active.get(account_id)
        if account is None or amount <= 0:
            return None

        self._change_balance(account, timestamp, amount, "DEPOSIT")
        return account.balance

    def transfer(
        self,
        timestamp: int,
        source_account_id: str,
        target_account_id: str,
        amount: int,
    ) -> Optional[int]:
        self._advance(timestamp)
        source = self._active.get(source_account_id)
        target = self._active.get(target_account_id)

        # Validate everything before changing either account: the operation is
        # atomic even when a hidden test fails one of these conditions.
        if (
            source is None
            or target is None
            or source is target
            or amount <= 0
            or source.balance < amount
        ):
            return None

        self._change_balance(
            source,
            timestamp,
            -amount,
            "TRANSFER_OUT",
            outgoing=amount,
            counterparty=target_account_id,
        )
        self._change_balance(
            target,
            timestamp,
            amount,
            "TRANSFER_IN",
            counterparty=source_account_id,
        )
        return source.balance

    # ------------------------------------------------------------------
    # Level 2
    # ------------------------------------------------------------------

    def top_spenders(self, timestamp: int, n: int) -> List[str]:
        self._advance(timestamp)
        if n <= 0:
            return []
        ranked = sorted(
            self._active.values(),
            key=lambda account: (-account.outgoing, account.account_id),
        )
        return [
            f"{account.account_id}({account.outgoing})"
            for account in ranked[:n]
        ]

    # ------------------------------------------------------------------
    # Level 3
    # ------------------------------------------------------------------

    def pay(self, timestamp: int, account_id: str, amount: int) -> Optional[str]:
        self._advance(timestamp)
        account = self._active.get(account_id)
        if account is None or amount <= 0 or account.balance < amount:
            return None

        # Failed payments never consume an ID.
        self._payment_counter += 1
        payment_id = f"payment{self._payment_counter}"
        cashback_at = timestamp + ONE_DAY_MS
        payment = Payment(
            payment_id=payment_id,
            amount=amount,
            created_at=timestamp,
            cashback_at=cashback_at,
            cashback_amount=amount * 2 // 100,
            owner=account,
        )
        self._payments[payment_id] = payment
        account.payment_ids.add(payment_id)

        self._change_balance(
            account,
            timestamp,
            -amount,
            "PAYMENT",
            outgoing=amount,
            reference=payment_id,
        )
        heapq.heappush(
            self._cashbacks,
            (cashback_at, self._payment_counter, payment_id),
        )
        return payment_id

    def get_payment_status(
        self,
        timestamp: int,
        account_id: str,
        payment_id: str,
    ) -> Optional[str]:
        self._advance(timestamp)
        account = self._active.get(account_id)
        payment = self._payments.get(payment_id)
        if account is None or payment is None or payment.owner is not account:
            return None
        return (
            self.CASHBACK_RECEIVED
            if payment.cashback_received
            else self.IN_PROGRESS
        )

    # ------------------------------------------------------------------
    # Level 4
    # ------------------------------------------------------------------

    def merge_accounts(
        self,
        timestamp: int,
        account_id_1: str,
        account_id_2: str,
    ) -> bool:
        """Merge account 2 into account 1."""

        self._advance(timestamp)
        destination = self._active.get(account_id_1)
        source = self._active.get(account_id_2)
        if destination is None or source is None or destination is source:
            return False

        source_balance = source.balance
        self._change_balance(
            destination,
            timestamp,
            source_balance,
            "MERGE_IN",
            counterparty=account_id_2,
        )
        destination.outgoing += source.outgoing

        # Preserve all audit records.  Historical balance queries do not use
        # this merged list; they use per-lifetime snapshots below, so account 2
        # still has its own correct pre-merge balance history.
        destination.transactions.extend(source.transactions)
        destination.transactions.sort(key=lambda entry: (entry.timestamp, entry.sequence))

        # Both pending and completed payments become queryable through account
        # 1.  Pending heap entries store only payment IDs and therefore resolve
        # the updated owner when their cashback becomes due.
        for payment_id in source.payment_ids:
            self._payments[payment_id].owner = destination
        destination.payment_ids.update(source.payment_ids)

        source.ended_at = timestamp
        del self._active[account_id_2]
        return True

    def get_balance(
        self,
        timestamp: int,
        account_id: str,
        time_at: int,
    ) -> Optional[int]:
        self._advance(timestamp)
        if time_at > timestamp:
            return None

        account = self._lifetime_at(account_id, time_at)
        if account is None:
            return None

        history = account.balance_history
        left, right = 0, len(history)
        while left < right:
            middle = (left + right) // 2
            if history[middle][0] <= time_at:
                left = middle + 1
            else:
                right = middle
        return None if left == 0 else history[left - 1][1]

    # ------------------------------------------------------------------
    # Internal event processing
    # ------------------------------------------------------------------

    def _advance(self, timestamp: int) -> None:
        if timestamp < self._last_timestamp:
            raise ValueError("timestamps must be non-decreasing")

        # The specification requires cashback due at timestamp T to be posted
        # before the user operation whose timestamp is also T.
        while self._cashbacks and self._cashbacks[0][0] <= timestamp:
            due_at, _, payment_id = heapq.heappop(self._cashbacks)
            payment = self._payments[payment_id]
            if payment.cashback_received:
                continue
            payment.cashback_received = True
            self._change_balance(
                payment.owner,
                due_at,
                payment.cashback_amount,
                "CASHBACK",
                reference=payment_id,
            )

        self._last_timestamp = timestamp

    def _change_balance(
        self,
        account: Account,
        timestamp: int,
        delta: int,
        kind: str,
        *,
        outgoing: int = 0,
        counterparty: Optional[str] = None,
        reference: Optional[str] = None,
    ) -> None:
        account.balance += delta
        account.outgoing += outgoing
        self._record_balance(account, timestamp)
        self._append_transaction(
            account,
            timestamp,
            kind,
            delta,
            counterparty=counterparty,
            reference=reference,
        )

    def _record_balance(self, account: Account, timestamp: int) -> None:
        snapshot = (timestamp, account.balance)
        if account.balance_history and account.balance_history[-1][0] == timestamp:
            account.balance_history[-1] = snapshot
        else:
            if account.balance_history and account.balance_history[-1][0] > timestamp:
                raise AssertionError("balance history must be chronological")
            account.balance_history.append(snapshot)

    def _append_transaction(
        self,
        account: Account,
        timestamp: int,
        kind: str,
        delta: int,
        *,
        counterparty: Optional[str] = None,
        reference: Optional[str] = None,
    ) -> None:
        self._transaction_counter += 1
        account.transactions.append(
            Transaction(
                timestamp=timestamp,
                sequence=self._transaction_counter,
                account_id=account.account_id,
                kind=kind,
                delta=delta,
                balance_after=account.balance,
                counterparty=counterparty,
                reference=reference,
            )
        )

    def _lifetime_at(self, account_id: str, timestamp: int) -> Optional[Account]:
        lifetimes = self._lifetimes.get(account_id, [])
        left, right = 0, len(lifetimes)
        while left < right:
            middle = (left + right) // 2
            if lifetimes[middle].created_at <= timestamp:
                left = middle + 1
            else:
                right = middle
        if left == 0:
            return None
        account = lifetimes[left - 1]
        if account.ended_at is not None and timestamp >= account.ended_at:
            return None
        return account
