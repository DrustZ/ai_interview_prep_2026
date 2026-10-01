from collections import defaultdict

# ==================================================================================
# ==================================================================================
# ==================================================================================


class CloudStorageVersionLvl1:
	def __init__(self):
		self.files = {}

	def command(self, *args):
		result = ""
		if args[0] == "ADD_FILE":
			result = self.add_file(args[1], int(args[2]))
		elif args[0] == "MOVE_FILE":
			result = self.move_file(args[1], args[2])
		elif args[0] == "GET_FILE_SIZE":
			result = self.get_file_size(args[1])
		
		return result

	def add_file(self, name, size):

		if name in self.files:
			operation = "overwritten"
		else:
			operation = "created"

		self.files[name] = size

		return operation

	def move_file(self, name_from, name_to):
		if name_from not in self.files or name_to in self.files:
			return "false"

		self.files[name_to] = self.files[name_from]
		del self.files[name_from]

		return "true"

	def get_file_size(self, name):
		if name not in self.files:
			return ""

		return str(self.files[name])


# ==================================================================================
# ==================================================================================
# ==================================================================================


class CloudStorageVersionLvl2:
	def __init__(self):
		self.files = {}

	def command(self, *args):
		result = ""
		if args[0] == "ADD_FILE":
			result = self.add_file(args[1], int(args[2]))
		elif args[0] == "MOVE_FILE":
			result = self.move_file(args[1], args[2])
		elif args[0] == "GET_FILE_SIZE":
			result = self.get_file_size(args[1])
		elif args[0] == "GET_LARGEST_N":
			result = self.get_largest_n(args[1], int(args[2]))
		
		return result

	def get_largest_n(self, prefix, n):
		if not self.files:
			return ""

		files = []
		for f, size in self.files.items():
			if f.startswith(prefix):
				files.append((f, size))
		files.sort(key=lambda x: (-x[1], x[0]))

		return ", ".join([f"{f[0]}({f[1]})" for f in files][:n])

	def add_file(self, name, size):

		if name in self.files:
			operation = "overwritten"
		else:
			operation = "created"

		self.files[name] = size

		return operation

	def move_file(self, name_from, name_to):
		if name_from not in self.files or name_to in self.files:
			return "false"

		self.files[name_to] = self.files[name_from]
		del self.files[name_from]

		return "true"

	def get_file_size(self, name):
		if name not in self.files:
			return ""

		return str(self.files[name])

# ==================================================================================
# ==================================================================================
# ==================================================================================


class CloudStorageVersionLvl3:
	def __init__(self):
		# key - file
		# value - history
		self.files = defaultdict(list)

	def command(self, *args):
		result = ""
		if args[0] == "ADD_FILE":
			result = self.add_file(args[1], int(args[2]))
		elif args[0] == "MOVE_FILE":
			result = self.move_file(args[1], args[2])
		elif args[0] == "GET_FILE_SIZE":
			result = self.get_file_size(args[1])
		elif args[0] == "GET_LARGEST_N":
			result = self.get_largest_n(args[1], int(args[2]))
		elif args[0] == "GET_VERSION":
			result = self.get_version(args[1], int(args[2]))
		elif args[0] == "DELETE_VERSION":
			result = self.delete_version(args[1], int(args[2]))
		
		return result

	def get_version(self, name, version):
		if name not in self.files or version > len(self.files[name]):
			return ""

		return str(self.files[name][version - 1])

	def delete_version(self, name, version):
		if name not in self.files or version > len(self.files[name]):
			return "false"

		self.files[name].pop(version - 1)

		# check if history empty
		if not self.files[name]:
			del self.files[name]

		return "true"

	def get_largest_n(self, prefix, n):
		if not self.files:
			return ""

		files = []
		for f, history in self.files.items():
			if f.startswith(prefix):
				files.append((f, history[-1]))
		files.sort(key=lambda x: (-x[1], x[0]))

		return ", ".join([f"{f[0]}({f[1]})" for f in files][:n])

	def add_file(self, name, size):
		if name in self.files:
			operation = "overwritten"
		else:
			operation = "created"

		self.files[name].append(size)

		return operation

	def move_file(self, name_from, name_to):
		if name_from not in self.files or name_to in self.files:
			return "false"

		self.files[name_to] = self.files[name_from]
		del self.files[name_from]

		return "true"

	def get_file_size(self, name):
		if name not in self.files:
			return ""

		return str(self.files[name][-1])

# ==================================================================================
# ==================================================================================
# ==================================================================================


class CloudStorageVersionLvl4:
	def __init__(self):
		# key - file
		# value - history
		self.files = defaultdict(list)

		# key - file
		# value - history
		self.trash = defaultdict(list)

	def command(self, *args):
		result = ""
		if args[0] == "ADD_FILE":
			result = self.add_file(args[1], int(args[2]))
		elif args[0] == "MOVE_FILE":
			result = self.move_file(args[1], args[2])
		elif args[0] == "GET_FILE_SIZE":
			result = self.get_file_size(args[1])
		elif args[0] == "GET_LARGEST_N":
			result = self.get_largest_n(args[1], int(args[2]))
		elif args[0] == "GET_VERSION":
			result = self.get_version(args[1], int(args[2]))
		elif args[0] == "DELETE_VERSION":
			result = self.delete_version(args[1], int(args[2]))
		elif args[0] == "DELETE_FILES":
			result = self.delete_files(args[1])
		elif args[0] == "RESTORE_FILES":
			result = self.restore_files(args[1])
		
		return result

	def delete_files(self, prefix):
		deleting_files = []
		
		for f, history in self.files.items():
			if f.startswith(prefix):
				deleting_files.append((f, history))

		# put a deleting file into trash and delete in self.files
		# (also replace existing f in trash if there is any)
		for del_f in deleting_files:
			self.trash[del_f[0]] = del_f[1]
			del self.files[del_f[0]]

		return str(len(deleting_files))

	def restore_files(self, prefix):
		restoring_files = []

		for f, history in self.trash.items():
			if f.startswith(prefix):
				restoring_files.append((f, history))

		# put a restoring file into files and delete in self.trash
		# (also replace existing f in files if there is any)
		for res_f in restoring_files:
			self.files[res_f[0]] = res_f[1]
			del self.trash[res_f[0]]

		return str(len(restoring_files))

	def get_version(self, name, version):
		if name not in self.files or version > len(self.files[name]):
			return ""

		return str(self.files[name][version - 1])

	def delete_version(self, name, version):
		if name not in self.files or version > len(self.files[name]):
			return "false"

		self.files[name].pop(version - 1)

		# check if history empty
		if not self.files[name]:
			del self.files[name]

		return "true"

	def get_largest_n(self, prefix, n):
		if not self.files:
			return ""

		files = []
		for f, history in self.files.items():
			if f.startswith(prefix):
				files.append((f, history[-1]))
		files.sort(key=lambda x: (-x[1], x[0]))

		return ", ".join([f"{f[0]}({f[1]})" for f in files][:n])

	def add_file(self, name, size):
		if name in self.files:
			operation = "overwritten"
		else:
			operation = "created"

		self.files[name].append(size)

		return operation

	def move_file(self, name_from, name_to):
		if name_from not in self.files or name_to in self.files:
			return "false"

		self.files[name_to] = self.files[name_from]
		del self.files[name_from]

		return "true"

	def get_file_size(self, name):
		if name not in self.files:
			return ""

		return str(self.files[name][-1])


class Test:
	def __init__(self):
		pass

	def test_lvl_1_2(self):
		print("========running test lvl 1+2 A========")
		cloud = CloudStorageVersionLvl2()

		commands = [
		    ["ADD_FILE", "/a", "10"],                 # created
		    ["ADD_FILE", "/ab", "5"],                 # created
		    ["ADD_FILE", "/a", "7"],                  # overwritten (v1=10, v2=7)
		    ["ADD_FILE", "/dir/x", "7"],              # created
		    ["ADD_FILE", "/dir/y", "7"],              # created
		    ["GET_LARGEST_N", "/dir", "5"],           # tie on size => lex by name
		    ["MOVE_FILE", "/dir/x", "/dir/y"],        # dest exists => false
		    ["MOVE_FILE", "/dir/x", "/dir/z"],        # true
		    ["GET_LARGEST_N", "/", "4"],              # root prefix includes everything
		    ["GET_FILE_SIZE", "/dir/x"],              # moved away => ""
		]

		expected_results = [
		    "created",
		    "created",
		    "overwritten",
		    "created",
		    "created",
		    "/dir/x(7), /dir/y(7)",
		    "false",
		    "true",
		    "/a(7), /dir/y(7), /dir/z(7), /ab(5)",
		    "",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl_3(self):
		print("========running test lvl 3 A========")
		cloud = CloudStorageVersionLvl3()

		commands = [
		    ["ADD_FILE", "/f", "1"],                  # created (v1=1)
		    ["ADD_FILE", "/f", "2"],                  # overwritten (v2=2)
		    ["ADD_FILE", "/f", "3"],                  # overwritten (v3=3)
		    ["DELETE_VERSION", "/f", "2"],            # delete middle => shift down
		    ["GET_VERSION", "/f", "2"],               # now should be old v3 => "3"
		    ["GET_FILE_SIZE", "/f"],                  # latest => "3"
		    ["DELETE_VERSION", "/f", "2"],            # delete last version (size 3)
		    ["GET_FILE_SIZE", "/f"],                  # latest becomes "1"
		    ["DELETE_VERSION", "/f", "1"],            # delete only version => file removed permanently
		    ["GET_FILE_SIZE", "/f"],                  # ""
		    ["DELETE_VERSION", "/f", "1"],            # non-existent => false
		    ["ADD_FILE", "/g", "4"],                  # created
		    ["MOVE_FILE", "/g", "/f"],                # move into previously-deleted name => true
		    ["GET_FILE_SIZE", "/f"],                  # "4"
		]

		expected_results = [
		    "created",
		    "overwritten",
		    "overwritten",
		    "true",
		    "3",
		    "3",
		    "true",
		    "1",
		    "true",
		    "",
		    "false",
		    "created",
		    "true",
		    "4",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 3 B========")
		cloud = CloudStorageVersionLvl3()

		commands = [
		    ["ADD_FILE", "/mv", "10"],                # created (v1=10)
		    ["ADD_FILE", "/mv", "20"],                # overwritten (v2=20)
		    ["ADD_FILE", "/mv", "30"],                # overwritten (v3=30)
		    ["MOVE_FILE", "/mv", "/dir/mv"],          # move all versions
		    ["GET_VERSION", "/dir/mv", "1"],          # "10"
		    ["GET_VERSION", "/dir/mv", "3"],          # "30"
		    ["GET_FILE_SIZE", "/mv"],                 # source gone => ""
		    ["GET_LARGEST_N", "/dir", "2"],           # latest size 30
		    ["ADD_FILE", "/dir/mv", "5"],             # overwritten (v4=5), latest becomes 5
		    ["GET_VERSION", "/dir/mv", "4"],          # "5"
		    ["GET_LARGEST_N", "/dir", "1"],           # uses latest => 5 (even though older versions larger)
		]

		expected_results = [
		    "created",
		    "overwritten",
		    "overwritten",
		    "true",
		    "10",
		    "30",
		    "",
		    "/dir/mv(30)",
		    "overwritten",
		    "5",
		    "/dir/mv(5)",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 3 C========")
		cloud = CloudStorageVersionLvl3()

		commands = [
		    ["ADD_FILE", "/v", "10"],          # created (v1=10)
		    ["ADD_FILE", "/v", "20"],          # overwritten (v2=20)
		    ["ADD_FILE", "/v", "30"],          # overwritten (v3=30)
		    ["ADD_FILE", "/v", "40"],          # overwritten (v4=40)

		    ["DELETE_VERSION", "/v", "1"],     # delete oldest => versions become [20,30,40]
		    ["GET_VERSION", "/v", "1"],        # 20
		    ["GET_VERSION", "/v", "3"],        # 40

		    ["DELETE_VERSION", "/v", "2"],     # delete middle (30) => [20,40]
		    ["GET_VERSION", "/v", "2"],        # 40
		    ["GET_VERSION", "/v", "3"],        # ""

		    ["DELETE_VERSION", "/v", "2"],     # delete last (40) => [20]
		    ["GET_FILE_SIZE", "/v"],           # 20

		    ["DELETE_VERSION", "/v", "1"],     # delete only => removed permanently
		    ["GET_FILE_SIZE", "/v"],           # ""
		    ["GET_VERSION", "/v", "1"],        # ""
		]

		expected_results = [
		    "created",
		    "overwritten",
		    "overwritten",
		    "overwritten",

		    "true",
		    "20",
		    "40",

		    "true",
		    "40",
		    "",

		    "true",
		    "20",

		    "true",
		    "",
		    "",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 3 D========")
		cloud = CloudStorageVersionLvl3()

		commands = [
		    ["ADD_FILE", "/src", "1"],             # created
		    ["ADD_FILE", "/src", "2"],             # overwritten (v2=2)
		    ["ADD_FILE", "/dest", "100"],          # created
		    ["MOVE_FILE", "/src", "/dest"],        # false (dest exists)

		    ["MOVE_FILE", "/src", "/moved"],       # true (move v1,v2)
		    ["GET_FILE_SIZE", "/src"],             # ""
		    ["GET_VERSION", "/moved", "1"],        # 1
		    ["GET_VERSION", "/moved", "2"],        # 2

		    ["DELETE_VERSION", "/moved", "1"],     # remove v1 => remaining [2] becomes v1
		    ["GET_VERSION", "/moved", "1"],        # 2
		    ["GET_VERSION", "/moved", "2"],        # ""
		]

		expected_results = [
		    "created",
		    "overwritten",
		    "created",
		    "false",

		    "true",
		    "",
		    "1",
		    "2",

		    "true",
		    "2",
		    "",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 3 E========")
		cloud = CloudStorageVersionLvl3()

		commands = [
		    ["ADD_FILE", "/k", "100"],          # created (v1=100)
		    ["ADD_FILE", "/k", "1"],            # overwritten (v2=1) latest small
		    ["ADD_FILE", "/dir/a", "50"],       # created
		    ["GET_LARGEST_N", "/", "3"],        # /dir/a(50), /k(1)

		    ["GET_VERSION", "/k", "1"],         # 100 (still exists)
		    ["GET_FILE_SIZE", "/k"],            # 1

		    ["ADD_FILE", "/k", "60"],           # overwritten (v3=60) latest big again
		    ["GET_LARGEST_N", "/", "2"],        # /k(60), /dir/a(50)
		]

		expected_results = [
		    "created",
		    "overwritten",
		    "created",
		    "/dir/a(50), /k(1)",

		    "100",
		    "1",

		    "overwritten",
		    "/k(60), /dir/a(50)",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 3 F========")
		cloud = CloudStorageVersionLvl3()

		commands = [
		    ["ADD_FILE", "/b", "7"],                 # created
		    ["ADD_FILE", "/a", "7"],                 # created
		    ["ADD_FILE", "/dir/c", "7"],             # created
		    ["GET_LARGEST_N", "/", "3"],             # all size 7 => lex by full name

		    ["MOVE_FILE", "/dir/c", "/aa"],          # true
		    ["GET_LARGEST_N", "/", "3"],             # /a, /aa, /b all size 7 lex
		]

		expected_results = [
		    "created",
		    "created",
		    "created",
		    "/a(7), /b(7), /dir/c(7)",

		    "true",
		    "/a(7), /aa(7), /b(7)",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 


	def test_lvl_4(self):
		print("========running test lvl 4 A========")
		cloud = CloudStorageVersionLvl4()

		commands = [
		    ["ADD_FILE", "/p/a", "1"],                # created
		    ["ADD_FILE", "/p/b", "2"],                # created
		    ["ADD_FILE", "/p/c", "3"],                # created
		    ["ADD_FILE", "/q/a", "4"],                # created (different prefix)
		    ["ADD_FILE", "/p/b", "5"],                # overwritten: /p/b versions [2,5]
		    ["DELETE_FILES", "/p"],                   # moves a,b,c to trash => "3"

		    ["GET_FILE_SIZE", "/p/a"],                # ""
		    ["GET_FILE_SIZE", "/p/b"],                # ""
		    ["GET_FILE_SIZE", "/p/c"],                # ""
		    ["GET_LARGEST_N", "/p", "10"],            # ""

		    ["RESTORE_FILES", "/p/b"],                # restore only /p/b => "1"
		    ["GET_FILE_SIZE", "/p/b"],                # latest "5"
		    ["GET_VERSION", "/p/b", "1"],             # "2"

		    # Create collision in filesystem before restoring everything:
		    ["ADD_FILE", "/p/b", "9"],                # overwritten: /p/b versions [2,5,9]
		    ["DELETE_FILES", "/p"],                   # deletes only /p/b now => "1" (goes to trash)

		    ["ADD_FILE", "/p/b", "100"],              # created (fs has /p/b again)
		    ["ADD_FILE", "/p/d", "7"],                # created

		    ["RESTORE_FILES", "/p"],                  # restore /p/a,/p/b,/p/c from trash => "3"
		                                               # collision: fs /p/b(100) replaced by trashed versions [2,5,9]
		    ["GET_FILE_SIZE", "/p/b"],                # "9"
		    ["GET_VERSION", "/p/b", "3"],             # "9"
		    ["GET_FILE_SIZE", "/p/a"],                # "1"

		    ["GET_LARGEST_N", "/p", "10"],            # sizes: b=9, d=7, c=3, a=1

		    # Trash replacement: delete /p/a again while trash still has no /p/a (it was restored),
		    # so first put /p/a into trash, then delete again with different size to replace it.
		    ["DELETE_FILES", "/p/a"],                 # delete /p/a => "1" (trash now has /p/a size 1)
		    ["ADD_FILE", "/p/a", "10"],               # created
		    ["DELETE_FILES", "/p/a"],                 # delete again => "1"; trash already has /p/a => replaced
		    ["RESTORE_FILES", "/p/a"],                # restore => "1"
		    ["GET_FILE_SIZE", "/p/a"],                # should be "10"
		]

		expected_results = [
		    "created",
		    "created",
		    "created",
		    "created",
		    "overwritten",
		    "3",

		    "",
		    "",
		    "",
		    "",

		    "1",
		    "5",
		    "2",

		    "overwritten",
		    "1",

		    "created",
		    "created",

		    "3",
		    "9",
		    "9",
		    "1",

		    "/p/b(9), /p/d(7), /p/c(3), /p/a(1)",

		    "1",
		    "created",
		    "1",
		    "1",
		    "10",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 4 B========")
		cloud = CloudStorageVersionLvl4()

		commands = [
		    ["ADD_FILE", "/x", "1"],                  # created
		    ["ADD_FILE", "/x1", "2"],                 # created (still matches prefix "/x")
		    ["ADD_FILE", "/x/inner", "3"],            # created
		    ["GET_LARGEST_N", "/x", "10"],            # should include /x, /x1, /x/inner

		    ["DELETE_FILES", "/x/"],                  # should delete only "/x/inner" (starts with "/x/")
		    ["GET_LARGEST_N", "/x", "10"],            # now only /x1 and /x remain

		    ["RESTORE_FILES", "/x"],                  # restores "/x/inner" from trash (prefix "/x" matches it)
		    ["GET_LARGEST_N", "/x", "10"],            # back to 3 entries
		]

		expected_results = [
		    "created",
		    "created",
		    "created",
		    "/x/inner(3), /x1(2), /x(1)",

		    "1",
		    "/x1(2), /x(1)",

		    "1",
		    "/x/inner(3), /x1(2), /x(1)",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 4 C========")
		cloud = CloudStorageVersionLvl4()

		commands = [
		    ["ADD_FILE", "/r/f", "1"],               # created
		    ["ADD_FILE", "/r/f", "2"],               # overwritten => versions [1,2]
		    ["ADD_FILE", "/r/g", "3"],               # created
		    ["DELETE_FILES", "/r"],                  # delete f,g => "2"

		    ["ADD_FILE", "/r/f", "999"],             # created (fs collision name for restore)
		    ["ADD_FILE", "/r/f", "1000"],            # overwritten => versions [999,1000]

		    ["RESTORE_FILES", "/r/f"],               # restore f from trash => "1"
		                                            # collision => existing fs /r/f and all versions removed
		    ["GET_FILE_SIZE", "/r/f"],               # latest should be "2" (restored latest)
		    ["GET_VERSION", "/r/f", "1"],            # "1"
		    ["GET_VERSION", "/r/f", "2"],            # "2"
		    ["GET_VERSION", "/r/f", "3"],            # ""
		]

		expected_results = [
		    "created",
		    "overwritten",
		    "created",
		    "2",

		    "created",
		    "overwritten",

		    "1",
		    "2",
		    "1",
		    "2",
		    "",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 4 D========")
		cloud = CloudStorageVersionLvl4()

		commands = [
		    ["ADD_FILE", "/t/x", "1"],            # created
		    ["DELETE_FILES", "/t/x"],             # "1" -> trash has /t/x size 1
		    ["ADD_FILE", "/t/x", "9"],            # created
		    ["ADD_FILE", "/t/x", "10"],           # overwritten => versions [9,10]
		    ["DELETE_FILES", "/t/x"],             # "1" -> trash already has /t/x => replaced by [9,10]

		    ["RESTORE_FILES", "/t/x"],            # restore => "1" -> should restore versions [9,10]
		    ["GET_FILE_SIZE", "/t/x"],            # 10
		    ["GET_VERSION", "/t/x", "1"],         # 9
		    ["GET_VERSION", "/t/x", "2"],         # 10
		]

		expected_results = [
		    "created",
		    "1",
		    "created",
		    "overwritten",
		    "1",

		    "1",
		    "10",
		    "9",
		    "10",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 4 E========")
		cloud = CloudStorageVersionLvl4()

		commands = [
		    ["ADD_FILE", "/p/only", "5"],           # created
		    ["DELETE_VERSION", "/p/only", "1"],     # true => permanently removed
		    ["RESTORE_FILES", "/p"],               # "0" because it was never trashed
		    ["GET_FILE_SIZE", "/p/only"],          # ""
		    ["ADD_FILE", "/p/only", "6"],          # created (fresh)
		    ["GET_FILE_SIZE", "/p/only"],          # "6"
		]

		expected_results = [
		    "created",
		    "true",
		    "0",
		    "",
		    "created",
		    "6",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 

		print("========running test lvl 4 F========")
		cloud = CloudStorageVersionLvl4()

		commands = [
		    ["ADD_FILE", "/s/a", "10"],            # created
		    ["ADD_FILE", "/s/b", "20"],            # created
		    ["ADD_FILE", "/s/c", "20"],            # created
		    ["ADD_FILE", "/s/d", "5"],             # created
		    ["DELETE_FILES", "/s"],                # delete 4 => "4"

		    ["RESTORE_FILES", "/s/b"],             # restore only b => "1"
		    ["RESTORE_FILES", "/s/c"],             # restore only c => "1"
		    ["GET_LARGEST_N", "/s", "5"],          # b and c sizes both 20 => lex by name

		    ["RESTORE_FILES", "/s"],               # restore remaining a,d => "2"
		    ["GET_LARGEST_N", "/s", "10"],         # b(20), c(20), a(10), d(5)
		]

		expected_results = [
		    "created",
		    "created",
		    "created",
		    "created",
		    "4",

		    "1",
		    "1",
		    "/s/b(20), /s/c(20)",

		    "2",
		    "/s/b(20), /s/c(20), /s/a(10), /s/d(5)",
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results) 


test = Test()
# test.test_lvl_1_2()
# test.test_lvl_3()
test.test_lvl_4()













