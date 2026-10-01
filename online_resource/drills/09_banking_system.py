from __future__ import annotations

import heapq
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Account:
    uid: int
    account_id: str
    created_at: int
    balance: int = 0          # Available balance; held money is excluded.
    held: int = 0
    outgoing: int = 0         # Completed payments and accepted transfers.
    ended_at: int | None = None
    history: list[tuple[int, int]] = field(default_factory=list)
    activity: dict[int, int] = field(default_factory=lambda: defaultdict(int))


@dataclass
class Transfer:
    transfer_id: str
    source: Account
    target: Account
    amount: int
    created_at: int
    expires_at: int | None


class BankSystem:
    """Single-threaded in-memory bank with pending transfers and account merges."""

    def __init__(self, transfer_ttl: int | None = None) -> None:
        self.transfer_ttl = transfer_ttl
        self.active: dict[str, Account] = {}
        self.lifetimes: dict[str, list[Account]] = defaultdict(list)
        self.pending: dict[str, Transfer] = {}
        self.pending_out: dict[int, set[str]] = defaultdict(set)
        self.pending_in: dict[int, set[str]] = defaultdict(set)
        self.expirations: list[tuple[int, int, str]] = []
        self.account_counter = 0
        self.transfer_counter = 0
        self.last_timestamp = -1

    def _record(self, account: Account, timestamp: int) -> None:
        entry = (timestamp, account.balance)
        if account.history and account.history[-1][0] == timestamp:
            account.history[-1] = entry
        else:
            account.history.append(entry)

    def _unlink(self, transfer: Transfer) -> None:
        self.pending.pop(transfer.transfer_id, None)
        self.pending_out[transfer.source.uid].discard(transfer.transfer_id)
        self.pending_in[transfer.target.uid].discard(transfer.transfer_id)

    def _cancel(self, transfer_id: str, timestamp: int) -> None:
        transfer = self.pending.get(transfer_id)
        if transfer is None:
            return
        transfer.source.balance += transfer.amount
        transfer.source.held -= transfer.amount
        self._record(transfer.source, timestamp)
        self._unlink(transfer)

    def _advance(self, timestamp: int) -> None:
        if timestamp < self.last_timestamp:
            raise ValueError("timestamps must be non-decreasing")
        while self.expirations and self.expirations[0][0] <= timestamp:
            expires_at, _, transfer_id = heapq.heappop(self.expirations)
            self._cancel(transfer_id, expires_at)
        self.last_timestamp = timestamp

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._advance(timestamp)
        if account_id in self.active:
            return False
        self.account_counter += 1
        account = Account(self.account_counter, account_id, timestamp)
        account.history.append((timestamp, 0))
        self.active[account_id] = account
        self.lifetimes[account_id].append(account)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._advance(timestamp)
        account = self.active.get(account_id)
        if account is None or amount < 0:
            return None
        account.balance += amount
        account.activity[timestamp] += amount
        self._record(account, timestamp)
        return account.balance

    def pay(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._advance(timestamp)
        account = self.active.get(account_id)
        if account is None or amount < 0 or account.balance < amount:
            return None
        account.balance -= amount
        account.outgoing += amount
        account.activity[timestamp] += amount
        self._record(account, timestamp)
        return account.balance

    def transfer(
        self,
        timestamp: int,
        source_id: str,
        target_id: str,
        amount: int,
    ) -> str | None:
        self._advance(timestamp)
        source = self.active.get(source_id)
        target = self.active.get(target_id)
        if (
            source is None
            or target is None
            or source is target
            or amount < 0
            or source.balance < amount
        ):
            return None

        source.balance -= amount
        source.held += amount
        self._record(source, timestamp)
        self.transfer_counter += 1
        transfer_id = f"transfer{self.transfer_counter}"
        expires_at = (
            None if self.transfer_ttl is None else timestamp + self.transfer_ttl
        )
        transfer = Transfer(
            transfer_id, source, target, amount, timestamp, expires_at
        )
        self.pending[transfer_id] = transfer
        self.pending_out[source.uid].add(transfer_id)
        self.pending_in[target.uid].add(transfer_id)
        if expires_at is not None:
            heapq.heappush(
                self.expirations,
                (expires_at, self.transfer_counter, transfer_id),
            )
        return transfer_id

    def transfer_accept(
        self,
        timestamp: int,
        account_id: str,
        transfer_id: str,
    ) -> bool:
        self._advance(timestamp)
        transfer = self.pending.get(transfer_id)
        if transfer is None or self.active.get(account_id) is not transfer.target:
            return False

        transfer.source.held -= transfer.amount
        transfer.source.outgoing += transfer.amount
        transfer.target.balance += transfer.amount
        transfer.source.activity[timestamp] += transfer.amount
        transfer.target.activity[timestamp] += transfer.amount
        self._record(transfer.target, timestamp)
        self._unlink(transfer)
        return True

    def balance(self, timestamp: int, account_id: str) -> int | None:
        self._advance(timestamp)
        account = self.active.get(account_id)
        return None if account is None else account.balance

    def on_hold(self, timestamp: int, account_id: str) -> int | None:
        self._advance(timestamp)
        account = self.active.get(account_id)
        return None if account is None else account.held

    def merge_accounts(
        self,
        timestamp: int,
        destination_id: str,
        source_id: str,
    ) -> bool:
        self._advance(timestamp)
        destination = self.active.get(destination_id)
        source = self.active.get(source_id)
        if destination is None or source is None or destination is source:
            return False

        # Cancel every transfer originating from the account being removed.
        for transfer_id in list(self.pending_out[source.uid]):
            self._cancel(transfer_id, timestamp)

        # A destination -> source transfer would become a self-transfer.
        self_transfers = self.pending_out[destination.uid] & self.pending_in[source.uid]
        for transfer_id in list(self_transfers):
            self._cancel(transfer_id, timestamp)

        # Other pending transfers into source now target destination.
        for transfer_id in list(self.pending_in[source.uid]):
            transfer = self.pending[transfer_id]
            self.pending_in[source.uid].discard(transfer_id)
            transfer.target = destination
            self.pending_in[destination.uid].add(transfer_id)

        destination.balance += source.balance
        destination.outgoing += source.outgoing
        self._record(destination, timestamp)
        source.ended_at = timestamp
        del self.active[source_id]
        return True

    def top_spenders(self, timestamp: int, count: int) -> list[str]:
        self._advance(timestamp)
        ranked = sorted(
            self.active.values(),
            key=lambda account: (-account.outgoing, account.account_id),
        )
        return [
            f"{account.account_id}({account.outgoing})"
            for account in ranked[:count]
        ]

    def top_activity(
        self,
        request_timestamp: int,
        at_timestamp: int,
        count: int,
    ) -> list[str]:
        self._advance(request_timestamp)
        if at_timestamp > request_timestamp:
            return []
        ranked = []
        for account_id in self.lifetimes:
            account = self._lifetime_at(account_id, at_timestamp)
            if account is not None and account.activity.get(at_timestamp, 0) > 0:
                ranked.append((account.activity[at_timestamp], account_id))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [account_id for _, account_id in ranked[:count]]

    def _lifetime_at(self, account_id: str, timestamp: int) -> Account | None:
        lifetimes = self.lifetimes.get(account_id, [])
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

    def get_balance(
        self,
        request_timestamp: int,
        account_id: str,
        at_timestamp: int,
    ) -> int | None:
        self._advance(request_timestamp)
        if at_timestamp > request_timestamp:
            return None
        account = self._lifetime_at(account_id, at_timestamp)
        if account is None:
            return None

        history = account.history
        left, right = 0, len(history)
        while left < right:
            middle = (left + right) // 2
            if history[middle][0] <= at_timestamp:
                left = middle + 1
            else:
                right = middle
        return None if left == 0 else history[left - 1][1]


if __name__ == "__main__":
    bank = BankSystem()
    assert bank.create_account(1, "A")
    assert bank.create_account(1, "B")
    assert bank.create_account(1, "C")
    assert bank.deposit(2, "A", 100) == 100
    assert bank.deposit(2, "B", 50) == 50
    assert bank.deposit(2, "C", 20) == 20
    assert bank.transfer(3, "A", "B", 10) == "transfer1"
    assert bank.transfer(4, "B", "C", 20) == "transfer2"
    assert bank.transfer(5, "C", "B", 5) == "transfer3"
    assert bank.merge_accounts(6, "A", "B")
    assert bank.balance(6, "A") == 150
    assert bank.transfer_accept(7, "A", "transfer3")
    assert bank.balance(7, "A") == 155
    assert bank.create_account(8, "B")
    assert bank.balance(8, "B") == 0
    assert bank.get_balance(9, "B", 5) == 30
    assert bank.get_balance(9, "B", 6) is None

    expiring = BankSystem(transfer_ttl=10)
    expiring.create_account(1, "A")
    expiring.create_account(1, "B")
    expiring.deposit(1, "A", 25)
    expiring.transfer(2, "A", "B", 10)
    assert expiring.deposit(12, "A", 0) == 25
    assert not expiring.transfer_accept(12, "B", "transfer1")
    print("banking system checks passed")
