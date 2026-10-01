from collections import defaultdict

# ==================================================================================
# ==================================================================================
# ==================================================================================


class Task:
	def __init__(self, task_id, name, priority):
		self.id = task_id
		self.name = name
		self.priority = priority


class TaskManagerLvl1:
	def __init__(self):
		self.tasks = defaultdict(Task)
		self.counter = 1

	def add_task(self, timestamp, name, priority):
		task_id = f"task_id_{self.counter}"
		self.counter += 1

		self.tasks[task_id] = Task(task_id, name, priority)

		return task_id

	def update_task(self, timestamp, task_id, name, priority):
		if task_id not in self.tasks:
			return False

		task = self.tasks[task_id]
		task.priority = priority
		task.name = name

		return True

	def get_task(self, timestamp, task_id):
		if task_id not in self.tasks:
			return None

		task = self.tasks[task_id]

		return f'{{"name":"{task.name}","priority":{task.priority}}}'


# ==================================================================================
# ==================================================================================
# ==================================================================================


class TaskLvl2:
	def __init__(self, task_id, name, priority, order):
		self.id = task_id
		self.name = name
		self.priority = priority
		self.order = order


class TaskManagerLvl2:
	def __init__(self):
		self.tasks = defaultdict(Task)
		self.counter = 1

	def search_tasks(self, timestamp, name_filter, max_results):
		if max_results <= 0:
			return []

		found_tasks = []
		for task in self.tasks.values():
			if name_filter in task.name:
				found_tasks.append((task.id, task.priority, task.order))

		# sort desc by priority, if tie, sort asc by creation order
		found_tasks.sort(key=lambda x: (-x[1], x[2]))
		return [t[0] for t in found_tasks[:max_results]]

	def list_tasks_sorted(self, timestamp, limit):
		all_tasks = [(task.id, task.priority, task.order) for task_id, task in self.tasks.items()]
		all_tasks.sort(key=lambda x: (-x[1], x[2]))

		return [t[0] for t in all_tasks[:limit]]

	def add_task(self, timestamp, name, priority):
		task_id = f"task_id_{self.counter}"
		self.tasks[task_id] = TaskLvl2(task_id, name, priority, self.counter)

		self.counter += 1
		return task_id

	def update_task(self, timestamp, task_id, name, priority):
		if task_id not in self.tasks:
			return False

		task = self.tasks[task_id]
		task.priority = priority
		task.name = name

		return True

	def get_task(self, timestamp, task_id):
		if task_id not in self.tasks:
			return None

		task = self.tasks[task_id]

		return f'{{"name":"{task.name}","priority":{task.priority}}}'

# ==================================================================================
# ==================================================================================
# ==================================================================================


class TaskLvl3:
	def __init__(self, task_id, name, priority, order):
		self.id = task_id
		self.name = name
		self.priority = priority
		self.order = order

class User:
	def __init__(self, user_id, quota):
		self.id = user_id
		self.quota = quota
		# [(start_time, end_time, task)]
		self.tasks = []


class TaskManagerLvl3:
	def __init__(self):
		self.tasks = defaultdict(TaskLvl3)
		self.users = defaultdict(User)
		self.counter = 1

	def add_user(self, timestamp, user_id, quota):
		if user_id in self.users:
			return False

		self.users[user_id] = User(user_id, quota)

		return True

	def assign_task(self, timestamp, task_id, user_id, finish_time):
		if user_id not in self.users or task_id not in self.tasks:
			return False

		user = self.users[user_id]
		cur_tasks = user.tasks
		cur_quota = 0

		# calculate quota
		# find overlap tasks on timestamp
		for start_time, end_time, task in cur_tasks:
			if end_time <= timestamp or start_time > timestamp:
				continue
			cur_quota += 1

		if cur_quota >= user.quota:
			return False

		user.tasks.append((timestamp, finish_time, self.tasks[task_id]))

		return True

	def get_user_tasks(self, timestamp, user_id):
		if user_id not in self.users:
			return []

		tasks = self.users[user_id].tasks

		tasks.sort(key=lambda x: x[0])

		selected_tasks = []
		for t in tasks:
			if t[1] <= timestamp or t[0] > timestamp:
				continue
			selected_tasks.append((t[0], t[1], t[2].id))

		selected_tasks.sort(key=lambda x: (x[1], x[0]))

		return [t[2] for t in selected_tasks]

	def search_tasks(self, timestamp, name_filter, max_results):
		if max_results <= 0:
			return []

		found_tasks = []
		for task in self.tasks.values():
			if name_filter in task.name:
				found_tasks.append((task.id, task.priority, task.order))

		# sort desc by priority, if tie, sort asc by creation order
		found_tasks.sort(key=lambda x: (-x[1], x[2]))
		return [t[0] for t in found_tasks[:max_results]]

	def list_tasks_sorted(self, timestamp, limit):
		all_tasks = [(task.id, task.priority, task.order) for task_id, task in self.tasks.items()]
		all_tasks.sort(key=lambda x: (-x[1], x[2]))

		return [t[0] for t in all_tasks[:limit]]

	def add_task(self, timestamp, name, priority):
		task_id = f"task_id_{self.counter}"
		self.tasks[task_id] = TaskLvl3(task_id, name, priority, self.counter)

		self.counter += 1
		return task_id

	def update_task(self, timestamp, task_id, name, priority):
		if task_id not in self.tasks:
			return False

		task = self.tasks[task_id]
		task.priority = priority
		task.name = name

		return True

	def get_task(self, timestamp, task_id):
		if task_id not in self.tasks:
			return None

		task = self.tasks[task_id]

		return f'{{"name":"{task.name}","priority":{task.priority}}}'

# ==================================================================================
# ==================================================================================
# ==================================================================================


class TaskLvl4:
	def __init__(self, task_id, name, priority, order):
		self.id = task_id
		self.name = name
		self.priority = priority
		self.order = order


class UserLvl4:
	def __init__(self, user_id, quota):
		self.id = user_id
		self.quota = quota
		# [(start_time, end_time, task)]
		self.tasks = []


class TaskManagerLvl4:
	def __init__(self):
		self.tasks = defaultdict(TaskLvl4)
		self.users = defaultdict(UserLvl4)
		self.counter = 1

	def complete_task(self, timestamp, task_id, user_id):
		if task_id not in self.tasks or user_id not in self.users:
			return False

		user = self.users[user_id]
		tasks = user.tasks

		tasks.sort(key=lambda x: x[0])

		target_idx = -1
		for idx, t in enumerate(tasks):
			if t[1] <= timestamp or t[0] > timestamp:
				continue
			if t[2].id == task_id:
				target_idx = idx
				break

		if target_idx == -1:
			return False

		tasks.pop(target_idx)

		return True

	def get_overdue_assignments(self, timestamp, user_id):
		if user_id not in self.users:
			return []

		overdue_tasks = []
		user = self.users[user_id]
		tasks = user.tasks

		for start_time, end_time, task in tasks:
			if end_time <= timestamp:
				overdue_tasks.append((start_time, end_time, task.id))

		overdue_tasks.sort(key=lambda x: (x[1], x[0]))

		return [t[2] for t in overdue_tasks]


	def add_user(self, timestamp, user_id, quota):
		if user_id in self.users:
			return False

		self.users[user_id] = UserLvl4(user_id, quota)

		return True

	def assign_task(self, timestamp, task_id, user_id, finish_time):
		if user_id not in self.users or task_id not in self.tasks:
			return False

		user = self.users[user_id]
		cur_tasks = user.tasks
		cur_quota = 0

		# calculate quota
		# find overlap tasks on timestamp
		for start_time, end_time, task in cur_tasks:
			if end_time <= timestamp or start_time > timestamp:
				continue
			cur_quota += 1

		if cur_quota >= user.quota:
			return False

		user.tasks.append((timestamp, finish_time, self.tasks[task_id]))

		return True

	def get_user_tasks(self, timestamp, user_id):
		if user_id not in self.users:
			return []

		tasks = self.users[user_id].tasks

		tasks.sort(key=lambda x: x[0])

		selected_tasks = []
		for t in tasks:
			if t[1] <= timestamp or t[0] > timestamp:
				continue
			selected_tasks.append((t[0], t[1], t[2].id))

		selected_tasks.sort(key=lambda x: (x[1], x[0]))

		return [t[2] for t in selected_tasks]

	def search_tasks(self, timestamp, name_filter, max_results):
		if max_results <= 0:
			return []

		found_tasks = []
		for task in self.tasks.values():
			if name_filter in task.name:
				found_tasks.append((task.id, task.priority, task.order))

		# sort desc by priority, if tie, sort asc by creation order
		found_tasks.sort(key=lambda x: (-x[1], x[2]))
		return [t[0] for t in found_tasks[:max_results]]

	def list_tasks_sorted(self, timestamp, limit):
		all_tasks = [(task.id, task.priority, task.order) for task_id, task in self.tasks.items()]
		all_tasks.sort(key=lambda x: (-x[1], x[2]))

		return [t[0] for t in all_tasks[:limit]]

	def add_task(self, timestamp, name, priority):
		task_id = f"task_id_{self.counter}"
		self.tasks[task_id] = TaskLvl4(task_id, name, priority, self.counter)

		self.counter += 1
		return task_id

	def update_task(self, timestamp, task_id, name, priority):
		if task_id not in self.tasks:
			return False

		task = self.tasks[task_id]
		task.priority = priority
		task.name = name

		return True

	def get_task(self, timestamp, task_id):
		if task_id not in self.tasks:
			return None

		task = self.tasks[task_id]

		return f'{{"name":"{task.name}","priority":{task.priority}}}'


class Test:
	def __init__(self):
		pass

	def test_level1(self):
		print("========running test lvl 1 A========")
		manager = TaskManagerLvl1()

		out = []

		t1 = manager.add_task(1, "Task 1", 5)
		out.append(t1)  # "task_id_1"

		t2 = manager.add_task(2, "Task 1", 5)
		out.append(t2)  # "task_id_2" (same name+priority allowed)

		out.append(manager.get_task(3, t2))
		out.append(manager.update_task(4, t1, " Updated  Task 1 ", 0))  # preserve spaces in name
		out.append(manager.get_task(5, t1))

		out.append(manager.get_task(6, "task_id_999"))                  # None
		out.append(manager.update_task(7, "task_id_999", "Nope", 1))     # False

		out.append(manager.update_task(8, t2, "Task 1", 5))              # True
		out.append(manager.get_task(9, t2))

		expected = [
		    "task_id_1",
		    "task_id_2",
		    '{"name":"Task 1","priority":5}',
		    True,
		    '{"name":" Updated  Task 1 ","priority":0}',
		    None,
		    False,
		    True,
		    '{"name":"Task 1","priority":5}',
		]

		print(f"expected {expected}")
		print(f"actual {out}")
		print(expected == out)

	def test_level2(self):
		print("========running test lvl 2 A========")
		manager = TaskManagerLvl2()

		out = []

		id1  = manager.add_task(1,  "Alpha",      5)
		id2  = manager.add_task(2,  "beta",       7)
		id3  = manager.add_task(3,  "Alpha beta", 7)
		id4  = manager.add_task(4,  "Gamma",      7)
		id5  = manager.add_task(5,  "Al",         7)
		id6  = manager.add_task(6,  "Alphabet",   7)
		id7  = manager.add_task(7,  "Alpha",      0)
		id8  = manager.add_task(8,  "alpha",      9)   # lowercase
		id9  = manager.add_task(9,  "Alpha10",    7)
		id10 = manager.add_task(10, "Alpha11",    7)
		id11 = manager.add_task(11, "Alpha12",    7)
		id12 = manager.add_task(12, "Alpha13",    7)

		out.extend([id1,id2,id3,id4,id5,id6,id7,id8,id9,id10,id11,id12])

		# list_tasks_sorted: priority desc, tie by creation order (numeric id asc)
		out.append(manager.list_tasks_sorted(13, 5))

		# search is case-sensitive substring match
		out.append(manager.search_tasks(14, "Alpha", 10))

		# update changes both name and priority
		out.append(manager.update_task(15, id1, "Alpha Updated", 10))
		out.append(manager.search_tasks(16, "Alpha", 3))

		# lowercase filter only matches lowercase names
		out.append(manager.search_tasks(17, "alpha", 10))

		# limits <= 0 => []
		out.append(manager.list_tasks_sorted(18, 0))
		out.append(manager.search_tasks(19, "Alpha", -1))

		expected = [
		    "task_id_1","task_id_2","task_id_3","task_id_4","task_id_5","task_id_6",
		    "task_id_7","task_id_8","task_id_9","task_id_10","task_id_11","task_id_12",

		    ["task_id_8", "task_id_2", "task_id_3", "task_id_4", "task_id_5"],

		    ["task_id_3", "task_id_6", "task_id_9", "task_id_10", "task_id_11", "task_id_12", "task_id_1", "task_id_7"],

		    True,

		    ["task_id_1", "task_id_3", "task_id_6"],

		    ["task_id_8"],

		    [],
		    [],
		]

		print(f"expected {expected}")
		print(f"actual {out}")
		print(expected == out)


	def test_level3(self):
		print("========running test lvl 3 A========")
		manager = TaskManagerLvl3()

		out = []

		out.append(manager.add_user(1, "u1", 2))
		out.append(manager.add_user(2, "u1", 5))      # duplicate => False
		out.append(manager.add_user(3, "u2", 1))

		t1 = manager.add_task(4, "Task A", 0)
		t2 = manager.add_task(5, "Task B", 0)
		t3 = manager.add_task(6, "Task C", 0)
		out.extend([t1, t2, t3])

		# assignment active during [start, finish)
		out.append(manager.assign_task(7, t1, "u1", 20))   # active at t=7..19
		out.append(manager.get_user_tasks(8, "u1"))

		out.append(manager.assign_task(9,  t2, "u1", 12))  # active at t=9..11
		out.append(manager.assign_task(10, t3, "u1", 15))  # should fail at t=10 (quota full: t1+t2)

		out.append(manager.get_user_tasks(11, "u1"))       # [t2, t1]
		out.append(manager.get_user_tasks(12, "u1"))       # at t=12 t2 expired => [t1]

		out.append(manager.assign_task(13, t3, "u1", 15))  # now succeeds
		out.append(manager.get_user_tasks(14, "u1"))       # [t3, t1]
		out.append(manager.get_user_tasks(15, "u1"))       # at t=15 t3 expired => [t1]

		out.append(manager.assign_task(16, t2, "u2", 18))  # u2 quota 1
		out.append(manager.assign_task(17, t3, "u2", 19))  # fails (quota full at t=17)
		out.append(manager.get_user_tasks(18, "u2"))       # at t=18 [16,18) expired => []

		out.append(manager.assign_task(19, t3, "u2", 25))  # succeeds
		out.append(manager.get_user_tasks(20, "u2"))       # [t3]

		out.append(manager.assign_task(21, "task_id_999", "u1", 30))  # bad task => False
		out.append(manager.assign_task(22, t1, "no_user", 30))        # bad user => False
		out.append(manager.get_user_tasks(23, "no_user"))             # [] if user doesn't exist

		expected = [
		    True,
		    False,
		    True,

		    "task_id_1",
		    "task_id_2",
		    "task_id_3",

		    True,
		    ["task_id_1"],

		    True,
		    False,

		    ["task_id_2", "task_id_1"],
		    ["task_id_1"],

		    True,
		    ["task_id_3", "task_id_1"],
		    ["task_id_1"],

		    True,
		    False,
		    [],

		    True,
		    ["task_id_3"],

		    False,
		    False,
		    [],
		]

		print(f"expected {expected}")
		print(f"actual {out}")
		print(expected == out)

		print("========running test lvl 3 B========")
		manager = TaskManagerLvl3()

		out = []

		# Users
		out.append(manager.add_user(1, "u1", 2))
		out.append(manager.add_user(2, "u2", 1))
		out.append(manager.add_user(3, "u1", 5))          # duplicate => False

		# Tasks
		t1 = manager.add_task(4, "A", 1)   # task_id_1
		t2 = manager.add_task(5, "B", 1)   # task_id_2
		t3 = manager.add_task(6, "C", 1)   # task_id_3
		t4 = manager.add_task(7, "D", 1)   # task_id_4
		out.extend([t1, t2, t3, t4])

		# Invalid assignments
		out.append(manager.assign_task(8, "task_id_999", "u1", 20))  # bad task
		out.append(manager.assign_task(9, t1, "no_user", 20))        # bad user

		# u1 quota=2: make two active assignments
		out.append(manager.assign_task(10, t1, "u1", 15))   # X1 [10,15)
		out.append(manager.assign_task(11, t2, "u1", 15))   # X2 [11,15) (same finish as X1)

		# Tie in finish_time => sort by start_time
		out.append(manager.get_user_tasks(12, "u1"))        # [t1, t2]

		# At t=15 both expire (t==finish => not active)
		out.append(manager.get_user_tasks(15, "u1"))        # []

		# At t=15 quota freed, can assign again at the boundary timestamp
		out.append(manager.assign_task(15, t3, "u1", 18))   # Y1 [15,18)
		out.append(manager.get_user_tasks(15, "u1"))        # [t3]

		# Multiple independent assignments of SAME task t3
		out.append(manager.assign_task(16, t3, "u1", 17))   # Y2 [16,17) (same task, earlier finish)
		# Now u1 has 2 actives again: Y1 + Y2
		out.append(manager.get_user_tasks(16, "u1"))        # sorted by finish: Y2(17) then Y1(18) => [t3, t3]

		# Quota full => cannot add t4 at t=16
		out.append(manager.assign_task(16, t4, "u1", 30))   # False

		# At t=17, Y2 expired; only Y1 remains; quota frees
		out.append(manager.get_user_tasks(17, "u1"))        # [t3]
		out.append(manager.assign_task(17, t4, "u1", 19))   # Z [17,19) should succeed
		out.append(manager.get_user_tasks(17, "u1"))        # [t3(18), t4(19)] => [t3, t4]

		# u2 quota=1: boundary expiry check
		out.append(manager.assign_task(20, t1, "u2", 21))   # [20,21)
		out.append(manager.assign_task(20, t2, "u2", 25))   # fails (quota full at t=20)
		out.append(manager.get_user_tasks(21, "u2"))        # at t=21 expired => []

		expected = [
		True,
		True,
		False,

		"task_id_1",
		"task_id_2",
		"task_id_3",
		"task_id_4",

		False,
		False,

		True,
		True,

		["task_id_1", "task_id_2"],

		[],

		True,
		["task_id_3"],

		True,
		["task_id_3", "task_id_3"],

		False,

		["task_id_3"],
		True,
		["task_id_3", "task_id_4"],

		True,
		False,
		[],
		]

		print(f"expected {expected}")
		print(f"actual {out}")
		print(expected == out)

	def test_level4(self):
		print("========running test lvl 4 A========")
		manager = TaskManagerLvl4()

		out = []

		out.append(manager.add_user(1, "u1", 2))
		t1 = manager.add_task(2, "T1", 1)
		t2 = manager.add_task(3, "T2", 1)
		t3 = manager.add_task(4, "T3", 1)
		out.extend([t1, t2, t3])

		# overlapping assignments of the same task to same user
		out.append(manager.assign_task(5, t1, "u1", 15))   # A1 [5,15)
		out.append(manager.assign_task(6, t1, "u1", 20))   # A2 [6,20)

		# completes earliest active assignment of t1 (A1)
		out.append(manager.complete_task(7, t1, "u1"))
		out.append(manager.get_user_tasks(8, "u1"))        # still A2 active => [t1]

		# quota freed immediately allows new assignment
		out.append(manager.assign_task(9, t2, "u1", 12))
		out.append(manager.get_user_tasks(10, "u1"))       # t2 (12) then t1 (20)
		out.append(manager.complete_task(11, t2, "u1"))
		out.append(manager.complete_task(12, t2, "u1"))    # no active => False

		# complete remaining t1 assignment
		out.append(manager.complete_task(13, t1, "u1"))
		out.append(manager.get_user_tasks(14, "u1"))       # []

		# overdue creation
		out.append(manager.assign_task(15, t3, "u1", 18))  # [15,18)
		out.append(manager.assign_task(16, t2, "u1", 17))  # [16,17)

		out.append(manager.get_overdue_assignments(17, "u1"))  # t2 becomes overdue at t=17
		out.append(manager.get_user_tasks(18, "u1"))           # at t=18 none active
		out.append(manager.get_overdue_assignments(18, "u1"))  # now t2 and t3 overdue

		out.append(manager.complete_task(19, t3, "u1"))        # too late => False

		out.append(manager.add_user(20, "u2", 1))
		out.append(manager.complete_task(21, t2, "u2"))        # wrong user => False

		# more overlap + overdue ordering
		out.append(manager.assign_task(22, t1, "u1", 30))       # B1 [22,30)
		out.append(manager.assign_task(23, t1, "u1", 28))       # B2 [23,28)
		out.append(manager.complete_task(24, t1, "u1"))         # completes earliest B1
		out.append(manager.assign_task(25, t2, "u1", 27))       # [25,27)

		out.append(manager.get_user_tasks(26, "u1"))            # t2(27), t1(28)
		out.append(manager.get_overdue_assignments(29, "u1"))   # at t=29: t2 overdue (27), B2 overdue (28)
		out.append(manager.complete_task(30, t1, "u1"))         # B2 already expired => False

		out.append(manager.get_overdue_assignments(100, "no_user"))  # []

		expected = [
		    True,
		    "task_id_1",
		    "task_id_2",
		    "task_id_3",

		    True,
		    True,

		    True,
		    ["task_id_1"],

		    True,
		    ["task_id_2", "task_id_1"],
		    True,
		    False,

		    True,
		    [],

		    True,
		    True,

		    ["task_id_2"],
		    [],
		    ["task_id_2", "task_id_3"],

		    False,

		    True,
		    False,

		    True,
		    True,
		    True,
		    True,

		    ["task_id_2", "task_id_1"],
		    ["task_id_2", "task_id_3", "task_id_2", "task_id_1"],
		    False,

		    [],
		]

		print(f"expected {expected}")
		print(f"actual {out}")
		print(expected == out)

		print("========running test lvl 4 B========")
		manager = TaskManagerLvl4()

		out = []

		out.append(manager.add_user(1, "u1", 2))
		out.append(manager.add_user(2, "u2", 1))

		t1 = manager.add_task(3, "T1", 1)   # task_id_1
		t2 = manager.add_task(4, "T2", 1)   # task_id_2
		t3 = manager.add_task(5, "T3", 1)   # task_id_3
		out.extend([t1, t2, t3])

		# Create overdue history early (never completed)
		out.append(manager.assign_task(6, t2, "u1", 10))    # A [6,10)
		out.append(manager.assign_task(7, t3, "u1", 11))    # B [7,11)

		# At t=10: A overdue (finish=10), B still active
		out.append(manager.get_overdue_assignments(10, "u1"))  # [t2]
		out.append(manager.get_user_tasks(10, "u1"))           # [t3]

		# At t=11: now B overdue too
		out.append(manager.get_overdue_assignments(11, "u1"))  # [t2, t3]

		# Now create overlapping assignments of same task t1, and complete earliest
		out.append(manager.assign_task(12, t1, "u1", 20))    # C1 [12,20)
		out.append(manager.assign_task(13, t1, "u1", 18))    # C2 [13,18) (same task, earlier finish)
		# Quota is 2: at t=13, are both active? Yes. (old ones already expired)
		out.append(manager.get_user_tasks(14, "u1"))         # [t1(18), t1(20)] => [t1, t1]

		# Complete t1 at t=15: should complete earliest active by start_time => C1 start=12 (earlier) completes
		out.append(manager.complete_task(15, t1, "u1"))
		# Remaining active should be only C2
		out.append(manager.get_user_tasks(15, "u1"))         # [t1] (the remaining assignment ends at 18)

		# Completing again at t=18 should FAIL (t==finish -> expired, not active)
		out.append(manager.complete_task(18, t1, "u1"))

		# Since C2 expired without completion, it becomes overdue at t>=18
		# Overdue list at t=18 should include previous overdue (t2,t3) plus C2 (t1)
		out.append(manager.get_overdue_assignments(18, "u1"))  # [t2(10), t3(11), t1(18)]

		# Add another assignment of t2 later and let it expire too => duplicate in overdue
		out.append(manager.assign_task(19, t2, "u1", 22))      # D [19,22)
		out.append(manager.get_user_tasks(20, "u1"))           # [t2]
		out.append(manager.get_overdue_assignments(22, "u1"))  # now includes t2 again (finish 22)

		# Wrong user cannot complete
		out.append(manager.complete_task(20, t2, "u2"))        # False
		# u2 can get overdue list even if user exists but none overdue => []
		out.append(manager.get_overdue_assignments(100, "u2")) # []

		# Non-existent user => []
		out.append(manager.get_overdue_assignments(100, "no_user"))

		expected = [
		True,
		True,

		"task_id_1",
		"task_id_2",
		"task_id_3",

		True,
		True,

		["task_id_2"],
		["task_id_3"],

		["task_id_2", "task_id_3"],

		True,
		True,
		["task_id_1", "task_id_1"],

		True,
		["task_id_1"],

		False,

		["task_id_2", "task_id_3", "task_id_1"],

		True,
		["task_id_2"],

		["task_id_2", "task_id_3", "task_id_1", "task_id_2"],

		False,
		[],
		[],
		]

		print(f"expected {expected}")
		print(f"actual {out}")
		print(expected == out)


test = Test()
test.test_level1()
test.test_level2()
test.test_level3()
test.test_level4()










