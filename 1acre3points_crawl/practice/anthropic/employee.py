from collections import defaultdict

# ==================================================================================
# ==================================================================================
# ==================================================================================



class Worker:
	def __init__(self, worker_id, position, compensation):
		self.id = worker_id
		self.position = position
		self.compensation = compensation

		# [(clockin, clockout)]
		self.work_time = []

class EmployeeManagementLvl1:
	def __init__(self):
		self.workers = {}

	def command(self, *args):
		result = ""
		if args[0] == "ADD_WORKER":
			result = self.add_worker(args[1], args[2], int(args[3]))
		elif args[0] == "REGISTER":
			result = self.register(args[1], int(args[2]))
		elif args[0] == "GET":
			result = self.get(args[1])

		return result

	def add_worker(self, worker_id, position, compensation):
		if worker_id in self.workers:
			return "false"

		self.workers[worker_id] = Worker(worker_id, position, compensation)
		return "true"

	def register(self, worker_id, timestamp):
		if worker_id not in self.workers:
			return "invalid_request"

		# insert timestamp into work_time
		# check if last register time is clockin or clockout
		work_time = self.workers[worker_id].work_time
		if work_time and work_time[-1][1] == -1:
			# is clockout
			last_clock_in, empty = work_time.pop()
			work_time.append((last_clock_in, timestamp)) 
		else:
			# is clockin
			work_time.append((timestamp, -1))

		return "registered"

	def get(self, worker_id):
		if worker_id not in self.workers:
			return ""

		work_time = self.workers[worker_id].work_time
		total_work_time = 0
		for session in work_time:
			if session[1] != -1:
				total_work_time += session[1] - session[0]

		return str(total_work_time)


# ==================================================================================
# ==================================================================================
# ==================================================================================



class WorkerLvl2:
	def __init__(self, worker_id, position, compensation):
		self.id = worker_id
		self.position = position
		self.compensation = compensation

		# [(clockin, clockout)]
		self.work_time = []

class EmployeeManagementLvl2:
	def __init__(self):
		self.workers = {}

	def command(self, *args):
		result = ""
		if args[0] == "ADD_WORKER":
			result = self.add_worker(args[1], args[2], int(args[3]))
		elif args[0] == "REGISTER":
			result = self.register(args[1], int(args[2]))
		elif args[0] == "GET":
			result = self.get(args[1])
		elif args[0] == "TOP_N_WORKERS":
			result = self.top_n_workers(int(args[1]), args[2])

		return result

	def top_n_workers(self, n, position):
		workers = []
		for worker in self.workers.values():
			# position match and has at least 1 register time
			if worker.position == position and worker.work_time:
				workers.append((worker.id, int(self.get(worker.id))))

		workers.sort(key=lambda x: (-x[1], x[0]))

		return ", ".join([f"{w[0]}({w[1]})" for w in workers[:n]])

	def add_worker(self, worker_id, position, compensation):
		if worker_id in self.workers:
			return "false"

		self.workers[worker_id] = WorkerLvl2(worker_id, position, compensation)
		return "true"

	def register(self, worker_id, timestamp):
		if worker_id not in self.workers:
			return "invalid_request"

		# insert timestamp into work_time
		# check if last register time is clockin or clockout
		work_time = self.workers[worker_id].work_time
		if work_time and work_time[-1][1] == -1:
			# is clockout
			last_clock_in, empty = work_time.pop()
			work_time.append((last_clock_in, timestamp)) 
		else:
			# is clockin
			work_time.append((timestamp, -1))

		return "registered"

	def get(self, worker_id):
		if worker_id not in self.workers:
			return ""

		work_time = self.workers[worker_id].work_time
		total_work_time = 0
		for session in work_time:
			if session[1] != -1:
				total_work_time += session[1] - session[0]

		return str(total_work_time)

# ==================================================================================
# ==================================================================================
# ==================================================================================

class PromotePackage:
	def __init__(self, worker_id, position, compensation, ts):
		self.id = worker_id
		self.position = position
		self.compensation = compensation
		self.ts = ts


class WorkerLvl3:
	def __init__(self, worker_id, position, compensation):
		self.id = worker_id
		self.position = position
		self.compensation = compensation

		# [(clockin, clockout, compensation)]
		self.work_time = []

		# PromotePackage
		self.promote_package = None

class EmployeeManagementLvl3:
	def __init__(self):
		self.workers = {}

	def command(self, *args):
		result = ""
		if args[0] == "ADD_WORKER":
			result = self.add_worker(args[1], args[2], int(args[3]))
		elif args[0] == "REGISTER":
			result = self.register(args[1], int(args[2]))
		elif args[0] == "GET":
			result = self.get(args[1])
		elif args[0] == "TOP_N_WORKERS":
			result = self.top_n_workers(int(args[1]), args[2])
		elif args[0] == "PROMOTE":
			result = self.promote(args[1], args[2], int(args[3]), int(args[4]))
		elif args[0] == "CALC_SALARY":
			result = self.calculate_salary(args[1], int(args[2]), int(args[3]))


		return result

	def promote(self, worker_id, position, compensation, timestamp):
		if worker_id not in self.workers:
			return "invalid_request"

		# check if this promotion is invalid
		# already has a promote before next clockin
		worker = self.workers[worker_id]
		if worker.promote_package:
			return "invalid_request"

		worker.promote_package = PromotePackage(worker_id, position, compensation, timestamp)

		return "success"

	def calculate_salary(self, worker_id, starttime, endtime):
		if worker_id not in self.workers:
			return ""

		worker = self.workers[worker_id]
		salary = 0
		for session in worker.work_time:
			if session[1] <= starttime or session[0] >= endtime:
				continue

			# find overlap of session and calculation period
			cal_starttime = max(session[0], starttime)
			cal_endtime = min(session[1], endtime)
			salary += (cal_endtime - cal_starttime) * session[2]

		return str(salary)

	def top_n_workers(self, n, position):
		workers = []
		for worker in self.workers.values():
			# position match and has at least 1 register time
			if worker.position == position and worker.work_time:
				workers.append((worker.id, int(self.get(worker.id))))

		workers.sort(key=lambda x: (-x[1], x[0]))

		return ", ".join([f"{w[0]}({w[1]})" for w in workers[:n]])

	def add_worker(self, worker_id, position, compensation):
		if worker_id in self.workers:
			return "false"

		self.workers[worker_id] = WorkerLvl3(worker_id, position, compensation)
		return "true"

	def register(self, worker_id, timestamp):
		if worker_id not in self.workers:
			return "invalid_request"

		worker = self.workers[worker_id]

		# insert timestamp into work_time
		# check if last register time is clockin or clockout
		work_time = worker.work_time
		if work_time and work_time[-1][1] == -1:
			# is clockout
			last_clock_in, empty, comp = work_time.pop()
			work_time.append((last_clock_in, timestamp, comp)) 
		else:
			# is clockin
			# check if has promotion
			if worker.promote_package:
				# update promotion
				worker.compensation = worker.promote_package.compensation
				worker.position = worker.promote_package.position
				worker.promote_package = None

			work_time.append((timestamp, -1, self.workers[worker_id].compensation))

		return "registered"

	def get(self, worker_id):
		if worker_id not in self.workers:
			return ""

		work_time = self.workers[worker_id].work_time
		total_work_time = 0
		for session in work_time:
			if session[1] != -1:
				total_work_time += session[1] - session[0]

		return str(total_work_time)


# ==================================================================================
# ==================================================================================
# ==================================================================================

class PromotePackagelvl4:
	def __init__(self, worker_id, position, compensation, ts):
		self.id = worker_id
		self.position = position
		self.compensation = compensation
		self.ts = ts


class WorkerLvl4:
	def __init__(self, worker_id, position, compensation):
		self.id = worker_id
		self.position = position
		self.compensation = compensation

		# [(clockin, clockout, compensation)]
		self.work_time = []

		# PromotePackage
		self.promote_package = None

class EmployeeManagementLvl4:
	def __init__(self):
		self.workers = {}
		# [(start, end)]
		self.double_pay = []

	def command(self, *args):
		result = ""
		if args[0] == "ADD_WORKER":
			result = self.add_worker(args[1], args[2], int(args[3]))
		elif args[0] == "REGISTER":
			result = self.register(args[1], int(args[2]))
		elif args[0] == "GET":
			result = self.get(args[1])
		elif args[0] == "TOP_N_WORKERS":
			result = self.top_n_workers(int(args[1]), args[2])
		elif args[0] == "PROMOTE":
			result = self.promote(args[1], args[2], int(args[3]), int(args[4]))
		elif args[0] == "CALC_SALARY":
			result = self.calculate_salary(args[1], int(args[2]), int(args[3]))
		elif args[0] == "SET_DOUBLE_PAID":
			result = self.set_double_pay(int(args[1]), int(args[2]))

		return result

	def set_double_pay(self, starttime, endtime):
		self.double_pay.append((starttime, endtime))
		self._merge_double_pay_period()

		return "success"

	def _merge_double_pay_period(self):
		self.double_pay.sort(key=lambda x: x[0])
		merged_period = [self.double_pay[0]]

		for period in self.double_pay[1:]:
			# if overlap
			if period[0] <= merged_period[-1][1]:
				start, end = merged_period.pop()
				cur_start = min(start, period[0])
				cur_end = max(end, period[1])
				
				merged_period.append((cur_start, cur_end))
			else:
				merged_period.append((period[0], period[1]))

		self.double_pay = merged_period

	def promote(self, worker_id, position, compensation, timestamp):
		if worker_id not in self.workers:
			return "invalid_request"

		# check if this promotion is invalid
		# already has a promote before next clockin
		worker = self.workers[worker_id]
		if worker.promote_package:
			return "invalid_request"

		worker.promote_package = PromotePackagelvl4(worker_id, position, compensation, timestamp)

		return "success"

	def calculate_salary(self, worker_id, starttime, endtime):
		if worker_id not in self.workers:
			return ""

		worker = self.workers[worker_id]
		salary = 0
		for session in worker.work_time:
			if session[1] <= starttime or session[0] >= endtime:
				continue

			session_comp = session[2]
			session_salary = 0
			# find overlap of session and calculation period
			cal_starttime = max(session[0], starttime)
			cal_endtime = min(session[1], endtime)
			session_remain_time = cal_endtime - cal_starttime

			for dp_start, dp_end in self.double_pay:
				if cal_starttime >= dp_end or cal_endtime <= dp_start:
					continue
				cal_dp_start = max(dp_start, cal_starttime)
				cal_dp_end = min(dp_end, cal_endtime)
				
				session_salary += session_comp * 2 * (cal_dp_end - cal_dp_start)
				session_remain_time -= cal_dp_end - cal_dp_start
			session_salary += session_remain_time * session_comp

			salary += session_salary

		return str(salary)

	def top_n_workers(self, n, position):
		workers = []
		for worker in self.workers.values():
			# position match and has at least 1 register time
			if worker.position == position and worker.work_time:
				workers.append((worker.id, int(self.get(worker.id))))

		workers.sort(key=lambda x: (-x[1], x[0]))

		return ", ".join([f"{w[0]}({w[1]})" for w in workers[:n]])

	def add_worker(self, worker_id, position, compensation):
		if worker_id in self.workers:
			return "false"

		self.workers[worker_id] = WorkerLvl4(worker_id, position, compensation)
		return "true"

	def register(self, worker_id, timestamp):
		if worker_id not in self.workers:
			return "invalid_request"

		worker = self.workers[worker_id]

		# insert timestamp into work_time
		# check if last register time is clockin or clockout
		work_time = worker.work_time
		if work_time and work_time[-1][1] == -1:
			# is clockout
			last_clock_in, empty, comp = work_time.pop()
			work_time.append((last_clock_in, timestamp, comp)) 
		else:
			# is clockin
			# check if has promotion
			if worker.promote_package:
				# update promotion
				worker.compensation = worker.promote_package.compensation
				worker.position = worker.promote_package.position
				worker.promote_package = None

			work_time.append((timestamp, -1, self.workers[worker_id].compensation))

		return "registered"

	def get(self, worker_id):
		if worker_id not in self.workers:
			return ""

		work_time = self.workers[worker_id].work_time
		total_work_time = 0
		for session in work_time:
			if session[1] != -1:
				total_work_time += session[1] - session[0]

		return str(total_work_time)


class Test:
	def __init__(self):
		pass

	def test_lvl1(self):
		print("========running test lvl 1 A========")
		cloud = EmployeeManagementLvl1()
		
		commands = [
		    ["ADD_WORKER", "Ann", "Engineer", "10"],           # true
		    ["ADD_WORKER", "Ann", "Engineer", "999"],          # false (no change)
		    ["REGISTER", "Ghost", "1"],                        # invalid_request
		    ["GET", "Ghost"],                                  # ""

		    ["REGISTER", "Ann", "10"],                         # registered (enter)
		    ["GET", "Ann"],                                    # "0" (unfinished session ignored)
		    ["REGISTER", "Ann", "20"],                         # registered (leave) => +10
		    ["GET", "Ann"],                                    # "10"

		    ["REGISTER", "Ann", "30"],                         # enter
		    ["REGISTER", "Ann", "35"],                         # leave => +5
		    ["GET", "Ann"],                                    # "15"
		]

		expected_results = [
		    "true",
		    "false",
		    "invalid_request",
		    "",

		    "registered",
		    "0",
		    "registered",
		    "10",

		    "registered",
		    "registered",
		    "15",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 1 B========")
		cloud = EmployeeManagementLvl1()
		
		commands = [
		    ["ADD_WORKER", "Bob", "Dev", "7"],
		    ["ADD_WORKER", "Cara", "Dev", "7"],

		    ["REGISTER", "Bob", "100"],        # Bob enters
		    ["REGISTER", "Cara", "110"],       # Cara enters
		    ["REGISTER", "Bob", "130"],        # Bob leaves (30)
		    ["GET", "Bob"],                    # 30
		    ["GET", "Cara"],                   # 0 (still inside; unfinished ignored)
		    ["REGISTER", "Cara", "200"],       # Cara leaves (90)
		    ["GET", "Cara"],                   # 90
		]

		expected_results = [
		    "true",
		    "true",

		    "registered",
		    "registered",
		    "registered",
		    "30",
		    "0",
		    "registered",
		    "90",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl2(self):
		print("========running test lvl 2 A========")
		cloud = EmployeeManagementLvl2()
		
		commands = [
		    ["ADD_WORKER", "Zoe", "Junior Developer", "10"],
		    ["ADD_WORKER", "Amy", "Junior Developer", "10"],
		    ["ADD_WORKER", "Eve", "Junior Developer", "10"],
		    ["ADD_WORKER", "Max", "Senior Developer", "20"],

		    ["REGISTER", "Zoe", "10"],     # enter
		    ["REGISTER", "Zoe", "20"],     # leave => 10

		    ["REGISTER", "Amy", "30"],     # enter
		    ["REGISTER", "Amy", "40"],     # leave => 10

		    ["REGISTER", "Eve", "50"],     # enter only (unfinished => 0)

		    ["TOP_N_WORKERS", "5", "Junior Developer"],  # Zoe(10), Amy(10), Eve(0) => tie 10 => Amy before Zoe
		    ["TOP_N_WORKERS", "2", "Junior Developer"],
		    ["TOP_N_WORKERS", "3", "Senior Developer"],  # Max has never registered => should be "" per screenshot rule (no reg periods)
		]

		expected_results = [
		    "true",
		    "true",
		    "true",
		    "true",

		    "registered",
		    "registered",

		    "registered",
		    "registered",

		    "registered",

		    "Amy(10), Zoe(10), Eve(0)",
		    "Amy(10), Zoe(10)",
		    "",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 2 B========")
		cloud = EmployeeManagementLvl2()
		
		commands = [
		    ["ADD_WORKER", "A", "Dev", "1"],
		    ["ADD_WORKER", "B", "Dev", "1"],
		    ["ADD_WORKER", "C", "Dev", "1"],

		    ["REGISTER", "A", "10"],      # A enters only => 0
		    ["REGISTER", "B", "20"],      # B enters
		    ["REGISTER", "B", "30"],      # B leaves => 10
		    # C never registers at all

		    ["TOP_N_WORKERS", "10", "Dev"],  # should include A(0), B(10). C excluded (no REGISTER ever)
		]

		expected_results = [
		    "true",
		    "true",
		    "true",

		    "registered",
		    "registered",
		    "registered",

		    "B(10), A(0)",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)


	def test_lvl3(self):
		print("========running test lvl 3 A========")
		cloud = EmployeeManagementLvl3()
		
		commands = [
		    ["ADD_WORKER", "John", "Middle Developer", "10"],

		    # session 1 under old comp
		    ["REGISTER", "John", "100"],     # enter
		    ["REGISTER", "John", "130"],     # leave => 30 time at 10/hr

		    # promote in the future (greater than last REGISTER=130)
		    ["PROMOTE", "John", "Senior Developer", "20", "200"],   # success

		    # if promote again before John has entered after 200 => invalid_request
		    ["PROMOTE", "John", "Staff Developer", "30", "250"],    # invalid_request

		    # John enters AFTER promotion start => new role active
		    ["REGISTER", "John", "210"],     # enter (promotion activates here)
		    ["REGISTER", "John", "260"],     # leave => 50 time at 20/hr

		    ["GET", "John"],                 # total time across roles = 30 + 50 = 80

		    # salary for [0, 500] includes both sessions:
		    # (130-100)*10 + (260-210)*20 = 30*10 + 50*20 = 300 + 1000 = 1300
		    ["CALC_SALARY", "John", "0", "500"],
		]

		expected_results = [
		    "true",

		    "registered",
		    "registered",

		    "success",
		    "invalid_request",

		    "registered",
		    "registered",

		    "80",
		    "1300",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 3 B========")
		cloud = EmployeeManagementLvl3()
		
		commands = [
		    ["ADD_WORKER", "Ada", "Junior Developer", "5"],
		    ["ADD_WORKER", "Ben", "Junior Developer", "5"],

		    ["REGISTER", "Ada", "10"],     # enter
		    ["REGISTER", "Ada", "20"],     # leave => 10

		    ["REGISTER", "Ben", "30"],     # enter
		    ["REGISTER", "Ben", "60"],     # leave => 30

		    # promote Ada in future (last REGISTER=60)
		    ["PROMOTE", "Ada", "Senior Developer", "50", "100"],   # success

		    # Ada does not enter yet; TOP_N by Junior should still include Ada as Junior (current position unchanged until activation)
		    ["TOP_N_WORKERS", "10", "Junior Developer"],           # Ben(30), Ada(10)

		    # Now Ada enters after 100 => promotion activates, current position becomes Senior
		    ["REGISTER", "Ada", "110"],    # enter (activate)
		    ["REGISTER", "Ada", "120"],    # leave => 10 at 50/hr

		    # Junior now only Ben counts; Ada moved to Senior
		    ["TOP_N_WORKERS", "10", "Junior Developer"],           # Ben(30)
		    ["TOP_N_WORKERS", "10", "Senior Developer"],           # Ada(20) time across all? NO: TOP_N uses total time but only among current position holders.
		                                                         # Ada total time=10(old)+10(new)=20, and she's current Senior now.

		    # Salary range that partially overlaps:
		    # salary in [15,115]:
		    # Ada: session [10,20] overlaps [15,20] => 5 * 5 = 25
		    # Ada: session [110,120] overlaps [110,115] => 5 * 50 = 250
		    # Total = 275
		    ["CALC_SALARY", "Ada", "15", "115"],
		]

		expected_results = [
		    "true",
		    "true",

		    "registered",
		    "registered",

		    "registered",
		    "registered",

		    "success",

		    "Ben(30), Ada(10)",

		    "registered",
		    "registered",

		    "Ben(30)",
		    "Ada(20)",

		    "275",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 3 C========")
		cloud = EmployeeManagementLvl3()
		
		commands = [
		    ["ADD_WORKER", "Kim", "Engineer", "10"],

		    ["REGISTER", "Kim", "10"],      # enter
		    ["REGISTER", "Kim", "20"],      # leave => 10 @10

		    # last REGISTER=20, promote startTimestamp=50 ok
		    ["PROMOTE", "Kim", "Engineer II", "100", "50"],   # success

		    ["REGISTER", "Kim", "50"],      # enter at exactly startTimestamp => activate now
		    ["GET", "Kim"],                 # still 10 (unfinished new session ignored)

		    ["CALC_SALARY", "Kim", "0", "100"],   # only finished session counts => 10*10=100
		    ["REGISTER", "Kim", "70"],      # leave => 20 @100

		    ["CALC_SALARY", "Kim", "0", "100"],   # now includes both => 10*10 + 20*100 = 100 + 2000 = 2100
		]

		expected_results = [
		    "true",

		    "registered",
		    "registered",

		    "success",

		    "registered",
		    "10",

		    "100",
		    "registered",

		    "2100",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl4(self):
		print("========running test lvl 4 A========")
		cloud = EmployeeManagementLvl4()
		
		commands = [
		    ["ADD_WORKER", "A", "Dev", "10"],

		    # Work session: [100, 200] at base 10
		    ["REGISTER", "A", "100"],
		    ["REGISTER", "A", "200"],

		    # Double-pay window partially overlaps: [150, 180]
		    ["SET_DOUBLE_PAID", "150", "180"],

		    # Salary in [0, 1000]:
		    # - [100,150): 50 * 10 = 500
		    # - [150,180): 30 * (2*10) = 600
		    # - [180,200): 20 * 10 = 200
		    # total = 1300
		    ["CALC_SALARY", "A", "0", "1000"],

		    # Salary in [160, 170] entirely inside double:
		    # 10 * 20 = 200
		    ["CALC_SALARY", "A", "160", "170"],

		    # Salary in [90, 160]:
		    # overlap with session is [100,160)
		    # [100,150): 50*10=500
		    # [150,160): 10*20=200
		    # total=700
		    ["CALC_SALARY", "A", "90", "160"],
		]

		expected_results = [
		    "true",

		    "registered",
		    "registered",

		    "success",

		    "1300",
		    "200",
		    "700",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 B========")
		cloud = EmployeeManagementLvl4()
		
		commands = [
		    ["ADD_WORKER", "B", "Dev", "10"],

		    # Session [0, 100]
		    ["REGISTER", "B", "0"],
		    ["REGISTER", "B", "100"],

		    # Two windows, overlapping:
		    # W1: [20, 60], W2: [50, 90]
		    # Union double-pay is [20, 90] (but overlap [50,60] still only 2x)
		    ["SET_DOUBLE_PAID", "20", "60"],
		    ["SET_DOUBLE_PAID", "50", "90"],

		    # Salary [0, 100]:
		    # [0,20): 20*10=200
		    # [20,90): 70*20=1400
		    # [90,100): 10*10=100
		    # total=1700
		    ["CALC_SALARY", "B", "0", "100"],

		    # Salary [45, 55] (in overlap of windows but still 2x):
		    # 10 * 20 = 200
		    ["CALC_SALARY", "B", "45", "55"],
		]

		expected_results = [
		    "true",

		    "registered",
		    "registered",

		    "success",
		    "success",

		    "1700",
		    "200",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 C========")
		cloud = EmployeeManagementLvl4()
		
		commands = [
		    ["ADD_WORKER", "C", "Junior", "10"],

		    # Session 1 (old rate): [100, 150]
		    ["REGISTER", "C", "100"],
		    ["REGISTER", "C", "150"],

		    # Promote in future (must be > last REGISTER=150)
		    ["PROMOTE", "C", "Senior", "30", "200"],   # activates on first entry >=200

		    # Double pay window overlaps both future and past
		    ["SET_DOUBLE_PAID", "120", "260"],

		    # Session 2 begins after 200 => promoted rate active: [210, 250] at base 30
		    ["REGISTER", "C", "210"],
		    ["REGISTER", "C", "250"],

		    # Salary [0, 1000]:
		    # Session 1 [100,150] base 10:
		    #   [100,120): 20*10 = 200
		    #   [120,150): 30*20 = 600
		    # Session 2 [210,250] base 30, fully inside double [120,260):
		    #   40 * (2*30)= 40*60=2400
		    # total = 200+600+2400=3200
		    ["CALC_SALARY", "C", "0", "1000"],

		    # Salary [140, 230]:
		    # overlaps session1: [140,150) 10 units @ double => 10*20=200
		    # overlaps session2: [210,230) 20 units @ double of 30 => 20*60=1200
		    # total=1400
		    ["CALC_SALARY", "C", "140", "230"],

		    # TOP_N_WORKERS should count only CURRENT position (Senior), time across all sessions still used for ranking
		    # C total time = 50 + 40 = 90, and current position is Senior
		    ["TOP_N_WORKERS", "3", "Senior"],
		    ["TOP_N_WORKERS", "3", "Junior"],
		]

		expected_results = [
		    "true",

		    "registered",
		    "registered",

		    "success",

		    "success",

		    "registered",
		    "registered",

		    "3200",
		    "1400",

		    "C(90)",
		    "",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 D========")
		cloud = EmployeeManagementLvl4()
		
		commands = [
		    ["SET_DOUBLE_PAID", "0", "100"],

		    ["ADD_WORKER", "D", "Dev", "10"],

		    ["REGISTER", "D", "200"],
		    ["REGISTER", "D", "220"],

		    # double window doesn't overlap this session at all
		    ["CALC_SALARY", "D", "0", "1000"],          # 20*10=200
		    ["CALC_SALARY", "D", "0", "210"],           # overlap with session is [200,210): 10*10=100
		    ["CALC_SALARY", "NoOne", "0", "1000"],      # ""
		]

		expected_results = [
		    "success",

		    "true",

		    "registered",
		    "registered",

		    "200",
		    "100",
		    "",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 E========")
		cloud = EmployeeManagementLvl4()
		
		commands = [
		    ["ADD_WORKER", "E", "Dev", "10"],

		    # Session1 [0, 10]
		    ["REGISTER", "E", "0"],
		    ["REGISTER", "E", "10"],
		    # Session2 [20, 40]
		    ["REGISTER", "E", "20"],
		    ["REGISTER", "E", "40"],

		    # Double windows: [5,25] and [30,35]
		    ["SET_DOUBLE_PAID", "5", "25"],
		    ["SET_DOUBLE_PAID", "30", "35"],

		    # Salary [0, 50]:
		    # Session1 [0,10]:
		    #   [0,5): 5*10=50
		    #   [5,10): 5*20=100
		    # Session2 [20,40]:
		    #   [20,25): 5*20=100
		    #   [25,30): 5*10=50
		    #   [30,35): 5*20=100
		    #   [35,40): 5*10=50
		    # total=50+100+100+50+100+50 = 450
		    ["CALC_SALARY", "E", "0", "50"],

		    # Salary [8, 32]:
		    # overlap Session1: [8,10) inside double => 2*10=20 => 2*20=40
		    # overlap Session2: [20,32)
		    #   [20,25): 5*20=100
		    #   [25,30): 5*10=50
		    #   [30,32): 2*20=40
		    # total=40+100+50+40=230
		    ["CALC_SALARY", "E", "8", "32"],
		]

		expected_results = [
		    "true",

		    "registered",
		    "registered",
		    "registered",
		    "registered",

		    "success",
		    "success",

		    "450",
		    "230",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 F========")
		cloud = EmployeeManagementLvl4()
		
		commands = [
		    ["ADD_WORKER", "F", "Jr", "10"],

		    # Session before promotion: [0, 50]
		    ["REGISTER", "F", "0"],
		    ["REGISTER", "F", "50"],

		    # Promote in future (last REGISTER=50)
		    ["PROMOTE", "F", "Sr", "40", "100"],  # activates on entry >=100

		    # Double windows overlapping: [20, 140] and [60, 120] => still max 2x
		    ["SET_DOUBLE_PAID", "20", "140"],
		    ["SET_DOUBLE_PAID", "60", "120"],

		    # Session after promotion: [110, 130] at base 40 (and inside double)
		    ["REGISTER", "F", "110"],
		    ["REGISTER", "F", "130"],

		    # Salary [0, 200]:
		    # Session1 [0,50] base 10:
		    #   [0,20): 20*10=200
		    #   [20,50): 30*20=600
		    # Session2 [110,130] base 40:
		    #   [110,130): 20*80=1600
		    # total=2400
		    ["CALC_SALARY", "F", "0", "200"],

		    # Salary [70, 115]:
		    # overlaps session1: [70,115) none (session1 ends at 50)
		    # overlaps session2: [110,115): 5 units inside double, base 40 => 5*80=400
		    ["CALC_SALARY", "F", "70", "115"],
		]

		expected_results = [
		    "true",

		    "registered",
		    "registered",

		    "success",

		    "success",
		    "success",

		    "registered",
		    "registered",

		    "2400",
		    "400",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 G========")
		cloud = EmployeeManagementLvl4()
		
		commands = [
		    ["ADD_WORKER", "F", "Jr", "10"],

		    # Session before promotion: [0, 50]
		    ["REGISTER", "F", "0"],
		    ["REGISTER", "F", "50"],

		    # Promote in future (last REGISTER=50)
		    ["PROMOTE", "F", "Sr", "40", "100"],  # activates on entry >=100

		    # Double windows overlapping: [20, 140] and [60, 120] => still max 2x
		    ["SET_DOUBLE_PAID", "20", "140"],
		    ["SET_DOUBLE_PAID", "60", "120"],

		    # Session after promotion: [110, 130] at base 40 (and inside double)
		    ["REGISTER", "F", "110"],
		    ["REGISTER", "F", "130"],

		    # Salary [0, 200]:
		    # Session1 [0,50] base 10:
		    #   [0,20): 20*10=200
		    #   [20,50): 30*20=600
		    # Session2 [110,130] base 40:
		    #   [110,130): 20*80=1600
		    # total=2400
		    ["CALC_SALARY", "F", "0", "200"],

		    # Salary [70, 115]:
		    # overlaps session1: [70,115) none (session1 ends at 50)
		    # overlaps session2: [110,115): 5 units inside double, base 40 => 5*80=400
		    ["CALC_SALARY", "F", "70", "115"],
		]

		expected_results = [
		    "true",

		    "registered",
		    "registered",

		    "success",

		    "success",
		    "success",

		    "registered",
		    "registered",

		    "2400",
		    "400",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)




test = Test()
test.test_lvl1()
test.test_lvl2()
test.test_lvl3()
test.test_lvl4()


