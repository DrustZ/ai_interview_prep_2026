# 0. job scheduling


# 1. Social Network with Snapshots

from collections import defaultdict
from queue import PriorityQueue
import copy

class SocialNetwork:
	def __init__(self):
		"""Initialize an empty social network."""
		self.users = set()
		self.followers = defaultdict(set)

	def add_user(self, user_id: str) -> None:
		"""
		Add a user to the network.
		Raises ValueError if the user already exists.
		"""
		if user_id in self.users:
			raise ValueError('duplicate users')

		self.users.add(user_id)

	def follow(self, follower: str, followee: str) -> None:
		"""
		Make `follower` follow `followee`.
		Raises ValueError if a user does not exist.
		Notes: A user cannot follow themselves. Duplicate follows do nothing.
		"""
		if follower not in self.users or followee not in self.users:
			raise ValueError('follower or followee does not exist')

		if follower == followee:
			raise ValueError('cannot follow self')

		self.followers[followee].add(follower)

	def create_snapshot(self) -> 'Snapshot':
		"""
		Create a snapshot of the current network state.
		This object must be immutable (it cannot change).
		"""
		return Snapshot(self.users, self.followers)


class Snapshot:
	def __init__(self, users, followers):
		self.users = copy.deepcopy(users)
		self.followers = copy.deepcopy(followers)
		self.following = defaultdict(set)

		for followee, follower_set in self.followers.items():
			for follower in follower_set:
				self.following[follower].add(followee)

	def is_following(self, follower: str, followee: str) -> bool:
		"""
		Check if `follower` is following `followee` in this snapshot.
		Returns True or False.
		"""
		if followee not in self.users or followee not in self.followers:
			return False

		return follower in self.followers[followee]

	# question 2 - Update the snapshot class so we can see the full list of followers.
	def get_following(self, user_id: str) -> list[str]:
		"""
		Get a list of people that `user_id` follows.
		"""
		if user_id not in self.users:
			raise ValueError('none exists user')

		return self.following[user_id]

	def get_followers(self, user_id: str) -> list[str]:
		"""
		Get a list of people who follow `user_id`.
		"""
		if user_id not in self.users:
			raise ValueError('none exists user')

		return self.followers[user_id]


	# question 3 - recommend top k
	# use priority queue - min heap
	# time complexity - O(F*C + ClgK) - F -> user followings | C -> candidates
	# space complexity - O(C + K)
	def recommend(self, user_id: str, k: int) -> list[str]:
		"""
		Recommend top K users for `user_id` to follow.
		"""
		if user_id not in self.users:
			raise ValueError('user id not exists')

		pq = PriorityQueue()
		counter = defaultdict(int)
		following = self.get_following(user_id)

		# find user_id following [follow-A]
		# find who following[follow-A] is following[follow-B]
		# filter follow-B if user_id already follows
		# count follow-B frequency, and find top k

		for follow_A in following:
			for candidate in self.following.get(follow_A, set()):
				if candidate in following:
					continue

				counter[candidate] += 1

		print(counter)


		for candidate, frequency in counter.items():
			if pq.qsize() < k:
				pq.put((frequency, candidate))
			elif frequency > pq.queue[0][0]:
				pq.get()
				pq.put((frequency, candidate))

		result = []
		while not pq.empty():
			_, candidate = pq.get()
			result.append(candidate)

		result.reverse()

		return result


# Immutability: How do you make sure snapshots don't break?
"Use deep copy"

# Scaling: What if there are millions of users?
"If all users cannot fit into mem or just too many of them, we should split it into partitions and keep"
"track which partitions have changed since"
"last snapshot, and take snapshot of those partitions"

# Handling many users at once?
"If we keep old snapshot while having new one"
"since snapshot are immutable, we are find"
"If we are replacing old one with new one"
"use Reader/Writer lock"
"Mutex for many reader to read snapshot, writer mutex for take snapshot"
"when all reader mutex released, writer mutex lock and release the new snapshot"


# 2. Infection Spread Simulation
from queue import deque
from collections import defaultdict


class InfectionSimulationWithNoBoardUpdate:
	# when N = 1
	# Each infected is a BFS starting point
	def infection(self, board):
		directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

		queue = deque()
		rows = len(board)
		cols = len(board[0])
		visited = [[False] * cols for _ in range(rows)]
		healthy = 0

		# check infected
		for r in range(rows):
			for c in range(cols):
				if board[r][c] == 1:
					queue.append((r, c))
					visited[r][c] = True
				else:
					healthy += 1

		if not healthy:
			return 0
		elif not queue:
			return -1

		# BFS
		steps = 0
		while queue and healthy > 0:
			# loop through each step and then add step++
			cur_step_size = len(queue)
			for _ in range(cur_step_size):
				cur_r, cur_c = queue.popleft()

				for direction in directions:
					next_r = cur_r + direction[0]
					next_c = cur_c + direction[1]

					if (next_r >= 0 
						and next_r < rows 
						and next_c >= 0 
						and next_c < cols 
						and board[next_r][next_c] == 0
						and not visited[next_r][next_c]
					):
						queue.append((next_r, next_c))
						healthy -= 1
						visited[next_r][next_c] = True
			# only step++ when there is next wave to spread, otherwise this is the last wave
			if queue:
				steps += 1

		return steps if not healthy else -1



	# return how many days the system can be STABLE
	def infection_with_immune(self, board):
		directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

		queue = deque()
		rows = len(board)
		cols = len(board[0])
		visited = [[False] * cols for _ in range(rows)]
		healthy = 0

		# check infected
		for r in range(rows):
			for c in range(cols):
				if board[r][c] == 1:
					queue.append((r, c))
					visited[r][c] = True
				elif board[r][c] == 0:
					healthy += 1

		if not healthy:
			return 0
		elif not queue:
			return -1

		# BFS
		steps = 0
		while queue:
			# loop through each step and then add step++
			cur_step_size = len(queue)
			for _ in range(cur_step_size):
				cur_r, cur_c = queue.popleft()

				for direction in directions:
					next_r = cur_r + direction[0]
					next_c = cur_c + direction[1]

					if (next_r >= 0 
						and next_r < rows 
						and next_c >= 0 
						and next_c < cols 
						and board[next_r][next_c] == 0
						and not visited[next_r][next_c]
					):
						queue.append((next_r, next_c))
						visited[next_r][next_c] = True

			# only step++ when there is next wave to spread, otherwise this is the last wave
			if queue:
				steps += 1

		return steps

	# the total stable days is the last person who infected plus the days they recovered
	# the last person who infected - total days of infections spreading
	# the days they recovered - D
	def infection_with_recover_math_way(self, board, D):
		directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

		queue = deque()
		rows = len(board)
		cols = len(board[0])
		visited = [[False] * cols for _ in range(rows)]
		healthy = 0

		# check infected
		for r in range(rows):
			for c in range(cols):
				if board[r][c] == 1:
					queue.append((r, c))
					visited[r][c] = True
				elif board[r][c] == 0:
					healthy += 1

		if not queue:
			return 0

		# BFS
		steps = 0
		while queue:
			# loop through each step and then add step++
			cur_step_size = len(queue)
			for _ in range(cur_step_size):
				cur_r, cur_c = queue.popleft()

				for direction in directions:
					next_r = cur_r + direction[0]
					next_c = cur_c + direction[1]

					if (next_r >= 0 
						and next_r < rows 
						and next_c >= 0 
						and next_c < cols 
						and board[next_r][next_c] == 0
						and not visited[next_r][next_c]
					):
						queue.append((next_r, next_c))
						visited[next_r][next_c] = True

			# only step++ when there is next wave to spread, otherwise this is the last wave
			if queue:
				steps += 1

		return steps + D

	def infection_with_recover_simulation_way(self, board, D):
		directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

		rows = len(board)
		cols = len(board[0])
		
		cur_infected = set()
		next_wave = deque()
		visited = [[False] * cols for _ in range(rows)]
		schedule_immune = defaultdict(set)

		healthy = 0

		for r in range(rows):
			for c in range(cols):
				if board[r][c] == 1:
					cur_infected.add((r, c))
					next_wave.append((r, c))
					visited[r][c] = True

					schedule_immune[D].add((r, c))

		if not cur_infected:
			return 0

		step = 0

		while cur_infected:
			step += 1
			# check who becomes immune
			for r, c in schedule_immune[step]:
				cur_infected.discard((r, c))

			# find next wave of infected
			cur_step_size = len(next_wave)
			for _ in range(cur_step_size):
				cur_r, cur_c = next_wave.popleft()

				for direction in directions:
					next_r = cur_r + direction[0]
					next_c = cur_c + direction[1]

					if (next_r >= 0 
						and next_r < rows 
						and next_c >= 0 
						and next_c < cols 
						and board[next_r][next_c] == 0
						and not visited[next_r][next_c]
					):
						cur_infected.add((next_r, next_c))
						next_wave.append((next_r, next_c))
						visited[next_r][next_c] = True

						schedule_immune[step + D].add((next_r, next_c))

		return step


	# when N > 1
	# use a infected neighbor count for recording
	# use a schedule board to record this slot has been added into queue or not
	def infection_with_multi_neighbor(self, board, N):
		directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
		rows = len(board)
		cols = len(board[0])

		next_wave = deque()
		infected_neighbor_count = [[0] * cols for _ in range(rows)]
		scheduled = [[False] * cols for _ in range(rows)]

		healthy = 0

		# init the first wave
		for r in range(rows):
			for c in range(cols):
				if board[r][c] == 1:
					next_wave.append((r, c))
					scheduled[r][c] = True
				else:
					healthy += 1

		if healthy == 0:
			return 0
		elif not next_wave:
			return -1

		step = 0

		while next_wave:
			cur_step_size = len(next_wave)
			for _ in range(cur_step_size):
				r, c = next_wave.popleft()

				# check neighbor and update infected count
				for direction in directions:
					next_r, next_c = r + direction[0], c + direction[1]

					if (
						next_r >= 0 
						and next_r < rows 
						and next_c >= 0 
						and next_c < cols 
						and board[next_r][next_c] == 0
					):
						infected_neighbor_count[next_r][next_c] += 1

						if infected_neighbor_count[next_r][next_c] >= N and not scheduled[next_r][next_c]:
							print(f'infected - {[next_r, next_c]}')

							next_wave.append((next_r, next_c))
							scheduled[next_r][next_c] = True
							healthy -= 1
			
			if next_wave:
				step += 1

		return step if healthy == 0 else -1

	def infection_with_multi_neighbor_with_immune(self, board, N):
		directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
		rows = len(board)
		cols = len(board[0])

		next_wave = deque()
		infected_neighbor_count = [[0] * cols for _ in range(rows)]
		scheduled = [[False] * cols for _ in range(rows)]

		healthy = 0

		# init the first wave
		for r in range(rows):
			for c in range(cols):
				if board[r][c] == 1:
					next_wave.append((r, c))
					scheduled[r][c] = True
				elif board[r][c] == 0:
					healthy += 1

		if healthy == 0 or not next_wave:
			return 0

		step = 0

		print(f'healthy-{healthy}')
		print(f'next-wave={next_wave}')

		while next_wave:
			cur_step_size = len(next_wave)
			for _ in range(cur_step_size):
				r, c = next_wave.popleft()

				# check neighbor and update infected count
				for direction in directions:
					next_r, next_c = r + direction[0], c + direction[1]

					if (
						next_r >= 0 
						and next_r < rows 
						and next_c >= 0 
						and next_c < cols 
						and board[next_r][next_c] == 0
					):
						infected_neighbor_count[next_r][next_c] += 1

						if infected_neighbor_count[next_r][next_c] >= N and not scheduled[next_r][next_c]:
							print(f'infected - {[next_r, next_c]}')

							next_wave.append((next_r, next_c))
							scheduled[next_r][next_c] = True
			
			if next_wave:
				step += 1

		return step

	# use a infected neighbor count for recording
	# use a schedule board to record this slot has been added into queue or not
	# use a schedule_immune board to record slot and recover date mapping
	# shcedule_to_spread - key - step | value - set of cells schedule to spread on that step
	def infection_with_multi_neighbor_with_recover(self, board, N, D):
		if D <= 0:
			return 0

		directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
		rows = len(board)
		cols = len(board[0])

		cur_infected = set()
		infected_neighbor_count = [[0] * cols for _ in range(rows)]
		scheduled = [[False] * cols for _ in range(rows)]
		# key - recover date
		# value - list of slots become immune this date
		schedule_immune = defaultdict(set)
		# key - action date
		# value - list of slots to infect neigbors on taht date
		shcedule_to_spread = defaultdict(set)

		for r in range(rows):
			for c in range(cols):
				if board[r][c] == 1:
					shcedule_to_spread[0].add((r, c))
					cur_infected.add((r, c))
					scheduled[r][c] = True
					schedule_immune[D].add((r, c))

		if not shcedule_to_spread:
			return 0

		step = 0
		while cur_infected:
			# check recover from immune
			if step in schedule_immune:
				for r, c in schedule_immune[step]:
					cur_infected.discard((r, c))
					shcedule_to_spread[step].discard((r, c))

					# reduce infected count for neighbor
					for direction in directions:
						next_r, next_c = r + direction[0], c + direction[1]
						if rows > next_r >= 0 and cols > next_c >= 0:
							infected_neighbor_count[next_r][next_c] -= 1

			# check next infected
			# infect
			next_step = step + 1
			for r, c in shcedule_to_spread[step]:
				for direction in directions:
					n_r, n_c = r + direction[0], c + direction[1]
					if 0 <= n_r < rows and 0 <= n_c < cols:
						infected_neighbor_count[n_r][n_c] += 1
						if infected_neighbor_count[next_r][next_c] >= N and not scheduled[next_r][next_c] and board[n_r][n_c] == 0:
							shcedule_to_spread[next_step].add((n_r, n_c))
							scheduled[next_r][next_c] = True
							cur_infected.add((next_r, next_c))
							schedule_immune[next_step + D].add((next_r, next_c))

			if cur_infected:
				steps += 1

		return step

	# if a infected slot about to turn after D days
	# if neighbors infected count >= K:
	# it turns to death
	# else immune
	# return stable days and count of death

	# Order of Operations Each Day
	# Transition: Identify cells infected for >= D days
	# Death vs Immunity: For each transitioning cell, count its currently infected neighbors
	# Apply transitions: Mark cells as dead or immune, remove from active set
	# Spread infection: Remaining active infected cells infect healthy neighbors

	# cur_infected - all infected in a set
	# shcedule_to_spread - key - step | value - set of cells schedule to spread on that step
	# schedule_to_transit - key - step | value - set of cells schedule to transit on that step
	# visited - avoid duplication visiting in BFS

	def infection_with_death_parameter(self, board, D, K):
		directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
		rows = len(board)
		cols = len(board[0])

		cur_infected = set()
		infected_neighbor_count = [[0] * cols for _ in range(rows)]
		visited = [[False] * cols for _ in range(rows)]
		# key - action date
		# value - list of slots to infect neigbors on taht date
		shcedule_to_spread = defaultdict(set)
		# key - change date
		# value - list of slots become immune this date
		schedule_transit = defaultdict(set)

		for r in range(rows):
			for c in range(cols):
				if board[r][c] == 1:
					shcedule_to_spread[0].add((r, c))
					cur_infected.add((r, c))
					visited[r][c] = True
					schedule_transit[D].add((r, c))

		if not shcedule_to_spread:
			return (0, 0)

		step = 0
		death_count = 0
		# death_ones = []
		while cur_infected:

			# cur_board = copy.deepcopy(board)
			# for r, c in cur_infected:
			# 	cur_board[r][c] = 1
			# print(f'-----step-{step}-----')
			# print(f'cur board - ')
			# for r in cur_board:
			# 	print(r)
			# print(f'cur_infected-{cur_infected}')
			# print(f'schedule_transit-{schedule_transit}')
			# print(f'shcedule_to_spread-{shcedule_to_spread}')
			# print(f'death_ones-{death_ones}')
			# print(f'infected_neighbor_count-')
			# for r in infected_neighbor_count:
			# 	print(r)

			# check transit
			if step in schedule_transit:
				for r, c in schedule_transit[step]:
					cur_infected.discard((r, c))
					# try to discard (r, c) out of cur step's spreading, if not there, nothing happen
					shcedule_to_spread[step].discard((r, c))
					# check if dead
					if infected_neighbor_count[r][c] >= K:
						death_count += 1
						# death_ones.append((r, c))
				
				# change neighbor count
				for r, c in schedule_transit[step]:
					# turn neighbor count to None a safe check to mark this cell not able infected
					infected_neighbor_count[r][c] = None
					for direction in directions:
						n_r, n_c = r + direction[0], c + direction[1]
						if 0 <= n_r < rows and 0 <= n_c < cols and infected_neighbor_count[n_r][n_c] is not None:
							infected_neighbor_count[n_r][n_c] -= 1

			# infect
			next_step = step + 1
			for r, c in shcedule_to_spread[step]:
				for direction in directions:
					n_r, n_c = r + direction[0], c + direction[1]
					if 0 <= n_r < rows and 0 <= n_c < cols:
						if infected_neighbor_count[n_r][n_c] is not None:
							infected_neighbor_count[n_r][n_c] += 1

						if not visited[n_r][n_c] and board[n_r][n_c] == 0:
							shcedule_to_spread[next_step].add((n_r, n_c))
							cur_infected.add((n_r, n_c))
							visited[n_r][n_c] = True
							schedule_transit[next_step + D].add((n_r, n_c))

			if cur_infected:
				step += 1

		return (step, death_count)


	# simulate the process
	# farmer can burn cells
	def infection_with_burner(self, board, D, K):
		burn_type = 'row'
		min_death = float('inf')
		index = 0

		rows = len(board)
		cols = len(board[0])

		# check by row
		for r in range(rows):
			new_board = copy.deepcopy(board)
			for c in range(cols):
				new_board[r][c] = -1

			_, death = self.infection_with_death_parameter(new_board, D, K)
			if death < min_death:
				min_death = death
				index = r

		# check by cols
		for c in range(cols):
			new_board = copy.deepcopy(board)
			for r in range(rows):
				new_board[r][c] = -1

			_, death = self.infection_with_death_parameter(new_board, D, K)
			if death < min_death:
				burn_type = 'col'
				min_death = death
				index = c

		return (burn_type, index, min_death)


# 3. Distributed Machine Cluster Count and Topology
class Node:
    def __init__(self, id, parentId, childIds, cluster):
        self.id = id
        self.parentId = parentId
        self.childIds = childIds[:] if childIds is not None else []
        self.cluster = cluster

        # start with itself
        self.global_counter = 1
        self.call_backed = set()

        self.topology_strs = []
        self.topo_call_backed = set()

    # This method is automatically invoked when a message arrives.
    def receiveMessage(self, fromId, message):
        # TODO: Implement receiveMessage logic.
        if message.startswith("count"):
            self._count(fromId, message)
        
        if message.startswith("topology"):
            self._topology(fromId, message)

    """
    if call root
    If no children, and is root print 1
    else call all children with count

    if called from parent and it is leaf, call parent with 1
    if called from parent and not leaf, call all children with count

    if called from child, add count to global count
    if all children have returned, call parent with sub-total count
    """
    def _count(self, from_id, message):
        # print(f'iam - {self.id} | take message from {from_id} | message {message}')

        if from_id == -1:
            if not self.childIds:
                print("1")
            else:
                for child_id in self.childIds:
                    self.cluster.sendAsyncMessage(child_id, message, self.id)
        
        elif from_id == self.parentId:
            if not self.childIds:
                self.cluster.sendAsyncMessage(self.parentId, "count-1", self.id)
            else:
                for child_id in self.childIds:
                    self.cluster.sendAsyncMessage(child_id, message, self.id)
        elif from_id in self.childIds:
            sub_count = int(message.split('-')[1])
            self.global_counter += sub_count
            self.call_backed.add(from_id)

            if len(self.call_backed) == len(self.childIds):
                if self.parentId >= 0:
                    self.cluster.sendAsyncMessage(self.parentId, f'count-{self.global_counter}', self.id)
                else:
                    print(self.global_counter)

    """
    if call root
    If no children, and is root print itself
    else call all children with topology

    if called from parent and it is leaf, call parent with itself
    if called from parent and not leaf, call all children with topoloy

    if called from child, add to global topology str
    if all children have returned, call parent with (topology str)
    """
    def _topology(self, from_id, message):
        # print(f'iam - {self.id} | take message from {from_id} | message {message}')
        if from_id == -1:
            if not self.childIds:
                print(self.id)
            else:
                for child_id in self.childIds:
                    self.cluster.sendAsyncMessage(child_id, message, self.id)
        
        elif from_id == self.parentId:
            if not self.childIds:
                self.cluster.sendAsyncMessage(self.parentId, f'topology-{self.id}', self.id)
            else:
                for child_id in self.childIds:
                    self.cluster.sendAsyncMessage(child_id, message, self.id)
        elif from_id in self.childIds:
            sub_topology = message.split('-')[1]
            self.topology_strs.append(sub_topology)
            self.topo_call_backed.add(from_id)

            # print(self.topology_strs)

            if len(self.topo_call_backed) == len(self.childIds):
                local_topology = f'{self.id}({",".join(self.topology_strs)})'

                if self.parentId >= 0:
                    self.cluster.sendAsyncMessage(self.parentId, f'topology-{local_topology}', self.id)
                else:
                    # print(self.topo_call_backed)
                    # print(self.childIds)
                    print(local_topology)
        


class Cluster:
    def __init__(self, rootId):
        self.nodes = {}
        self.rootId = rootId

    def addNode(self, id, parentId, childIds):
        self.nodes[id] = Node(id, parentId, childIds, self)

    def sendAsyncMessage(self, targetId, message, fromId):
        """
        Provided API to simulate the process of sending a message to a target node
        asynchronously.
        """
        targetNode = self.nodes.get(targetId)
        if targetNode is not None:
            targetNode.receiveMessage(fromId, message)


# 4. Toy Language Type System
class Node:
    def __init__(self, value_or_tuple):
        if isinstance(value_or_tuple, str):
            # for primitive or generic types
            self.value = value_or_tuple
            self.tuple = None
            self.isTuple = False
        else:
            # for tuple types
            self.value = None
            self.tuple = value_or_tuple
            self.isTuple = True

    def __str__(self):
        if self.isTuple:
            values_strs = [str(node) for node in self.tuple]

            return f'[{",".join(values_strs)}]'
        else:
            return self.value


class Function:
    def __init__(self, params, returnType):
        self._params = params
        self._returnType = returnType

    def __str__(self):
        params_strs = [str(node) for node in self._params]

        return f'[{",".join(params_strs)}] -> {self._returnType}'


"""
inferReturnType
1. bind generic type to actual type (Node) and also raise error is unmatched
2. replace generic type in return type
"""


class Node:
    def __init__(self, value_or_tuple):
        if isinstance(value_or_tuple, str):
            # for primitive or generic types
            self.value = value_or_tuple
            self.tuple = None
            self.isTuple = False
        else:
            # for tuple types
            self.value = None
            self.tuple = value_or_tuple
            self.isTuple = True

    def is_generic(self):
        primitives = set(["int", "char", "float"])

        if not self.isTuple:
            return self.value not in primitives
        else:
            return any([node.is_generic() for node in self.tuple])

    def getValue(self):
        return self.value

    def getTuple(self):
        return self.tuple

    def get_content(self):
        return self.value if not self.isTuple else self.tuple
    
    def __eq__(self, other):
        if self.isTuple != other.isTuple:
            return False
        if self.isTuple and other.isTuple:
            if len(self.tuple) != len(other.tuple):
                return False
            return all([my_node == other_node for my_node, other_node in zip(self.tuple, other.tuple)])
        else:
            return self.value == other.value

    def __str__(self):
        # TODO: Implement __str__ logic.
        if self.isTuple:
            values_strs = [str(node) for node in self.tuple]

            return f'[{",".join(values_strs)}]'
        else:
            return self.value

class Function:
    def __init__(self, params, returnType):
        self.params = params
        self.returnType = returnType

    def getParams(self):
        return self.params

    def getReturnType(self):
        return self.returnType

    def __str__(self):
        # TODO: Implement __str__ logic.
        params_strs = [str(node) for node in self._params]

        return f'[{",".join(params_strs)}] -> {self._returnType}'


class Solution:
    @staticmethod
    def inferReturnType(function, params):
    	# key - generic type
    	# value - Node
        binding_map = {}

        func_params = function.getParams()
        func_return = function.getReturnType()

        if len(func_params) != len(params):
            return None

        for func_param, param in zip(func_params, params):
            try:
                Solution.binding(func_param, param, binding_map)
            except ValueError as e:
                print(e)
                return None

        print(str(binding_map))

        if not func_return.is_generic():
            return str(func_return)
        else:
            return Solution.replace_generic(func_return, binding_map)

    @staticmethod
    def replace_generic(func_return, binding_map):
        if func_return.isTuple:
            content = []
            for node in func_return.tuple:
                content.append(Solution.replace_generic(node, binding_map))
            return Node(content)
        elif func_return.is_generic():
            generic = func_return.value
            if generic not in binding_map:
                return None
            return binding_map[generic]
        else:
            return Node(func_return.value)
        
    @staticmethod
    def binding(func_param, param, binding_map):
        if not func_param.is_generic() and func_param.isTuple != param.isTuple:
            raise ValueError(f'param isTuple miss matched | fp - {func_param} | p - {param}')
        elif func_param.isTuple and param.isTuple and len(func_param.tuple) != len(param.tuple):
            raise ValueError('param length miss matched')
        elif not func_param.is_generic() and func_param.value != param.value:
            raise ValueError('param base type miss matched')
        else if param.is_generic():
        	raise ValueError('param cannot be generic')

        """
        both tuple, recursively binding
        func_param is generic, bind into map - check if already binded and conflict
        """
        if func_param.isTuple and param.isTuple:
            for sub_func_param, sub_param in zip(func_param.tuple, param.tuple):
                Solution.binding(sub_func_param, sub_param, binding_map)
        elif func_param.is_generic():
            generic = func_param.value
            
            # print(f'generic - {generic} | value - {value}')

            if generic in binding_map and binding_map[generic] != param:
                raise ValueError(f'{generic} already binded to {binding_map[generic]} and conflict to {param}')
            
            binding_map[generic] = param
        
# 5. chat bot
"""
Use a event bus to allow communications between bots
Allow bots connects to output (a string list of messages) so bots and print message themselves


message process logic

for /meet
1. check if target use if away
2. setup meeting
3. set both sender and target user to away with meeting reason

for /away
subscribe to 'meet' event and 'check_away' event


IF asked to support multiple channels, let chatApp supports it
Each channel has its own bots and event bus

"""



from typing import List, Dict, Callable, Any, Type
from collections import defaultdict

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Event:
    event_name: str
    content: dict


class EventBus:
    def __init__(self):
        self.bus = defaultdict(list) # list of callable

    def subscribe(self, event_name, handler):
        self.bus[event_name].append(handler)

    def publish(self, event):
        if event['event_name'] in self.bus:
            for handler in self.bus[event['event_name']]:
                handler(event['content'])


class ChatBotInterface(ABC):
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.subscribe_event()
        self.output = None

    def connect_to_output(self, output):
        self.output = output

    def _publish_message(self, message):
        self.output.append(message)

    @abstractmethod
    def subscribe_event(self):
        pass

    @abstractmethod
    def process_message(self, name, message):
        pass


class AwayBot(ChatBotInterface):
    def __init__(self, event_bus):
        # away users -> away reason
        self.away_people = {}

        super().__init__(event_bus)

    def _build_message(self, target_user, away_message):
        return f'AwayBot: {target_user} is away: {away_message}'

    def subscribe_event(self):
        self.event_bus.subscribe('meet', self._handle_meet)
        self.event_bus.subscribe('check_away', self._handle_message_mention)

    def _handle_message_mention(self, event):
        target_user = event['target_user']

        # check if target use is away
        if target_user in self.away_people:
            self._publish_message(self._build_message(target_user, self.away_people[target_user]))

    def _handle_meet(self, event):
        target_user = event['target_user']
        self.away_people[target_user] = event['away_reason']

    def process_message(self, name, message):
        if message.startswith('/away'):
            away_reason = message.split('/away ')[1]
            self.away_people[name] = away_reason
            self._publish_message(self._build_message(name, away_reason))
        
        # for user, away_message in self.away_people.items():
        #     if user in message:
        #         self._publish_message(self._build_message(user, away_message))


class MeetBot(ChatBotInterface):
    def __init__(self, event_bus):
        super().__init__(event_bus)

    def subscribe_event(self):
        pass

    def _build_message(self, user, target_usr):
        return f'MeetBot: Google Meet with @{user}, and {target_usr} starting at /abc-def-123'

    def process_message(self, name, message):
        target_user = message.split(' ')[1]

        # check if target user away first
        self.event_bus.publish({
            'event_name': 'check_away',
            'content': {
                'target_user': target_user
            }
        })

        self._publish_message(self._build_message(name, target_user))

        self.event_bus.publish({
            'event_name': 'meet',
            'content': {
                'target_user': target_user,
                'away_reason': f'@{target_user} may be in a meeting right now'
            }
        })
        self.event_bus.publish({
            'event_name': 'meet',
            'content': {
                'target_user': name,
                'away_reason': f'@{name} may be in a meeting right now'
            }
        })


class TacoBot(ChatBotInterface):
    def __init__(self, event_bus):
        super().__init__(event_bus)
        self.taco_counter = defaultdict(int)

    def subscribe_event(self):
        pass

    def _get_taco_word(self, count):
        return 'taco' if count == 1 else 'tacos'

    def _build_message(self, name, target_user, given, cur):
        given_taco_word = self._get_taco_word(given)
        cur_taco_word = self._get_taco_word(cur)
        return f'TacoBot: @{name} gave @{target_user} {given} {given_taco_word}. @{target_user} now has {cur} {cur_taco_word}.'

    def process_message(self, name, message):
        splited_message = message.split(' ')
        recipient = splited_message[1][1:] # discard the first char - @
        
        if len(splited_message) == 3:
            count = int(splited_message[2])
        else:
            count = 1

        self.taco_counter[recipient] += count

        self._publish_message(self._build_message(name, recipient, count, self.taco_counter[recipient]))

class ChatApp:
    def __init__(self):
        # TODO: Implement __init__ logic.
        self.messages = []
        self.bots = {}

    def register_bot(self, bot, command):
        self.bots[command] = bot
        bot.connect_to_output(self.messages)

    def sendMessage(self, name: str, text: str):
        # TODO: Implement sendMessage logic.
        self.messages.append(f'{name}: {text}')

        for command, bot in self.bots.items():
            if text.startswith(command):
                bot.process_message(name, text)


    def getMessages(self) -> List[str]:
        # TODO: Implement getMessages logic.
        return self.messages


class MultiChannelChatApp:
    def __init__(self):
        """TODO: Implement ChatApp.__init__ logic."""
        self.messages = {}
        self.bots = {}

    def _register_bot(self, channel, bot, command):
        self.bots[channel][command] = bot
        bot.connect_to_output(self.messages[channel])

    def createChannel(self, channelName: str):
        """TODO: Implement createChannel logic."""
        if channelName not in self.messages:
            self.messages[channelName] = []
        if channelName not in self.bots:
            self.bots[channelName] = {}

        event_bus = EventBus()

        away_bot = AwayBot(event_bus)
        meet_bot = MeetBot(event_bus)
        taco_bot = TacoBot(event_bus)

        self._register_bot(channelName, away_bot, '/away')
        self._register_bot(channelName, meet_bot, '/meet')
        self._register_bot(channelName, taco_bot, '/givetaco')

    def sendMessage(self, channelName: str, name: str, text: str):
        """TODO: Implement sendMessage logic."""
        if channelName not in self.messages:
            raise ValueError(f'channel not exists - {channelName}')

        self.messages[channelName].append(f'{name}: {text}')

        for command, bot in self.bots[channelName].items():
            if text.startswith(command):
                bot.process_message(name, text)

    def getMessages(self, channelName: str) -> List[str]:
        """TODO: Implement getMessages logic."""
        return self.messages[channelName]

# 6. GPU credit
from typing import List, Optional
from queue import PriorityQueue
from dataclasses import dataclass

"""
simulate the process
When a subtact happen, burn credit from the one expire soonest -> use priorityqueue to handle the process

use a timeline to record events
"""

@dataclass
class Event:
    id: str
    event_type: str
    amount: int
    timestamp: int
    expired: int

class CreditSystem:
    def __init__(self, ):
        # each event is a Event
        # sort them when try to getbalance
        self.timeline = [] 

    def grantCredit(self, id: str, amount: int, startTime: int, expirationTime: int) -> None:
        self.timeline.append(Event(id, 'grant', amount, startTime, expirationTime - 1))

    def subtract(self, amount: int, timestamp: int) -> None:
        self.timeline.append(Event(None, 'subtract', amount, timestamp, None))

    def getBalance(self, timestamp: int) -> int:
        # order by expiration time
        credits = PriorityQueue()
        self.timeline.sort(key=lambda x: x.timestamp)

        # reset when we have new granted credit
        negative_amount = False

        print(f'==========================query-ts-{timestamp}================================')
        print(self.timeline)

        for event in self.timeline:
            if event.timestamp > timestamp:
                break

            if event.event_type == 'grant':
                negative_amount = False
                credits.put((event.expired, event.amount))
            else:
                processed_credits = PriorityQueue()

                subtract_amount = event.amount
                subtract_ts = event.timestamp

                print(f'=====ts-{subtract_ts} | sub-amount-{subtract_amount}======')

                while not credits.empty() and subtract_amount > 0:
                    """
                    Get expired soonest one
                    if subtract more than its amount, carry the left to next one
                    """
                    credit = credits.get()
                    # if credit already expired
                    if credit[0] < subtract_ts:
                        continue

                    # calculate credit amount
                    if credit[1] < subtract_amount:
                        subtract_amount -= credit[1]
                        new_credit_amount = 0
                    else:
                        new_credit_amount = credit[1] - subtract_amount
                        subtract_amount = 0
                    
                    processed_credits.put((credit[0], new_credit_amount))

                if subtract_amount > 0:
                    negative_amount = True
                
                while not credits.empty():
                    processed_credits.put(credits.get())
                credits = processed_credits

                # in the end, whether credits have all used (still have subtract_amount > 0)
                # or subtract_amount = 0 we do nothing anymore

        print(f'credits - {credits.queue}')

        # kick out all expired
		while not credits.empty():
			if credits.queue[0][0] < timestamp:
				credits.get()
			else:
				break

        amount = 0
        if credits.empty() or negative_amount:
        	"Return specific value if credit amount not enough for subtraction at query time"
        	"or no credits available at query time"
            return 0

        while not credits.empty() and not negative_amount:
            credit = credits.get()
            if credit[0] < timestamp:
                continue
            amount += credit[1]
        
        print(f'amount - {amount}')
        return amount



# 7. Durable / presistent DB

"""
Storage structure
first int (4 bytes) - total number of key/value pair
key value pair - int(total byte length)|int(key str byte length)|key-bytes|int(value str byte length)|value-bytes|
"""



# The Medium interface allows persisting and retrieving raw binary data.
class Medium(ABC):
    @abstractmethod
    def saveBlob(self, data):
        pass

    @abstractmethod
    def getBlob(self):
        pass

# An in-memory implementation of the Medium interface for testing purposes.
class InMemoryMedium(Medium):
    def __init__(self):
        self.storage = None

    def saveBlob(self, data):
        self.storage = data

    def getBlob(self):
        return self.storage

# Helper functions provided to you
def serialize_int(value: int) -> bytes:
    """Turn an integer into bytes"""
    return value.to_bytes(4, byteorder='big')

def deserialize_int(data: bytes) -> int:
    """Turn bytes back into an integer"""
    return int.from_bytes(data, byteorder='big')

def serialize_str(value: str) -> bytes:
    """Turn a string into bytes"""
    return value.encode('utf-8')

def deserialize_str(data: bytes) -> str:
    """Turn bytes back into a string"""
    return data.decode('utf-8') 

class KVStore:
    def __init__(self, medium):
        self.medium = medium
        self.content = {}

    def put(self, key, value):
        self.content[key] = value

    def get(self, key):
        return self.content.get(key, "")

    """
    Storage structure
    first int (4 bytes) - total number of key/value pair
    key value pair - int(total byte length)|int(key str byte length)|key-bytes|int(value str byte length)|value-bytes|
    """
    def shutdown(self):
        total_count = len(self.content)
        serialized_content = b'' + serialize_int(total_count)

        for key, value in self.content.items():
            key_bytes = serialize_str(key)
            value_bytes = serialize_str(value)

            serialize_key_byte_length = serialize_int(len(key_bytes))
            serialize_value_byte_length = serialize_int(len(value_bytes))

            total_pair_length = len(key_bytes) + len(value_bytes) + len(serialize_key_byte_length) + len(serialize_value_byte_length)
            serialize_total_pair_length = serialize_int(total_pair_length)

            key_value_pair = serialize_key_byte_length + key_bytes + serialize_value_byte_length + value_bytes
            serialized_content += serialize_total_pair_length + key_value_pair

        self.medium.saveBlob(serialized_content)

    def restore(self):
        self.content = {}
        saved_bytes = self.medium.getBlob()

        # first int is total count
        total_count = deserialize_int(saved_bytes[0:4])

        mover = 4
        for _ in range(total_count):
            key_value_pair_size = deserialize_int(saved_bytes[mover: mover + 4])
            mover += 4

            key_value_pair_seriazlied = saved_bytes[mover: mover + key_value_pair_size]
            key, value = self._fetch_key_value(key_value_pair_seriazlied)

            self.content[key] = value

            mover += key_value_pair_size

    def _fetch_key_value(self, key_value_pair_seriazlied):
        key_size = deserialize_int(key_value_pair_seriazlied[0:4])
        key = deserialize_str(key_value_pair_seriazlied[4: 4 + key_size])
        
        value_idx = 4 + key_size
        value_size = deserialize_int(key_value_pair_seriazlied[value_idx:value_idx + 4])
        value = deserialize_str(key_value_pair_seriazlied[value_idx + 4: value_idx + 4 + value_size])

        return (key, value)

# 8. In-mem DB SQL


from typing import List, Optional

from functools import cmp_to_key

class SQLManager:
    def __init__(self, ):
        # table name -> columns as list of string
        self.tables = {}
        # table name -> rows as list of dict
        self.content = {}

    def createTable(self, tableName: str, columnNames: List[str]) -> None:
        self.tables[tableName] = columnNames
        self.content[tableName] = []

    def insert(self, tableName: str, values: List[str]) -> None:
        if tableName not in self.tables:
            raise ValueError(f'table - {tableName} not exists')

        cur_id = len(self.content[tableName])
        row = {column: values[idx] for idx, column in enumerate(self.tables[tableName])}
        row['row_id'] = cur_id

        self.content[tableName].append(row)

    def select(self, tableName: str, conditions: List[List[str]], orderBy: List[str]) -> List[int]:
        if tableName not in self.tables:
            raise ValueError(f'table - {tableName} not exists')

        results = []

        for row in self.content[tableName]:
            meet_condition = True
            for condition in conditions:
                meet_condition = meet_condition and self._process_filter(
                    row[condition[0]], condition[1], condition[2]
                )
            if meet_condition:
                results.append(row)
        
        if orderBy:
            # sorted_res = self._sort_rows(results, orderBy)

            sorted_res = sorted(results, key=lambda x: tuple(x[c] for c in orderBy))
            # if we have is_ascending
            # sorted_res = sorted(results, key=lambda x: tuple(x[c] for c in orderBy), reverse=not is_ascending)
        else:
            sorted_res = sorted(results, key=lambda x: x['row_id'])

        return [r['row_id'] for r in sorted_res]
    
    def _process_filter(self, content, operator, value):
        if self._is_number(content):
            content = float(content)
            value = float(value)

        if operator == '=':
            return content == value
        elif operator == '>':
            return content > value
        elif operator == '<':
            return content < value
        else:
            raise ValueError(f'unsupported ops - {operator}')

    def _is_number(self, value):
        try:
            float(value)
            return True
        except Exception:
            return False

    # def _sort_rows(self, content, orderBy):
    #     def comparator(row_a, row_b):
    #         for col in orderBy:
    #             val_a = row_a[col]
    #             val_b = row_b[col]

    #             if self._is_number(val_a):
    #                 val_a = float(val_a)
    #                 val_b = float(val_b)

    #             # in ascending order, if a > b, return 1
    #             # in descending order, if a < b return -1
    #             if val_a > val_b:
    #                 return 1
    #             elif val_a < val_b:
    #                 return -1
    #         return 0

    #     return sorted(content, key=cmp_to_key(comparator))



# 9. IP address

# count forward
# ip address can be represented as integer as a int has 32 bits
# thus ip -> int
# (blocks[0] << 24) + (blocks[1] << 16) + (blocks[2] << 8) + int(blocks[3])
from typing import List, Optional

class IPv4Iterator:
    def __init__(self, startIp: str):
        self.startNum = self._ip_to_int(startIp)
        self.limit = self._ip_to_int('255.255.255.255')

        self.mover = self.startNum

    def hasNext(self) -> bool:
        return self.mover <= self.limit

    def next(self) -> str:
        cur = self.mover
        self.mover += 1

        return self._int_to_ip(cur)

    # Python iteration style
    def __iter__(self):
    	return self

	def __next__(self):
		if self.mover > self.limit:
			raise StopIteration

		cur = self.mover
        self.mover += 1

        return self._int_to_ip(cur)

    def _ip_to_int(self, ip):
        blocks = [int(b) for b in ip.split('.')]

        return (blocks[0] << 24) + (blocks[1] << 16) + (blocks[2] << 8) + blocks[3]

    def _int_to_ip(self, ip_value):
        return f'{(ip_value >> 24) & 255}.{(ip_value >> 16) & 255}.{(ip_value >> 8) & 255}.{ip_value & 255}'





class CIDRIterator:
    def __init__(self, cidr: str):
        ip, prefix = cidr.split('/')
        start_int_raw = self._ip_to_int(ip)

        mask_length = int(prefix)
        host_bits = 32 - mask_length
        mask_int = 0xFFFFFFFF << (32 - mask_length)
        # remove masked int. 
        # ie, 0.0.0.00000101 where mask is 30
        # start ip is 0.0.0.00000100 where the 01 must be removed
        self.start_int = start_int_raw & mask_int
        self.limit = self.start_int + (2**host_bits) - 1

        self.mover = self.start_int

    def hasNext(self) -> bool:
        return self.mover <= self.limit

    def next(self) -> str:
        cur = self.mover
        self.mover += 1

        return self._int_to_ip(cur)

    def _ip_to_int(self, ip):
        blocks = [int(b) for b in ip.split('.')]

        return (blocks[0] << 24) + (blocks[1] << 16) + (blocks[2] << 8) + blocks[3]

    def _int_to_ip(self, ip_value):
        return f'{(ip_value >> 24) & 255}.{(ip_value >> 16) & 255}.{(ip_value >> 8) & 255}.{ip_value & 255}'


# 10. mem allocate
# O(N) - first-fit
class Allocator:
    class Block:
        def __init__(self, size: int, index: int, is_free: bool=True, next_ptr=None, prev_ptr=None):
            self.size = size
            self.index = index
            self.is_free = is_free
            self.next = next_ptr
            self.prev = prev_ptr

            # self.mID = mID

    def __init__(self, n: int):
        mem = self.Block(n, 0)
        dummy_head = self.Block(0, 0, False)
        dummy_head.next = mem
        mem.prev = dummy_head

        self.blocks = dummy_head
        self.allocated = defaultdict(set)

    def print_block(self, command):
        pointer = self.blocks
        print(f'========={command}===============')
        while pointer:
            print(f'size - {pointer.size} | index - {pointer.index} | free - {pointer.is_free}')
            pointer = pointer.next
        # print(self.allocated)
        
    def allocate(self, size: int, mID: int) -> int:
        # go through blocks find left most consecutive block with size > required size
        # mark in allocated
        # if block size > required size, put remain free block back to blocks

        pointer = self.blocks
        while pointer and (not pointer.is_free or pointer.size < size):
            pointer = pointer.next
        
        if not pointer:
            # print(f'alloc size-{size} mID-{mID} but not found')
            return -1
        
        if pointer.size == size:
            self.allocated[mID].add(pointer)
            pointer.is_free = False
            # pointer.mID = mID

            # self.print_block(f'alloc size-{size} mID-{mID}')

            return pointer.index
        else:
            # break the pointer into smaller ones
            remain_block = self.Block(pointer.size - size, pointer.index + size, True, pointer.next, None)
            allocated_block = self.Block(size, pointer.index, False, remain_block, pointer.prev)
            remain_block.prev = allocated_block

            if pointer.prev != None:
                pointer.prev.next = allocated_block
            if pointer.next != None:
                pointer.next.prev = remain_block

            self.allocated[mID].add(allocated_block)
            # self.print_block(f'alloc size-{size} mID-{mID}')
        
            return allocated_block.index

    def freeMemory(self, mID: int) -> int:
        if mID not in self.allocated:
            # print(f'free mID-{mID} but not exists')
            return 0

        released = 0
        for block in self.allocated[mID]:
            cur_block = block
            released += cur_block.size

            cur_block.is_free = True
            # cur_block.mID = -1
            # merge previous node
            if cur_block.prev and cur_block.prev.is_free:
                cur_block.size = cur_block.size + cur_block.prev.size
                cur_block.index = cur_block.prev.index

                if cur_block.prev.prev:
                    cur_block.prev.prev.next = cur_block

                cur_block.prev = cur_block.prev.prev
                
            # merge next node
            if cur_block.next and cur_block.next.is_free:
                cur_block.size = cur_block.size + cur_block.next.size
                
                if cur_block.next.next:
                    cur_block.next.next.prev = cur_block
                
                cur_block.next = cur_block.next.next
                    

        del self.allocated[mID]
        # self.print_block(f'free mID-{mID}')

        return released


"""
If we just use double linked-list to manage the lookup of blocks
for allocate operation will be O(N) as we need to loop through all blocks
We can keep a sorted map where key is the size and value is the list of blocks of that size
In python we can use SortedDict, internally it keep a SortedList of keys which is optimized 
like a tree to minimize the element shifting

from sortedcontainers import SortedDict
sortedcontainers is NOT in original python lib

WE NEED pip install sortedcontainers


double linked-list manage mem block [break, release]
a map manage index to block mapping
a sortedDict (treemap in java), manage current available blocks
key - block size
value - set of blocks of this size

Time complexity: 
allocate - O(logN) -> 1 binary search, 1 insert into sortedDict
free - O(logN) -> 1 insert into sortedDict, 1-3 delete from sortedDict
"""


from sortedcontainers import SortedDict
from collections import defaultdict

import bisect

class Block:
	def __init__(self, size: int, index: int, is_free: bool=True, next_ptr=None, prev_ptr=None):
		self.size = size
		self.index = index
		self.is_free = is_free
		self.next = next_ptr
		self.prev = prev_ptr
	
	def __repr__(self):
		return f'size-{self.size} | index-{self.index} | isFree-{self.is_free}'

class BlockList:
	def __init__(self, block):
		self.dummy_head = Block(0, 0, False)
		self.dummy_tail = Block(0, 0, False)

		self.dummy_head.next = block
		block.prev = self.dummy_head
		self.dummy_tail.prev = block
		block.next = self.dummy_tail
	
	# this might break block
	# return a tuple of ptr (allocated_block, free_block)
	def allocate_block(self, block_ptr, size):
		if block_ptr.size < size:
			raise ValueError(f'invalid allocation - block size {block_ptr.size}, requested - {size}')

		remain_size = block_ptr.size - size
		if not remain_size:
			block_ptr.is_free = False
			return (block_ptr, None)

		allocated_block = Block(size, block_ptr.index, False)
		remain_block = Block(remain_size, block_ptr.index + size, True)

		# connect blocks
		allocated_block.prev = block_ptr.prev
		allocated_block.next = remain_block
		remain_block.prev = allocated_block
		remain_block.next = block_ptr.next

		block_ptr.next.prev = remain_block
		block_ptr.prev.next = allocated_block

		return (allocated_block, remain_block)

	# this might merge blocks
	# return a tuple of ptr (merged_block, [discarded_blocks])
	def free_block(self, block_ptr):
		merged_block = Block(block_ptr.size, block_ptr.index, True)
		discarded_blocks = [block_ptr]

		merged_block.prev = block_ptr.prev
		merged_block.next = block_ptr.next
		block_ptr.prev.next = merged_block
		block_ptr.next.prev = merged_block

		# merge prev
		if block_ptr.prev.is_free:
			prev_block = block_ptr.prev
			merged_block.size += prev_block.size
			merged_block.index = prev_block.index
			discarded_blocks.append(prev_block)

			# connect blocks
			merged_block.prev = prev_block.prev
			prev_block.prev.next = merged_block

		# merge next
		if block_ptr.next.is_free:
			next_block = block_ptr.next
			merged_block.size += next_block.size
			# merged_block.index not changed since it is smaller
			
			discarded_blocks.append(next_block)

			# connect blocks
			merged_block.next = next_block.next
			next_block.next.prev = merged_block
		
		return (merged_block, discarded_blocks)


class Allocator:
	"""
	double linked-list manage mem block [break, release]
	a map manage index to block mapping
	a sortedDict (treemap in java), manage current available blocks
	key - block size
	value - set of blocks of this size
	"""
	def __init__(self, n: int):
		self.idx_block_map = {}
		self.size_block_map = SortedDict()

		block = Block(n, 0, True)
		self.block_list = BlockList(block)

		self.idx_block_map[0] = block

		self.size_block_map[n] = set()
		self.size_block_map[n].add(block)

	def _add_block_to_size_map(self, block):
		if block.size not in self.size_block_map:
			self.size_block_map[block.size] = set()
		self.size_block_map[block.size].add(block)

	def _discard_block_from_size_map(self, block):
		# if block not in the size_block_map
		if block.size not in self.size_block_map:
			return

		self.size_block_map[block.size].discard(block)

		if not self.size_block_map[block.size]:
			del self.size_block_map[block.size]

	def allocate(self, size: int) -> int:
		# find the block if there is one - by binary search (bisect)
		# allocate from blockList
		# update size_block_map
		# update idx_block_map
		block_sizes = self.size_block_map.keys()
		found_idx = bisect.bisect_left(block_sizes, size)

		if found_idx >= len(block_sizes):
			return -1
		
		matched_size = block_sizes[found_idx]
		found_block = self.size_block_map[matched_size].pop()
		allocated_block, remain_block = self.block_list.allocate_block(found_block, size)

		# after allocating, the found_block can be breakdown into small one
		if remain_block:
			self._add_block_to_size_map(remain_block)
			self.idx_block_map[remain_block.index] = remain_block

		self.idx_block_map[allocated_block.index] = allocated_block
		if not self.size_block_map[matched_size]:
			del self.size_block_map[matched_size]

		#	 print('======================')
		#	 print(f'---------------allocate mem - size-{size}| mID-{mID}')
		#	 print(f'-----------------allocated-{allocated_block} --- remain_block-{remain_block}')
		#	 print(f'-----------------size_block-{self.size_block_map} --- idx_block_map-{self.idx_block_map}')
		return allocated_block.index


	def free(self, address: int, size: int) -> int:
		# if address < 0 or address >= self.capacity:
        #     raise ValueError(f"Invalid address: {address}")

        # if size <= 0:
        #     raise ValueError("Size must be positive")

		if address not in self.idx_block_map or self.idx_block_map[address].is_free or self.idx_block_map[address].size != size:
			raise ValueError('invalid free requested')

		block = self.idx_block_map[address]

		merged_block, discarded_blocks = self.block_list.free_block(block)

		# discard first in case later add block with same indx
		for dis_b in discarded_blocks:
			# notice the block we are freeing is also in the discarded blocks
			# this block is not in the size map as it is not available
			# we can
			# 1. let _discard_block_from_size_map deal with it
			# 2. skip it here
			self._discard_block_from_size_map(dis_b)
			del self.idx_block_map[dis_b.index]

		self._add_block_to_size_map(merged_block)
		self.idx_block_map[merged_block.index] = merged_block

		print('======================')
		print(f'---------------free mem - add-{address} | size-{size}')
		print(f'size map - {self.size_block_map}')
		print(f'index map - {self.idx_block_map}')
		#	 print(f'----------merged_block-{merged_block} --- discarded_blocks - {discarded_blocks}')


# 11. monster battle

class Monster:
	def __init__(self, name, health, attack_damage):
		self.name = name
		self.health = health
		self.attack_damage = attack_damage

	def is_alive(self):
		return self.health > 0

	def take_damage(self, damage):
		self.health -= damage


class Team:
	def __init__(self, name, monsters):
		self.monsters = monsters
		self.name = name
		self.cur_monster_idx = 0

	def first_alive(self):
		self._move_index()
		if self.cur_monster_idx >= len(self.monsters):
			return None

		return self.monsters[self.cur_monster_idx]

	def is_defeated(self):
		self._move_index()

		return self.cur_monster_idx >= len(self.monsters)

	def _move_index(self):
		while self.cur_monster_idx < len(self.monsters) and not self.monsters[self.cur_monster_idx].is_alive():
			self.cur_monster_idx += 1



class Battle:
	def __init__(self):
		pass

	def battle_simulator(self, team_a, team_b):
		cur_attacker = team_a
		cur_defender = team_b

		events = []

		start_message = f'battle begin - team {team_a.name} fights team {team_b.name}'
		events.append(start_message)

		while not team_a.is_defeated() and not team_b.is_defeated():
			attack_monster = cur_attacker.first_alive()
			defend_monster = cur_defender.first_alive()

			defend_monster.take_damage(attack_monster.attack_damage)

			message = f'{attack_monster.name} attacks {defend_monster.name} with {attack_monster.attack_damage} damage.'
			if defend_monster.is_alive():
				result_message = f'{defend_monster.name} has {defend_monster.health} health remain'
			else:
				result_message = f'{defend_monster.name} is eliminated'

			events.append(message + result_message)

			cur_attacker, cur_defender = cur_defender, cur_attacker

		defeated_team = team_a if team_a.is_defeated() else team_b
		winning_team = team_a if not team_a.is_defeated() else team_b
		
		final_message = f'{winning_team.name} wins and {defeated_team.name} defeated'

		events.append(final_message)

		return events

# with elemental type

from enum import Enum

class ElementalType(Enum):
	FIRE = 'fire'
	GRASS = 'grass'
	WATER = 'water'
	ELECTRIC = 'electric'


# attacker - defender -> damage ratio
DAMAGE_RATIO_CHART = {
	(ElementalType.FIRE, ElementalType.GRASS): 2.0,
	(ElementalType.FIRE, ElementalType.WATER): 0.5,
	(ElementalType.WATER, ElementalType.FIRE): 2.0,
	(ElementalType.WATER, ElementalType.GRASS): 0.5,
	(ElementalType.GRASS, ElementalType.WATER): 2.0,
	(ElementalType.GRASS, ElementalType.FIRE): 0.5,
	(ElementalType.ELECTRIC, ElementalType.WATER): 2.0,
}


class Monster:
	def __init__(self, name, health, attack_damage, elemental_type):
		self.name = name
		self.health = health
		self.attack_damage = attack_damage
		self.type = elemental_type

	def is_alive(self):
		return self.health > 0

	def take_damage(self, attacker):
		attack_ele = attacker.type
		damage = attacker.attack_damage
		elemental_tuple = (attack_ele, self.type)

		ratio = DAMAGE_RATIO_CHART.get(elemental_tuple, 1.0)
		final_damage = int(damage * ratio)

		self.health -= final_damage

		return final_damage


class Team:
	def __init__(self, name, monsters):
		self.monsters = monsters
		self.name = name
		self.cur_monster_idx = 0

	def first_alive(self):
		self._move_index()
		if self.cur_monster_idx >= len(self.monsters):
			return None

		return self.monsters[self.cur_monster_idx]

	def is_defeated(self):
		self._move_index()

		return self.cur_monster_idx >= len(self.monsters)

	def _move_index(self):
		while self.cur_monster_idx < len(self.monsters) and not self.monsters[self.cur_monster_idx].is_alive():
			self.cur_monster_idx += 1



class Battle:
	def __init__(self):
		pass

	def battle_simulator(self, team_a, team_b):
		cur_attacker = team_a
		cur_defender = team_b

		events = []

		start_message = f'battle begin - team {team_a.name} fights team {team_b.name}'
		events.append(start_message)

		while not team_a.is_defeated() and not team_b.is_defeated():
			attack_monster = cur_attacker.first_alive()
			defend_monster = cur_defender.first_alive()

			final_damage = defend_monster.take_damage(attack_monster)

			message = f'{attack_monster.name} attacks {defend_monster.name} with {final_damage} damage.'
			if defend_monster.is_alive():
				result_message = f'{defend_monster.name} has {defend_monster.health} health remain'
			else:
				result_message = f'{defend_monster.name} is eliminated'

			events.append(message + result_message)

			cur_attacker, cur_defender = cur_defender, cur_attacker

		defeated_team = team_a if team_a.is_defeated() else team_b
		winning_team = team_a if not team_a.is_defeated() else team_b
		
		final_message = f'{winning_team.name} wins and {defeated_team.name} defeated'

		events.append(final_message)

		return events


# 12. sharding
"""
This is a line sweeping and overlapping problem.

Use a min heap to record current overlapped shard at any point
In the min heap, we push the end of shards in here. 

1. When meet a new shard, pop heap until heap.peek is >= start
Thus for any start of a shard, the size of heap is the count of overlap
(since we sort the shards by start and end, it is guarantee the 
shards have ends in the heap cover current start)
2. if heap size >= limit, we keep popping until size < limit
3. the last popped end + 1 is where the current start need to be


Time complexity: O(NlgN)
"""

from queue import PriorityQueue

class Shard:
    def __init__(self, id, start, end):
        self.id = id
        self.start = start
        self.end = end

class Solution:
    def rebalance(self, limit: int, input: List[str]) -> List[str]:
        shards = []

        for raw_shard in input:
            s_id, start, end = raw_shard.split(':')
            shards.append(Shard(s_id, int(start), int(end)))
        shards.sort(key=lambda x: (x.start, x.end))
        
        min_heap = PriorityQueue()
        results = []

        for shard in shards:
            s_id, start, end = shard.id, shard.start, shard.end
            # check overlap
            # 1. pop out shards ended before start
            while not min_heap.empty() and min_heap.queue[0] < start:
                min_heap.get()

            # 2. check overlap count (heap.qsize)
            last_pop = None
            while min_heap.qsize() >= limit:
                last_pop = min_heap.get()
            # 3. assign new start if needed
            if last_pop:
                start = last_pop + 1

            # drop if needed
            if start > end:
                continue
            
            # extend previous shard end if needed
            prev_shard = results[-1] if results else None
            if prev_shard and prev_shard.end < start - 1:
                prev_shard.end = start - 1

            # add to result and heap
            results.append(Shard(s_id, start, end))
            min_heap.put(end)

        return [f'{s.id}:{s.start}:{s.end}' for s in results]


# 13.
# 要求实现cd(current_dir, new dir), 返回最终的path, 比如：
# cd(/foo/bar, baz) = /foo/bar/baz
# cd(/foo/../, ./baz) = /baz
# cd(/, foo/bar/../../baz) = /baz
# cd(/, ..) = Null
# 第二问可不可以加上对～符号也就是home directory的支持
# 完成以后难度加大，第三个参数是soft link的dictionary，比如：
# cd(/foo/bar, baz, {/foo/bar: /abc}) = /abc/baz
# cd(/foo/bar, baz, {/foo/bar: /abc, /abc: /bcd, /bcd/baz: /xyz}) = /xyz
# dictionary 里有可能有短匹配和长匹配，应该先匹配长的(more specific), 比如：
# cd(/foo/bar, baz, {/foo/bar: /abc, /foo/bar/baz: /xyz}) = /xyz
# 要判断dictionary里是否有循环

'USE trie tree traverse through the symlink build the tree'
'each walk through will the O(n) n as length of input path'



from typing import Union, List

def cd(current_dir: str, new_dir: str) -> str:
	return simplify_path(current_dir + '/' + new_dir)

def simplify_path(path: str) -> str:
	if not path:
		return '/'

	path_stack = []
	path_tokens = path.split('/')

	for token in path_tokens:
		if token == '..' and path_stack:
			path_stack.pop()
		elif not token or token == '.':
			continue
		elif token == '..' and not path_stack:
			return 'NULL'
		else:
			path_stack.append(token)

	return '/' + '/'.join(path_stack)


class TrieNode:
	def __init__(self, path: str):
		self.path = path
		self.link_path = None
		self.children = {}

def build_trie(symlinks: dict) -> TrieNode:
	root = TrieNode('')

	for symlink_path, link in symlinks.items():
		insert_path(symlink_path, root, link)
	return root


def insert_path(path: str, root: TrieNode, symlink: str):
	path_tokens = path.split('/')
	mover = root

	for token in path_tokens:
		if token not in mover.children:
			mover.children[token] = TrieNode(token)
		
		mover = mover.children[token]

	mover.link_path = symlink.split('/')

def convert_path(path_tokens: List[str], trie_root: TrieNode) -> List[str]: 
	mover = trie_root

	cur_replaced = []
	cur_index = -1

	for index, token in enumerate(path_tokens):
		if token not in mover.children:
			break

		mover = mover.children[token]
		if mover.link_path:
			# print(f"matched - {index} - {token} - {mover.link_path}")
			cur_replaced = mover.link_path
			cur_index = index + 1

	if not cur_replaced:
		return []

	if cur_index == len(path_tokens):
		suffix = []
	else:
		suffix = path_tokens[cur_index:]


	return cur_replaced + suffix



def cd_symlinks(current_dir: str, new_dir: str, symlinks: dict) -> str:
	path = simplify_path(current_dir + '/' + new_dir)

	if path == 'NULL':
		return path

	trie_root = build_trie(symlinks)
	result_path = path.split('/')
	visited = set('/'.join(result_path))

	while result_path:
		converted = convert_path(result_path, trie_root)

		if '/'.join(converted) in visited:
			raise Exception("loop detected in symlink")
		if not converted:
			break

		visited.add('/'.join(result_path))
		result_path = converted

	return '/'.join(result_path)


# 14. version dependency
"""
for question 1 - binary search
for question 2 - binary search on each group (major, minor, patch)
Time complexity - O(nlgn)
is_supported api call - O(lgMajor + lgMinor + lgPatch)
"""

from collections import defaultdict


def parse_version(version: str) -> tuple:
    """
    Parse version string into comparable tuple.
    "103.003.02" -> (103, 3, 2)
    """
    raw_parts = version.split('.')
    return tuple(int(part) for part in raw_parts)

def find_earliest_supported(versions: list, is_supported) -> str:
    """
    Part 1: Find earliest version that supports the feature.
    Assumes support is monotonic (once True, stays True).

    Args:
        versions: List of version strings
        is_supported: Function that takes a version string, returns bool

    Returns:
        Earliest supporting version string, or None
    """
    converted_vers = sorted([(parse_version(v), v) for v in versions])
    result = _binary_search_first_match(converted_vers, is_supported)

    if result:
        return converted_vers[result][1]
    else:
        return None

def _binary_search_first_match(versions, is_supported):
    left, right = 0, len(versions) - 1

    result = None
    while left <= right:
        mid = (left + right) // 2
        if is_supported(versions[mid][1]):
            result = mid
            right = mid - 1
        else:
            left = mid + 1
    
    return result


def find_earliest_with_regressions(versions: list, is_supported) -> str:
    """
    Part 2: Find earliest version when support can regress.
    Must check every version since support is non-monotonic.

    Args:
        versions: List of version strings
        is_supported: Function that takes a version string, returns bool

    Returns:
        Earliest supporting version string, or None
    """
    converted_vers = sorted([(parse_version(v), v) for v in versions])

    for v in converted_vers:
        if is_supported(v[1]):
            return v[1]
    return None


def find_earliest_optimized(versions: list, is_supported) -> str:
    """
    Part 3: Find earliest version with minimal API calls.
    Uses hierarchical binary search on major -> minor -> patch.

    Assumption: the latest version in each major/minor group reliably
    indicates whether support exists in that group (monotonic at
    group boundaries).

    Args:
        versions: List of version strings
        is_supported: Function that takes a version string, returns bool

    Returns:
        Earliest supporting version string, or None
    """
    converted_vers = sorted([(parse_version(v), v) for v in versions])

    # group majors and find first major
    major_ranges = group_versions(converted_vers, 0, len(converted_vers) - 1, 0)
    first_major_idx = _binary_search_first_match_ranges(converted_vers, major_ranges, is_supported)

    if first_major_idx is None:
        return None
    first_major = major_ranges[first_major_idx]
    
    # group minor and find first minor
    minor_ranges = group_versions(converted_vers, first_major[0], first_major[1], 1)
    first_minor_idx = _binary_search_first_match_ranges(converted_vers, minor_ranges, is_supported)
    first_minor = minor_ranges[first_minor_idx]

    # find first patch
    patch_idx = _binary_search_first_match_patch(converted_vers, first_minor[0], first_minor[1], is_supported)

    return converted_vers[patch_idx][1]

# return [(start-index, end-index)]
def group_versions(converted_versions, start, end, version_idx):
    result = []

    if not converted_versions:
        return result
    cur_ver = converted_versions[0][0][version_idx]
    start_idx = start

    for idx in range(start, end + 1):
        conv_v, _ = converted_versions[idx]
        if conv_v[version_idx] != cur_ver:
            result.append((start_idx, idx - 1))
            start_idx = idx
            cur_ver = conv_v[version_idx]

    result.append((start_idx, end))

    return result

def _binary_search_first_match_ranges(versions, ranges, is_supported):
    left, right = 0, len(ranges) - 1

    result = None
    while left <= right:
        mid = (left + right) // 2
        # for version search always check the last version
        mid_idx = ranges[mid][1]
        if is_supported(versions[mid_idx][1]):
            result = mid
            right = mid - 1
        else:
            left = mid + 1
    
    return result 

def _binary_search_first_match_patch(versions, start, end, is_supported):
    left, right = start, end
    result = None
    while left <= right:
        mid = (left + right) // 2
        if is_supported(versions[mid][1]):
            result = mid
            right = mid - 1
        else:
            left = mid + 1
    
    return result 

# 15. resume iterator

from abc import ABC, abstractmethod
from typing import Any, Dict


class ResumableIterator(ABC):
    """Abstract base class for iterators that support pause/resume."""

    @abstractmethod
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Capture current position as a serializable dictionary."""
        pass

    @abstractmethod
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore to a previously saved state."""
        pass


class ResumableListIterator(ResumableIterator):
    """1D resumable iterator over a list."""

    def __init__(self, items: list):
        self.items = items
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.items):
            raise StopIteration
        result = self.items[self.index]
        self.index += 1

        return result

    def get_state(self) -> Dict[str, Any]:
        return {
            'index': self.index
        }

    def set_state(self, state: Dict[str, Any]) -> None:
        self.index = state['index']


class Resumable2DIterator(ResumableIterator):
    """2D resumable iterator over a list of lists."""

    def __init__(self, items: list):
        self.items = items
        self.outer_index = 0
        self.inner_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.outer_index < len(self.items):
            cur_row = self.items[self.outer_index]
            if self.inner_index >= len(cur_row):
                self.outer_index += 1
                self.inner_index = 0
                continue
            result = cur_row[self.inner_index]
            self.inner_index += 1

            return result
        
        raise StopIteration


    def get_state(self) -> Dict[str, Any]:
        return {
            'outer_index': self.outer_index,
            'inner_index': self.inner_index,
        }

    def set_state(self, state: Dict[str, Any]) -> None:
        self.outer_index = state['outer_index']
        self.inner_index = state['inner_index']


class Resumable3DIterator(ResumableIterator):
    """3D resumable iterator over a list of lists of lists."""

    def __init__(self, items: list):
        self.items = items
        self.outer_index = 0
        self.middle_index = 0
        self.inner_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.outer_index < len(self.items):
            outer_row = self.items[self.outer_index]
            if self.middle_index >= len(outer_row):
                self.outer_index += 1
                self.middle_index = 0
                self.inner_index = 0
                continue
            
            middle_row = outer_row[self.middle_index]
            if self.inner_index >= len(middle_row):
                self.middle_index += 1
                self.inner_index = 0
                continue

            result = middle_row[self.inner_index]
            self.inner_index += 1

            return result
        
        raise StopIteration

    def get_state(self) -> Dict[str, Any]:
        return {
            'outer_index': self.outer_index,
            'inner_index': self.inner_index,
            'middle_index': self.middle_index
        }

    def set_state(self, state: Dict[str, Any]) -> None:
        self.outer_index = state['outer_index']
        self.middle_index = state['middle_index']
        self.inner_index = state['inner_index']


# 16. 
