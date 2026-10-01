from collections import defaultdict

class Account:
	def __init__(self, acc_id):
		self.id = acc_id
		self.amount = 0

	def __str__(self):
		return f"id - {self.id} \n" + f"amount - {self.amount}\n"


class BankLevel1:
	def __init__(self):
		self.accounts = defaultdict(Account)

	def create_account(self, timestamp, account_id):
		if account_id in self.accounts:
			return False

		self.accounts[account_id] = Account(account_id)

		return True

	def deposit(self, timestamp, account_id, amount):
		if account_id not in self.accounts:
			return None

		self.accounts[account_id].amount += amount

		return self.accounts[account_id].amount


	def transfer(self, timestamp, source_account_id, target_account_id, amount):
		if source_account_id == target_account_id or \
			source_account_id not in self.accounts or \
			target_account_id not in self.accounts or \
			self.accounts[source_account_id].amount < amount:
			return None

		self.accounts[source_account_id].amount -= amount
		self.accounts[target_account_id].amount += amount

		return self.accounts[source_account_id].amount


# ================================================================================
# ================================================================================
# ================================================================================

class AccountLvl2:
	def __init__(self, acc_id):
		self.id = acc_id
		self.amount = 0
		self.spend = 0

	def __str__(self):
		return f"""
			id - {self.id} 
			amount - {self.amount}
			spend - {self.spend}
			"""

	def __repr__(self):
		return f"""id - {self.id} | amount - {self.amount} | spend - {self.spend}"""

class BankLevel2:
	def __init__(self):
		self.accounts = defaultdict(AccountLvl2)

	def top_spenders(self, timestamp, n):
		if not self.accounts:
			return []

		# spend decending, name accending
		all_accounts_sorted = sorted(list(self.accounts.values()), key=lambda x: (-x.spend, x.id))

		result = [f"{a.id}({a.spend})" for a in all_accounts_sorted[:n]]

		return result

	def create_account(self, timestamp, account_id):
		if account_id in self.accounts:
			return False

		self.accounts[account_id] = AccountLvl2(account_id)

		return True

	def deposit(self, timestamp, account_id, amount):
		if account_id not in self.accounts:
			return None

		self.accounts[account_id].amount += amount

		return self.accounts[account_id].amount


	def transfer(self, timestamp, source_account_id, target_account_id, amount):
		if source_account_id == target_account_id or \
			source_account_id not in self.accounts or \
			target_account_id not in self.accounts or \
			self.accounts[source_account_id].amount < amount:
			return None

		self.accounts[source_account_id].amount -= amount
		self.accounts[target_account_id].amount += amount

		self.accounts[source_account_id].spend += amount

		return self.accounts[source_account_id].amount

# ================================================================================
# ================================================================================
# ================================================================================

class Payment:
	def __init__(self, payment_id, ts, amount):
		self.id = payment_id
		self.cash_back_ts = ts + 86400000
		self.is_closed = False
		self.amount = amount

	def __repr__(self):
		return f"""id - {self.id} | amount - {self.amount} | ts - {self.ts} | is_closed - {self.is_closed}"""

class AccountLvl3:
	def __init__(self, acc_id):
		self.id = acc_id
		self.amount = 0
		self.spend = 0
		self.payments = defaultdict(Payment)

	def __str__(self):
		return f"""
			id - {self.id} 
			amount - {self.amount}
			spend - {self.spend}
			"""

	def __repr__(self):
		return f"""id - {self.id} | amount - {self.amount} | spend - {self.spend}"""

class BankLevel3:
	def __init__(self):
		self.accounts = defaultdict(AccountLvl3)

	def pay(self, timestamp, account_id, amount):
		if account_id not in self.accounts or amount > self.accounts[account_id].amount:
			return None

		account = self.accounts[account_id]

		payment_id = f"pay-{account_id}-{timestamp}-{amount}"
		account.payments[payment_id] = Payment(payment_id, timestamp, amount)

		account.amount -= amount
		account.spend += amount

		return payment_id

	def get_payment_status(self, timestamp, account_id, payment_id):
		if account_id not in self.accounts or payment_id not in self.accounts[account_id].payments:
			return None

		payment = self.accounts[account_id].payments[payment_id]

		if payment.is_closed:
			return "CASHBACK_RECEIVED"
		elif payment.cash_back_ts <= timestamp:
			self.accounts[account_id].amount += int(payment.amount * 0.02)
			return "CASHBACK_RECEIVED"
		else:
			return "IN_PROGRESS"


	def top_spenders(self, timestamp, n):
		if not self.accounts:
			return []

		# spend decending, name accending
		all_accounts_sorted = sorted(list(self.accounts.values()), key=lambda x: (-x.spend, x.id))

		if len(all_accounts_sorted) >= n:
			result = [f"{a.id}({a.spend})" for a in all_accounts_sorted[:n]]
		else:
			result = [f"{a.id}({a.spend})" for a in all_accounts_sorted]

		return result

	def create_account(self, timestamp, account_id):
		if account_id in self.accounts:
			return False

		self.accounts[account_id] = AccountLvl3(account_id)

		return True

	def deposit(self, timestamp, account_id, amount):
		if account_id not in self.accounts:
			return None

		self.accounts[account_id].amount += amount

		return self.accounts[account_id].amount


	def transfer(self, timestamp, source_account_id, target_account_id, amount):
		if source_account_id == target_account_id or \
			source_account_id not in self.accounts or \
			target_account_id not in self.accounts or \
			self.accounts[source_account_id].amount < amount:
			return None

		self.accounts[source_account_id].amount -= amount
		self.accounts[target_account_id].amount += amount

		self.accounts[source_account_id].spend += amount

		return self.accounts[source_account_id].amount


# ================================================================================
# ================================================================================
# ================================================================================

class PaymentLvl4:
	def __init__(self, payment_id, ts, amount):
		self.id = payment_id
		self.cash_back_ts = ts + 86400000
		self.is_closed = False
		self.amount = amount

	def __repr__(self):
		return f"""id - {self.id} | amount - {self.amount} | ts - {self.ts} | is_closed - {self.is_closed}"""

class AccountLvl4:
	def __init__(self, acc_id):
		self.id = acc_id
		self.amount = 0
		self.spend = 0
		self.payments = defaultdict(PaymentLvl4)

	def __str__(self):
		return f"""
			id - {self.id} 
			amount - {self.amount}
			spend - {self.spend}
			"""

	def __repr__(self):
		return f"""id - {self.id} | amount - {self.amount} | spend - {self.spend}"""

class BankLevel4:
	def __init__(self):
		self.accounts = defaultdict(AccountLvl4)
		self.history = defaultdict(list)

	def merge(self, timestamp, account_id_1, account_id_2):
		if account_id_1 not in self.accounts or account_id_2 not in self.accounts:
			return False

		account1 = self.accounts[account_id_1]
		account2 = self.accounts[account_id_2]

		account1.amount += account2.amount
		account1.spend += account2.spend
		account1.payments.update(account2.payments)

		del self.accounts[account_id_2]

		return True

	def merge_with_history(self, timestamp, account_id_1, account_id_2):
		if account_id_1 not in self.accounts or account_id_2 not in self.accounts or account_id_1 == account_id_2:
			return False

		account1 = self.accounts[account_id_1]
		account2 = self.accounts[account_id_2]

		account1.amount += account2.amount
		account1.spend += account2.spend
		account1.payments.update(account2.payments)

		# merge history
		new_history = sorted(self.history[account_id_1] + self.history[account_id_2], key=lambda x: x[0])
		self.history[account_id_1] = new_history

		print("new history")
		print(new_history)

		# deactivate
		del self.accounts[account_id_2]
		# add a negative amount to indicate current balance = 0
		self.history[account_id_2].append((timestamp, -account2.amount))

		return True


	def get_balance(self, timestamp, account_id, time_at):
		# if account not exists [not in both history and accounts]
		if account_id not in self.history and account_id not in self.accounts:
			return None
		# if account is deactiavete right now and we are check time after deactivation
		if account_id not in self.accounts and time_at > self.history[account_id][-1][0]:
			return None

		balance = 0
		for history in self.history[account_id]:
			if history[0] <= time_at:
				balance += history[1]

		return balance

	def _add_history(self, timestamp, account_id, amount):
		self.history[account_id].append((timestamp, amount))

	def pay(self, timestamp, account_id, amount):
		if account_id not in self.accounts or amount > self.accounts[account_id].amount:
			return None

		account = self.accounts[account_id]

		payment_id = f"pay-{account_id}-{timestamp}-{amount}"
		account.payments[payment_id] = PaymentLvl4(payment_id, timestamp, amount)

		account.amount -= amount
		account.spend += amount

		self._add_history(timestamp, account_id, -amount)

		return payment_id

	def get_payment_status(self, timestamp, account_id, payment_id):
		if account_id not in self.accounts or payment_id not in self.accounts[account_id].payments:
			return None

		payment = self.accounts[account_id].payments[payment_id]

		if payment.is_closed:
			return "CASHBACK_RECEIVED"
		elif payment.cash_back_ts <= timestamp:
			self.accounts[account_id].amount += int(payment.amount * 0.02)

			self._add_history(timestamp, account_id, int(payment.amount * 0.02))

			return "CASHBACK_RECEIVED"
		else:
			return "IN_PROGRESS"


	def top_spenders(self, timestamp, n):
		if not self.accounts:
			return []

		# spend decending, name accending
		all_accounts_sorted = sorted(list(self.accounts.values()), key=lambda x: (-x.spend, x.id))

		if len(all_accounts_sorted) >= n:
			result = [f"{a.id}({a.spend})" for a in all_accounts_sorted[:n]]
		else:
			result = [f"{a.id}({a.spend})" for a in all_accounts_sorted]

		return result

	def create_account(self, timestamp, account_id):
		if account_id in self.accounts:
			return False

		self.accounts[account_id] = AccountLvl4(account_id)

		return True

	def deposit(self, timestamp, account_id, amount):
		if account_id not in self.accounts:
			return None

		self.accounts[account_id].amount += amount
		self._add_history(timestamp, account_id, amount)

		return self.accounts[account_id].amount


	def transfer(self, timestamp, source_account_id, target_account_id, amount):
		if source_account_id == target_account_id or \
			source_account_id not in self.accounts or \
			target_account_id not in self.accounts or \
			self.accounts[source_account_id].amount < amount:
			return None

		self.accounts[source_account_id].amount -= amount
		self.accounts[target_account_id].amount += amount

		self.accounts[source_account_id].spend += amount

		self._add_history(timestamp, source_account_id, -amount)
		self._add_history(timestamp, target_account_id, amount)

		return self.accounts[source_account_id].amount


# ================================================================================
# ================================================================================
# ================================================================================

MAX_TIME = 2**63 - 1

class PaymentLvl5:
	def __init__(self, payment_id, ts, amount):
		self.id = payment_id
		self.cash_back_ts = ts + 86400000
		self.is_closed = False
		self.amount = amount

	def __repr__(self):
		return f"""id - {self.id} | amount - {self.amount} | ts - {self.ts} | is_closed - {self.is_closed}"""

class AccountLvl5:
	def __init__(self, acc_id):
		self.id = acc_id
		self.amount = 0
		self.spend = 0
		self.payments = defaultdict(PaymentLvl5)
		self.transfers = defaultdict(TransferExp)

	def __str__(self):
		return f"""
			id - {self.id} 
			amount - {self.amount}
			spend - {self.spend}
			"""

	def __repr__(self):
		return f"""id - {self.id} | amount - {self.amount} | spend - {self.spend}"""

class TransferExp:
	def __init__(self, source_acc_id, target_acc_id, amount, timestamp, exp):
		self.source_acc_id = source_acc_id
		self.target_acc_id = target_acc_id
		self.amount = amount
		self.expired_ts = timestamp + exp if exp != MAX_TIME else exp
		self.accepted = False

class BankLevel5:
	def __init__(self):
		self.accounts = defaultdict(AccountLvl5)
		self.history = defaultdict(list)
		self.transfers = defaultdict(TransferExp)

	def transfer_with_exp(self, timestamp, source_account_id, target_account_id, amount, ttl):
		if source_account_id not in self.accounts or target_account_id not in self.accounts or target_account_id == source_account_id:
			return None

		source_account = self.accounts[source_account_id]

		self._scan_expired_transfers(timestamp)

		# not enough money to withold
		if source_account.amount < amount:
			return None

		transfer_id = f"transf-{source_account_id}-{target_account_id}-{amount}-{timestamp}"
		transfer = TransferExp(source_account_id, target_account_id, amount, timestamp, ttl)

		source_account.transfers[transfer_id] = transfer
		self.transfers[transfer_id] = transfer

		source_account.amount -= amount
		self._add_history(timestamp, source_account_id, -amount)

		return transfer_id

	def accept_transfer(self, timestamp, account_id, transfer_id):
		if account_id not in self.accounts or transfer_id not in self.transfers:
			return False

		transfer = self.transfers[transfer_id]
		if transfer.target_acc_id != account_id or self._check_transfer_expire(timestamp, transfer):
			return False

		source_account = self.accounts[transfer.source_acc_id]
		target_account = self.accounts[transfer.target_acc_id]

		source_account.spend += transfer.amount
		target_account.amount += transfer.amount
		# add history, source account history already added when transfer created
		self._add_history(timestamp, transfer.target_acc_id, +transfer.amount)

		transfer.accepted = True

		return True

	def _scan_expired_transfers(self, timestamp):
		for transfer in self.transfers.values():
			self._check_transfer_expire(timestamp, transfer)

	def _check_transfer_expire(self, timestamp, transfer):
		if transfer.accepted:
			return True

		if transfer.expired_ts <= timestamp and not transfer.accepted:
			account = self.accounts[transfer.source_acc_id]
			account.amount += transfer.amount

			self._add_history(timestamp, transfer.source_acc_id, transfer.amount)

			return True
		
		return False

	def merge(self, timestamp, account_id_1, account_id_2):
		if account_id_1 not in self.accounts or account_id_2 not in self.accounts:
			return False

		account1 = self.accounts[account_id_1]
		account2 = self.accounts[account_id_2]

		account1.amount += account2.amount
		account1.spend += account2.spend
		account1.payments.update(account2.payments)

		del self.accounts[account_id_2]

		return True

	def merge_with_history(self, timestamp, account_id_1, account_id_2):
		if account_id_1 not in self.accounts or account_id_2 not in self.accounts or account_id_1 == account_id_2:
			return False

		account1 = self.accounts[account_id_1]
		account2 = self.accounts[account_id_2]

		account1.amount += account2.amount
		account1.spend += account2.spend
		account1.payments.update(account2.payments)
		account1.transfers.update(account2.transfers)

		# update transfer target id/source id
		for transfer in self.transfers.values():
			if transfer.source_acc_id == account_id_2:
				transfer.source_acc_id = account_id_1
			if transfer.target_acc_id == account_id_2:
				transfer.target_acc_id = account_id_1

		# merge history
		new_history = sorted(self.history[account_id_1] + self.history[account_id_2], key=lambda x: x[0])
		self.history[account_id_1] = new_history

		# print("new history")
		# print(new_history)

		# deactivate
		del self.accounts[account_id_2]
		# add a negative amount to indicate current balance = 0
		self.history[account_id_2].append((timestamp, -account2.amount))

		return True


	def get_balance(self, timestamp, account_id, time_at):
		# if account not exists [not in both history and accounts]
		if account_id not in self.history and account_id not in self.accounts:
			return None
		# if account is deactiavete right now and we are check time after deactivation
		if account_id not in self.accounts and time_at > self.history[account_id][-1][0]:
			return None

		self._scan_expired_transfers(timestamp)

		balance = 0
		for history in self.history[account_id]:
			if history[0] <= time_at:
				balance += history[1]

		return balance

	def _add_history(self, timestamp, account_id, amount):
		self.history[account_id].append((timestamp, amount))

	def pay(self, timestamp, account_id, amount):
		if account_id not in self.accounts:
			return None

		self._scan_expired_transfers(timestamp)

		if amount > self.accounts[account_id].amount:
			return None

		account = self.accounts[account_id]

		payment_id = f"pay-{account_id}-{timestamp}-{amount}"
		account.payments[payment_id] = PaymentLvl5(payment_id, timestamp, amount)

		account.amount -= amount
		account.spend += amount

		self._add_history(timestamp, account_id, -amount)

		return payment_id

	def get_payment_status(self, timestamp, account_id, payment_id):
		if account_id not in self.accounts or payment_id not in self.accounts[account_id].payments:
			return None

		payment = self.accounts[account_id].payments[payment_id]

		if payment.is_closed:
			return "CASHBACK_RECEIVED"
		elif payment.cash_back_ts <= timestamp:
			self.accounts[account_id].amount += int(payment.amount * 0.02)

			self._add_history(timestamp, account_id, int(payment.amount * 0.02))

			return "CASHBACK_RECEIVED"
		else:
			return "IN_PROGRESS"


	def top_spenders(self, timestamp, n):
		if not self.accounts:
			return []

		# spend decending, name accending
		all_accounts_sorted = sorted(list(self.accounts.values()), key=lambda x: (-x.spend, x.id))

		if len(all_accounts_sorted) >= n:
			result = [f"{a.id}({a.spend})" for a in all_accounts_sorted[:n]]
		else:
			result = [f"{a.id}({a.spend})" for a in all_accounts_sorted]

		return result

	def create_account(self, timestamp, account_id):
		if account_id in self.accounts:
			return False

		self.accounts[account_id] = AccountLvl5(account_id)

		return True

	def deposit(self, timestamp, account_id, amount):
		if account_id not in self.accounts:
			return None

		self.accounts[account_id].amount += amount
		self._add_history(timestamp, account_id, amount)

		return self.accounts[account_id].amount


	def transfer(self, timestamp, source_account_id, target_account_id, amount):
		if source_account_id == target_account_id or \
			source_account_id not in self.accounts or \
			target_account_id not in self.accounts:
			return None

		self._scan_expired_transfers(timestamp)

		if self.accounts[source_account_id].amount < amount:
			return None

		self.accounts[source_account_id].amount -= amount
		self.accounts[target_account_id].amount += amount

		self.accounts[source_account_id].spend += amount

		self._add_history(timestamp, source_account_id, -amount)
		self._add_history(timestamp, target_account_id, amount)

		return self.accounts[source_account_id].amount


class Test:
	def __init__(self):
		pass

	def test_level1(self):
		print("------------------------------------------")
		print("------------Run test level 1 A------------------")
		bank = BankLevel1()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "A"))            # duplicate
		results.append(bank.deposit(3, "A", 100))
		results.append(bank.deposit(4, "B", 10))               # missing account
		results.append(bank.create_account(5, "B"))
		results.append(bank.transfer(6, "A", "B", 30))         # ok -> A becomes 70
		results.append(bank.transfer(7, "A", "B", 1000))       # insufficient
		results.append(bank.transfer(8, "A", "A", 1))          # self-transfer forbidden
		results.append(bank.transfer(9, "A", "C", 1))          # target missing
		results.append(bank.deposit(10, "B", 5))               # B becomes 35

		expected = [
		  True,
		  False,
		  100,
		  None,
		  True,
		  70,
		  None,
		  None,
		  None,
		  35
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 1 B------------------")
		bank = BankLevel1()

		results = []

		results.append(bank.create_account(1, "X"))
		results.append(bank.create_account(2, "Y"))
		results.append(bank.create_account(3, "Z"))
		results.append(bank.deposit(4, "X", 50))
		results.append(bank.transfer(5, "X", "Y", 20))         # X=30
		results.append(bank.transfer(6, "Y", "Z", 10))         # Y=10
		results.append(bank.transfer(7, "Z", "X", 5))          # Z=5

		expected = [True, True, True, 50, 30, 10, 5]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

	def test_level2(self):
		print("------------------------------------------")
		print("------------Run test level 2 A------------------")
		bank = BankLevel2()

		results = []

		results.append(bank.create_account(1, "C"))
		results.append(bank.create_account(2, "A"))
		results.append(bank.create_account(3, "B"))

		results.append(bank.deposit(4, "A", 100))              # A=100
		results.append(bank.deposit(5, "B", 100))              # B=100
		results.append(bank.deposit(6, "C", 100))              # C=100

		results.append(bank.transfer(7, "A", "B", 40))         # A=60 ; outgoing A+=40 ; returns 60
		results.append(bank.transfer(8, "B", "C", 40))         # B=100; outgoing B+=40 ; returns 100
		results.append(bank.transfer(9, "C", "A", 10))         # C=130; outgoing C+=10 ; returns 130

		results.append(bank.top_spenders(10, 2))
		results.append(bank.top_spenders(11, 10))

		expected = [
		  True, True, True,
		  100, 100, 100,
		  60, 100, 130,
		  ["A(40)", "B(40)"],          # tie -> alphabetical
		  ["A(40)", "B(40)", "C(10)"]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 2 B------------------")
		bank = BankLevel2()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 10))
		results.append(bank.top_spenders(4, 5))                # no outgoing yet

		expected = [True, True, 10, ["A(0)", "B(0)"]]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

	def test_level3(self):
		print("------------------------------------------")
		print("------------Run test level 3 A------------------")
		bank = BankLevel3()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.deposit(2, "A", 1000))

		# payment1 at t=10, cashback=floor(0.02*501)=10, posts at t=86400010
		payment_id1 = bank.pay(10, "A", 501)
		results.append(payment_id1)                             # A:1000->499 ; returns "payment1"
		results.append(bank.get_payment_status(11, "A", payment_id1))       # before cashback
		results.append(bank.get_payment_status(86400009, "A", payment_id1)) # still before cashback
		results.append(bank.get_payment_status(86400010, "A", payment_id1)) # exactly when cashback posts

		# After t=86400010, A becomes 499+10=509.
		# payment2 at t=86400020, cashback=floor(0.02*500)=10, posts at t=172800020
		payment_id2 = bank.pay(86400020, "A", 500)
		results.append(payment_id2)                       # A:509->9 ; returns "payment2"

		results.append(bank.top_spenders(86400021, 1))                     # outgoing = 501+500 = 1001

		expected = [
		  True,
		  1000,
		  "pay-A-10-501",
		  "IN_PROGRESS",
		  "IN_PROGRESS",
		  "CASHBACK_RECEIVED",
		  "pay-A-86400020-500",
		  ["A(1001)"]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 3 B------------------")
		bank = BankLevel3()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 10))

		results.append(bank.pay(4, "A", 11))                    # insufficient -> None
		results.append(bank.pay(5, "X", 1))                     # missing account -> None

		# payment1 at t=6, amount=10, cashback=floor(0.2)=0, posts at t=86400006
		payment_id1 = bank.pay(6, "A", 10)
		results.append(payment_id1)                    # A:10->0 ; "payment1"

		results.append(bank.get_payment_status(7, "B", payment_id1))        # wrong account -> None
		results.append(bank.get_payment_status(7, "A", "payment999"))      # missing payment -> None
		results.append(bank.get_payment_status(7, "X", payment_id1))        # missing account -> None

		# check boundary: cashback=0, but status should flip at refund time
		results.append(bank.get_payment_status(86400005, "A", payment_id1)) # before refund time
		results.append(bank.get_payment_status(86400006, "A", payment_id1)) # at refund time

		expected = [
		  True,
		  True,
		  10,
		  None,
		  None,
		  "pay-A-6-10",
		  None,
		  None,
		  None,
		  "IN_PROGRESS",
		  "CASHBACK_RECEIVED"
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

	def test_level4(self):
		print("------------------------------------------")
		print("------------Run test level 4 A------------------")
		bank = BankLevel4()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 200))               # A=200
		results.append(bank.deposit(4, "B", 300))               # B=300

		# payment1 from B at t=5, amount=101, cashback=floor(2.02)=2, posts at t=86400005
		payment_id = bank.pay(5, "B", 101)
		results.append(payment_id)                   # B:300->199 ; "payment1"
		results.append(bank.get_payment_status(6, "B", payment_id))        # IN_PROGRESS

		# Merge B into A at t=7 => A becomes 200+199=399; B deleted; payment1 now owned by A
		results.append(bank.merge_with_history(7, "A", "B"))

		results.append(bank.get_payment_status(8, "A", payment_id))        # IN_PROGRESS
		results.append(bank.get_payment_status(86400004, "A", payment_id)) # still IN_PROGRESS
		results.append(bank.get_payment_status(86400005, "A", payment_id)) # cashback posted

		# top_spenders: outgoing from merged histories, B's pay(101) now counts under A
		results.append(bank.top_spenders(86400006, 2))

		expected = [
		  True, True,
		  200, 300,
		  payment_id,
		  "IN_PROGRESS",
		  True,
		  "IN_PROGRESS",
		  "IN_PROGRESS",
		  "CASHBACK_RECEIVED",
		  ["A(101)"]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 4 B------------------")
		bank = BankLevel4()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 100))               # A=100
		results.append(bank.deposit(4, "B", 50))                # B=50
		results.append(bank.transfer(5, "A", "B", 20))          # A:100->80 returns 80; B=70

		# Balances at exact times (timestamps are unique and increasing):
		# At t=4: B has 50
		# At t=5: transfer occurred, so after op B has 70
		results.append(bank.get_balance(6, "B", 4))
		results.append(bank.get_balance(7, "B", 5))

		results.append(bank.merge_with_history(8, "A", "B"))        # A becomes 80+70=150; B deleted

		# Ask for B before merge -> old B history exists
		results.append(bank.get_balance(9, "B", 7))             # B was 70 at t=7
		# Ask for B after merge -> None (until recreated)
		results.append(bank.get_balance(10, "B", 9))

		results.append(bank.create_account(11, "B"))            # new B, balance 0
		results.append(bank.get_balance(12, "B", 12))           # should be 0

		results.append(bank.top_spenders(13, 2))                # A spent 20 via transfer; new B spent 0

		expected = [
		  True, True,
		  100, 50,
		  80,
		  50,
		  70,
		  True,
		  70,
		  None,
		  True,
		  0,
		  ["A(20)", "B(0)"]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 4 C------------------")
		bank = BankLevel4()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.deposit(2, "A", 10))

		results.append(bank.merge_with_history(3, "A", "A"))        # self-merge -> False
		results.append(bank.merge_with_history(4, "A", "B"))        # missing B -> False

		results.append(bank.create_account(5, "B"))
		results.append(bank.deposit(6, "B", 10))
		payment_id = bank.pay(7, "B", 10)
		results.append(payment_id)                    # "payment1"

		results.append(bank.get_payment_status(8, "A", payment_id))   # wrong account before merge -> None
		results.append(bank.merge_with_history(9, "A", "B"))              # merge ok
		results.append(bank.get_payment_status(10, "A", payment_id))  # now visible under A -> IN_PROGRESS

		expected = [
		  True,
		  10,
		  False,
		  False,
		  True,
		  10,
		  payment_id,
		  None,
		  True,
		  "IN_PROGRESS"
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 4 D merge with history------------------")
		bank = BankLevel4()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))

		results.append(bank.deposit(3, "A", 10))                 # A=10
		results.append(bank.deposit(4, "B", 30))                 # B=30

		# Pre-merge checks (normal):
		results.append(bank.get_balance(5, "A", 4))              # A-only => 10
		results.append(bank.get_balance(6, "B", 4))              # B-only => 30

		# Merge with history at T=7
		results.append(bank.merge_with_history(7, "A", "B"))     # A becomes 40, B deleted

		# After merge_with_history, A's past should be retroactively combined:
		results.append(bank.get_balance(8, "A", 2))              # at t=2, neither had deposits yet => 0 (both existed)
		results.append(bank.get_balance(9, "A", 3))              # at t=3, A=10, B=0 => 10
		results.append(bank.get_balance(10, "A", 4))             # at t=4, A=10, B=30 => 40
		results.append(bank.get_balance(11, "A", 7))             # at merge time, A should be 40

		# B rules after merge:
		results.append(bank.get_balance(12, "B", 4))             # old B pre-merge still queryable => 30
		results.append(bank.get_balance(13, "B", 8))             # after merge, old B gone => None

		expected = [
		  True, True,
		  10, 30,
		  10, 30,
		  True,
		  0,
		  10,
		  40,
		  40,
		  30,
		  None
		]
		# [True, True, 10, 30, 10, 30, True, 0, 10, 10, 10, 30, None]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 4 E merge with history------------------")
		bank = BankLevel4()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.create_account(3, "C"))

		results.append(bank.deposit(4, "A", 100))                # A=100
		results.append(bank.deposit(5, "B", 50))                 # B=50
		results.append(bank.deposit(6, "C", 20))                 # C=20

		results.append(bank.transfer(7, "A", "B", 30))           # A=70, B=80 ; outgoing A+=30
		results.append(bank.transfer(8, "B", "C", 10))           # B=70, C=30 ; outgoing B+=10

		# Merge with history B into A at T=9
		results.append(bank.merge_with_history(9, "A", "B"))     # A becomes 70+70=140, B deleted

		# Retroactive combined A balance:
		# at t=6: A=100, B=50 => 150
		# at t=7: after A->B 30, A=70, B=80 => 150
		# at t=8: after B->C 10, A=70, B=70 => 140
		results.append(bank.get_balance(10, "A", 6))
		results.append(bank.get_balance(11, "A", 7))
		results.append(bank.get_balance(12, "A", 8))
		results.append(bank.get_balance(13, "A", 9))             # at merge time => 140

		# top_spenders should include B's outgoing moved to A (but not retroactively change IDs, just aggregate):
		results.append(bank.top_spenders(14, 3))

		expected = [
		  True, True, True,
		  100, 50, 20,
		  70, 70,
		  True,
		  150,
		  150,
		  140,
		  140,
		  ["A(40)", "C(0)"]   # A spent 30 + B spent 10 = 40; B deleted; C spent 0
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 4 F merge with history------------------")
		bank = BankLevel4()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))

		results.append(bank.deposit(3, "A", 0))                   # A=0
		results.append(bank.deposit(4, "B", 1000))                # B=1000

		# B pays at t=5: amount=501, cashback=10 at 86400005
		payment_id = bank.pay(5, "B", 501)
		results.append(payment_id)                     # payment1; B=499

		# Merge_with_history at T=6
		results.append(bank.merge_with_history(6, "A", "B"))      # A current becomes 0+499=499

		# Retroactive combined A:
		results.append(bank.get_balance(7, "A", 4))               # at t=4: A=0, B=1000 => 1000
		results.append(bank.get_balance(8, "A", 5))               # at t=5 after pay: A=0, B=499 => 499
		results.append(bank.get_balance(9, "A", 6))               # at merge time => 499

		# Cashback later goes to A
		results.append(bank.get_payment_status(10, "A", payment_id))         # IN_PROGRESS
		results.append(bank.get_payment_status(86400005, "A", payment_id))   # CASHBACK_RECEIVED

		# Balance after cashback should be 499 + 10 = 509
		results.append(bank.get_balance(86400006, "A", 86400006))

		expected = [
		  True, True,
		  0, 1000,
		  payment_id,
		  True,
		  1000,
		  499,
		  499,
		  "IN_PROGRESS",
		  "CASHBACK_RECEIVED",
		  509
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

	def test_level5(self):
		print("------------------------------------------")
		print("------------Run test level 5 A------------------")
		bank = BankLevel5()

		# bank = BankLevel5()
		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 100))                     # A=100

		tid = "transf-A-B-30-4"
		results.append(bank.transfer_with_exp(4, "A", "B", 30, 10))   # withhold 30 => A available 70
		results.append(bank.get_balance(5, "A", 5))                   # should be 70 (withheld)
		results.append(bank.get_balance(6, "B", 6))                   # still 0 (not accepted)

		results.append(bank.accept_transfer(7, "B", tid))             # accept => A 70, B 30
		results.append(bank.get_balance(8, "A", 8))
		results.append(bank.get_balance(9, "B", 9))

		results.append(bank.top_spenders(10, 2))                      # A spent 30 (accepted), B spent 0

		expected = [
		  True, True, 100,
		  tid,
		  70,
		  0,
		  True,
		  70,
		  30,
		  ["A(30)", "B(0)"]
		]


		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 B------------------")
		bank = BankLevel5()

		# bank = BankLevel5()
		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 20))

		results.append(bank.transfer_with_exp(4, "A", "C", 5, 10))    # target missing
		results.append(bank.transfer_with_exp(5, "C", "B", 5, 10))    # source missing
		results.append(bank.transfer_with_exp(6, "A", "B", 25, 10))   # insufficient
		results.append(bank.transfer_with_exp(7, "A", "A", 1, 10))    # self-transfer forbidden

		# ensure no money withheld from failures
		results.append(bank.get_balance(8, "A", 8))
		results.append(bank.get_balance(9, "B", 9))

		expected = [
		  True, True, 20,
		  None, None, None, None,
		  20,
		  0
		]


		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 C------------------")
		bank = BankLevel5()

		# bank = BankLevel5()
		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 50))

		tid = "transf-A-B-10-4"
		results.append(bank.transfer_with_exp(4, "A", "B", 10, 100))  # A available 40

		results.append(bank.accept_transfer(5, "A", tid))             # wrong accepter (source) -> False
		results.append(bank.accept_transfer(6, "C", tid))             # account missing -> False
		results.append(bank.accept_transfer(7, "B", "nope"))          # transfer missing -> False

		results.append(bank.accept_transfer(8, "B", tid))             # first accept -> True
		results.append(bank.accept_transfer(9, "B", tid))             # already accepted -> False

		results.append(bank.get_balance(10, "A", 10))                 # A 40
		results.append(bank.get_balance(11, "B", 11))                 # B 10

		expected = [
		  True, True, 50,
		  tid,
		  False,
		  False,
		  False,
		  True,
		  False,
		  40,
		  10
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 D------------------")
		bank = BankLevel5()

		# bank = BankLevel5()
		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 100))

		# ttl=5 => alive in [4,9); expires at t=9
		tid = "transf-A-B-60-4"
		results.append(bank.transfer_with_exp(4, "A", "B", 60, 5))    # A available 40

		results.append(bank.get_balance(8, "A", 8))                  # still withheld => 40
		results.append(bank.get_balance(9, "A", 9))                  # expired exactly now => refunded => 100
		results.append(bank.get_balance(9, "B", 9))                  # still 0

		results.append(bank.accept_transfer(10, "B", tid))            # too late -> False

		results.append(bank.top_spenders(11, 2))                      # should be A(0) because never accepted

		expected = [
		  True, True, 100,
		  tid,
		  40,
		  100,
		  0,
		  False,
		  ["A(0)", "B(0)"]
		]


		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 E------------------")
		bank = BankLevel5()

		# bank = BankLevel5()
		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 100))

		# withhold 80
		tid = "transf-A-B-80-4"
		results.append(bank.transfer_with_exp(4, "A", "B", 80, 5))     # A available 20

		results.append(bank.pay(5, "A", 30))                           # should fail (only 20 available)
		payment_id1 = bank.pay(6, "A", 20)
		results.append(payment_id1)                           # ok -> payment1; A becomes 0; cashback floor(0.4)=0

		# expire at t=9 -> refund 80 => A becomes 80
		results.append(bank.get_balance(8, "A", 8))                    # 0 (still withheld)
		results.append(bank.get_balance(9, "A", 9))                    # 80 refunded

		payment_id2 = bank.pay(10, "A", 50)
		results.append(payment_id2)                          # ok -> payment2; A becomes 30
		results.append(bank.get_payment_status(11, "A", payment_id2))   # IN_PROGRESS
		results.append(bank.get_payment_status(86400010, "A", payment_id2))  # cashback floor(1)=1 received at 86400010

		expected = [
		  True, True, 100,
		  tid,
		  None,
		  payment_id1,
		  0,
		  80,
		  payment_id2,
		  "IN_PROGRESS",
		  "CASHBACK_RECEIVED"
		]


		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 F------------------")
		bank = BankLevel5()

		# bank = BankLevel5()
		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 100))

		tid = "transf-A-B-40-4"
		results.append(bank.transfer_with_exp(4, "A", "B", 40, 100))   # A available 60

		results.append(bank.top_spenders(5, 2))                        # not accepted yet => A(0)
		results.append(bank.accept_transfer(6, "B", tid))              # accept => B=40
		results.append(bank.top_spenders(7, 2))                        # now A(40)

		expected = [
		  True, True, 100,
		  tid,
		  ["A(0)", "B(0)"],
		  True,
		  ["A(40)", "B(0)"]
		]


		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 H------------------")
		bank = BankLevel5()

		# bank = BankLevel5()
		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.create_account(3, "C"))

		results.append(bank.deposit(4, "B", 100))

		# B -> C pending, ttl long enough
		tid = "transf-B-C-70-5"
		results.append(bank.transfer_with_exp(5, "B", "C", 70, 100))   # B available 30

		# merge B into A at t=6
		results.append(bank.merge_with_history(6, "A", "B"))           # A now has B's current balance (30), B deleted

		# After merge, this pending transfer should behave as if source is now A.
		# Accept should still be done by target C.
		results.append(bank.accept_transfer(7, "C", tid))              # True
		results.append(bank.get_balance(8, "A", 8))                    # A should still be 30-70? NO: 70 already withheld pre-merge.
		                                                            # At accept, withheld moves to C; source balance stays same (30).
		results.append(bank.get_balance(9, "C", 9))                    # C should be 70

		# Outgoing should now be attributed to A (merged)
		results.append(bank.top_spenders(10, 3))

		expected = [
		  True, True, True,
		  100,
		  tid,
		  True,
		  True,
		  30,
		  70,
		  ["A(70)", "C(0)"]
		]


		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 I------------------")
		bank = BankLevel5()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.create_account(3, "C"))
		results.append(bank.deposit(4, "C", 100))

		# C -> B pending
		tid = "transf-C-B-60-5"
		results.append(bank.transfer_with_exp(5, "C", "B", 60, 100))   # C available 40

		# Merge B into A at t=6. Now B deleted; pending transfer's target should become A.
		results.append(bank.merge_with_history(6, "A", "B"))

		results.append(bank.accept_transfer(7, "B", tid))              # B no longer exists -> False
		results.append(bank.accept_transfer(8, "A", tid))              # A is new target -> True

		results.append(bank.get_balance(9, "A", 9))                    # A should receive 60
		results.append(bank.get_balance(10, "C", 10))                  # C should remain 40

		results.append(bank.top_spenders(11, 3))                       # outgoing counts to C after acceptance

		expected = [
		  True, True, True, 100,
		  tid,
		  True,
		  False,
		  True,
		  60,
		  40,
		  ["C(60)", "A(0)"]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 J------------------")
		bank = BankLevel5()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.create_account(3, "C"))

		results.append(bank.deposit(4, "B", 200))

		# payment1 by B at t=5 amount=101 cashback=2 at 86400005
		payment_id = bank.pay(5, "B", 101)
		results.append(payment_id)                           # B=99

		# pending transfer B->C amount=50 ttl=5 expires at 11
		tid = "transf-B-C-50-6"
		results.append(bank.transfer_with_exp(6, "B", "C", 50, 5))      # B available 49

		results.append(bank.merge_with_history(7, "A", "B"))            # A now has 49, B deleted

		# payment status should be checkable via A
		results.append(bank.get_payment_status(8, "A", payment_id))     # IN_PROGRESS

		# transfer expires at t=11 refund should go to source (now A)
		results.append(bank.get_balance(10, "A", 10))                   # still withheld -> 49
		results.append(bank.get_balance(11, "A", 11))                   # refunded +50 => 99

		# later cashback posts to A at 86400005 => +2 => 101 (we check status boundary)
		results.append(bank.get_payment_status(86400005, "A", payment_id))

		expected = [
		  True, True, True,
		  200,
		  payment_id,
		  tid,
		  True,
		  "IN_PROGRESS",
		  49,
		  99,
		  "CASHBACK_RECEIVED"
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 5 K------------------")
		bank = BankLevel5()

		results = []

		results.append(bank.create_account(1, "A"))
		results.append(bank.create_account(2, "B"))
		results.append(bank.deposit(3, "A", 100))

		# create at t=4 ttl=5 expires at 9
		tid = "transf-A-B-30-4"
		results.append(bank.transfer_with_exp(4, "A", "B", 30, 5))      # A available 70

		# Pre/after moments:
		results.append(bank.get_balance(5, "A", 3))                    # before transfer => 100
		results.append(bank.get_balance(6, "A", 4))                    # after creation => 70 (withheld)
		results.append(bank.get_balance(7, "B", 4))                    # B still 0

		# accept at t=8 (before expiry)
		results.append(bank.accept_transfer(8, "B", tid))              # True

		results.append(bank.get_balance(9, "A", 8))                    # after accept => still 70
		results.append(bank.get_balance(10, "B", 8))                   # after accept => 30

		# expiry time t=9 should have no effect now (already accepted)
		results.append(bank.get_balance(11, "A", 9))                   # 70
		results.append(bank.get_balance(12, "B", 9))                   # 30

		expected = [
		  True, True, 100,
		  tid,
		  100,
		  70,
		  0,
		  True,
		  70,
		  30,
		  70,
		  30
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)


test = Test()

# test.test_level1()
test.test_level2()
# test.test_level3()
# test.test_level4()
test.test_level5()

















