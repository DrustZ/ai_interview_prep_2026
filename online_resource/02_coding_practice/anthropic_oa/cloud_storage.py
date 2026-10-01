from collections import defaultdict

# ==================================================================================
# ==================================================================================
# ==================================================================================


class CloudStorageLvl1:
	def __init__(self):
		self.files = defaultdict(int)

	def command(self, *args):
		result = ""
		if args[0] == "ADD_FILE":
			result = self.add_file(args[1], int(args[2]))
		elif args[0] == "COPY_FILE":
			result = self.copy_file(args[1], args[2])
		elif args[0] == "GET_FILE_SIZE":
			result = self.get_file_size(args[1])
		
		return result

	def add_file(self, name, size):
		if name in self.files:
			return "false"

		self.files[name] = size

		return "true"

	def copy_file(self, name_from, name_to):
		if name_from not in self.files or name_to in self.files:
			return "false"

		self.files[name_to] = self.files[name_from]

		return "true"

	def get_file_size(self, name):
		if name not in self.files:
			return ""

		return str(self.files[name])

# ==================================================================================
# ==================================================================================
# ==================================================================================


class CloudStorageLvl2:
	def __init__(self):
		self.files = defaultdict(int)

	def command(self, *args):
		result = ""
		if args[0] == "ADD_FILE":
			result = self.add_file(args[1], int(args[2]))
		elif args[0] == "COPY_FILE":
			result = self.copy_file(args[1], args[2])
		elif args[0] == "GET_FILE_SIZE":
			result = self.get_file_size(args[1])
		elif args[0] == "FIND_FILE":
			result = self.find_file(args[1], args[2])

		return result

	def find_file(self, prefix, suffix):
		results = []

		for file_name, size in self.files.items():
			if file_name.startswith(prefix) and file_name.endswith(suffix):
				results.append((file_name, size))

		results.sort(key=lambda x: (-x[1], x[0]))
		return ", ".join([f"{x[0]}({x[1]})" for x in results])

	def add_file(self, name, size):
		if name in self.files:
			return "false"

		self.files[name] = size

		return "true"

	def copy_file(self, name_from, name_to):
		if name_from not in self.files or name_to in self.files:
			return "false"

		self.files[name_to] = self.files[name_from]

		return "true"

	def get_file_size(self, name):
		if name not in self.files:
			return ""

		return str(self.files[name])

# ==================================================================================
# ==================================================================================
# ==================================================================================


class CloudStorageLvl3:
	def __init__(self):
		# key - file name
		# value - (owner, size)
		self.files = {}

		# key - user name
		# value - (cur_capcity, max_capcity)
		self.users = {}

	def command(self, *args):
		result = ""
		if args[0] == "ADD_FILE":
			result = self.add_file(args[1], int(args[2]))
		elif args[0] == "COPY_FILE":
			result = self.copy_file(args[1], args[2])
		elif args[0] == "GET_FILE_SIZE":
			result = self.get_file_size(args[1])
		elif args[0] == "FIND_FILE":
			result = self.find_file(args[1], args[2])
		elif args[0] == "ADD_USER":
			result = self.add_user(args[1], int(args[2]))
		elif args[0] == "ADD_FILE_BY":
			result = self.add_file_by(args[1], args[2], int(args[3]))
		elif args[0] == "UPDATE_CAPACITY":
			result = self.update_capacity(args[1], int(args[2]))

		return result

	def add_user(self, user, capcity):
		if user in self.users:
			return "false"

		self.users[user] = (capcity, capcity)

		return "true"

	def add_file_by(self, user, name, size):
		if user not in self.users or name in self.files:
			return ""

		cur_capcity, max_capcity = self.users[user]
		if cur_capcity < size:
			return ""

		self.files[name] = (user, size)
		self.users[user] = (cur_capcity - size, max_capcity)

		return str(cur_capcity - size)


	def update_capacity(self, user, capcity):
		if user not in self.users:
			return ""

		cur_capcity, max_capcity = self.users[user]
		used_capcity = max_capcity - cur_capcity

		if capcity > max_capcity or used_capcity <= capcity:
			self.users[user] = (capcity - used_capcity, capcity)
			return "0"

		ranked_files = []
		for file, file_info in self.files.items():
			if file_info[0] == user:
				ranked_files.append((file, file_info[1]))

		# sort by size desc, if tie, name asc
		ranked_files.sort(key=lambda x: (-x[1], x[0]))
		deleted_count = 0
		for owned_file in ranked_files:
			if used_capcity <= capcity:
				break

			used_capcity -= owned_file[1]
			del self.files[owned_file[0]]
			deleted_count += 1

		self.users[user] = (capcity - used_capcity, capcity)

		return str(deleted_count)

	def find_file(self, prefix, suffix):
		results = []

		for file_name, size_pair in self.files.items():
			if file_name.startswith(prefix) and file_name.endswith(suffix):
				results.append((file_name, size_pair[1]))

		results.sort(key=lambda x: (-x[1], x[0]))
		return ", ".join([f"{x[0]}({x[1]})" for x in results])

	def add_file(self, name, size):
		if name in self.files:
			return "false"

		self.files[name] = ("admin", size)

		return "true"

	def copy_file(self, name_from, name_to):
		if name_from not in self.files or name_to in self.files:
			return "false"

		file_info = self.files[name_from]

		if file_info[0] == "admin":
			self.files[name_to] = self.files[name_from]
			return "true"

		cur_capcity, max_capcity = self.users[file_info[0]]
		if cur_capcity < file_info[1]:
			return "false"

		self.files[name_to] = self.files[name_from]
		self.users[file_info[0]] = (cur_capcity - file_info[1], max_capcity)

		return "true"

	def get_file_size(self, name):
		if name not in self.files:
			return ""

		return str(self.files[name][1])

# ==================================================================================
# ==================================================================================
# ==================================================================================


class CloudStorageLvl4:
	def __init__(self):
		# key - file name
		# value - (owner, size)
		self.files = {}

		# key - user name
		# value - (cur_capcity, max_capcity)
		self.users = {}

	def command(self, *args):
		result = ""
		if args[0] == "ADD_FILE":
			result = self.add_file(args[1], int(args[2]))
		elif args[0] == "COPY_FILE":
			result = self.copy_file(args[1], args[2])
		elif args[0] == "GET_FILE_SIZE":
			result = self.get_file_size(args[1])
		elif args[0] == "FIND_FILE":
			result = self.find_file(args[1], args[2])
		elif args[0] == "ADD_USER":
			result = self.add_user(args[1], int(args[2]))
		elif args[0] == "ADD_FILE_BY":
			result = self.add_file_by(args[1], args[2], int(args[3]))
		elif args[0] == "UPDATE_CAPACITY":
			result = self.update_capacity(args[1], int(args[2]))
		elif args[0] == "COMPRESS_FILE":
			result = self.compress_file(args[1], args[2])
		elif args[0] == "DECOMPRESS_FILE":
			result = self.decompress_file(args[1], args[2])

		return result

	def compress_file(self, user, name):
		if user not in self.users or name not in self.files or name.endswith(".COMPRESSED"):
			return ""

		# check if user is the owner of file
		old_file_info = self.files[name]
		if old_file_info[0] != user:
			return ""

		new_size = old_file_info[1] // 2
		# replace file
		self._replace_file(name, f"{name}.COMPRESSED", user, new_size)

		# update capcity
		cur_capcity, max_capcity = self.users[user]
		new_capcity = cur_capcity + old_file_info[1] - new_size
		self.users[user] = (new_capcity, max_capcity)

		return str(new_capcity)

	def decompress_file(self, user, name):
		if user not in self.users or name not in self.files or not name.endswith(".COMPRESSED"):
			return ""

		# check if user is the owner of file
		compress_file_info = self.files[name]
		if compress_file_info[0] != user:
			return ""

		# check if uncompressed file name used
		decompress_file_name = name[0:len(name) - len(".COMPRESSED")]
		if decompress_file_name in self.files:
			return ""

		# check if user capacity allows
		cur_capcity, max_capcity = self.users[user]
		new_size = compress_file_info[1] * 2
		if cur_capcity + compress_file_info[1] < new_size:
			return ""

		# replace file
		self._replace_file(name, decompress_file_name, user, new_size)
		# update capcity
		new_capcity = cur_capcity + compress_file_info[1] - new_size
		self.users[user] = (new_capcity, max_capcity)

		return str(new_capcity)

	def _replace_file(self, old_file, new_file, user, new_size):
		del self.files[old_file]
		self.files[new_file] = (user, new_size)

	def add_user(self, user, capcity):
		if user in self.users:
			return "false"

		self.users[user] = (capcity, capcity)

		return "true"

	def add_file_by(self, user, name, size):
		if user not in self.users or name in self.files:
			return ""

		cur_capcity, max_capcity = self.users[user]
		if cur_capcity < size:
			return ""

		self.files[name] = (user, size)
		self.users[user] = (cur_capcity - size, max_capcity)

		return str(cur_capcity - size)


	def update_capacity(self, user, capcity):
		if user not in self.users:
			return ""

		cur_capcity, max_capcity = self.users[user]
		used_capcity = max_capcity - cur_capcity

		if capcity > max_capcity or used_capcity <= capcity:
			self.users[user] = (capcity - used_capcity, capcity)
			return "0"

		ranked_files = []
		for file, file_info in self.files.items():
			if file_info[0] == user:
				ranked_files.append((file, file_info[1]))

		# sort by size desc, if tie, name asc
		ranked_files.sort(key=lambda x: (-x[1], x[0]))
		deleted_count = 0
		for owned_file in ranked_files:
			if used_capcity <= capcity:
				break

			used_capcity -= owned_file[1]
			del self.files[owned_file[0]]
			deleted_count += 1

		self.users[user] = (capcity - used_capcity, capcity)

		return str(deleted_count)

	def find_file(self, prefix, suffix):
		results = []

		for file_name, size_pair in self.files.items():
			if file_name.startswith(prefix) and file_name.endswith(suffix):
				results.append((file_name, size_pair[1]))

		results.sort(key=lambda x: (-x[1], x[0]))
		return ", ".join([f"{x[0]}({x[1]})" for x in results])

	def add_file(self, name, size):
		if name in self.files:
			return "false"

		self.files[name] = ("admin", size)

		return "true"

	def copy_file(self, name_from, name_to):
		if name_from not in self.files or name_to in self.files:
			return "false"

		file_info = self.files[name_from]

		if file_info[0] == "admin":
			self.files[name_to] = self.files[name_from]
			return "true"

		cur_capcity, max_capcity = self.users[file_info[0]]
		if cur_capcity < file_info[1]:
			return "false"

		self.files[name_to] = self.files[name_from]
		self.users[file_info[0]] = (cur_capcity - file_info[1], max_capcity)

		return "true"

	def get_file_size(self, name):
		if name not in self.files:
			return ""

		return str(self.files[name][1])



class Test:
	def __init__(self):
		pass

	def test_lvl_1(self):
		print("========running test lvl 1 A========")
		cloud = CloudStorageLvl1()
		
		commands = [
		  ["ADD_FILE", "/a.txt", "10"],
		  ["ADD_FILE", "/a.txt", "10"],
		  ["GET_FILE_SIZE", "/a.txt"],
		  ["COPY_FILE", "/missing.txt", "/b.txt"],
		  ["COPY_FILE", "/a.txt", "/b.txt"],
		  ["COPY_FILE", "/a.txt", "/b.txt"],
		  ["GET_FILE_SIZE", "/b.txt"],
		  ["ADD_FILE", "/b.txt", "99"],
		  ["GET_FILE_SIZE", "/missing.txt"]
		]

		expected_results = ["true", "false", "10", "false", "true", "false", "10", "false", ""]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)


		print("========running test lvl 1 B========")
		cloud = CloudStorageLvl1()
		
		commands = [
		  ["ADD_FILE", "/dir1/dir2/file.bin", "42"],
		  ["COPY_FILE", "/dir1/dir2/file.bin", "/dir1/file2.bin"],
		  ["COPY_FILE", "/dir1/file2.bin", "/dirX/dirY/file3.bin"],
		  ["GET_FILE_SIZE", "/dir1/dir2/file.bin"],
		  ["GET_FILE_SIZE", "/dir1/file2.bin"],
		  ["GET_FILE_SIZE", "/dirX/dirY/file3.bin"],
		  ["GET_FILE_SIZE", "/dirX/file3.bin"]
		]

		expected_results = ["true", "true", "true", "42", "42", "42", ""]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl_2(self):
		print("========running test lvl 2 A========")
		cloud = CloudStorageLvl2()
		
		commands = [
		  ["ADD_FILE", "/root/a.txt", "10"],
		  ["ADD_FILE", "/root/b.txt", "10"],
		  ["ADD_FILE", "/root/c.txt", "9"],
		  ["ADD_FILE", "/root/aa.txt", "10"],
		  ["ADD_FILE", "/x/root/a.txt", "10"],
		  ["COPY_FILE", "/root/c.txt", "/root/z.txt"],
		  ["FIND_FILE", "/root", ".txt"],
		  ["FIND_FILE", "/root/", "a.txt"],
		  ["FIND_FILE", "/nope", ".txt"]
		]

		expected_results = [
		  "true", "true", "true", "true", "true", "true",
		  "/root/a.txt(10), /root/aa.txt(10), /root/b.txt(10), /root/c.txt(9), /root/z.txt(9)",
		  "/root/a.txt(10), /root/aa.txt(10)",
		  ""
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 2 B========")
		cloud = CloudStorageLvl2()
		
		commands = [
		  ["ADD_FILE", "/p/q/file.tar.gz", "100"],
		  ["ADD_FILE", "/p/file.gz", "50"],
		  ["ADD_FILE", "/p/q/r/file.gz", "70"],
		  ["FIND_FILE", "/p", ".gz"],
		  ["FIND_FILE", "/p/q", ".tar.gz"],
		  ["FIND_FILE", "/p/q", ".gz"],
		  ["FIND_FILE", "/p/q", ".zip"]
		]

		expected_results = [
		  "true", "true", "true",
		  "/p/q/file.tar.gz(100), /p/q/r/file.gz(70), /p/file.gz(50)",
		  "/p/q/file.tar.gz(100)",
		  "/p/q/file.tar.gz(100), /p/q/r/file.gz(70)",
		  ""
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl_3(self):
		print("========running test lvl 3 A========")
		cloud = CloudStorageLvl3()
		
		commands = [
		  ["ADD_USER", "user1", "125"],
		  ["ADD_USER", "user1", "100"],
		  ["ADD_USER", "user2", "100"],
		  ["ADD_FILE_BY", "user1", "/dir/file.big", "50"],
		  ["ADD_FILE_BY", "user1", "/file.med", "30"],
		  ["ADD_FILE_BY", "user2", "/file.med", "40"],
		  ["COPY_FILE", "/file.med", "/dir/another/file.med"],
		  ["COPY_FILE", "/file.med", "/dir/another/another/file.med"],
		  ["ADD_FILE_BY", "user1", "/dir/file.small", "10"],
		  ["ADD_FILE", "/dir/admin_file", "200"],
		  ["ADD_FILE_BY", "user1", "/dir/file.small", "5"],
		  ["ADD_FILE_BY", "user1", "/my_folder/file.huge", "100"],
		  ["ADD_FILE_BY", "user3", "/my_folder/file.huge", "100"],
		  ["UPDATE_CAPACITY", "user1", "300"],
		  ["UPDATE_CAPACITY", "user1", "50"],
		  ["UPDATE_CAPACITY", "user2", "1000"]
		]

		expected_results = ["true", "false", "true", "75", "45", "", "true", "false", "5", "true", "", "", "", "0", "2", "0"]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 3 B========")
		cloud = CloudStorageLvl3()
		
		commands = [
		  ["ADD_USER", "u1", "60"],
		  ["ADD_USER", "u2", "100"],

		  ["ADD_FILE_BY", "u1", "/u1/a.bin", "20"],
		  ["ADD_FILE_BY", "u1", "/u1/b.bin", "20"],
		  ["ADD_FILE_BY", "u1", "/u1/c.bin", "20"],

		  ["COPY_FILE", "/u1/a.bin", "/u1/a_copy.bin"],
		  ["ADD_FILE", "/admin/x.bin", "1000"],
		  ["COPY_FILE", "/admin/x.bin", "/u1/admin_copy.bin"],

		  ["GET_FILE_SIZE", "/u1/c.bin"],
		  ["GET_FILE_SIZE", "/u1/admin_copy.bin"],

		  ["ADD_FILE_BY", "u2", "/u1/c.bin", "1"]
		]

		expected_results = [
		  "true", "true",
		  "40", "20", "0",
		  "false",
		  "true",
		  "true",
		  "20",
		  "1000",
		  ""
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 3 C========")
		cloud = CloudStorageLvl3()
		
		commands = [
		  ["ADD_USER", "u1", "200"],
		  ["ADD_FILE_BY", "u1", "/c.bin", "40"],
		  ["ADD_FILE_BY", "u1", "/b.bin", "40"],
		  ["ADD_FILE_BY", "u1", "/a.bin", "40"],
		  ["ADD_FILE_BY", "u1", "/z.bin", "10"],

		  ["UPDATE_CAPACITY", "u1", "50"],

		  ["GET_FILE_SIZE", "/a.bin"],
		  ["GET_FILE_SIZE", "/b.bin"],
		  ["GET_FILE_SIZE", "/c.bin"],
		  ["GET_FILE_SIZE", "/z.bin"]
		]

		expected_results = [
		  "true",
		  "160", "120", "80", "70",
		  "2",
		  "",
		  "",
		  "40",
		  "10"
		]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 3 D========")
		cloud = CloudStorageLvl3()
		
		commands = [
		  ["ADD_USER", "u1", "100"],
		  ["ADD_FILE_BY", "u1", "/f.txt", "10"],
		  ["COPY_FILE", "/missing.txt", "/x.txt"],
		  ["COPY_FILE", "/f.txt", "/f.txt"],
		  ["COPY_FILE", "/f.txt", "/x.txt"],
		  ["COPY_FILE", "/f.txt", "/x.txt"],
		  ["GET_FILE_SIZE", "/x.txt"]
		]

		expected_results = ["true", "90", "false", "false", "true", "false", "10"]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

	def test_lvl_4(self):
		print("========running test lvl 4 A========")
		cloud = CloudStorageLvl4()
		
		commands = [
		  ["ADD_USER", "u1", "100"],
		  ["ADD_FILE_BY", "u1", "/a.bin", "60"],
		  ["COMPRESS_FILE", "u1", "/a.bin"],
		  ["GET_FILE_SIZE", "/a.bin.COMPRESSED"],
		  ["GET_FILE_SIZE", "/a.bin"],
		  ["COMPRESS_FILE", "u1", "/a.bin.COMPRESSED"],
		  ["DECOMPRESS_FILE", "u1", "/a.bin.COMPRESSED"],
		  ["GET_FILE_SIZE", "/a.bin"],
		  ["GET_FILE_SIZE", "/a.bin.COMPRESSED"]
		]

		expected_results = ["true", "40", "70", "30", "", "", "40", "60", ""]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 A========")
		cloud = CloudStorageLvl4()
		
		commands = [
		  ["ADD_USER", "u1", "100"],
		  ["ADD_FILE_BY", "u1", "/a.bin", "60"],
		  ["COMPRESS_FILE", "u1", "/a.bin"],
		  ["GET_FILE_SIZE", "/a.bin.COMPRESSED"],
		  ["GET_FILE_SIZE", "/a.bin"],
		  ["COMPRESS_FILE", "u1", "/a.bin.COMPRESSED"],
		  ["DECOMPRESS_FILE", "u1", "/a.bin.COMPRESSED"],
		  ["GET_FILE_SIZE", "/a.bin"],
		  ["GET_FILE_SIZE", "/a.bin.COMPRESSED"]
		]

		expected_results = ["true", "40", "70", "30", "", "", "40", "60", ""]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 B========")
		cloud = CloudStorageLvl4()
		
		commands = [
		  ["ADD_USER", "u1", "100"],
		  ["ADD_USER", "u2", "100"],
		  ["ADD_FILE_BY", "u1", "/v.mp4", "80"],

		  ["COMPRESS_FILE", "u2", "/v.mp4"],
		  ["COMPRESS_FILE", "uX", "/v.mp4"],
		  ["COMPRESS_FILE", "u1", "/missing.bin"],

		  ["COMPRESS_FILE", "u1", "/v.mp4"],
		  ["DECOMPRESS_FILE", "u2", "/v.mp4.COMPRESSED"],
		  ["DECOMPRESS_FILE", "uX", "/v.mp4.COMPRESSED"],
		  ["DECOMPRESS_FILE", "u1", "/missing.COMPRESSED"]
		]

		expected_results = ["true", "true", "20", "", "", "", "60", "", "", ""]


		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 C========")
		cloud = CloudStorageLvl4()
		
		commands = [
		  ["ADD_USER", "u1", "60"],
		  ["ADD_FILE_BY", "u1", "/f.bin", "60"],
		  ["COMPRESS_FILE", "u1", "/f.bin"],

		  ["ADD_FILE_BY", "u1", "/g.bin", "20"],

		  ["COPY_FILE", "/f.bin.COMPRESSED", "/f2.bin.COMPRESSED"],

		  ["ADD_FILE", "/admin.dat", "1000"],
		  ["COPY_FILE", "/admin.dat", "/u1/admin_copy.dat"],

		  ["GET_FILE_SIZE", "/f2.bin.COMPRESSED"],
		  ["GET_FILE_SIZE", "/u1/admin_copy.dat"]
		]

		expected_results = ["true", "0", "30", "10", "false", "true", "true", "", "1000"]

		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)

		print("========running test lvl 4 D========")
		cloud = CloudStorageLvl4()
		
		commands = [
		  ["ADD_USER", "u1", "300"],

		  ["ADD_FILE_BY", "u1", "/vid.mp4", "100"],
		  ["COMPRESS_FILE", "u1", "/vid.mp4"],
		  ["ADD_FILE_BY", "u1", "/vid.mp4", "50"],

		  ["DECOMPRESS_FILE", "u1", "/vid.mp4.COMPRESSED"],

		  ["ADD_FILE_BY", "u1", "/b.bin", "60"],
		  ["ADD_FILE_BY", "u1", "/a.bin", "60"],
		  ["UPDATE_CAPACITY", "u1", "140"],

		  ["GET_FILE_SIZE", "/a.bin"],
		  ["GET_FILE_SIZE", "/b.bin"],
		  ["GET_FILE_SIZE", "/vid.mp4"],
		  ["GET_FILE_SIZE", "/vid.mp4.COMPRESSED"]
		]

		expected_results = ["true", "200", "250", "200", "", "140", "80", "2", "", "", "50", "50"]


		results = []

		for c in commands:
			results.append(cloud.command(*c))

		print(f"expected {expected_results}")
		print(f"actual {results}")
		print(expected_results == results)





test = Test()
# test.test_lvl_1()
# test.test_lvl_2()
# test.test_lvl_3()
test.test_lvl_4()








