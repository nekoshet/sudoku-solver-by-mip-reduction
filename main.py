from mip.model import *

# init mlp model
m = Model()

# init model variables
matrix = [[[m.add_var(var_type=BINARY) for digit in range(9)] for column in range(9)] for row in range(9)]

# add constraints
# add one digit per square constraints
for row in range(9):
	for column in range(9):
		m += xsum(matrix[row][column][digit] for digit in range(9)) <= 1
		m += xsum(matrix[row][column][digit] for digit in range(9)) >= 1

# no double digits in row constraint
for row in range(9):
	for digit in range(9):
		m += xsum(matrix[row][column][digit] for column in range(9)) <= 1

# no double digits in column constraint
for column in range(9):
	for digit in range(9):
		m += xsum(matrix[row][column][digit] for row in range(9)) <= 1

# no double digits in 'box' constraint
for box_top in range(0, 7, 3):
	for box_left in range(0, 7, 3):
		for digit in range(9):
			m += xsum(matrix[box_top + (i // 3)][box_left + (i % 3)][digit] for i in range(9)) <= 1

# add predefined digits constraints
f = open("hardest.txt", "r")
rows = f.readlines()
f.close()
for row in range(9):
	for column in range(9):
		char = rows[row][column]
		if char.isdigit():
			m += matrix[row][column][int(char) - 1] >= 1

# configure and solve
m.emphasis = 1 # search for feasible first
m.max_solutions = 1 # stop when a solution is found
status = m.optimize(max_seconds=5)

# print solution
for row in range(9):
	for column in range(9):
		for digit in range(9):
			if matrix[row][column][digit].x == 1:
				print(digit + 1, end = " ")
	print()
