from random import randint		# Dice rolling
from tabulate import tabulate		# Pretty-printing the roster
from os import listdir			# List files that can be loaded
from re import compile			# Regexing "dice pattern"

roster = {}

# for the "help" command
cmd_list = ["init", "roll", "end", "load", "save", "add", "roster", "hp", "sethp", "damage", "next", "start", "turn", "quit"]

# finds strings that look like "4d5" or "10d6 + 7"
dice_pattern = compile(r"(\d+)d(\d+)(\s*[+-]\s*\d+)?")

# given a "XdY" string (with or without "+ Z"), rolls X dice that have Y sides and adds Z to the result 
def roll(dice):
	dice = dice_pattern.match(dice)
	num = int(dice[1])	# the number of dice to roll
	die = int(dice[2])	# the maximum number on each die
	mod = dice[3]	# the modifier to add to the roll
	total = 0
	for x in range(num):	# roll 'em
		total += randint(1,die)
	return eval(str(total) + mod)

# rolls the most common dice roll
def d20(mod):
	result = roll("1d20")
	if result == 1:
		print("CRITICAL FAILURE")
	elif result == 20:
		print("CRITICAL SUCCESS!")
	return result + mod

# roll initiative for [number] of [name]s with a modifier of [mod]
def initiative(number, name, mod):
	name = name.lower().capitalize()	# standardize the names
	global roster
	# create "[name] 1", "[name] 2", etc. with separate initiatives  
	for x in range(int(number)):
		roster[name + " " + str(x + 1)] = { "initiative": d20(mod) }

# manually add someone to the roster with a given initiative
def roster_add(name, initiative):
	global roster
	roster[name.lower().capitalize()] = { "initiative": int(initiative) }

# roll hp using [dice](can include a modifier) for a number of monsters with [name]
def roll_hp(name, dice):
	global roster
	name = name.lower().capitalize()
	for character in roster:
		if name in character:
			roster[character]["max_hp"] = roll(dice)
			roster[character]["hp"] = roster[character]["max_hp"]

# manually set hp for one entry in the roster
def set_hp(name, hp):
	global roster
	name = name.lower().capitalize()
	try:
		roster[name]["max_hp"] = int(hp)
		roster[name]["hp"] = int(hp)
	except KeyError:
		print("NAME NOT FOUND")

# deal damage to a monster on the roster
def damage(name, dmg):
	global roster
	name = name.lower().capitalize()
	try:
		roster[name]["hp"] -= int(dmg)
		# if they go down, delete them from the initiative order
		if roster[name]["hp"] <= 0:
			print(name + " is down!")
			roster.pop(name)
	except KeyError:
		print("NAME NOT FOUND")

# print out the full roster in initiative order
def get_roster():
	sorted_roster = sorted(roster.items(), key=lambda x: x[1]["initiative"], reverse=True)
	final_roster = []
	for character in sorted_roster:
		to_add = [character[0], character[1]["initiative"]]
		try:
			to_add.extend([str(character[1]["hp"]), str(character[1]["max_hp"])])
		except KeyError:
			pass
		final_roster.append(to_add)
	print(tabulate(final_roster, headers=["Name","Init","HP", "Max"]))

# save roster as a file for pre-building encounters
def save(filename):
	filename.replace(" ", "_")	# spaces in a filename make parsing commands tricky, so just avoid it.
	if ".dnd" != filename[-4:]:
		filename += ".dnd"
	with open(filename, "w+") as f:
		# go through each character and write them a line in the file 
		for character in roster:
			name = character
			character = roster[character]
			f.write(name + "||" + str(character["initiative"]))	# since spaces can show up in character names, split by ||
			try:
				# if they have hp, store that
				f.write("||" + str(character["hp"]) + "||" + str(character["max_hp"]) + "\n")
			except KeyError:
				# otherwise forget it
				f.write("\n")

# load a file
def load(filename):
	global roster
	if filename == "help":			# list files that are able to be loaded
		files = [f for f in listdir() if ".dnd" in f[-4:]]
		for entry in files:
			print(entry)
	filename.replace(" ", "_")	# spaces in filenames. ick.
	if ".dnd" != filename[-4:]:
		filename += ".dnd"
	try:
		with open(filename, "r") as f:
			lines = f.readlines()
		roster = {}
		for character in lines:
			character = character.split("||")
			name = character[0]
			roster[name] = { "initiative": int(character[1]) }
			try:
				roster[name]["hp"] = character[2]
				roster[name]["max_hp"] = character[3]
			except IndexError:
				pass
	except FileNotFoundError:
		print("No file by that name!")

# create the list of intiative order
def get_initiative_order():
	global roster
	# since dictionaries are unordered, this returns an ordered list of tuples with the highest initiative at the front
	sorted_roster = sorted(roster.items(), key=lambda x: x[1]["initiative"],reverse=True)
	order = [character[0] for character in sorted_roster]
	return order

turn = 0

while True:
	# all commands start with the command and then have options loaded into them like bash
	command = input("> ")
	try:
		cmd = command.split()[0]	# get the first word in a command
		# roll dice
		if cmd == "roll":
			print(roll(dice_pattern.search(command)[0]))
		# end combat, clearing the roster
		elif cmd == "end":
			roster = {}
			order = []
			turn = 0
		# load a saved roster
		elif cmd == "load":
			try:
				load(command.split()[1])
			except IndexError:
				filename = input("Load File: ")
				load(filename)
			order = get_initiative_order()
		# save the current roster
		elif cmd == "save":
			try:
				save(command.split()[1])
			except IndexError:
				filename = input("Save As: ")
				save(filename)
		# roll initiative
		elif cmd == "init":
			try:
				command = command.split()
				num = command[1]		# number of the creatures to roll
				name = command[2]		# name of the creature to rol
				mod = command[3]		# modifier to their initiative
				initiative(num, name, mod)
				order = get_initiative_order()
			except IndexError:
				print("Not enough arguments!")
		# roll hp
		elif cmd == "hp":
			try:
				dice = dice_pattern.search(command)[0]	# dice + mod to roll for hp
				command = command.split()
				name = command[1]			# name of the type of creature to roll hp for
				roll_hp(name, dice)
			except IndexError:
				print("Not enough arguments!")
		# manually add a person to the roster
		elif cmd == "add":
			try:
				command = command.split()
				name = command[1]
				init = command[2]
				roster_add(name, init)
				order = get_initiative_order()
			except IndexError:
				print("Not enough arguments!")
		elif cmd == "roster":
			get_roster()
		# give damage to a person
		elif cmd == "damage":
			try:
				command = command.split()
				if len(command) == 3:
					name = command[1]
					damage = command[2]
				else:
					name = " ".join([command[1], command[2]])
					dmg = command[3]
				damage(name, dmg)
				if len(roster) < len(order):
					order.remove(name.lower().capitalize())
			except IndexError:
				print("Not enough arguments!")
		# manually set a creature's hp
		elif cmd == "sethp":
			try:
				command = command.split()
				name = command[1]
				hp = command[2]
				set_hp(name, hp)
			except IndexError:
				print("Not enough arguments!")
		# move on to the next turn in the initiative order
		elif cmd == "next":
			if turn == len(order) - 1:
				turn = 0
				print("TOP OF THE ROUND!")
			else:
				turn += 1
			turn_name = order[turn]
			print(turn_name + "'s turn!")
		# start combat
		elif cmd == "start":
			turn_name = order[turn]
			print(turn_name + "'s turn!")
		# set it to be someone's turn
		elif cmd == "turn":
			turn = int(command.split()[1])
		elif cmd == "help":
			for entry in cmd_list:
				print(entry)
		elif cmd == "quit":
			quit()
		else:
			print("INVALID COMMAND")
	# catch an empty string
	except IndexError:
		if turn == len(order) - 1:
				turn = 0
				print("TOP OF THE ROUND!")
		else:
			turn += 1
		turn_name = order[turn]
		print(turn_name + "'s turn!")
