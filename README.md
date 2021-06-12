# Sudoku Solver by MIP Reduction
A sudoku solver based on a reduction to Integer Programming. Written in Python. Uses Python MIP.

# How to use
1. Make sure you have Python MIP installed
2. Create a text file representing your sudoku. The file must have 9 lines, each line having 9 characters + end-of-line char ('\n'). Use digits to represent a square with a predefined digit and '-' to represent empty squares.
3. Run the program using python 3 - usage: sudoku_solver.py [-h] [-t timeout] [-v verbose] input_file
4. The result will be printed.

# How it works
The program creates an Integer Program representing this specific sudoku problem. The program has 9x9x9 binary variables - a binary variable for each square and digit, representing whether this square is filled with this digit or not. The constraints are as follows:
1. Each square contains exactly one digit (no more, no less)
2. Each row must contain each digit exactly once
3. Each column must contain each digit exactly once
4. Each 3x3 'box' must contain each digit exactly once
5. Each square with a predefined digit in the sudoku file must contain this digit (and no other digit).

The objective function is irelevant. The goal is to find a feasible solution to the program and the model is tuned to stop after finding a feasible solution.

The model is then optimized using python MIP, and the result is printed to the screen. A value of 1 to a variable of square x,y and digit d indicates that square x,y is to be filled with digit d. Because of our constraints, we are ensured that there will be exactly one variable with value 1 for each square.

# Author
Tal Levy
