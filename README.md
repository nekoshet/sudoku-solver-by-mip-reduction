# sudoku-solver-by-mip-reduction
A sudoku solver based on a reduction to Integer Programming. Written in Python. Uses Python MIP.

# How to use
1. Make sure you have Python MIP installed
2. Create a text file representing your sudoku. The file must have 9 lines, each line having 9 characters + end-of-line char ('\n'). Use digits to represent a square with a predefined digit and '-' to represent empty squares.
3. Replace the path in 'f.open(...)' with your file's path.
4. Run the script using python

# How it works
The script creates an Integer Program representing this specific sudoku problem. The program has 9*9*9 binary variables - a binary variable for each square and digit, representing whether this square is filled with this digit or not. The constraints are as follows:
1. Each square contains exactly one digit (no more, no less)
2. Each row must not contain the same digit more than once.
3. Each column must not contain the same digit more than once.
4. Each 3x3 'box' must not contain the same digit more than once.

The object function is irelevant. The object is to find a feasible solution to the program.
The model is tuned to stop after finding a feasible solution.

The model is then optimized using python MIP, and the result is printed to the screen. A value of 1 to a variable of square x,y and digit d indicates that square x,y is to be filled with digit d. Because of our constraints, we are ensured that there will be exactly one variable with value 1 for each square.

In case of no solution, the script will raise an exception.

# Author
Tal Levy
