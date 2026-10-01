from collections import defaultdict

'''
Whenever use names, always do name.lower()! unless store in recipes dict
'''
class ReciptManagerLvl1:
	def __init__(self):
		self.recipes = defaultdict(dict)
		self.cur_names = set()

	def add_recipe(self, recipe_id, name, ingredients):
		if recipe_id in self.recipes or name.lower() in self.cur_names:
			return False

		self.recipes[recipe_id] = {
			"id": recipe_id,
			"name": name,
			"ingredients": ingredients
		}
		self.cur_names.add(name.lower())

		return True

	def get_recipe(self, recipe_id):
		if recipe_id not in self.recipes:
			return None

		return self.recipes[recipe_id]

	def update_recipe(self, recipe_id, name, ingredients):
		# print("UPDATE")
		# print(f"{recipe_id} - {name}")
		# print(self.recipes)
		if recipe_id not in self.recipes:
			return False

		# if the name is used by other recipe
		if name.lower() != self.recipes[recipe_id]["name"].lower() and name.lower() in self.cur_names:
			return False

		# update name set
		if name.lower() != self.recipes[recipe_id]["name"].lower():
			self.cur_names.add(name.lower())
			self.cur_names.remove(self.recipes[recipe_id]["name"].lower())
		
		self.recipes[recipe_id] = {
			"id": recipe_id,
			"name": name,
			"ingredients": ingredients
		}

		return True

	def delete_recipe(self, recipe_id):
		if recipe_id not in self.recipes:
			return False

		deleted = self.recipes[recipe_id]

		del self.recipes[recipe_id]
		self.cur_names.remove(deleted["name"].lower())

		return True

# ==================================================================================
# ==================================================================================
# ==================================================================================

'''
Whenever use names, always do name.lower()! unless store in recipes dict
'''
class ReciptManagerLvl2:
	def __init__(self):
		self.recipes = defaultdict(dict)
		self.cur_names = set()

	def search_recipes(self, query):
		find_recipes = []

		for recipe in self.recipes.values():
			if query.lower() in recipe["name"].lower():
				find_recipes.append(recipe)

		return self._sort_recipes(find_recipes)

	def get_all_recipes(self):
		return self._sort_recipes(self.recipes.values())

	def _sort_recipes(self, recipes):
		return sorted(recipes, key=lambda x: (len(x["ingredients"]), x["id"]))

	def add_recipe(self, recipe_id, name, ingredients):
		if recipe_id in self.recipes or name.lower() in self.cur_names:
			return False

		self.recipes[recipe_id] = {
			"id": recipe_id,
			"name": name,
			"ingredients": ingredients
		}
		self.cur_names.add(name.lower())

		return True

	def get_recipe(self, recipe_id):
		if recipe_id not in self.recipes:
			return None

		return self.recipes[recipe_id]

	def update_recipe(self, recipe_id, name, ingredients):
		# print("UPDATE")
		# print(f"{recipe_id} - {name}")
		# print(self.recipes)
		if recipe_id not in self.recipes:
			return False

		# if the name is used by other recipe
		if name.lower() != self.recipes[recipe_id]["name"].lower() and name.lower() in self.cur_names:
			return False

		# update name set
		if name.lower() != self.recipes[recipe_id]["name"].lower():
			self.cur_names.add(name.lower())
			self.cur_names.remove(self.recipes[recipe_id]["name"].lower())
		
		self.recipes[recipe_id] = {
			"id": recipe_id,
			"name": name,
			"ingredients": ingredients
		}

		return True

	def delete_recipe(self, recipe_id):
		if recipe_id not in self.recipes:
			return False

		deleted = self.recipes[recipe_id]

		del self.recipes[recipe_id]
		self.cur_names.remove(deleted["name"].lower())

		return True

# ==================================================================================
# ==================================================================================
# ==================================================================================

'''
Whenever use names, always do name.lower()! unless store in recipes dict
'''
class ReciptManagerLvl3:
	def __init__(self):
		self.recipes = defaultdict(dict)
		self.users = defaultdict(str)
		self.cur_names = set()

	def add_user(self, user_id, username):
		if user_id in self.users:
			return False

		self.users[user_id] = username
		return True

	def edit_recipe(self, user_id, recipe_id, name, ingredients):
		if user_id not in self.users:
			return False

		return self.update_recipe(recipe_id, name, ingredients)

	def search_recipes(self, query):
		find_recipes = []

		for recipe in self.recipes.values():
			if query.lower() in recipe["name"].lower():
				find_recipes.append(recipe)

		return self._sort_recipes(find_recipes)

	def get_all_recipes(self):
		return self._sort_recipes(self.recipes.values())

	def _sort_recipes(self, recipes):
		return sorted(recipes, key=lambda x: (len(x["ingredients"]), x["id"]))

	def add_recipe(self, recipe_id, name, ingredients):
		if recipe_id in self.recipes or name.lower() in self.cur_names:
			return False

		self.recipes[recipe_id] = {
			"id": recipe_id,
			"name": name,
			"ingredients": ingredients
		}
		self.cur_names.add(name.lower())

		return True

	def get_recipe(self, recipe_id):
		if recipe_id not in self.recipes:
			return None

		return self.recipes[recipe_id]

	def update_recipe(self, recipe_id, name, ingredients):
		# print("UPDATE")
		# print(f"{recipe_id} - {name}")
		# print(self.recipes)
		if recipe_id not in self.recipes:
			return False

		# if the name is used by other recipe
		if name.lower() != self.recipes[recipe_id]["name"].lower() and name.lower() in self.cur_names:
			return False

		# update name set
		if name.lower() != self.recipes[recipe_id]["name"].lower():
			self.cur_names.add(name.lower())
			self.cur_names.remove(self.recipes[recipe_id]["name"].lower())
		
		self.recipes[recipe_id] = {
			"id": recipe_id,
			"name": name,
			"ingredients": ingredients
		}

		return True

	def delete_recipe(self, recipe_id):
		if recipe_id not in self.recipes:
			return False

		deleted = self.recipes[recipe_id]

		del self.recipes[recipe_id]
		self.cur_names.remove(deleted["name"].lower())

		return True

# ==================================================================================
# ==================================================================================
# ==================================================================================

'''
Whenever use names, always do name.lower()! unless store in recipes dict
'''
import copy

class ReciptManagerLvl4:
	def __init__(self):
		self.recipes = defaultdict(dict)
		self.users = defaultdict(str)
		self.cur_names = set()
		self.history = defaultdict(list)

	def get_recipe_history(self, recipe_id):
		if recipe_id not in self.history:
			return None

		return self.history[recipe_id]

	def rollback_recipe(self, user_id, recipe_id, version):
		if user_id not in self.users or recipe_id not in self.history or version > len(self.history[recipe_id]):
			return False
		history_recipe = self.history[recipe_id][version - 1] 
		
		if recipe_id in self.recipes:
			cur_recipe = self.recipes[recipe_id]
			# if history recipe name is used by another recipe
			if cur_recipe["name"].lower() != history_recipe["name"].lower() and history_recipe["name"].lower() in self.cur_names:
				return False
			self.cur_names.remove(cur_recipe["name"].lower())
		
		self.cur_names.add(history_recipe["name"].lower())
		self.recipes[recipe_id] = copy.deepcopy(history_recipe)

		self._update_history(recipe_id, history_recipe)

		return True


	def _update_history(self, recipe_id, content):
		self.history[recipe_id].append(content)

	def add_user(self, user_id, username):
		if user_id in self.users:
			return False

		self.users[user_id] = username
		return True

	def edit_recipe(self, user_id, recipe_id, name, ingredients):
		if user_id not in self.users:
			return False

		return self.update_recipe(recipe_id, name, ingredients)

	def search_recipes(self, query):
		find_recipes = []

		for recipe in self.recipes.values():
			if query.lower() in recipe["name"].lower():
				find_recipes.append(recipe)

		return self._sort_recipes(find_recipes)

	def get_all_recipes(self):
		return self._sort_recipes(self.recipes.values())

	def _sort_recipes(self, recipes):
		return sorted(recipes, key=lambda x: (len(x["ingredients"]), x["id"]))

	def add_recipe(self, recipe_id, name, ingredients):
		if recipe_id in self.recipes or name.lower() in self.cur_names:
			return False

		content = {
			"id": recipe_id,
			"name": name,
			"ingredients": ingredients
		}

		self.recipes[recipe_id] = content
		self.cur_names.add(name.lower())
		self._update_history(recipe_id, content)

		return True

	def get_recipe(self, recipe_id):
		if recipe_id not in self.recipes:
			return None

		return self.recipes[recipe_id]

	def update_recipe(self, recipe_id, name, ingredients):
		if recipe_id not in self.recipes:
			return False

		# if the name is used by other recipe
		if name.lower() != self.recipes[recipe_id]["name"].lower() and name.lower() in self.cur_names:
			return False

		# update name set
		if name.lower() != self.recipes[recipe_id]["name"].lower():
			self.cur_names.add(name.lower())
			self.cur_names.remove(self.recipes[recipe_id]["name"].lower())
		
		content = {
			"id": recipe_id,
			"name": name,
			"ingredients": ingredients
		}

		self.recipes[recipe_id] = content
		self._update_history(recipe_id, content)

		return True

	def delete_recipe(self, recipe_id):
		if recipe_id not in self.recipes:
			return False

		deleted = self.recipes[recipe_id]

		del self.recipes[recipe_id]
		self.cur_names.remove(deleted["name"].lower())

		return True

class Test:
	def __init__(self):
		pass

	def test_lvl1(self):
		print("------------------------------------------")
		print("------------Run test level 1 A------------------")
		manager = ReciptManagerLvl1()

		results = []

		results.append(manager.add_recipe("r1", "Pasta Carbonara", ["egg", "cheese", "bacon"]))
		results.append(manager.add_recipe("r2", "Salad", ["lettuce"]))
		results.append(manager.add_recipe("r3", "pasta carbonara", ["x"]))  # name conflict (ignore case)
		results.append(manager.add_recipe("r1", "Soup", ["water"]))         # id conflict

		results.append(manager.get_recipe("r1"))
		results.append(manager.get_recipe("missing"))

		results.append(manager.update_recipe("r1", "PASTA CARBONARA", ["egg"]))   # same recipe keeps its own name (case-insensitive)
		results.append(manager.update_recipe("r1", "Salad", ["egg"]))             # conflict with r2's name
		results.append(manager.update_recipe("missing", "New", []))               # missing id

		results.append(manager.get_recipe("r1"))

		results.append(manager.delete_recipe("r2"))
		results.append(manager.delete_recipe("r2"))  # already deleted

		results.append(manager.add_recipe("r4", "salad", []))  # now ok after delete; empty ingredients ok
		results.append(manager.get_recipe("r4"))

		expected = [
		  True,
		  True,
		  False,
		  False,
		  {"id": "r1", "name": "Pasta Carbonara", "ingredients": ["egg", "cheese", "bacon"]},
		  None,
		  True,
		  False,
		  False,
		  {"id": "r1", "name": "PASTA CARBONARA", "ingredients": ["egg"]},
		  True,
		  False,
		  True,
		  {"id": "r4", "name": "salad", "ingredients": []}
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 1 B------------------")

		manager = ReciptManagerLvl1()

		results = []

		results.append(manager.add_recipe("a", "Tea", ["water"]))
		results.append(manager.add_recipe("b", "Coffee", ["water", "beans"]))
		results.append(manager.update_recipe("a", "Matcha", ["matcha", "water"]))  # rename ok
		results.append(manager.get_recipe("a"))
		results.append(manager.delete_recipe("a"))
		results.append(manager.get_recipe("a"))
		results.append(manager.update_recipe("a", "Tea", ["water"]))              # can't update missing
		results.append(manager.delete_recipe("missing"))

		expected = [
		  True,
		  True,
		  True,
		  {"id": "a", "name": "Matcha", "ingredients": ["matcha", "water"]},
		  True,
		  None,
		  False,
		  False
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

	def test_lvl2(self):
		print("------------------------------------------")
		print("------------Run test level 2 A------------------")
		manager = ReciptManagerLvl2()

		results = []

		results.append(manager.add_recipe("r2", "Chicken Soup", ["chicken", "water", "salt"]))  # 3
		results.append(manager.add_recipe("r1", "Soup Dumplings", ["pork"]))                   # 1
		results.append(manager.add_recipe("r3", "Tomato soup", ["tomato", "water"]))           # 2
		results.append(manager.add_recipe("r10", "Miso Soup", []))                             # 0
		results.append(manager.add_recipe("r4", "Sushi", ["rice", "fish"]))                    # doesn't match "soup"

		results.append(manager.search_recipes("SOUP"))
		results.append(manager.search_recipes("dum"))
		results.append(manager.search_recipes("xyz"))

		results.append(manager.get_all_recipes())

		expected = [
		  True, True, True, True, True,
		  # search "SOUP": sort by ingredient count, then id
		  [
		    {"id": "r10", "name": "Miso Soup", "ingredients": []},
		    {"id": "r1", "name": "Soup Dumplings", "ingredients": ["pork"]},
		    {"id": "r3", "name": "Tomato soup", "ingredients": ["tomato", "water"]},
		    {"id": "r2", "name": "Chicken Soup", "ingredients": ["chicken", "water", "salt"]}
		  ],
		  [
		    {"id": "r1", "name": "Soup Dumplings", "ingredients": ["pork"]}
		  ],
		  [],
		  # all recipes sorted by (#ingredients asc, id asc)
		  [
		    {"id": "r10", "name": "Miso Soup", "ingredients": []},
		    {"id": "r1", "name": "Soup Dumplings", "ingredients": ["pork"]},
		    {"id": "r3", "name": "Tomato soup", "ingredients": ["tomato", "water"]},
		    {"id": "r4", "name": "Sushi", "ingredients": ["rice", "fish"]},
		    {"id": "r2", "name": "Chicken Soup", "ingredients": ["chicken", "water", "salt"]}
		  ]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 2 B------------------")
		manager = ReciptManagerLvl2()

		results = []

		results.append(manager.add_recipe("2", "Apple Pie", ["apple", "flour"]))     # 2
		results.append(manager.add_recipe("10", "Pineapple Pie", ["pineapple"]))     # 1
		results.append(manager.add_recipe("1", "Pie Crust", ["flour"]))              # 1

		results.append(manager.search_recipes("pie"))
		# tie: "10" and "1" both have 1 ingredient, sort by recipe_id lexicographically: "1" < "10" < "2"

		results.append(manager.update_recipe("2", "APPLE PIE", ["apple"]))           # same recipe name allowed (case-insensitive), ingredients now 1
		results.append(manager.search_recipes("pie"))

		expected = [
		  True, True, True,
		  [
		    {"id": "1", "name": "Pie Crust", "ingredients": ["flour"]},
		    {"id": "10", "name": "Pineapple Pie", "ingredients": ["pineapple"]},
		    {"id": "2", "name": "Apple Pie", "ingredients": ["apple", "flour"]}
		  ],
		  True,
		  [
		    {"id": "1", "name": "Pie Crust", "ingredients": ["flour"]},
		    {"id": "10", "name": "Pineapple Pie", "ingredients": ["pineapple"]},
		    {"id": "2", "name": "APPLE PIE", "ingredients": ["apple"]}
		  ]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

	def test_lvl3(self):
		print("------------------------------------------")
		print("------------Run test level 3 A------------------")
		manager = ReciptManagerLvl3()

		results = []

		results.append(manager.add_user("u1", "Alice"))
		results.append(manager.add_user("u2", "Bob"))
		results.append(manager.add_user("u1", "Eve"))  # id conflict

		results.append(manager.add_recipe("r1", "Tacos", ["tortilla", "beef"]))
		results.append(manager.add_recipe("r2", "Burrito", ["tortilla", "beans"]))

		results.append(manager.edit_recipe("missing", "r1", "Tacos Supreme", ["tortilla"])) # invalid user
		results.append(manager.edit_recipe("u1", "missing", "X", []))                       # invalid recipe
		results.append(manager.edit_recipe("u1", "r1", "Burrito", ["tortilla"]))            # name conflict with r2
		results.append(manager.edit_recipe("u1", "r1", "TACOS", ["tortilla"]))              # same recipe keeps its own name ok
		results.append(manager.get_recipe("r1"))

		expected = [
		  True, True, False,
		  True, True,
		  False, False, False, True,
		  {"id": "r1", "name": "TACOS", "ingredients": ["tortilla"]}
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 3 B------------------")
		manager = ReciptManagerLvl3()

		results = []

		results.append(manager.add_user("u1", "A"))
		results.append(manager.add_recipe("a", "Soup A", ["x", "y", "z"]))  # 3
		results.append(manager.add_recipe("b", "Soup B", ["x"]))            # 1

		results.append(manager.search_recipes("soup"))  # b then a

		results.append(manager.edit_recipe("u1", "a", "Soup A", []))        # now 0 ingredients
		results.append(manager.search_recipes("soup"))                      # a then b now

		expected = [
		  True, True, True,
		  [
		    {"id": "b", "name": "Soup B", "ingredients": ["x"]},
		    {"id": "a", "name": "Soup A", "ingredients": ["x", "y", "z"]}
		  ],
		  True,
		  [
		    {"id": "a", "name": "Soup A", "ingredients": []},
		    {"id": "b", "name": "Soup B", "ingredients": ["x"]}
		  ]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

	def test_lvl4(self):
		print("------------------------------------------")
		print("------------Run test level 4 A------------------")
		manager = ReciptManagerLvl4()

		results = []

		results.append(manager.add_user("u1", "A"))
		results.append(manager.add_recipe("r1", "Pasta", ["noodles"]))
		results.append(manager.edit_recipe("u1", "r1", "Spaghetti", ["noodles", "sauce"]))
		results.append(manager.edit_recipe("u1", "r1", "Pasta", ["noodles", "egg"]))  # allowed: name uniqueness across recipes, not within history

		results.append(manager.get_recipe("r1"))
		results.append(manager.get_recipe_history("r1"))
		results.append(manager.get_recipe_history("missing"))

		expected = [
		  True,
		  True,
		  True,
		  True,
		  {"id": "r1", "name": "Pasta", "ingredients": ["noodles", "egg"]},
		  [
		    {"id": "r1", "name": "Pasta", "ingredients": ["noodles"]},                 # v1
		    {"id": "r1", "name": "Spaghetti", "ingredients": ["noodles", "sauce"]},    # v2
		    {"id": "r1", "name": "Pasta", "ingredients": ["noodles", "egg"]}           # v3
		  ],
		  None
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 4 B------------------")
		manager = ReciptManagerLvl4()

		results = []

		results.append(manager.add_user("u1", "A"))
		results.append(manager.add_recipe("r1", "Toast", ["bread"]))
		results.append(manager.edit_recipe("u1", "r1", "French Toast", ["bread", "egg"]))
		results.append(manager.rollback_recipe("u1", "r1", 1))  # -> v3 copy of v1

		results.append(manager.get_recipe("r1"))
		results.append(manager.get_recipe_history("r1"))

		expected = [
		  True,
		  True,
		  True,
		  True,
		  {"id": "r1", "name": "Toast", "ingredients": ["bread"]},
		  [
		    {"id": "r1", "name": "Toast", "ingredients": ["bread"]},                  # v1
		    {"id": "r1", "name": "French Toast", "ingredients": ["bread", "egg"]},    # v2
		    {"id": "r1", "name": "Toast", "ingredients": ["bread"]}                   # v3 rollback copy
		  ]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 4 C------------------")
		manager = ReciptManagerLvl4()

		results = []

		results.append(manager.add_user("u1", "A"))

		results.append(manager.add_recipe("r1", "Pasta", ["a"]))
		results.append(manager.edit_recipe("u1", "r1", "Spaghetti", ["b"]))          # r1 history: v1 Pasta, v2 Spaghetti (current=Spaghetti)

		results.append(manager.add_recipe("r2", "Pasta", ["x"]))                     # allowed because r1 current is Spaghetti now

		results.append(manager.rollback_recipe("u1", "r1", 1))                       # try restore old name "Pasta" -> conflicts with r2 current "Pasta"
		results.append(manager.get_recipe("r1"))
		results.append(manager.get_recipe_history("r1"))

		expected = [
		  True,
		  True,
		  True,
		  True,
		  False,
		  {"id": "r1", "name": "Spaghetti", "ingredients": ["b"]},
		  [
		    {"id": "r1", "name": "Pasta", "ingredients": ["a"]},                     # v1
		    {"id": "r1", "name": "Spaghetti", "ingredients": ["b"]}                  # v2 (no v3 because rollback failed)
		  ]
		]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

		print("------------------------------------------")
		print("------------Run test level 4 D------------------")
		manager = ReciptManagerLvl4()

		results = []

		results.append(manager.add_user("u1", "A"))
		results.append(manager.add_recipe("r1", "Tea", ["water"]))
		results.append(manager.edit_recipe("u1", "r1", "Milk Tea", ["water", "milk"]))

		results.append(manager.rollback_recipe("missing", "r1", 1))  # invalid user
		results.append(manager.rollback_recipe("u1", "missing", 1))  # invalid recipe
		results.append(manager.rollback_recipe("u1", "r1", 99))       # invalid version

		expected = [True, True, True, False, False, False]

		print(f"expected {expected}")
		print(f"actual {results}")
		print(expected == results)

test = Test()
test.test_lvl1()
test.test_lvl2()
test.test_lvl3()
test.test_lvl4()





