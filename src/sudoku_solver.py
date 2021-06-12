import mip
from typing import List
import argparse
from itertools import product

# constants
######################################
TIMEOUT_SECONDS_DEFAULT = 2
MIP_VERBOSE_DEFAULT = 0

# types
######################################
SudokuVariableTensor = List[List[List[mip.Var]]]
SudokuMatrix = List[List[str]]


# read and parse file functions
######################################
# convert list of string lines to a matrix of characters
def matrix_from_lines(lines: List[str]) -> SudokuMatrix:
    return [[c for c in line] for line in lines]


# parse sudoku matrix - verify contents and return
def parse_sudoku(sudoku_lines: List[str]) -> SudokuMatrix:
    # convert sudoku lines to matrix
    sudoku = matrix_from_lines(sudoku_lines)

    # check 9 rows
    assert len(sudoku) == 9

    # check all rows contain 9 characters
    for line in sudoku:
        assert len(line) == 9

    # check all characters are either a digit or a '-'
    for line in sudoku:
        for character in line:
            assert character.isdigit() or character == '-'

    # return lines
    return sudoku


# read file and return as list of lines
def read_file_lines(path: str) -> List[str]:
    with open(path, 'r') as file:
        return file.read().splitlines()


# read a sudoku file and return a matrix of digits/'-'
def read_sudoku_file(path: str) -> SudokuMatrix:
    sudoku_lines = read_file_lines(path)
    return parse_sudoku(sudoku_lines)


# build model functions
######################################
# allow exactly one digit in each square
def add_single_digit_constraints(model: mip.Model, variable_tensor: SudokuVariableTensor) -> None:
    for row in range(9):
        for column in range(9):
            model += mip.xsum(variable_tensor[row][column][digit] for digit in range(9)) == 1


# don't allow a double occurrence of a digit in a row
def add_no_double_digit_in_row_constraints(model: mip.Model, variable_tensor: SudokuVariableTensor) -> None:
    for row in range(9):
        for digit in range(9):
            model += mip.xsum(variable_tensor[row][column][digit] for column in range(9)) == 1


# don't allow a double occurrence of a digit in a column
def add_no_double_digit_in_column_constraints(model: mip.Model, variable_tensor: SudokuVariableTensor) -> None:
    for column in range(9):
        for digit in range(9):
            model += mip.xsum(variable_tensor[row][column][digit] for row in range(9)) == 1


# don't allow a double occurrence of a digit in a 3x3 box
def add_no_double_digit_in_box_constraints(model: mip.Model, variable_tensor: SudokuVariableTensor) -> None:
    for box_top in range(0, 7, 3):
        for box_left in range(0, 7, 3):
            for digit in range(9):
                model += mip.xsum(variable_tensor[box_top + row_shift][box_left + column_shift][digit]
                                  for row_shift, column_shift in product(range(3), repeat=2)) == 1


# add the constraints common to all sudoku problems - one digit per square, no double occurrence in a row/column/box
def add_general_sudoku_constraints(model: mip.Model, variable_tensor: SudokuVariableTensor) -> None:
    add_single_digit_constraints(model, variable_tensor)
    add_no_double_digit_in_row_constraints(model, variable_tensor)
    add_no_double_digit_in_column_constraints(model, variable_tensor)
    add_no_double_digit_in_box_constraints(model, variable_tensor)


# add the constraints unique to this sudoku - in squares with a predefined digit, force the square to contain the digit
def add_predefined_digits_constraints(model: mip.Model, variable_tensor: SudokuVariableTensor,
                                      sudoku: SudokuMatrix) -> None:
    for row in range(9):
        for column in range(9):
            char = sudoku[row][column]
            if char.isdigit():
                model += variable_tensor[row][column][int(char) - 1] == 1


# add variables to the model and return them as a 3D tensor
# 1st dimension = rows, 2nd dimension = column, 3rd dimension = digits
def init_model_variables(model: mip.Model) -> SudokuVariableTensor:
    return [[[model.add_var(var_type=mip.BINARY) for _ in range(9)] for _ in range(9)] for _ in range(9)]


# create an mip model for the sudoku problem and return the model and the variable tensor
def create_model(sudoku: SudokuMatrix, verbose: int) -> (mip.Model, SudokuVariableTensor):
    model = mip.Model()
    model.verbose = verbose

    variable_tensor = init_model_variables(model)
    add_general_sudoku_constraints(model, variable_tensor)
    add_predefined_digits_constraints(model, variable_tensor, sudoku)
    return model, variable_tensor


# print sudoku variable tensor as sudoku
def print_variable_tensor(variable_tensor: SudokuVariableTensor) -> None:
    for row in range(9):
        for column in range(9):
            for digit in range(9):
                if variable_tensor[row][column][digit].x == 1:
                    print(digit + 1, end=" ")
        print()


# handle the result of the Python MIP optimization of the problem
def handle_optimization_result(optimization_status: mip.OptimizationStatus,
                               variable_tensor: SudokuVariableTensor) -> None:
    # check no impossible status
    assert optimization_status not in {mip.OptimizationStatus.CUTOFF, mip.OptimizationStatus.UNBOUNDED}

    # handle possible statuses
    # error
    if optimization_status == mip.OptimizationStatus.ERROR:
        print('Python MIP encountered an error while trying to solve the problem.')

    # proven no solution exists
    if optimization_status in {mip.OptimizationStatus.INFEASIBLE, mip.OptimizationStatus.INT_INFEASIBLE}:
        print('No solution exists for this sodoku')

    # not enough time was given
    if optimization_status in {mip.OptimizationStatus.LOADED, mip.OptimizationStatus.NO_SOLUTION_FOUND}:
        print('The given time was not enough to solve the sodoku')

    # solution found
    if optimization_status in {mip.OptimizationStatus.FEASIBLE, mip.OptimizationStatus.OPTIMAL}:
        print('A solution was found. solution:')
        print_variable_tensor(variable_tensor)


# solve the sudoku in path $path given %timeout_seconds seconds
def solve_sudoku(path: str, timeout_seconds, mip_verbose: int) -> None:
    # read sudoku
    sudoku = read_sudoku_file(path)

    # initialize an mip model
    model, variable_tensor = create_model(sudoku, mip_verbose)

    # log solve start
    print(f'Solving sudoku at path {path}, given a timeout of {timeout_seconds} seconds with verbosity {mip_verbose}')

    # solve model
    optimization_status = model.optimize(max_seconds=timeout_seconds, max_solutions=1)

    # handle status
    handle_optimization_result(optimization_status, variable_tensor)


# create command line parser
def create_parser() -> argparse.ArgumentParser:
    # init parser
    parser = argparse.ArgumentParser()

    # add input file argument
    parser.add_argument('ifile', type=str, help='sudoku to solve', metavar='input_file')

    # add timeout argument
    parser.add_argument('-t', '--timeout', type=float, default=TIMEOUT_SECONDS_DEFAULT,
                        help="number of seconds (or fraction) allowed for the solver's computation", metavar='timeout')

    # add mip verbose argument
    parser.add_argument('-v', '--verbose', type=int, default=MIP_VERBOSE_DEFAULT,
                        help='verbosity level of Python MIP solver', metavar='verbose')

    return parser


# main function
def main() -> None:
    # create parser
    parser = create_parser()

    # parse command line arguments
    namespace = parser.parse_args()

    # solve sudoku
    solve_sudoku(namespace.ifile, namespace.timeout, namespace.verbose)


# if main module, run main
if __name__ == "__main__":
    main()
