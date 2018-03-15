from random import randint
from tabulate import tabulate
import operator, re, os

roster = {}
cmd_list = ["init", "roll", "end", "load", "save", "add", "roster", "hp", "sethp", "damage", "next", "start", "turn", "quit"]
dice_pattern = re.compile(r"(\d+)d(\d+)\s*([+\-]\s*\d+)?")

def roll(dice):
	dice = dice_pattern.match(dice)
	num = int(dice[1])
	type = int(dice[2])
	mod = dice[3]
	if not mod:
		mod = "+0"
	total = 0
	for x in range(num):
		total += randint(1,type)
	return eval(str(total) + mod)

def d20(mod):
	return roll("1d20+" + str(mod))

def initiative(number, name, mod):
	name = name.lower().capitalize()
	global roster
	for x in range(int(number)):
		roster[name + " " + str(x + 1)] = { "initiative": d20(mod) }

def roster_add(name, initiative):
	global roster
	roster[name.lower().capitalize()] = { "initiative": int(initiative) }

def roll_hp(name, dice):
	global roster
	name = name.lower().capitalize()
	for character in roster:
		if name in character:
			roster[character]["max_hp"] = roll(dice)
			roster[character]["hp"] = roster[character]["max_hp"]

def set_hp(name, hp):
	global roster
	name = name.lower().capitalize()
	try:
		roster[name]["max_hp"] = int(hp)
		roster[name]["hp"] = int(hp)
	except KeyError:
		print("NAME NOT FOUND")

def damage(name, dmg):
	global roster
	name = name.lower().capitalize()
	try:
		roster[name]["hp"] -= int(dmg)
		if roster[name]["hp"] <= 0:
			print(name + " is down!")
			roster.pop(name)
	except KeyError:
		print("NAME NOT FOUND")

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

def save(filename):
	filename.replace(" ", "_")
	if ".dnd" != filename[-4:]:
		filename += ".dnd"
	with open(filename, "w+") as f:
		for character in roster:
			name = character
			character = roster[character]
			f.write(name + "||" + str(character["initiative"]))
			try:
				f.write("||" + str(character["hp"]) + "||" + str(character["max_hp"]) + "\n")
			except KeyError:
				f.write("\n")

def load(filename):
	global roster
	filename.replace(" ", "_")
	if ".dnd" != filename[-4:]:
		filename += ".dnd"
	try:
		with open(filename, "r") as f:
			lines = f.readlines()
		roster = {}
		for character in lines:
			character = character.split("||")
			roster[character[0]] = { "initiative": int(character[1]) }
			try:
				roster[character[0]]["hp"] = character[2]
				roster[character[0]]["max_hp"] = character[3]
			except IndexError:
				pass
	except FileNotFoundError:
		print("No file by that name!")

def get_initiative_order():
	global roster
	sorted_roster = sorted(roster.items(), key=lambda x: x[1]["initiative"],reverse=True)
	order = [character[0] for character in sorted_roster]
	return order

turn = 0

while True:
	command = input("> ")
	try:
		cmd = command.split()[0]
		if cmd == "roll":
			print(roll(dice_pattern.search(command)[0]))
		elif cmd == "end":
			roster = {}
		elif cmd == "load":
			try:
				load(command.split()[1])
			except IndexError:
				filename = input("Load File: ")
				load(filename)
		elif cmd == "save":
			try:
				save(command.split()[1])
			except IndexError:
				filename = input("Save As: ")
				save(filename)
		elif cmd == "init":
			try:
				command = command.split()
				num = command[1]
				name = command[2]
				mod = command[3]
				initiative(num, name, mod)
			except IndexError:
				print("Not enough arguments!")
		elif cmd == "hp":
			try:
				dice = dice_pattern.search(command)[0]
				command = command.split()
				name = command[1]
				roll_hp(name, dice)
			except IndexError:
				print("Not enough arguments!")
		elif cmd == "add":
			try:
				command = command.split()
				name = command[1]
				initiative = command[2]
				roster_add(name, initiative)
				order = get_initiative_order()
			except IndexError:
				print("Not enough arguments!")
		elif cmd == "roster":
			get_roster()
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
		elif cmd == "sethp":
			try:
				command = command.split()
				name = command[1]
				hp = command[2]
				set_hp(name, hp)
			except IndexError:
				print("Not enough arguments!")
		elif cmd == "next":
			if turn == len(order) - 1:
				turn = 0
				print("TOP OF THE ROUND!")
			else:
				turn += 1
			turn_name = order[turn]
			print(turn_name + "'s turn!")
		elif cmd == "start":
			turn_name = order[turn]
			print(turn_name + "'s turn!")
		elif cmd == "turn":
			turn = int(command.split()[1])
		elif cmd == "help":
			for entry in cmd_list:
				print(entry)
		elif cmd == "quit":
			quit()
		else:
			print("INVALID COMMAND")
	except IndexError:
		print("INVALID COMMAND")