from collections import defaultdict


class InMemLvl1:
	def __init__(self):
		self.keys = defaultdict(dict)

	def command(self, *args):
		if args[0] == "SET":
			return self.set(args[1], args[2], args[3], args[4])
		elif args[0] == "COMPARE_AND_SET":
			return self.compare_and_set(args[1], args[2], args[3], args[4], args[5])
		elif args[0] == "COMPARE_AND_DELETE":
			return self.compare_and_delete(args[1], args[2], args[3], args[4])
		elif args[0] == "GET":
			return self.get(args[1], args[2], args[3])

	def set(self, timestamp, key, field, value):
		print(f"args - ts {timestamp}, key {key}, field {field}, value {value}")

		if self._is_in_mem(key, field):
			self.keys[key][field] = value

		self.keys[key][field] = value

		return ""


	def compare_and_set(self, timestamp, key, field, expected_value, new_value):
		if self._is_in_mem(key, field) and self.keys[key][field] == expected_value:
			self.keys[key][field] = new_value

			return "true"

		return "false"


	def compare_and_delete(self, timestamp, key, field, expected_value):
		if self._is_in_mem(key, field) and self.keys[key][field] == expected_value:
			del self.keys[key][field]

			return "true"

		return "false"

	def get(self, timestamp, key, field):
		if self._is_in_mem(key, field):
			return self.keys[key][field]

		return ""

	def _is_in_mem(self, key, field):
		return key in self.keys and field in self.keys[key]

# ==================================================================================
# ==================================================================================
# ==================================================================================

class InMemLvl2:
	def __init__(self):
		self.keys = defaultdict(dict)

	def command(self, *args):
		if args[0] == "SET":
			return self.set(args[1], args[2], args[3], args[4])
		elif args[0] == "COMPARE_AND_SET":
			return self.compare_and_set(args[1], args[2], args[3], args[4], args[5])
		elif args[0] == "COMPARE_AND_DELETE":
			return self.compare_and_delete(args[1], args[2], args[3], args[4])
		elif args[0] == "GET":
			return self.get(args[1], args[2], args[3])
		elif args[0] == "SCAN":
			return self.scan(args[1], args[2])
		elif args[0] == "SCAN_BY_PREFIX":
			return self.scan_by_prefix(args[1], args[2], args[3])

	def scan(self, timestamp, key):
		if key not in self.keys:
			return ""

		fields = sorted(self.keys[key].keys())

		result = []
		for field in fields:
			result.append(f"{field}({self.keys[key][field]})")

		return ", ".join(result)


	def scan_by_prefix(self, timestamp, key, prefix):
		if key not in self.keys:
			return ""

		fields = sorted(self.keys[key].keys())

		result = []
		for field in fields:
			if field.startswith(prefix):
				result.append(f"{field}({self.keys[key][field]})")

		return ", ".join(result)


	def set(self, timestamp, key, field, value):
		print(f"args - ts {timestamp}, key {key}, field {field}, value {value}")

		if self._is_in_mem(key, field):
			old = self.keys[key][field]

			self.keys[key][field] = value

		self.keys[key][field] = value

		return ""


	def compare_and_set(self, timestamp, key, field, expected_value, new_value):
		if self._is_in_mem(key, field) and self.keys[key][field] == expected_value:
			self.keys[key][field] = new_value

			return "true"

		return "false"


	def compare_and_delete(self, timestamp, key, field, expected_value):
		if self._is_in_mem(key, field) and self.keys[key][field] == expected_value:
			del self.keys[key][field]

			return "true"

		return "false"

	def get(self, timestamp, key, field):
		if self._is_in_mem(key, field):
			return self.keys[key][field]

		return ""

	def _is_in_mem(self, key, field):
		return key in self.keys and field in self.keys[key]

# ==================================================================================
# ==================================================================================
# ==================================================================================


class InMemLvl3:
	def __init__(self):
		self.keys = defaultdict(dict)

	def command(self, *args):
		if args[0] == "SET":
			return self.set(args[1], args[2], args[3], args[4])
		elif args[0] == "SET_WITH_TTL":
			return self.set_with_ttl(args[1], args[2], args[3], args[4], args[5])
		elif args[0] == "COMPARE_AND_SET":
			return self.compare_and_set(args[1], args[2], args[3], args[4], args[5])
		elif args[0] == "COMPARE_AND_DELETE":
			return self.compare_and_delete(args[1], args[2], args[3], args[4])
		elif args[0] == "GET":
			return self.get(args[1], args[2], args[3])
		elif args[0] == "SCAN":
			return self.scan(args[1], args[2])
		elif args[0] == "SCAN_BY_PREFIX":
			return self.scan_by_prefix(args[1], args[2], args[3])

	def scan(self, timestamp, key):
		if key not in self.keys:
			return ""

		fields = sorted(self.keys[key].keys())

		result = []
		for field in fields:
			if self.keys[key][field][1] > int(timestamp):
				result.append(f"{field}({self.keys[key][field][0]})")

		return ", ".join(result)


	def scan_by_prefix(self, timestamp, key, prefix):
		if key not in self.keys:
			return ""

		fields = sorted(self.keys[key].keys())

		result = []
		for field in fields:
			if field.startswith(prefix) and self.keys[key][field][1] > int(timestamp):
				result.append(f"{field}({self.keys[key][field][0]})")

		return ", ".join(result)

	def set_with_ttl(self, timestamp, key, field, value, ttl):
		self.keys[key][field] = (value, int(ttl) + int(timestamp))

		return ""

	def set(self, timestamp, key, field, value):
		# print(f"args - ts {timestamp}, key {key}, field {field}, value {value}")
		self.keys[key][field] = (value, 2**63 - 1)

		return ""


	def compare_and_set(self, timestamp, key, field, expected_value, new_value):
		if self._is_in_mem(key, field) and \
			self.keys[key][field][0] == expected_value and \
			self.keys[key][field][1] > int(timestamp):
			
			self.keys[key][field] = (new_value, self.keys[key][field][1])

			return "true"

		return "false"


	def compare_and_delete(self, timestamp, key, field, expected_value):
		if self._is_in_mem(key, field) and \
			self.keys[key][field][0] == expected_value and \
			self.keys[key][field][1] > int(timestamp):
			
			del self.keys[key][field]

			return "true"

		return "false"

	def get(self, timestamp, key, field):
		if self._is_in_mem(key, field) and self.keys[key][field][1] > int(timestamp):
			return self.keys[key][field][0]

		return ""

	def _is_in_mem(self, key, field):
		return key in self.keys and field in self.keys[key]

# ==================================================================================
# ==================================================================================
# ==================================================================================


class InMemLvl4GetWhen:
	def __init__(self):
		self.keys = defaultdict(dict)
		self.history = defaultdict(lambda: defaultdict(list))

	def command(self, *args):
		result = ""
		if args[0] == "SET":
			result = self.set(args[1], args[2], args[3], args[4])
		elif args[0] == "SET_WITH_TTL":
			result = self.set_with_ttl(args[1], args[2], args[3], args[4], args[5])
		elif args[0] == "COMPARE_AND_SET":
			result = self.compare_and_set(args[1], args[2], args[3], args[4], args[5])
		elif args[0] == "COMPARE_AND_DELETE":
			result = self.compare_and_delete(args[1], args[2], args[3], args[4])
		elif args[0] == "GET":
			result = self.get(args[1], args[2], args[3])
		elif args[0] == "SCAN":
			result = self.scan(args[1], args[2])
		elif args[0] == "SCAN_BY_PREFIX":
			result = self.scan_by_prefix(args[1], args[2], args[3])
		elif args[0] == "GET_WHEN":
			result = self.get_when(args[1], args[2], args[3], args[4])

		# print(args)
		# print("history")
		# print(self.history)
		# print("keys")
		# print(self.keys)

		return result

	def get_when(self, timestamp, key, field, at_timestamp):
		if not at_timestamp:
			return get(timestamp, key, field)

		if key in self.history and field in self.history[key]:
			for value_history in self.history[key][field]:
				if value_history[1] <= int(at_timestamp) < value_history[2]:
					return value_history[0]

		return ""

	def scan(self, timestamp, key):
		if key not in self.keys:
			return ""

		fields = sorted(self.keys[key].keys())

		result = []
		for field in fields:
			if self.keys[key][field][1] > int(timestamp):
				result.append(f"{field}({self.keys[key][field][0]})")

		return ", ".join(result)


	def scan_by_prefix(self, timestamp, key, prefix):
		if key not in self.keys:
			return ""

		fields = sorted(self.keys[key].keys())

		result = []
		for field in fields:
			if field.startswith(prefix) and self.keys[key][field][1] > int(timestamp):
				result.append(f"{field}({self.keys[key][field][0]})")

		return ", ".join(result)

	def set_with_ttl(self, timestamp, key, field, value, ttl):
		self.keys[key][field] = (value, int(ttl) + int(timestamp))
		self._set_history(key, field, value, int(ttl), int(timestamp))

		return ""

	def set(self, timestamp, key, field, value):
		# print(f"args - ts {timestamp}, key {key}, field {field}, value {value}")
		self.keys[key][field] = (value, 2**63 - 1)
		self._set_history(key, field, value, 2**63 - 1, int(timestamp))

		return ""


	def compare_and_set(self, timestamp, key, field, expected_value, new_value):
		if self._is_in_mem(key, field) and \
			self.keys[key][field][0] == expected_value and \
			self.keys[key][field][1] > int(timestamp):
			
			self.keys[key][field] = (new_value, self.keys[key][field][1])
			self._set_history(key, field, value, int(ttl), int(timestamp))

			return "true"

		return "false"


	def compare_and_delete(self, timestamp, key, field, expected_value):
		if self._is_in_mem(key, field) and \
			self.keys[key][field][0] == expected_value and \
			self.keys[key][field][1] > int(timestamp):

			self.history[key][field][-1][2] = int(timestamp)
			
			del self.keys[key][field]

			return "true"

		return "false"

	def get(self, timestamp, key, field):
		if self._is_in_mem(key, field) and self.keys[key][field][1] > int(timestamp):
			return self.keys[key][field][0]

		return ""

	def _is_in_mem(self, key, field):
		return key in self.keys and field in self.keys[key]

	def _set_history(self, key, field, value, ttl, timestamp):
		field_history = self.history[key][field]
		# update last field history for expire time
		if field_history and field_history[-1][2] > timestamp:
			field_history[-1][2] = timestamp

		field_history.append([value, timestamp, ttl + timestamp if ttl != 2**63 - 1 else 2**63 - 1])
		field_history.sort(key=lambda x: x[1])


# ==================================================================================
# ==================================================================================
# ==================================================================================
import copy
import bisect # binary search

class InMemLvl4Backup:
	def __init__(self):
		self.keys = defaultdict(dict)
		self.snapshots = defaultdict(lambda: defaultdict(dict))

	def command(self, *args):
		result = ""
		if args[0] == "SET":
			result = self.set(args[1], args[2], args[3], args[4])
		elif args[0] == "SET_WITH_TTL":
			result = self.set_with_ttl(args[1], args[2], args[3], args[4], args[5])
		elif args[0] == "COMPARE_AND_SET":
			result = self.compare_and_set(args[1], args[2], args[3], args[4], args[5])
		elif args[0] == "COMPARE_AND_DELETE":
			result = self.compare_and_delete(args[1], args[2], args[3], args[4])
		elif args[0] == "GET":
			result = self.get(args[1], args[2], args[3])
		elif args[0] == "SCAN":
			result = self.scan(args[1], args[2])
		elif args[0] == "SCAN_BY_PREFIX":
			result = self.scan_by_prefix(args[1], args[2], args[3])
		elif args[0] == "BACKUP":
			result = self.backup(args[1])
		elif args[0] == "RESTORE":
			result = self.restore(args[1], args[2])

		# print("----------------------------------")
		# print(args)
		# # print("history")
		# # print(self.history)
		# print("keys")
		# print(self.keys)
		# print("snapshots")
		# print(self.snapshots)
		# print(f"result - {result}")
		# print("----------------------------------")

		return result

	def backup(self, timestamp):
		self.snapshots[int(timestamp)] = copy.deepcopy(self.keys)

		key_count = 0
		for key, fields in self.keys.items():
			for field, value_pair in fields.items():
				if value_pair[1] > int(timestamp):
					key_count += 1
					break

		return str(key_count)

	def restore(self, timestamp, at_timestamp):
		snapshots_ts = sorted(self.snapshots.keys())
		if not snapshots_ts:
			return

		last_ts = snapshots_ts[bisect.bisect_right(snapshots_ts, int(at_timestamp)) - 1]
		last_snapshot_copy = copy.deepcopy(self.snapshots[last_ts])

		# print(f"last_ts - {last_ts}")
		# print(f"last_snapshot_copy - {last_snapshot_copy}")

		# update ttl
		for key, fields in last_snapshot_copy.items():
			for field, value_pair in fields.items():
				if value_pair[1] > last_ts and value_pair[1] != 2**63 - 1:
					remain_ttl = value_pair[1] - last_ts
					new_ttl = int(timestamp) + remain_ttl
					fields[field] = (value_pair[0], new_ttl)

		self.keys = last_snapshot_copy

		return ""

	def scan(self, timestamp, key):
		if key not in self.keys:
			return ""

		fields = sorted(self.keys[key].keys())

		result = []
		for field in fields:
			if self.keys[key][field][1] > int(timestamp):
				result.append(f"{field}({self.keys[key][field][0]})")

		return ", ".join(result)


	def scan_by_prefix(self, timestamp, key, prefix):
		if key not in self.keys:
			return ""

		fields = sorted(self.keys[key].keys())

		result = []
		for field in fields:
			if field.startswith(prefix) and self.keys[key][field][1] > int(timestamp):
				result.append(f"{field}({self.keys[key][field][0]})")

		return ", ".join(result)

	def set_with_ttl(self, timestamp, key, field, value, ttl):
		self.keys[key][field] = (value, int(ttl) + int(timestamp))

		return ""

	def set(self, timestamp, key, field, value):
		# print(f"args - ts {timestamp}, key {key}, field {field}, value {value}")
		self.keys[key][field] = (value, 2**63 - 1)

		return ""


	def compare_and_set(self, timestamp, key, field, expected_value, new_value):
		if self._is_in_mem(key, field) and \
			self.keys[key][field][0] == expected_value and \
			self.keys[key][field][1] > int(timestamp):
			
			self.keys[key][field] = (new_value, self.keys[key][field][1])

			return "true"

		return "false"


	def compare_and_delete(self, timestamp, key, field, expected_value):
		if self._is_in_mem(key, field) and \
			self.keys[key][field][0] == expected_value and \
			self.keys[key][field][1] > int(timestamp):
			
			del self.keys[key][field]

			return "true"

		return "false"

	def get(self, timestamp, key, field):
		if self._is_in_mem(key, field) and self.keys[key][field][1] > int(timestamp):
			return self.keys[key][field][0]

		return ""

	def _is_in_mem(self, key, field):
		return key in self.keys and field in self.keys[key]




class TestsRun:
	def __init__(self):
		self.in_mem = InMemLvl4GetWhen()

	def test1(self):
		print("========running test1========")
		commands = [
		  ["SET", "0", "A", "B", "4"],
		  ["SET", "1", "A", "C", "6"],
		  ["COMPARE_AND_SET", "2", "A", "B", "4", "9"],
		  ["COMPARE_AND_SET", "3", "A", "C", "4", "9"],
		  ["COMPARE_AND_DELETE", "4", "A", "C", "6"],
		  ["GET", "5", "A", "C"],
		  ["GET", "6", "A", "B"]
		]
		expected_results = ["", "", "true", "false", "true", "", "9"]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)


	def test2(self):
		print("========running test2========")
		commands = [
		  ["SET", "160000000", "a", "a", "1"],
		  ["SET", "160000001", "a", "A", "2"],
		  ["GET", "160000002", "a", "a"],
		  ["COMPARE_AND_DELETE", "160000003", "a", "a", "0"],
		  ["GET", "160000004", "a", "a"],
		  ["COMPARE_AND_DELETE", "160000005", "a", "a", "1"],
		  ["GET", "160000006", "a", "a"],
		  ["GET", "160000007", "a", "A"],
		  ["COMPARE_AND_DELETE", "160000008", "a", "A", "2"],
		  ["SET", "160000009", "a", "A", "7"],
		  ["SET", "160000010", "a", "A", "9"],
		  ["GET", "160000011", "a", "a"],
		  ["GET", "160000012", "a", "A"]
		]

		expected_results = ["", "", "1", "false", "1", "true", "", "2", "true", "", "", "", "9"]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test3(self):
		print("========running test3========")
		commands = [
		  ["SET", "1", "A", "BC", "1"],
		  ["SET", "2", "A", "BD", "2"],
		  ["SET", "3", "A", "C", "3"],
		  ["SCAN_BY_PREFIX", "4", "A", "B"],
		  ["SCAN", "5", "A"],
		  ["SCAN_BY_PREFIX", "6", "B", "B"]
		]

		expected_results = ["", "", "", "BC(1), BD(2)", "BC(1), BD(2), C(3)", ""]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test4(self):
		print("========running test4========")
		commands = [
		  ["SET_WITH_TTL", "1", "A", "BC", "1", "9"],
		  ["SET_WITH_TTL", "5", "A", "BC", "2", "10"],
		  ["SET", "6", "A", "BD", "3"],
		  ["SCAN_BY_PREFIX", "14", "A", "B"],
		  ["SCAN_BY_PREFIX", "15", "A", "B"]
		]

		expected_results = ["", "", "", "BC(2), BD(3)", "BD(3)"]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test5(self):
		print("========running test5========")
		commands = [
		  ["SET", "1", "A", "B", "1"],
		  ["SET_WITH_TTL", "2", "X", "Y", "5", "15"],
		  ["GET", "3", "X", "Y"],
		  ["SET_WITH_TTL", "4", "A", "D", "2", "10"],
		  ["SCAN", "13", "A"],
		  ["SCAN", "14", "A"],
		  ["SCAN", "16", "X"],
		  ["SCAN", "17", "X"],
		  ["COMPARE_AND_DELETE", "20", "X", "Y", "5"]
		]

		expected_results = ["", "", "5", "", "B(1), D(2)", "B(1)", "Y(5)", "", "false"]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test6(self):
		print("========running test6========")
		commands = [
		  ["SET_WITH_TTL", "1", "A", "B", "10", "5"],
		  ["GET", "2", "A", "B"],
		  ["SET", "3", "A", "B", "20"],
		  ["GET_WHEN", "10", "A", "B", "2"],
		  ["GET_WHEN", "10", "A", "B", "7"],
		  ["GET", "10", "A", "B"]
		]

		expected_results = ["", "10", "", "10", "20", "20"]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl_1(self):
		self.in_mem = InMemLvl1()

		print("========running test lvl 1 A========")
		commands = [
		  ["SET", "1", "k1", "f", "1"],
		  ["COMPARE_AND_SET", "2", "k1", "f", "2", "3"],
		  ["GET", "3", "k1", "f"],
		  ["COMPARE_AND_DELETE", "4", "k1", "g", "0"],
		  ["SET", "5", "k2", "x", "7"],
		  ["GET", "6", "k2", "x"],
		  ["COMPARE_AND_SET", "7", "k2", "x", "7", "8"],
		  ["GET", "8", "k2", "x"],
		  ["COMPARE_AND_DELETE", "9", "k2", "x", "9"],
		  ["COMPARE_AND_DELETE", "10", "k2", "x", "8"],
		  ["GET", "11", "k2", "x"],
		  ["GET", "12", "k2", "y"],
		  ["SET", "13", "k2", "y", "-5"],
		  ["GET", "14", "k2", "y"]
		]

		expected_results = ["", "false", "1", "false", "", "7", "true", "8", "false", "true", "", "", "", "-5"]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 1 B========")
		commands = [
		  ["SET", "100", "A", "b", "1"],
		  ["SET", "101", "A", "b", "2"],
		  ["COMPARE_AND_SET", "102", "A", "b", "2", "0"],
		  ["COMPARE_AND_DELETE", "103", "A", "b", "0"],
		  ["COMPARE_AND_SET", "104", "A", "b", "0", "9"],
		  ["GET", "105", "A", "b"],
		  ["SET", "106", "A", "b", "9"],
		  ["COMPARE_AND_DELETE", "107", "A", "b", "9"],
		  ["GET", "108", "A", "b"]
		]

		expected_results = ["", "", "true", "true", "false", "", "", "true", ""]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl_2(self):
		self.in_mem = InMemLvl2()

		print("========running test lvl 2 A========")
		commands = [
		  ["SET", "1", "R", "aa", "1"],
		  ["SET", "2", "R", "ab", "2"],
		  ["SET", "3", "R", "b", "3"],
		  ["SET", "4", "R", "ba", "4"],
		  ["SCAN_BY_PREFIX", "5", "R", "a"],
		  ["COMPARE_AND_DELETE", "6", "R", "ab", "2"],
		  ["SCAN", "7", "R"],
		  ["SCAN_BY_PREFIX", "8", "R", "ab"],
		  ["SCAN_BY_PREFIX", "9", "R", ""],
		  ["COMPARE_AND_DELETE", "10", "R", "aa", "1"],
		  ["COMPARE_AND_DELETE", "11", "R", "b", "3"],
		  ["COMPARE_AND_DELETE", "12", "R", "ba", "4"],
		  ["SCAN", "13", "R"],
		  ["SCAN_BY_PREFIX", "14", "R", "b"]
		]

		expected_results = [
		  "", "", "", "",
		  "aa(1), ab(2)",
		  "true",
		  "aa(1), b(3), ba(4)",
		  "",
		  "aa(1), b(3), ba(4)",
		  "true", "true", "true",
		  "",
		  ""
		]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 2 B========")
		commands = [
		  ["SET", "20", "K", "f", "1"],
		  ["SET", "21", "K", "foo", "2"],
		  ["SET", "22", "K", "fo", "3"],
		  ["SCAN", "23", "K"],
		  ["SCAN_BY_PREFIX", "24", "K", "fo"],
		  ["SCAN_BY_PREFIX", "25", "K", "fooo"],
		  ["SCAN", "26", "Z"],
		  ["GET", "27", "K", "f"]
		]

		expected_results = ["", "", "", "f(1), fo(3), foo(2)", "fo(3), foo(2)", "", "", "1"]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)


	def test_lvl_3(self):
		self.in_mem = InMemLvl3()

		print("========running test lvl 3 A========")
		commands = [
		  ["SET_WITH_TTL", "1", "A", "x", "10", "5"],
		  ["GET", "5", "A", "x"],
		  ["GET", "6", "A", "x"],
		  ["COMPARE_AND_SET", "7", "A", "x", "10", "11"],
		  ["SET_WITH_TTL", "8", "A", "x", "12", "0"],
		  ["GET", "9", "A", "x"],
		  ["SET", "10", "A", "y", "1"],
		  ["SCAN", "11", "A"],
		  ["SET_WITH_TTL", "12", "A", "y", "2", "5"],
		  ["GET", "16", "A", "y"],
		  ["GET", "17", "A", "y"],
		  ["SCAN", "18", "A"]
		]

		expected_results = ["", "10", "", "false", "", "", "", "y(1)", "", "2", "", ""]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 3 B========")
		commands = [
		  ["SET", "100", "R", "a", "1"],
		  ["SET_WITH_TTL", "101", "R", "b", "2", "4"],
		  ["SET_WITH_TTL", "102", "R", "c", "3", "2"],
		  ["SCAN", "103", "R"],
		  ["SCAN", "104", "R"],
		  ["SCAN_BY_PREFIX", "105", "R", "b"],
		  ["COMPARE_AND_DELETE", "106", "R", "b", "2"],
		  ["SET_WITH_TTL", "107", "R", "b", "5", "10"],
		  ["COMPARE_AND_SET", "108", "R", "b", "2", "6"],
		  ["COMPARE_AND_SET", "109", "R", "b", "5", "6"],
		  ["GET", "116", "R", "b"],
		  ["GET", "117", "R", "b"]
		]

		expected_results = [
		  "", "", "",
		  "a(1), b(2), c(3)",
		  "a(1), b(2)",
		  "",
		  "false",
		  "",
		  "false",
		  "true",
		  "6",
		  ""
		]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)


	def test_lvl_4(self):
		print("========running test lvl 4 A========")
		self.in_mem = InMemLvl4GetWhen()
		commands = [
		  ["SET_WITH_TTL", "1", "K", "f", "1", "5"],
		  ["SET", "2", "K", "g", "7"],
		  ["SET", "3", "K", "f", "2"],
		  ["COMPARE_AND_DELETE", "4", "K", "g", "7"],
		  ["GET_WHEN", "10", "K", "f", "2"],
		  ["GET_WHEN", "10", "K", "f", "5"],
		  ["GET_WHEN", "10", "K", "f", "7"],
		  ["GET_WHEN", "10", "K", "g", "3"],
		  ["GET_WHEN", "10", "K", "g", "4"],
		  ["GET_WHEN", "10", "K", "g", "0"],
		  ["GET", "10", "K", "f"],
		  ["SCAN", "10", "K"]
		]

		expected_results = [
		  "", "", "", "true",
		  "1",
		  "2",
		  "2",
		  "7",
		  "",
		  "",
		  "2",
		  "f(2)"
		]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 B========")
		self.in_mem = InMemLvl4GetWhen()
		commands = [
		  ["SET_WITH_TTL", "100", "A", "x", "5", "10"],
		  ["SET_WITH_TTL", "105", "A", "x", "6", "3"],
		  ["GET_WHEN", "120", "A", "x", "104"],
		  ["GET_WHEN", "120", "A", "x", "106"],
		  ["GET_WHEN", "120", "A", "x", "108"],
		  ["SET", "109", "A", "x", "7"],
		  ["GET_WHEN", "120", "A", "x", "108"],
		  ["GET_WHEN", "120", "A", "x", "110"],
		  ["COMPARE_AND_DELETE", "111", "A", "x", "7"],
		  ["GET_WHEN", "120", "A", "x", "111"],
		  ["GET_WHEN", "120", "A", "x", "110"],
		  ["GET", "120", "A", "x"]
		]

		expected_results = ["", "", "5", "6", "", "", "", "7", "true", "", "7", ""]


		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl_4_backup(self):
		print("========running test lvl 4 backup A========")
		self.in_mem = InMemLvl4Backup()
		commands = [
		  ["SET_WITH_TTL", "1", "A", "f", "1", "10"],
		  ["SET", "2", "B", "x", "5"],
		  ["BACKUP", "3"],
		  ["SET_WITH_TTL", "4", "A", "g", "2", "3"],
		  ["BACKUP", "5"],
		  ["COMPARE_AND_DELETE", "6", "B", "x", "5"],
		  ["BACKUP", "7"],
		  ["RESTORE", "8", "6"],
		  ["SCAN", "9", "A"],
		  ["SCAN", "10", "A"],
		  ["GET", "11", "A", "f"],
		  ["SCAN", "12", "B"],
		  ["BACKUP", "13"],
		  ["GET", "14", "A", "f"]
		]

		expected_results = [
		  "", "",
		  "2",
		  "",
		  "2",
		  "true",
		  "1",
		  "",
		  "f(1), g(2)",
		  "f(1)",
		  "1",
		  "x(5)",
		  "2",
		  ""
		]

		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 backup B========")
		self.in_mem = InMemLvl4Backup()
		commands = [
		  ["SET_WITH_TTL", "1", "K", "a", "1", "2"],
		  ["SET_WITH_TTL", "2", "K", "b", "2", "1"],
		  ["BACKUP", "2"],
		  ["GET", "3", "K", "a"],
		  ["BACKUP", "3"],
		  ["RESTORE", "4", "2"],
		  ["SCAN", "4", "K"],
		  ["SCAN", "5", "K"],
		  ["SET", "6", "K", "c", "3"],
		  ["BACKUP", "6"],
		  ["RESTORE", "7", "3"],
		  ["SCAN", "7", "K"],
		  ["GET", "8", "K", "c"]
		]
		expected_results = [
		  "", "",
		  "1",
		  "",
		  "0",
		  "",
		  "a(1), b(2)",
		  "",
		  "",
		  "1",
		  "",
		  "",
		  ""
		]


		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 backup C========")
		self.in_mem = InMemLvl4Backup()
		commands = [
		  ["SET_WITH_TTL", "1", "A", "p", "10", "5"],
		  ["SET", "2", "A", "q", "1"],
		  ["SET_WITH_TTL", "3", "B", "x", "7", "10"],
		  ["BACKUP", "4"],
		  ["SET_WITH_TTL", "5", "A", "p", "11", "2"],
		  ["BACKUP", "6"],
		  ["GET", "7", "A", "p"],
		  ["COMPARE_AND_SET", "8", "A", "p", "11", "12"],
		  ["RESTORE", "9", "4"],
		  ["GET", "10", "A", "p"],
		  ["SCAN_BY_PREFIX", "12", "A", "p"],
		  ["SCAN", "12", "B"],
		  ["BACKUP", "12"],
		  ["RESTORE", "20", "12"],
		  ["GET", "25", "B", "x"],
		  ["GET", "26", "B", "x"]
		]
		expected_results = [
		  "", "", "", 
		  "2",
		  "",
		  "2",
		  "",
		  "false",
		  "",
		  "10",
		  "",
		  "x(7)",
		  "2",
		  "",
		  "7",
		  ""
		]


		results = []

		for c in commands:
			results.append(self.in_mem.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)






test = TestsRun()

test.test_lvl_1()
test.test_lvl_2()
test.test_lvl_3()
test.test_lvl_4()
test.test_lvl_4_backup()
